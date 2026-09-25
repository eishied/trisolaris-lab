# Phase 9.1 — Dynamic interplanetary network

A successful transfer no longer creates a permanent colony by definition.

Phase 9.1 gives every persistent off-world settlement its own demographic and
infrastructure history.

## State variables

Each colony tracks:

- explicit founder-derived population;
- modeled carrying capacity;
- habitat capacity;
- infrastructure integrity;
- local self-sufficiency;
- dependency on external supply;
- resource margin;
- failure pressure;
- return migration;
- active or collapsed state.

## Network

H-01 can maintain supply routes to active colonies. Colonies can also develop
colony-to-colony exchange if more than one settlement survives and both retain
enough infrastructure and contact capacity.

Supply is a scenario parameter. It is never assumed to be unlimited.

## Failure

A settlement that survived Phase 9.0 can still collapse in Phase 9.1 if local
resource support and infrastructure become too weak.

This is intentional. Arrival is not equivalent to permanence.

## Population model

The first implementation uses a reduced-order logistic population trajectory
bounded by a modeled carrying capacity. The carrying capacity is determined by
habitat support, infrastructure, self-sufficiency, burden and supply.

The model is suitable for interactive causal exploration, not population
forecasting.
