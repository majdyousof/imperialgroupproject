"""Validated records at the boundaries of the coursework analysis.

CSV observations preserve the historical missing-data policy: unusable numeric
observations become unknown without discarding an origin's other measurements.
Scenario selections use strict, explicit constraints.
"""

import math
from typing import Annotated, Literal, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator


def optional_number(value: object) -> float | None:
    """Treat missing, nonnumeric and nonfinite observations as unknown."""
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (str, int, float)):
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


Observation = Annotated[float | None, BeforeValidator(optional_number)]
CostMultiplier = Annotated[int, Field(strict=True, ge=50, le=200, multiple_of=5)]
PassengerShare = Annotated[int, Field(strict=True, ge=1, le=100)]
Route = Literal["reading", "woking", "uxbridge", "staines"]
Mode = Literal["train", "trolley"]


class AuthorityRecord(BaseModel):
    """Required source columns; unrelated coursework columns remain in the table."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    local_authority: str = Field(alias="Local Auth", min_length=1)
    latitude: Observation = Field(alias="lat")
    longitude: Observation = Field(alias="lng")

    @classmethod
    def source_columns(cls) -> list[str]:
        return [field.alias or name for name, field in cls.model_fields.items()]


class DemandRecord(AuthorityRecord):
    annual_demand: Observation = Field(alias="Total Annual Demand")
    car_share: Observation = Field(alias="Mode Share Car")
    taxi_share: Observation = Field(alias="Mode Share Taxi")
    rail_share: Observation = Field(alias="Mode Share Rail")
    car_distance_m: Observation = Field(alias="Car Distance [m]")
    car_duration_s: Observation = Field(alias="Car Time Taken [s]")
    transit_distance_m: Observation = Field(alias="Transit Distance [m]")
    transit_duration_s: Observation = Field(alias="Transit Time Taken [s]")

    @model_validator(mode="after")
    def usable_demand_and_shares(self) -> Self:
        if self.annual_demand is not None and self.annual_demand < 0:
            self.annual_demand = None
        shares = (self.car_share, self.taxi_share, self.rail_share)
        known = [share for share in shares if share is not None]
        if len(known) != 3 or any(not 0 <= share <= 1 for share in known) or sum(known) > 1 + 1e-9:
            self.car_share = self.taxi_share = self.rail_share = None
        return self


def missing_route(value: object) -> object:
    """Keep unavailable routes unknown, including NaN values."""
    if value is None or isinstance(value, float) and math.isnan(value):
        return None
    return value


class NetworkRecord(AuthorityRecord):
    old_transit_cost: Observation = Field(alias="GC Existing Public Transport")
    new_transit_cost: Observation = Field(alias="GC Proposed Public Transport")
    time_saved_minutes: Observation = Field(alias="Travel time saved [minutes]")
    best_route: Annotated[
        Literal["Direct", "Reading", "Woking", "Uxbridge", "Staines"] | None,
        BeforeValidator(missing_route),
    ] = Field(alias="Best Public Transport Route")


class ScenarioSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    route: Route
    mode: Mode
    cost_multiplier_pct: CostMultiplier = 100
    passenger_share_pct: PassengerShare = 10

    @property
    def share_index(self) -> int:
        return self.passenger_share_pct - 1
