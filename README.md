# LURL canvas image crawler

This repository contains a small Python crawler for LURL pages that render
images through JavaScript calls such as:

```js
canvas_img('https://r2limit2.lurl.cc/20260530/4dc0715c23f6259e6ffaf7cb7e5112a1.jpg','canvas_1','0');
```

The crawler is for pages you are authorized to access. It does not guess,
brute-force, or bypass passwords; provide the password yourself with
`--password` or enter it at the prompt.

## Usage

```bash
python3 lurl_canvas_crawler.py 'https://lurl.cc/TxqzI' --password 'YOUR_PASSWORD' --out-dir downloads
```

Useful options:

- `--list-only`: print the extracted `canvas_img` image URLs without downloading.
- `--no-password`: fetch and parse a public/unlocked page without submitting a password.
- `--html-file page.html`: parse saved post-unlock HTML if the site needs browser-only JavaScript.
- `--save-html unlocked.html`: save the fetched/unlocked HTML for debugging.
- `--delay 0.5`: wait between image downloads to reduce load on the remote server.

## Notes

The page at `https://lurl.cc/TxqzI` currently displays a password unlock screen.
After successful unlock, this script extracts every URL passed as the first
argument of `canvas_img(...)`, preserves cookies from the unlock request, and
sends the original page as the download `Referer`.
