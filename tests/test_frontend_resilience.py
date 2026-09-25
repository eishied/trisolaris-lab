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

    def test_orbital_window_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn('id="orbitScanCanvas"', html)
        self.assertIn('id="orbitBestWindow"', html)
        self.assertIn("function evaluateOrbitPoint(", app)
        self.assertIn("function renderOrbitWindow()", app)
        self.assertIn("function initOrbitWindow()", app)

    def test_regional_climate_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn('id="climateCanvas"', html)
        self.assertIn('id="climateHeadline"', html)
        self.assertIn('id="climateMetrics"', html)
        self.assertIn("function solveClimateBands(", app)
        self.assertIn("function renderClimateWorld()", app)

    def test_surface_systems_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "pressure",
            "water",
            "surfaceCanvas",
            "surfaceHeadline",
            "surfaceMetrics",
            "atmoNarrative",
            "waterNarrative",
            "bioNarrative",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function solveSurfaceSystems(", app)
        self.assertIn("function renderSurfaceWorld()", app)

    def test_ecology_foodweb_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "oxygen",
            "nutrients",
            "seedLifeBtn",
            "foodWebCanvas",
            "ecologyHeadline",
            "ecologyMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function evaluateFoodWeb(", app)
        self.assertIn("function renderFoodWeb()", app)
        self.assertIn("lifeSeeded", app)

    def test_settlement_support_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "techSupport",
            "seedHumansBtn",
            "settlementCanvas",
            "settlementHeadline",
            "settlementMetrics",
            "naturalSettlementNarrative",
            "assistedSettlementNarrative",
            "dependencyNarrative",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function evaluateSettlementSupport(", app)
        self.assertIn("function renderSettlementWorld()", app)
        self.assertIn("humanSeeded", app)

    def test_refugia_migration_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "mobility",
            "refugiaCanvas",
            "refugiaHeadline",
            "refugiaList",
            "refugiaMetrics",
            "refugiaState",
            "refugiaDetail",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function buildRefugiaNetwork(", app)
        self.assertIn("function renderRefugiaNetwork()", app)

    def test_lineage_divergence_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "lineageYears",
            "lineageCanvas",
            "lineageHeadline",
            "lineageCards",
            "lineageDetail",
            "lineageMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulateLineages(", app)
        self.assertIn("function renderLineages()", app)
        self.assertIn("selectedLineageId", app)

    def test_population_genetics_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "geneticsCanvas",
            "geneticsHeadline",
            "geneticsList",
            "geneticsMetrics",
            "geneticsState",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulatePopulationGenetics(", app)
        self.assertIn("function renderGenetics()", app)

    def test_runtime_views_are_isolated(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn("function safeRender(", app)
        self.assertIn('safeRender("lineage-inspector",renderLineageInspector)', app)
        self.assertIn('safeRender("genetics",renderGenetics)', app)
        self.assertIn('safeRender("surface",renderSurfaceWorld)', app)
        self.assertIn('document.querySelectorAll(".lineageCard[data-lineage-id]").forEach', app)
        self.assertNotIn('\n  $(".lineageCard[data-lineage-id]").forEach', app)

    def test_all_interactive_controls_are_wired(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for control_id in ("techSupport", "mobility", "lineageYears"):
            self.assertIn(control_id, app)
        self.assertIn('localStorage.setItem("trisolaris-human-seeded"', app)

    def test_lineage_inspector_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "phenotypeCanvas",
            "lineagePartner",
            "admixtureBtn",
            "functionalAtlas",
            "admixtureResult",
            "lineageInspectorMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function renderLineageInspector()", app)
        self.assertIn("function drawRepresentativePortrait(", app)

    def test_reveal_is_progressive_enhancement(self):
        css = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn(".reveal{opacity:1;transform:none}", css)
        self.assertIn(".reveal.reveal-ready{opacity:0", css)
        self.assertIn("IntersectionObserver", app)
        self.assertIn("never leave scientific modules hidden", app)

    def test_planetary_history_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "planetHistoryCanvas",
            "planetHistoryMode",
            "planetHistoryPopulations",
            "historyEvents",
            "planetHistoryMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulatePlanetaryHistory(", app)
        self.assertIn("function renderPlanetaryHistory()", app)
        self.assertIn('safeRender("planetary-history",renderPlanetaryHistory)', app)

    def test_reveal_startup_uses_multi_element_selector(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        self.assertIn('const items=$$(".reveal:not([data-observed])")', app)
        self.assertIn('$$(".reveal.reveal-ready:not(.in)").forEach', app)
        self.assertIn('$$(".chapter").forEach', app)
        self.assertNotIn('const items=$(".reveal:not([data-observed])")', app)
        self.assertNotIn('\n$(".chapter").forEach', app)

    def test_phase7_history_is_in_main_render_chain(self):
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        start = app.index("function renderCandidate()")
        end = app.index("\nfunction ", start + 20)
        block = app[start:end]
        self.assertIn('safeRender("planetary-history",renderPlanetaryHistory)', block)

    def test_phase7_1_playback_demography_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "historyPlayback",
            "historyPlaybackOut",
            "historyDisturbance",
            "historySeverity",
            "historySeverityOut",
            "historyPlayBtn",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulateDemography(", app)
        self.assertIn("function demographicVulnerability(", app)
        self.assertIn("historyPlaybackTimer", app)
        self.assertIn('population:"población / capacidad"', app)

    def test_static_assets_are_version_busted(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        self.assertIn("styles.css?v=phase7c-20260925", html)
        self.assertIn("app.js?v=phase7c-20260925", html)


if __name__ == "__main__":
    unittest.main()
