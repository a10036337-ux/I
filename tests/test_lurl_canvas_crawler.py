import unittest

import lurl_canvas_crawler as crawler


class ExtractCanvasImageUrlsTest(unittest.TestCase):
    def test_extracts_and_deduplicates_canvas_img_urls(self):
        html = r"""
        <script>
        canvas_img('https://r2limit2.lurl.cc/20260530/4dc0715c23f6259e6ffaf7cb7e5112a1.jpg','canvas_1','0');
        canvas_img("https:\/\/r2limit2.lurl.cc\/20260530\/second.webp", "canvas_2", "0");
        canvas_img('https://r2limit2.lurl.cc/20260530/4dc0715c23f6259e6ffaf7cb7e5112a1.jpg','canvas_1','0');
        </script>
        """
        self.assertEqual(
            crawler.extract_canvas_image_urls(html),
            [
                "https://r2limit2.lurl.cc/20260530/4dc0715c23f6259e6ffaf7cb7e5112a1.jpg",
                "https://r2limit2.lurl.cc/20260530/second.webp",
            ],
        )


class PasswordPayloadTest(unittest.TestCase):
    def test_keeps_hidden_fields_and_sets_password_field(self):
        form = crawler.FormInfo(
            action="/TxqzI",
            method="post",
            inputs=[
                crawler.InputField(name="csrf", value="abc", input_type="hidden"),
                crawler.InputField(name="password", value="", input_type="password", field_id="password"),
                crawler.InputField(name="submit", value="go", input_type="submit"),
            ],
        )
        self.assertEqual(
            crawler.build_password_payload(form, "1234"),
            {"csrf": "abc", "password": "1234"},
        )


if __name__ == "__main__":
    unittest.main()
