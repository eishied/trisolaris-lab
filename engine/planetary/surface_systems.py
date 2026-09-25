#!/usr/bin/env python3
"""Coupled atmosphere-water-biosphere potential model.

This is a deliberately transparent bridge between climate and later ecology.
It does not simulate a mature biosphere or assert the existence of life.

Inputs are the latitude-band climate output plus simple planetary controls:
surface pressure and water inventory. The model estimates:
- boiling-point shift with pressure,
- thermal state of surface water by latitude,
- liquid/ice/vapor-stress fractions,
- broad atmospheric-retention and water-cycle proxies,
- potential primary productivity under an M-dwarf spectral penalty.

All biological outputs are POTENTIAL / MODELED, not observed life.
"""

from __future__ import annotations

import math
from typing import Any


def boiling_point_c_approx(pressure_bar: float) -> float:
    """Coarse water boiling-point approximation for UI-scale exploration.

    Around terrestrial pressures, a log-pressure approximation is adequate for
    educational screening. It is intentionally clamped outside that regime.
    """
    pressure_bar = max(0.05, min(5.0, pressure_bar))
    return max(45.0, min(150.0, 100.0 + 25.0 * math.log10(pressure_bar)))


def _temperature_productivity(temp_c: float) -> float:
    """Broad terrestrial-like productivity response to temperature."""
    if temp_c <= -10.0 or temp_c >= 50.0:
        return 0.0
    if temp_c <= 22.0:
        return max(0.0, min(1.0, (temp_c + 10.0) / 32.0))
    return max(0.0, min(1.0, (50.0 - temp_c) / 28.0))


