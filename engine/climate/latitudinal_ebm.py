#!/usr/bin/env python3
"""Educational 1-D latitudinal energy-balance model.

The model is designed to answer one specific product/science requirement:
a planet must not be represented by one global temperature.

This is an Earth-calibrated annual-mean energy-balance approximation, not a
3-D general circulation model. It resolves latitude bands, meridional heat
transport, absorbed stellar energy, and a user-controlled greenhouse offset.

Equations (simplified)
----------------------
Annual-mean incoming flux by latitude:

    Q(phi) = (S0 / 4) * S_rel * [1 + s2 * P2(sin(phi))]

where P2(x)=(3x^2-1)/2 and s2=-0.482 is an Earth-like annual-mean shape.

Linearized outgoing longwave radiation:

    OLR = A + B*T

with A=210 W/m2 and B=2 W/m2/K, using temperature in Celsius.

A diffusive neighbor-mixing term approximates meridional heat transport.
The greenhouse control in the UI is interpreted relative to an Earth-like
reference of 33 K, because the A/B calibration already represents an
Earth-like greenhouse state.
"""

from __future__ import annotations

import math
from typing import Any

SOLAR_CONSTANT_W_M2 = 1361.0
OLR_A_W_M2 = 210.0
OLR_B_W_M2_K = 2.0
DIFFUSION_W_M2_K = 0.55
S2_EARTHLIKE = -0.482
REFERENCE_GREENHOUSE_K = 33.0


def _p2(x: float) -> float:
    return 0.5 * (3.0 * x * x - 1.0)


def solve_latitudinal_climate(
    *,
    stellar_flux_earth: float,
    albedo: float,
    greenhouse_k: float,
    bands: int = 36,
    iterations: int = 1600,
    relaxation: float = 0.08,
) -> dict[str, Any]:
    if stellar_flux_earth <= 0:
        raise ValueError("stellar_flux_earth must be positive")
    if not 0.0 <= albedo < 1.0:
        raise ValueError("albedo must be in [0, 1)")
    if bands < 8:
        raise ValueError("bands must be >= 8")

    # Equal-angle latitude centers from south to north.
    latitudes = [
        -90.0 + (i + 0.5) * (180.0 / bands)
        for i in range(bands)
    ]

    absorbed = []
    targets_c = []
    greenhouse_delta = greenhouse_k - REFERENCE_GREENHOUSE_K

    for lat in latitudes:
        phi = math.radians(lat)
        shape = max(0.10, 1.0 + S2_EARTHLIKE * _p2(math.sin(phi)))
        incoming = (SOLAR_CONSTANT_W_M2 / 4.0) * stellar_flux_earth * shape
        absorbed_flux = incoming * (1.0 - albedo)
        target_c = (absorbed_flux - OLR_A_W_M2) / OLR_B_W_M2_K + greenhouse_delta
        absorbed.append(absorbed_flux)
        targets_c.append(target_c)

    # Start from the local radiative-equilibrium profile, then smooth by
    # meridional heat transport.
    temperatures_c = targets_c[:]
    mixing_strength = DIFFUSION_W_M2_K / OLR_B_W_M2_K

    for _ in range(iterations):
        updated = temperatures_c[:]
        for i, current in enumerate(temperatures_c):
            south = temperatures_c[i - 1] if i > 0 else temperatures_c[i]
            north = temperatures_c[i + 1] if i < bands - 1 else temperatures_c[i]
            neighbor_mean = 0.5 * (south + north)
            equilibrium = targets_c[i] + mixing_strength * (neighbor_mean - current)
            updated[i] = current + relaxation * (equilibrium - current)
        temperatures_c = updated

    rows = []
    area_weights = []
    thermal_window_weight = 0.0

    for lat, temp_c, absorbed_flux in zip(latitudes, temperatures_c, absorbed):
        phi = math.radians(lat)
        weight = max(0.0, math.cos(phi))
        area_weights.append(weight)
        temp_k = temp_c + 273.15

        if temp_c < -30:
            state = "deep-freeze"
        elif temp_c < 0:
            state = "cold"
        elif temp_c <= 30:
            state = "temperate"
        elif temp_c <= 50:
            state = "hot"
        else:
            state = "extreme-hot"

        # Temperature-only proxy. Pressure, salinity, atmosphere and water
        # inventory are not yet solved.
        liquid_thermal_proxy = max(0.0, min(1.0, 1.0 - abs(temp_c - 15.0) / 50.0))
        if 0.0 <= temp_c <= 40.0:
            thermal_window_weight += weight

        rows.append({
            "latitude_deg": lat,
            "temperature_c": temp_c,
            "temperature_k": temp_k,
            "absorbed_flux_w_m2": absorbed_flux,
            "thermal_state": state,
            "liquid_water_thermal_proxy": liquid_thermal_proxy,
        })

    total_weight = sum(area_weights) or 1.0
    global_mean_c = sum(
        row["temperature_c"] * weight
        for row, weight in zip(rows, area_weights)
    ) / total_weight

    temps = [r["temperature_c"] for r in rows]
    return {
        "model": "latitudinal_ebm_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "stellar_flux_earth": stellar_flux_earth,
            "albedo": albedo,
            "greenhouse_k": greenhouse_k,
            "bands": bands,
        },
        "parameters": {
            "solar_constant_w_m2": SOLAR_CONSTANT_W_M2,
            "olr_a_w_m2": OLR_A_W_M2,
            "olr_b_w_m2_k": OLR_B_W_M2_K,
            "diffusion_w_m2_k": DIFFUSION_W_M2_K,
            "s2_annual_mean_shape": S2_EARTHLIKE,
            "reference_greenhouse_k": REFERENCE_GREENHOUSE_K,
        },
        "summary": {
            "global_mean_temperature_c": global_mean_c,
            "minimum_band_temperature_c": min(temps),
            "maximum_band_temperature_c": max(temps),
            "equator_to_pole_contrast_k": max(temps) - min(temps),
            "thermal_liquid_window_area_fraction": thermal_window_weight / total_weight,
        },
        "bands": rows,
        "limitations": [
            "annual-mean latitude-only model",
            "Earth-calibrated outgoing-longwave coefficients",
            "no longitude, continents, ocean dynamics, clouds, seasons, topography, pressure, or atmospheric chemistry",
            "liquid-water score is temperature-only and is not evidence of actual surface water",
            "greenhouse control is an offset relative to an Earth-like calibration",
        ],
        "next_model": "seasonal latitude-longitude energy balance followed by a validated GCM experiment",
    }
