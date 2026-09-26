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

    def test_phase8_astroanthropology_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "astroAnthroHeadline",
            "astroAnthroPopulationList",
            "astroAnthroAlias",
            "astroAnthroSystems",
            "astroAnthroWhy",
            "astroAnthroMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulateAstroanthropology(", app)
        self.assertIn("function renderAstroanthropology()", app)
        self.assertIn('safeRender("astroanthropology",renderAstroanthropology)', app)
        self.assertIn("populationAlias", app)
        self.assertIn("knowledgeLossPressure", app)
        self.assertNotIn("technologyRank", app)

    def test_phase9_interplanetary_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "interplanetaryHeadline",
            "interplanetaryWorldList",
            "interplanetaryDestination",
            "interplanetaryFounder",
            "interplanetaryExchange",
            "interplanetaryLaunchBtn",
            "interplanetaryStatus",
            "interplanetaryBranch",
            "interplanetaryMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function interplanetaryHohmannDays(", app)
        self.assertIn("function simulateInterplanetarySettlement(", app)
        self.assertIn("function renderInterplanetary()", app)
        self.assertIn('safeRender("interplanetary",renderInterplanetary)', app)
        self.assertIn("launch-not-feasible", app)
        self.assertIn("persistent-offworld-branch", app)
        self.assertNotIn("newSpecies", app)

    def test_phase9_1_colony_network_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "interplanetaryResupply",
            "interplanetaryShock",
            "interplanetaryColonyState",
            "interplanetaryColonyPopulation",
            "interplanetarySelfSufficiency",
            "interplanetaryInfrastructure",
            "interplanetaryColonyTimeline",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulateInterplanetaryNetworkLive(", app)
        self.assertIn("function interplanetaryLogisticPopulation(", app)
        self.assertIn("returnMigrants", app)

    def test_phase9_2_offworld_divergence_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "offworldGeneFlow",
            "offworldDrift",
            "offworldSelection",
            "offworldDivergence",
            "offworldContinuity",
            "offworldWhy",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function simulateOffworldDivergenceLive(", app)
        self.assertIn("No es una afirmación de especiación", app)
        self.assertNotIn("speciesClaim", app)

    def test_phase10_evolutionary_replay_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "evolutionaryReplayHeadline",
            "replayRuns",
            "replayUncertainty",
            "replaySeed",
            "replayRunBtn",
            "replayOutcomeDistribution",
            "replaySensitivity",
            "replayDominant",
            "replayContingency",
            "replayMetrics",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function replayMulberry32(", app)
        self.assertIn("function runEvolutionaryReplayLive(", app)
        self.assertIn("function renderEvolutionaryReplay()", app)
        self.assertIn('safeRender("evolutionary-replay",renderEvolutionaryReplay)', app)
        self.assertIn("not real-world probabilities", (ROOT / "docs/EVOLUTIONARY_REPLAY_MODEL.md").read_text(encoding="utf-8"))
        self.assertNotIn("realWorldProbability", app)

    def test_phase10_1_counterfactual_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "counterfactualParameter",
            "counterfactualDelta",
            "counterfactualFlipRate",
            "counterfactualReference",
            "counterfactualIntervention",
            "counterfactualDivergenceDelta",
            "counterfactualDeltas",
            "counterfactualInterpretation",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function runCounterfactualReplayLive(", app)
        self.assertIn("function renderCounterfactual(", app)
        self.assertIn("same seed", (ROOT / "docs/COUNTERFACTUAL_REPLAY_MODEL.md").read_text(encoding="utf-8"))

    def test_phase11_research_release_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "researchReleaseHeadline",
            "researchReleaseState",
            "researchReleaseId",
            "researchReleaseCommit",
            "researchReleaseChecks",
            "researchEvidenceLedger",
            "researchClaims",
            "researchValidationChecks",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("RESEARCH_RELEASE_URL", app)
        self.assertIn("function loadResearchRelease()", app)
        self.assertIn("function renderResearchRelease()", app)
        self.assertIn("loadResearchRelease();", app)
        self.assertIn("must not automatically mark", (ROOT / "docs/RESEARCH_RELEASE_MODEL.md").read_text(encoding="utf-8"))

    def test_phase11_1_research_note_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "researchNoteTitle",
            "researchNoteResult",
            "researchNoteId",
            "researchNoteRuns",
            "researchNoteCounterfactual",
            "researchNoteStatus",
            "researchNoteLink",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("RESEARCH_NOTE_URL", app)
        self.assertIn("function loadResearchNote()", app)
        self.assertIn("function renderResearchNote()", app)
        self.assertIn("loadResearchNote();", app)
        self.assertIn(
            "arxiv_ready = false",
            (ROOT / "docs/RESEARCH_NOTE_BUILDER.md").read_text(encoding="utf-8"),
        )

    def test_phase11_2_manuscript_review_gate_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "manuscriptPromotionState",
            "manuscriptAutoChecks",
            "manuscriptHumanChecks",
            "manuscriptReviewer",
            "manuscriptCurrentState",
            "manuscriptHumanCheckList",
            "manuscriptReviewExplanation",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("MANUSCRIPT_REVIEW_URL", app)
        self.assertIn("function loadManuscriptReviewGate()", app)
        self.assertIn("function renderManuscriptReviewGate()", app)
        self.assertIn("loadManuscriptReviewGate();", app)
        self.assertIn(
            "cannot move a manuscript automatically",
            (ROOT / "docs/MANUSCRIPT_REVIEW_GATE.md").read_text(encoding="utf-8"),
        )

    def test_phase12_transition_threshold_atlas_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        for element_id in (
            "thresholdAtlasHeadline",
            "thresholdTarget",
            "thresholdParameterCount",
            "thresholdReachedCount",
            "thresholdSeed",
            "thresholdGrid",
            "thresholdInterpretation",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("THRESHOLD_ATLAS_URL", app)
        self.assertIn("function loadThresholdAtlas()", app)
        self.assertIn("function renderThresholdAtlas()", app)
        self.assertIn("loadThresholdAtlas();", app)
        self.assertIn(
            "properties of the current reduced-order simulator",
            (ROOT / "docs/TRANSITION_THRESHOLD_ATLAS.md").read_text(encoding="utf-8"),
        )

    def test_ux_v4_routed_light_shell_contract(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        app = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
        css = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")

        for element_id in (
            "navPlanetButtons",
            "subViewNav",
            "worldsTitle",
            "worldsIntro",
        ):
            self.assertIn(f'id="{element_id}"', html)

        for section_name in ("environment", "life", "humanity", "expansion"):
            self.assertIn(f'data-h01-section="{section_name}"', html)
        for section_name in ("replay", "thresholds", "publication", "method"):
            self.assertIn(f'data-research-section="{section_name}"', html)

        self.assertIn('data-app-view="system"', html)
        self.assertIn("function initAppNavigation()", app)
        self.assertIn("function setAppView(", app)
        self.assertIn("function setH01Panel(", app)
        self.assertIn("function setResearchPanel(", app)
        self.assertIn("function updateObservedHeading()", app)
        self.assertIn('appView==="observed"', app)
        self.assertIn("UX v4 — routed light application shell", css)
        self.assertIn('body[data-app-view="observed"]', css)
        self.assertIn('body[data-h01-tab', css)
        self.assertIn("color-scheme:light", css)
        self.assertNotIn('id="contextSwitcher"', html)

    def test_static_assets_are_version_busted(self):
        html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
        self.assertIn("styles.css?v=uxv4-20260925", html)
        self.assertIn("app.js?v=uxv4-20260925", html)


if __name__ == "__main__":
    unittest.main()
