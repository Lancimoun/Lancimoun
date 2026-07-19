from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "docs" / "index.html"


class DocumentInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.html_lang = None
        self.title = []
        self.in_title = False
        self.meta_names = {}
        self.ids = set()
        self.links = []
        self.h1_count = 0
        self.canvases = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.html_lang = attributes.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "meta" and attributes.get("name"):
            self.meta_names[attributes["name"]] = attributes.get("content", "")
        elif tag == "a":
            self.links.append(attributes)
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "canvas":
            self.canvases.append(attributes)
        if attributes.get("id"):
            self.ids.add(attributes["id"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)


class PortfolioHeroContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HERO.read_text(encoding="utf-8")
        cls.document = DocumentInventory()
        cls.document.feed(cls.source)

    def test_complete_accessible_document_shell(self):
        self.assertTrue(self.source.lower().startswith("<!doctype html>"))
        self.assertEqual(self.document.html_lang, "en")
        self.assertIn("width=device-width", self.document.meta_names["viewport"])
        self.assertIn("Lance Jilliard Galicia", "".join(self.document.title))
        self.assertEqual(self.document.h1_count, 1)

    def test_canvas_is_decorative_and_counts_are_explicit(self):
        self.assertEqual(len(self.document.canvases), 1)
        canvas = self.document.canvases[0]
        self.assertEqual(canvas.get("aria-hidden"), "true")
        self.assertEqual(canvas.get("data-desktop-nodes"), "140")
        self.assertEqual(canvas.get("data-mobile-nodes"), "90")
        self.assertIn("canvas.dataset.desktopNodes", self.source)
        self.assertIn("canvas.dataset.mobileNodes", self.source)

    def test_navigation_has_real_secure_destinations(self):
        hrefs = {link.get("href") for link in self.document.links}
        self.assertIn("#portfolio-hero", hrefs)
        self.assertIn("https://github.com/Lancimoun", hrefs)
        self.assertIn("https://www.linkedin.com/in/lance-jilliard-galicia-8b5b99312", hrefs)
        self.assertFalse(any(href and href.startswith("http://") for href in hrefs))

    def test_motion_respects_user_preference(self):
        self.assertIn("prefers-reduced-motion: reduce", self.source)
        self.assertIn('matchMedia("(prefers-reduced-motion: reduce)")', self.source)
        self.assertRegex(self.source, r"if \(!reducedMotion\) window\.requestAnimationFrame\(frame\)")

    def test_page_is_self_contained(self):
        external_assets = re.findall(r"<(?:script|link|img)\b[^>]*(?:src|href)=\"https?://", self.source, re.I)
        self.assertEqual(external_assets, [])
        self.assertNotIn("onclick=", self.source.lower())


if __name__ == "__main__":
    unittest.main()