def solve_surface_systems(
    climate: dict[str, Any],
    *,
    pressure_bar: float = 1.0,
    water_inventory_earth_oceans: float = 1.0,
    stellar_flux_earth: float = 1.0,
    spectral_productivity_factor: float = 0.55,
) -> dict[str, Any]:
    if pressure_bar <= 0:
        raise ValueError("pressure_bar must be positive")
    if water_inventory_earth_oceans < 0:
        raise ValueError("water inventory cannot be negative")

    boiling_c = boiling_point_c_approx(pressure_bar)
    rows = climate["bands"]

    liquid_weight = 0.0
    ice_weight = 0.0
    vapor_weight = 0.0
    productivity_weight = 0.0
    habitable_refugia_weight = 0.0
    total_weight = 0.0

    band_results = []

    # A bounded inventory factor: tiny inventories sharply constrain the cycle,
    # while >1 Earth ocean provides diminishing returns.
    water_factor = 1.0 - math.exp(-2.2 * water_inventory_earth_oceans)

    # Pressure proxy: very thin atmospheres suppress hydrological buffering.
    pressure_cycle_factor = max(0.0, min(1.0, pressure_bar / 0.7))

    # M-dwarf spectral penalty is exploratory, not a measured PAR fraction for
    # this system. It explicitly remains a parameter.
    usable_light_factor = max(
        0.0,
        min(1.0, spectral_productivity_factor * math.sqrt(max(0.0, stellar_flux_earth))),
    )

    for row in rows:
        lat = float(row.get("latitude_deg", row.get("latitudeDeg")))
        temp_c = float(row.get("temperature_c", row.get("temperatureC")))
        phi = math.radians(lat)
        weight = max(0.0, math.cos(phi))
        total_weight += weight

        if water_inventory_earth_oceans <= 0.001:
            water_state = "dry"
            liquid = ice = vapor = 0.0
        elif temp_c < 0.0:
            water_state = "ice-dominated"
            ice = water_factor
            liquid = max(0.0, water_factor * (1.0 - min(1.0, abs(temp_c) / 35.0)) * 0.15)
            vapor = 0.0
        elif temp_c < boiling_c:
            water_state = "liquid-permitted"
            liquid = water_factor
            ice = 0.0
            vapor = water_factor * max(0.0, min(1.0, (temp_c - 20.0) / max(1.0, boiling_c - 20.0))) * 0.35
        else:
            water_state = "vapor-stressed"
            vapor = water_factor
            liquid = max(0.0, water_factor * 0.05)
            ice = 0.0

        hydro_cycle = water_factor * pressure_cycle_factor
        if 0.0 <= temp_c < boiling_c:
            hydro_cycle *= 0.45 + 0.55 * max(0.0, min(1.0, (temp_c + 5.0) / 35.0))
        else:
            hydro_cycle *= 0.2

        temp_productivity = _temperature_productivity(temp_c)
        liquid_support = max(0.0, min(1.0, liquid))
        productivity = (
            temp_productivity
            * liquid_support
            * hydro_cycle
            * usable_light_factor
        )

        refugia = (
            1.0
            if (
                0.0 <= temp_c <= 40.0
                and liquid_support > 0.25
                and pressure_bar >= 0.2
            )
            else 0.0
        )

        liquid_weight += weight * liquid_support
        ice_weight += weight * ice
        vapor_weight += weight * vapor
        productivity_weight += weight * productivity
        habitable_refugia_weight += weight * refugia

        band_results.append({
            "latitude_deg": lat,
            "temperature_c": temp_c,
            "water_state": water_state,
            "liquid_water_proxy": liquid_support,
            "ice_proxy": ice,
            "vapor_stress_proxy": vapor,
            "hydrological_cycle_proxy": hydro_cycle,
            "productivity_potential": productivity,
            "thermal_refugium": bool(refugia),
        })

    total_weight = total_weight or 1.0

    # Very coarse atmosphere-retention screening for an Earth-mass/radius world.
    # Higher temperature and lower pressure imply a more fragile atmospheric state.
    global_mean = float(climate["summary"].get(
        "global_mean_temperature_c",
        climate["summary"].get("globalMeanC", 0.0),
    ))
    thermal_escape_stress = max(0.0, min(1.0, (global_mean + 20.0) / 180.0))
    retention_proxy = max(
        0.0,
        min(1.0, 0.72 + 0.16 * math.log10(max(0.05, pressure_bar)) - 0.35 * thermal_escape_stress),
    )

    biosphere_score = productivity_weight / total_weight
    refugia_fraction = habitable_refugia_weight / total_weight

    if biosphere_score >= 0.45 and refugia_fraction >= 0.50:
        biosphere_state = "broad primary-productivity potential"
    elif biosphere_score >= 0.15 and refugia_fraction >= 0.15:
        biosphere_state = "regional biosphere potential"
    elif refugia_fraction > 0.0:
        biosphere_state = "limited thermal-hydrological refugia"
    else:
        biosphere_state = "little surface biosphere potential under current assumptions"

    return {
        "model": "surface_systems_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "pressure_bar": pressure_bar,
            "water_inventory_earth_oceans": water_inventory_earth_oceans,
            "stellar_flux_earth": stellar_flux_earth,
            "spectral_productivity_factor": spectral_productivity_factor,
        },
        "summary": {
            "boiling_point_c_approx": boiling_c,
            "liquid_surface_proxy_area_fraction": liquid_weight / total_weight,
            "ice_proxy_area_fraction": ice_weight / total_weight,
            "vapor_stress_area_fraction": vapor_weight / total_weight,
            "hydrological_cycle_strength": water_factor * pressure_cycle_factor,
            "atmospheric_retention_proxy": retention_proxy,
            "biosphere_productivity_potential": biosphere_score,
            "thermal_hydrological_refugia_fraction": refugia_fraction,
            "biosphere_state": biosphere_state,
        },
        "bands": band_results,
        "limitations": [
            "assumes an Earth-mass/radius reference world for atmospheric-retention screening",
            "does not solve atmospheric chemistry or radiative transfer",
            "water fractions are thermodynamic proxies, not a 3-D ocean model",
            "no topography, salinity, groundwater, clouds, precipitation transport, or ocean circulation",
            "productivity is a potential index, not simulated or observed life",
            "spectral productivity factor is exploratory and not a measured PAR spectrum for LTT 1445 A",
            "no UV flare ecology, nutrient cycles, evolution, predation, or food web yet",
        ],
        "next_model": "seasonal hydrology, atmospheric chemistry, nutrient cycling, and explicit ecological guilds",
    }
