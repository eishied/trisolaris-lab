#!/usr/bin/env python3
"""Dynamic interplanetary settlement network for TRISOLARIS LAB Phase 9.1.

A successful arrival is not treated as a permanent colony. This layer models
whether an off-world settlement can maintain population, infrastructure,
self-sufficiency and exchange with H-01 through time.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _logistic_population(initial: float, capacity: float, rate: float, years: float) -> float:
    if initial <= 0 or capacity <= 0:
        return 0.0
    if initial >= capacity:
        return capacity
    exponent = min(60.0, max(-60.0, rate * max(0.0, years)))
    denominator = 1.0 + ((capacity - initial) / initial) * math.exp(-exponent)
    return capacity / denominator


def simulate_interplanetary_network(
    interplanetary: dict[str, Any],
    *,
    years: float,
    resupply_strength: float = 0.35,
    infrastructure_shock: float = 0.0,
    enable_return_migration: bool = True,
) -> dict[str, Any]:
    """Evolve persistent Phase 9.0 settlements into a dynamic colony network."""
    if years < 0:
        raise ValueError("years cannot be negative")

    resupply_strength = _clamp01(resupply_strength)
    infrastructure_shock = _clamp01(infrastructure_shock)
    worlds = {
        world["world_id"]: world
        for world in interplanetary.get("worlds", [])
    }

    colonies: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for attempt in interplanetary.get("attempts", []):
        if not attempt.get("settlement_persists"):
            continue

        destination_id = attempt["destination_id"]
        world = worlds.get(destination_id, {})
        arrival = max(0, int(attempt.get("arrival_survivors", 0)))
        habitat = _clamp01(attempt.get("habitat_capacity", 0.0))
        burden = _clamp01(attempt.get("settlement_burden", 0.0))
        technical = _clamp01(attempt.get("technology_continuity", 0.0))
        contact = _clamp01(attempt.get("post_settlement_contact", 0.0))

        resupply = _clamp01(
            resupply_strength * (0.42 + 0.58 * contact)
        )
        infrastructure_integrity = _clamp01(
            0.44 * technical
            + 0.32 * habitat
            + 0.24 * resupply
            - 0.52 * infrastructure_shock
        )
        self_sufficiency = _clamp01(
            0.36 * habitat
            + 0.30 * technical
            + 0.20 * (1.0 - burden)
            + 0.14 * infrastructure_integrity
        )
        supply_dependency = _clamp01(
            1.0 - self_sufficiency
            + 0.20 * burden
            - 0.18 * resupply
        )
        resource_margin = _clamp01(
            0.42 * habitat
            + 0.30 * infrastructure_integrity
            + 0.28 * max(self_sufficiency, resupply)
            - 0.34 * burden
        )

        capacity_multiplier = (
            1.0
            + 8.0
            * resource_margin
            * (0.45 + 0.55 * infrastructure_integrity)
        )
        carrying_capacity = max(float(arrival), float(arrival) * capacity_multiplier)
        annual_rate = max(
            -0.0015,
            0.00012
            + 0.00062 * resource_margin
            - 0.00075 * infrastructure_shock
        )
        population = _logistic_population(
            max(1.0, float(arrival)),
            carrying_capacity,
            annual_rate,
            years,
        )

        failure_pressure = _clamp01(
            0.38 * burden
            + 0.34 * (1.0 - infrastructure_integrity)
            + 0.28 * supply_dependency
            - 0.24 * resupply
        )

        active = bool(
            arrival >= 40
            and infrastructure_integrity >= 0.10
            and resource_margin >= 0.08
            and failure_pressure < 0.88
            and population >= 20
        )
        if not active:
            population = 0.0

        return_fraction = (
            _clamp01(
                contact
                * (0.06 + 0.18 * failure_pressure)
                * (1.0 - self_sufficiency)
            )
            if enable_return_migration and active
            else 0.0
        )
        return_migrants = int(round(population * return_fraction)) if active else 0

        local_growth = (
            "expansion"
            if active and population > arrival * 1.35
            else "stable"
            if active and population >= arrival * 0.75
            else "decline"
            if active
            else "collapse"
        )

        snapshots = []
        for fraction in (0.0, 0.10, 0.25, 0.50, 0.75, 1.0):
            t = years * fraction
            p = _logistic_population(
                max(1.0, float(arrival)),
                carrying_capacity,
                annual_rate,
                t,
            )
            if not active and fraction == 1.0:
                p = 0.0
            snapshots.append({
                "years": t,
                "population": p,
                "capacity": carrying_capacity,
            })

        colony = {
            "colony_id": f"C-{attempt.get('lineage_id', 'L?')}-{destination_id}",
            "lineage_id": attempt.get("lineage_id"),
            "population_alias": attempt.get("population_alias"),
            "destination_id": destination_id,
            "destination_name": attempt.get("destination_name"),
            "epistemic_level": "MODELED",
            "initial_population": arrival,
            "population": population,
            "carrying_capacity": carrying_capacity,
            "growth_state": local_growth,
            "active": active,
            "habitat_capacity": habitat,
            "settlement_burden": burden,
            "infrastructure_integrity": infrastructure_integrity,
            "self_sufficiency": self_sufficiency,
            "supply_dependency": supply_dependency,
            "resource_margin": resource_margin,
            "resupply_strength": resupply,
            "failure_pressure": failure_pressure,
            "return_migration_fraction": return_fraction,
            "return_migrants": return_migrants,
            "post_settlement_contact": contact,
            "gravity_earth": world.get("gravity_earth"),
            "controlled_habitat_required": world.get("controlled_habitat_required", False),
            "timeline": snapshots,
        }
        colonies.append(colony)

        routes.append({
            "route_id": f"H-01->{destination_id}",
            "source_id": "H-01",
            "target_id": destination_id,
            "lineage_id": attempt.get("lineage_id"),
            "outbound_support": resupply,
            "return_migrants": return_migrants,
            "active": active and resupply > 0.02,
            "transfer_days": attempt.get("transfer_days", 0.0),
        })

        if not active:
            events.append({
                "type": "colony-collapse",
                "colony_id": colony["colony_id"],
                "label": f"{attempt.get('population_alias')} loses its settlement on {attempt.get('destination_name')}",
            })
        elif failure_pressure >= 0.60:
            events.append({
                "type": "colony-fragility",
                "colony_id": colony["colony_id"],
                "label": f"{attempt.get('population_alias')} remains on {attempt.get('destination_name')} under high failure pressure",
            })
        elif self_sufficiency >= 0.55:
            events.append({
                "type": "colony-local-capacity",
                "colony_id": colony["colony_id"],
                "label": f"{attempt.get('population_alias')} develops substantial local support capacity",
            })

    active_colonies = [colony for colony in colonies if colony["active"]]

    # Colony-to-colony routes exist only when more than one active settlement is
    # present and both retain enough infrastructure to exchange.
    for i, left in enumerate(active_colonies):
        for right in active_colonies[i + 1:]:
            exchange = _clamp01(
                0.5
                * min(left["infrastructure_integrity"], right["infrastructure_integrity"])
                * (left["post_settlement_contact"] + right["post_settlement_contact"])
            )
            if exchange < 0.08:
                continue
            routes.append({
                "route_id": f"{left['destination_id']}->{right['destination_id']}",
                "source_id": left["destination_id"],
                "target_id": right["destination_id"],
                "lineage_id": None,
                "outbound_support": exchange,
                "return_migrants": 0,
                "active": True,
                "transfer_days": None,
            })

    return {
        "model": "interplanetary_network_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "resupply_strength": resupply_strength,
            "infrastructure_shock": infrastructure_shock,
            "enable_return_migration": bool(enable_return_migration),
        },
        "colonies": colonies,
        "routes": routes,
        "events": events,
        "summary": {
            "colony_count": len(colonies),
            "active_colony_count": len(active_colonies),
            "collapsed_colony_count": sum(1 for colony in colonies if not colony["active"]),
            "network_route_count": sum(1 for route in routes if route["active"]),
            "offworld_population": sum(colony["population"] for colony in active_colonies),
            "return_migrants": sum(colony["return_migrants"] for colony in active_colonies),
        },
        "limitations": [
            "population dynamics are reduced-order demographic proxies, not forecasts",
            "resource production, life support and infrastructure are aggregated indices rather than engineering mass balances",
            "resupply strength is an explicit scenario parameter, not an assumed capability",
            "colony collapse remains possible after a successful Phase 9.0 arrival",
            "population values are scenario headcounts only after the explicit founder cohort is created",
        ],
    }
