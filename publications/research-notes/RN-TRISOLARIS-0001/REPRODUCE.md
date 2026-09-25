# Reproduce RN-TRISOLARIS-0001

1. Checkout Git commit f56231a665b532414f041182f2ee46c56a3e4372.
2. Install requirements-science.txt.
3. Run python pipelines/evolution/build_evolutionary_replay_baseline.py.
4. Run python pipelines/evolution/build_counterfactual_replay_baseline.py.
5. Run python pipelines/research/build_research_release_baseline.py.
6. Run python pipelines/research/build_research_note.py.
7. Compare the generated tables and SVG figures with this package.

Replay seed: 1445. Counterfactual seed: 1445.

External submission still requires human scientific review.
