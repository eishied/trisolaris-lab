# Orbital engine — Phase 2

The first orbital component is a transparent **analytic pre-screen**.

It does **not** claim long-term stability. Its purpose is to identify obviously crowded candidate orbits before direct N-body ensembles.

## Current calculation

For a hypothetical H-01 orbit around LTT 1445 A, the screen calculates:

- Keplerian orbital period,
- spacing from each observed planet in mutual Hill radii,
- the classical two-planet Hill threshold `2√3`,
- a simple strong-spacing flag at `Δ ≥ 8`,
- an approximate scale for the differential tidal influence of the distant B+C pair.

## Why this exists before N-body

Direct integrations should explore a large parameter space. A cheap analytic screen lets TRISOLARIS avoid spending integration time on configurations that are obviously too crowded.

## Scientific status

**DERIVED / screening model**

The result must never be shown as “stable”. Allowed language:

- fails the simple Hill screen,
- passes the simple Hill screen,
- well separated in the analytic screen,
- requires N-body verification.

## Next step

Implement long-term N-body ensembles using a dedicated scientific integrator and observed-parameter uncertainty distributions.
