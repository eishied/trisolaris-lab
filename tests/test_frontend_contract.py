import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FrontendContractTests(unittest.TestCase):
    def test_frontend_and_pages_app_are_identical(self):
        frontend = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        docs = (ROOT / "docs/app.js").read_text(encoding="utf-8")
        self.assertEqual(frontend, docs)

    def test_world_selector_uses_query_selector_all(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertNotIn('$(".world[data-focus-name]").forEach', app)
        self.assertIn('$$(".world[data-focus-name]").forEach', app)

    def test_required_interactive_elements_exist(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        for element_id in (
            "systemCanvas",
            "planetCards",
            "axis",
            "albedo",
            "greenhouse",
            "orbitSentence",
            "objectFocus",
            "focusClose",
        ):
            self.assertIn(f'id="{element_id}"', html)


if __name__ == "__main__":
    unittest.main()
