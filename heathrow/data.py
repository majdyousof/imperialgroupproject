"""Load, validate and calculate the dashboard data."""

import math
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import SupportsFloat

import pandas as pd
import streamlit as st

from heathrow.analysis import SHARES as PASSENGER_SHARES
from heathrow.analysis import (
    YEARS,
    calculate_network,
    calculate_scenario,
    validate_annual_factors,
)
from heathrow.models import (
    AuthorityRecord,
    DemandRecord,
    NetworkRecord,
    ScenarioSelection,
)
from heathrow.paths import INPUTS

MODES = ("Car", "Taxi", "Rail", "Other")
LONDON_AUTHORITIES = frozenset(
    {
        "Barking and Dagenham",
        "Barnet",
        "Bexley",
        "Brent",
        "Bromley",
        "Camden",
        "City of London",
        "Croydon",
        "Ealing",
        "Enfield",
        "Greenwich",
        "Hackney",
        "Hammersmith and Fulham",
        "Haringey",
        "Harrow",
        "Havering",
        "Hillingdon",
        "Hounslow",
        "Islington",
        "Kensington and Chelsea",
        "Kingston upon Thames",
        "Lambeth",
        "Lewisham",
        "Merton",
        "Newham",
        "Redbridge",
        "Richmond upon Thames",
        "Southwark",
        "Sutton",
        "Tower Hamlets",
        "Waltham Forest",
        "Wandsworth",
        "Westminster",
    }
)
SHARES = ["Mode Share Car", "Mode Share Taxi", "Mode Share Rail"]


def validated_frame(frame: pd.DataFrame, model: type[AuthorityRecord]) -> pd.DataFrame:
    """Validate CSV records while retaining extra columns and the original index."""
    columns = model.source_columns()
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    data = frame.copy()
    data = data.dropna(subset=["Local Auth"])
    data["Local Auth"] = data["Local Auth"].astype(str).str.strip()
    data = data.loc[data["Local Auth"].ne("")].copy()
    if data["Local Auth"].duplicated().any():
        raise ValueError("Local-authority names must be unique to avoid double counting.")
    records = [
        model.model_validate(row).model_dump(by_alias=True) for row in data.to_dict("records")
    ]
    for column in columns:
        if column in ("Local Auth", "Best Public Transport Route"):
            data[column] = [record[column] for record in records]
        else:
            data[column] = pd.to_numeric(
                pd.Series([record[column] for record in records], index=data.index, dtype="float64")
            )
    return data


@st.cache_data(show_spinner=False, max_entries=2)
def prepare_demand(frame: pd.DataFrame) -> pd.DataFrame:
    data = validated_frame(frame, DemandRecord)
    data = data.loc[data["Local Auth"].ne("South Holland")].copy()
    shares = data[SHARES]
    totals = shares.sum(axis=1, min_count=3)
    valid = totals.notna()
    data["Mode Share Other"] = (1 - totals).clip(lower=0).where(valid)
    for mode in MODES:
        data[f"{mode} Demand"] = (data["Total Annual Demand"] * data[f"Mode Share {mode}"]).round()
    data["Car + taxi demand"] = data["Car Demand"] + data["Taxi Demand"]
    for mode in ["Car", "Transit"]:
        distance = data[f"{mode} Distance [m]"].where(data[f"{mode} Distance [m]"] > 0)
        duration = data[f"{mode} Time Taken [s]"].where(data[f"{mode} Time Taken [s]"] >= 0)
        data[f"{mode} minutes per km"] = duration / 60 / (distance / 1000)
    return data


def rail_share(data: pd.DataFrame) -> float | None:
    """Use only rows with both demand and a valid modal split in the denominator."""
    valid = data.dropna(subset=["Total Annual Demand", "Mode Share Rail"])
    total = valid["Total Annual Demand"].sum()
    if total <= 0:
        return None
    return float((valid["Total Annual Demand"] * valid["Mode Share Rail"]).sum() / total)


def prepare_network(frame: pd.DataFrame) -> pd.DataFrame:
    data = validated_frame(frame, NetworkRecord)
    data = data.loc[~data["Local Auth"].isin(["South Holland", "Angus"])].copy()
    data["Generalised cost saving"] = (
        data["GC Existing Public Transport"] - data["GC Proposed Public Transport"]
    )
    return data


def map_rows(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    data = frame.dropna(subset=["lat", "lng", column])
    return data.loc[data["lat"].between(-90, 90) & data["lng"].between(-180, 180)].copy()


def validate_scenario(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.shape != (len(YEARS), len(PASSENGER_SHARES)):
        raise ValueError("Scenario data must contain all configured years and passenger shares.")
    data = frame.apply(pd.to_numeric, errors="coerce")
    if data.isna().any().any() or data.isin([float("inf"), -float("inf")]).any().any():
        raise ValueError("Scenario earnings must all be finite numbers.")
    data.columns = pd.RangeIndex(len(PASSENGER_SHARES))
    return data


def first_break_even(years: Iterable[int], earnings: Iterable[SupportsFloat]) -> int | None:
    """First sampled year with non-negative earnings; no interpolation."""
    years = list(years)
    earnings = [float(value) for value in earnings]
    if len(years) != len(earnings):
        raise ValueError("Years and earnings must have the same length.")
    for year, value in zip(years, earnings):
        if math.isfinite(value) and value >= 0:
            return int(year)
    return None


@st.cache_data(show_spinner=False)
def read_csv(path: Path, modified_at_ns: int) -> pd.DataFrame:
    """Include file modification time in the cache key after a recalculation."""
    return pd.read_csv(path, float_precision="round_trip")


def load_data(path: Path, transform: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
    try:
        modified_at_ns = path.stat().st_mtime_ns
        return transform(read_csv(path, modified_at_ns))
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Unable to load {path.name}. Check the bundled data and installed dependencies.")
        with st.expander("Details"):
            st.code(str(error))
        st.stop()


def load_demand() -> pd.DataFrame:
    return load_data(INPUTS / "heathrow_flow.csv", prepare_demand)


def load_network() -> pd.DataFrame:
    return load_data(
        INPUTS / "journeys_via_hubs.csv", lambda frame: prepare_network(calculate_network(frame))
    )


def load_scenario(selection: ScenarioSelection) -> pd.DataFrame:
    annual = load_data(INPUTS / "annual_factors.csv", validate_annual_factors)
    return validate_scenario(calculate_scenario(selection, annual))
