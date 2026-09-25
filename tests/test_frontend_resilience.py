import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FrontendResilienceTests(unittest.TestCase):
    def test_bundled_science_snapshot_exists(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn("const BUNDLED_DATA=", app)
        self.assertIn('runtimeSource="bundled-snapshot"', app)

    def test_data_failure_does_not_abort_application(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn("data=JSON.parse(JSON.stringify(BUNDLED_DATA))", app)
        self.assertNotIn("No se pudo cargar el archivo científico</h3>", app)

    def test_nbody_ui_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in ("nbodyHeadline", "nbodySummary", "nbodyMeta", "nbodyDetail"):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("async function loadNbodyResult()", app)
        self.assertIn("function renderNbodyResult(result)", app)

    def test_static_assets_are_version_busted(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        self.assertIn("styles.css?v=phase2-20260925", html)
        self.assertIn("app.js?v=phase2-20260925", html)


if __name__ == "__main__":
    unittest.main()
