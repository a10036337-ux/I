#!/usr/bin/env python3
"""Download images referenced by LURL ``canvas_img(...)`` calls.

The tool is intentionally designed for pages you are allowed to access.  It can
submit a password that you provide, then extracts all image URLs embedded in
JavaScript calls such as::

    canvas_img('https://r2limit2.lurl.cc/...jpg', 'canvas_1', '0');

No password guessing, brute forcing, or access-control bypass is performed.
"""

from __future__ import annotations

import argparse
import getpass
import html
import os
import posixpath
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Iterable

DEFAULT_URL = "https://lurl.cc/TxqzI"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
CANVAS_IMG_RE = re.compile(
    r"canvas_img\(\s*([\"'])(?P<url>https?:\\?/\\?/[^\"']+)\1",
    re.IGNORECASE,
)


@dataclass
class InputField:
    name: str | None = None
    value: str = ""
    input_type: str = "text"
    field_id: str | None = None


@dataclass
class FormInfo:
    action: str | None = None
    method: str = "get"
    inputs: list[InputField] = field(default_factory=list)


class FormParser(HTMLParser):
    """Small form parser sufficient for password forms and hidden fields."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.forms: list[FormInfo] = []
        self._current: FormInfo | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "form":
            self._current = FormInfo(
                action=attr.get("action") or None,
                method=(attr.get("method") or "get").lower(),
            )
            return
        if tag.lower() == "input" and self._current is not None:
            self._current.inputs.append(
                InputField(
                    name=attr.get("name") or None,
                    value=attr.get("value") or "",
                    input_type=(attr.get("type") or "text").lower(),
                    field_id=attr.get("id") or None,
                )
            )

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "form" and self._current is not None:
            self.forms.append(self._current)
            self._current = None


def fetch(opener: urllib.request.OpenerDirector, url: str, *, referer: str | None = None) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(url, headers=headers)
    with opener.open(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def select_password_form(forms: list[FormInfo]) -> FormInfo | None:
    for form in forms:
        for input_field in form.inputs:
            haystack = " ".join(
                value for value in (input_field.name, input_field.field_id, input_field.input_type) if value
            ).lower()
            if input_field.input_type == "password" or "password" in haystack:
                return form
    return None


def build_password_payload(form: FormInfo | None, password: str) -> dict[str, str]:
    if form is None:
        return {"password": password}

    payload: dict[str, str] = {}
    password_field_name: str | None = None
    for input_field in form.inputs:
        if not input_field.name:
            continue
        if input_field.input_type in {"submit", "button", "image", "file"}:
            continue
        haystack = " ".join(
            value for value in (input_field.name, input_field.field_id, input_field.input_type) if value
        ).lower()
        if password_field_name is None and (
            input_field.input_type == "password" or "password" in haystack
        ):
            password_field_name = input_field.name
            payload[input_field.name] = password
        else:
            payload[input_field.name] = input_field.value

    if password_field_name is None:
        payload["password"] = password
    return payload


def submit_password(
    opener: urllib.request.OpenerDirector,
    page_url: str,
    page_html: str,
    password: str,
) -> str:
    parser = FormParser()
    parser.feed(page_html)
    form = select_password_form(parser.forms)
    payload = build_password_payload(form, password)
    action = urllib.parse.urljoin(page_url, form.action) if form and form.action else page_url
    method = (form.method if form else "post").lower()
    encoded = urllib.parse.urlencode(payload).encode("utf-8")

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": page_url,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml",
    }
    if method == "get":
        separator = "&" if urllib.parse.urlsplit(action).query else "?"
        action = f"{action}{separator}{encoded.decode('ascii')}"
        data = None
    else:
        data = encoded
    request = urllib.request.Request(action, data=data, headers=headers)
    with opener.open(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_canvas_image_urls(page_html: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for match in CANVAS_IMG_RE.finditer(page_html):
        url = html.unescape(match.group("url")).replace("\\/", "/")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def safe_filename(url: str, index: int) -> str:
    path = urllib.parse.urlsplit(url).path
    name = posixpath.basename(path) or f"image_{index:03d}"
    name = urllib.parse.unquote(name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    if not name:
        name = f"image_{index:03d}"
    stem, suffix = os.path.splitext(name)
    return f"{index:03d}_{stem}{suffix or '.jpg'}"


def download_images(
    opener: urllib.request.OpenerDirector,
    urls: Iterable[str],
    out_dir: Path,
    referer: str,
    delay: float,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for index, url in enumerate(urls, start=1):
        target = out_dir / safe_filename(url, index)
        headers = {"User-Agent": USER_AGENT, "Referer": referer, "Accept": "image/*,*/*;q=0.8"}
        request = urllib.request.Request(url, headers=headers)
        with opener.open(request, timeout=60) as response, target.open("wb") as fh:
            fh.write(response.read())
        saved.append(target)
        print(f"downloaded {url} -> {target}")
        if delay > 0:
            time.sleep(delay)
    return saved


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unlock an authorized LURL page and download every image URL inside canvas_img(...)."
    )
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help=f"LURL page URL (default: {DEFAULT_URL})")
    parser.add_argument("-p", "--password", help="Password for the page. If omitted, you will be prompted when needed.")
    parser.add_argument("-o", "--out-dir", default="downloads", help="Directory for downloaded images.")
    parser.add_argument("--html-file", help="Read HTML from a local file instead of fetching the URL.")
    parser.add_argument("--save-html", help="Save the fetched/unlocked HTML for debugging.")
    parser.add_argument("--list-only", action="store_true", help="Only print image URLs; do not download files.")
    parser.add_argument("--no-password", action="store_true", help="Do not submit a password; parse the fetched page as-is.")
    parser.add_argument("--delay", type=positive_float, default=0.2, help="Delay in seconds between image downloads.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    try:
        if args.html_file:
            page_html = Path(args.html_file).read_text(encoding="utf-8")
        else:
            page_html = fetch(opener, args.url)
            if not args.no_password:
                password = args.password
                if password is None:
                    password = getpass.getpass("LURL password (leave empty to skip): ")
                if password:
                    page_html = submit_password(opener, args.url, page_html, password)

        if args.save_html:
            Path(args.save_html).write_text(page_html, encoding="utf-8")

        urls = extract_canvas_image_urls(page_html)
        if not urls:
            print("No canvas_img image URLs were found.", file=sys.stderr)
            print("If the page is password protected, rerun with --password or provide post-unlock HTML via --html-file.", file=sys.stderr)
            return 2

        for url in urls:
            print(url)

        if args.list_only:
            return 0

        saved = download_images(opener, urls, Path(args.out_dir), args.url, args.delay)
        print(f"Saved {len(saved)} file(s) to {Path(args.out_dir).resolve()}")
        return 0
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
