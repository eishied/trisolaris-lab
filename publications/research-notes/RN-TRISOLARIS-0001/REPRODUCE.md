# Reproduce RN-TRISOLARIS-0001

1. Checkout Git commit 58a6a8cdeb661d8277b3830e57a0b740dce82cb5.
2. Install requirements-science.txt.
3. Run python pipelines/evolution/build_evolutionary_replay_baseline.py.
4. Run python pipelines/evolution/build_counterfactual_replay_baseline.py.
5. Run python pipelines/research/build_research_release_baseline.py.
6. Run python pipelines/research/build_research_note.py.
7. Compare the generated tables and SVG figures with this package.

Replay seed: 1445. Counterfactual seed: 1445.

External submission still requires human scientific review.
