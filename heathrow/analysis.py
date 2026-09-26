"""Recalculate both assessments from shared historical coursework assumptions.

The dashboard calculates from these inputs at runtime.
All monetary calculations use pounds; only link chart outputs use £ million.
"""

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from heathrow.models import Mode, ScenarioSelection

YEARS = tuple(range(2025, 2101))
SHARES = tuple(range(1, 101))
MULTIPLIERS = tuple(range(50, 201, 5))


class AssessmentAssumptions(BaseModel):
    """Common inputs, retaining the project's 2024 appraisal context."""

    model_config = ConfigDict(frozen=True, extra="forbid", validate_default=True)

    metres_per_mile: float = Field(default=1609.344, gt=0)
    rail_fare_per_mile: float = Field(default=0.54, ge=0)
    trolleybus_fare: float = Field(default=2.0, ge=0)
    rail_co2_g_per_passenger_mile: float = Field(default=56.0, ge=0)
    trolleybus_co2_g_per_passenger_mile: float = Field(default=46.4, ge=0)
    carbon_gbp_per_tonne_2024: float = Field(default=256.0, ge=0)
    optimism_bias: float = Field(default=1.56, ge=1)
    working_value_of_time: float = Field(default=26.94, ge=0)
    nonworking_value_of_time: float = Field(default=9.95 * 1.493, ge=0)
    business_share: float = Field(default=0.252, ge=0, le=1)
    passengers_2024: float = Field(default=81_400_000, gt=0)
    passengers_2036: float = Field(default=132_000_000, gt=0)
    rail_operating_gbp_per_km_year: float = Field(default=80_000, ge=0)
    trolleybus_operating_gbp_per_km_year: float = Field(default=200_000, ge=0)
    rail_refurbishment_years: int = Field(default=60, gt=0)
    trolleybus_refurbishment_years: int = Field(default=15, gt=0)
    rail_refurbishment_gbp_per_km: float = Field(default=170_000, ge=0)
    trolleybus_infrastructure_gbp_per_km: float = Field(default=1_008_000, ge=0)
    trolleybus_fixed_infrastructure_gbp: float = Field(default=11_250_000, ge=0)
    trolleybus_fleet_gbp: float = Field(default=15_000_000, ge=0)

    @property
    def value_of_time(self) -> float:
        return self.working_value_of_time * self.business_share + self.nonworking_value_of_time * (
            1 - self.business_share
        )


class LinkInputs(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rail_km: float = Field(gt=0)
    trolleybus_km: float = Field(gt=0)
    rail_capital_gbp: float = Field(gt=0)
    proposed_minutes: float = Field(gt=0)
    selected_mode: Mode

    def length_km(self, mode: Mode) -> float:
        return self.rail_km if mode == "train" else self.trolleybus_km


ASSUMPTIONS = AssessmentAssumptions()
LINKS = {
    "reading": LinkInputs(
        rail_km=47.16,
        trolleybus_km=44.25,
        rail_capital_gbp=1_337_217_000,
        proposed_minutes=26,
        selected_mode="train",
    ),
    "uxbridge": LinkInputs(
        rail_km=10.6,
        trolleybus_km=13.2,
        rail_capital_gbp=884_229_000,
        proposed_minutes=12,
        selected_mode="train",
    ),
    "woking": LinkInputs(
        rail_km=9.1,
        trolleybus_km=24.14,
        rail_capital_gbp=795_600_000,
        proposed_minutes=19,
        selected_mode="train",
    ),
    "staines": LinkInputs(
        rail_km=4.59,
        trolleybus_km=4.59,
        rail_capital_gbp=401_297_000,
        proposed_minutes=6,
        selected_mode="trolley",
    ),
}


def fare_per_passenger(distance_km: float, mode: Mode) -> float:
    if mode == "trolley":
        return ASSUMPTIONS.trolleybus_fare
    return distance_km * 1000 / ASSUMPTIONS.metres_per_mile * ASSUMPTIONS.rail_fare_per_mile


def co2_tonnes_per_passenger(distance_km: float, mode: Mode) -> float:
    grams = (
        ASSUMPTIONS.rail_co2_g_per_passenger_mile
        if mode == "train"
        else ASSUMPTIONS.trolleybus_co2_g_per_passenger_mile
    )
    return distance_km * 1000 / ASSUMPTIONS.metres_per_mile * grams / 1_000_000


def passenger_forecast(year: int) -> float:
    growth = (ASSUMPTIONS.passengers_2036 - ASSUMPTIONS.passengers_2024) / (2036 - 2024)
    return ASSUMPTIONS.passengers_2024 + (year - 2024) * growth


def validate_annual_factors(annual: pd.DataFrame) -> pd.DataFrame:
    annual = annual.copy()
    columns = ["year", "carbon_gbp_per_tonne", "inflation_index"]
    annual[columns] = annual[columns].apply(pd.to_numeric, errors="raise")
    annual = annual.sort_values("year")
    if annual["year"].tolist() != list(YEARS):
        raise ValueError("Annual factors must cover each year from 2025 to 2100 exactly once.")
    factors = annual[["carbon_gbp_per_tonne", "inflation_index"]]
    if not np.isfinite(factors.to_numpy()).all() or (factors <= 0).any().any():
        raise ValueError("Carbon values and inflation indices must be finite and positive.")
    return annual


def calculate_scenario(selection: ScenarioSelection, annual: pd.DataFrame) -> pd.DataFrame:
    """Inflation-adjusted cumulative earnings; initial expenditure occurs in 2025."""
    link = LINKS[selection.route]
    mode = selection.mode
    length = link.length_km(mode)
    is_rail = mode == "train"
    capital = (
        link.rail_capital_gbp
        if is_rail
        else length * ASSUMPTIONS.trolleybus_infrastructure_gbp_per_km
        + ASSUMPTIONS.trolleybus_fixed_infrastructure_gbp
        + ASSUMPTIONS.trolleybus_fleet_gbp
    )
    passengers = np.array([passenger_forecast(year) for year in YEARS])[:, None]
    passengers = passengers * np.array(SHARES)[None, :] / 100
    fares = passengers * fare_per_passenger(length, mode)
    carbon = (
        passengers
        * co2_tonnes_per_passenger(length, mode)
        * annual["carbon_gbp_per_tonne"].to_numpy()[:, None]
    )
    operating_rate = (
        ASSUMPTIONS.rail_operating_gbp_per_km_year
        if is_rail
        else ASSUMPTIONS.trolleybus_operating_gbp_per_km_year
    )
    operation = np.full((len(YEARS), 1), operating_rate * length)
    interval = (
        ASSUMPTIONS.rail_refurbishment_years
        if is_rail
        else ASSUMPTIONS.trolleybus_refurbishment_years
    )
    renewal_cost = length * ASSUMPTIONS.rail_refurbishment_gbp_per_km if is_rail else capital
    age = np.arange(len(YEARS))
    operation[(age > 0) & (age % interval == 0)] += renewal_cost
    uplift = ASSUMPTIONS.optimism_bias * selection.cost_multiplier_pct / 100
    deflator = (annual["inflation_index"].iloc[0] / annual["inflation_index"]).to_numpy()
    contributions = (fares - (operation + carbon) * uplift) * deflator[:, None]
    # Retain the original timing convention: capital only in the first year.
    contributions[0, :] = -capital * uplift
    return pd.DataFrame(np.cumsum(contributions, axis=0) / 1_000_000)


def calculate_network(journeys: pd.DataFrame) -> pd.DataFrame:
    """Compare existing public transport with the four selected hub connections."""
    journeys = journeys.copy()
    names = journeys["Local Auth"].astype("string").str.strip()
    if names.isna().any() or names.eq("").any() or names.duplicated().any():
        raise ValueError("Journey inputs must have unique, nonempty authority names.")
    travel_columns = [
        c for c in journeys if isinstance(c, str) and ("Distance [m]" in c or "Time Taken [s]" in c)
    ]
    for column in travel_columns:
        values = pd.to_numeric(journeys[column], errors="raise")
        if ((values < 0) | np.isinf(values)).any():
            raise ValueError(f"Invalid journey input: {column}")
        journeys[column] = values

    def access_cost(distance: pd.Series, duration: pd.Series) -> pd.Series:
        miles = distance / ASSUMPTIONS.metres_per_mile
        return (
            miles * ASSUMPTIONS.rail_fare_per_mile
            + duration / 3600 * ASSUMPTIONS.value_of_time
            + miles
            * ASSUMPTIONS.rail_co2_g_per_passenger_mile
            / 1_000_000
            * ASSUMPTIONS.carbon_gbp_per_tonne_2024
        )

    direct_time = journeys["Transit Time Taken [s]"]
    costs = {"Direct": access_cost(journeys["Transit Distance [m]"], direct_time)}
    times = {"Direct": direct_time}
    for route, link in LINKS.items():
        name = route.title()
        duration = journeys[f"({name}) Transit Time Taken [s]"]
        distance = journeys[f"({name}) Transit Distance [m]"]
        length = link.length_km(link.selected_mode)
        leg_cost = (
            fare_per_passenger(length, link.selected_mode)
            + link.proposed_minutes / 60 * ASSUMPTIONS.value_of_time
            + co2_tonnes_per_passenger(length, link.selected_mode)
            * ASSUMPTIONS.carbon_gbp_per_tonne_2024
        )
        costs[name] = access_cost(distance, duration) + leg_cost
        times[name] = duration + link.proposed_minutes * 60
    cost_options = pd.DataFrame(costs)
    time_options = pd.DataFrame(times).where(cost_options.notna())
    result = journeys[
        [
            "Local Auth",
            "Total Annual Demand",
            "Mode Share Taxi",
            "Mode Share Car",
            "Mode Share Rail",
            "lat",
            "lng",
        ]
    ].copy()
    result["GC Existing Public Transport"] = costs["Direct"]
    result["GC Proposed Public Transport"] = cost_options.min(axis=1)
    result["Best Public Transport Route"] = cost_options.dropna(how="all").idxmin(axis=1)
    result["Travel time saved [minutes]"] = (direct_time - time_options.min(axis=1)) / 60
    return result
