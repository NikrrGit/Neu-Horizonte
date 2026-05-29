import json
from pathlib import Path

import duckdb

from schemas.asset_profile import AssetProfile, AssetClass, ConversionPotential

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "sax_pipeline.duckdb"


def get_connection() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def init_db() -> None:
    """
    Create the asset_profiles table if it doesn't exist yet.
    Run this once at pipeline startup — safe to call repeatedly.
    """
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asset_profiles (
                source_file           TEXT PRIMARY KEY,
                extracted_at          TIMESTAMP,
                location_city         TEXT,
                location_address      TEXT,
                asset_class           TEXT,
                conversion_potential  TEXT,
                plot_size_sqm         DOUBLE,
                building_size_sqm     DOUBLE,
                estimated_value_eur   DOUBLE,
                value_threshold_met   BOOLEAN,
                zoning_flags          TEXT,
                distress_signals      TEXT,
                sax_fit_score         DOUBLE,
                summary               TEXT,
                raw_source_text       TEXT
            )
        """)


def upsert_profile(profile: AssetProfile) -> None:
    """
    Insert or replace a profile keyed on source_file.
    Safe to re-run the pipeline without creating duplicates.
    """
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO asset_profiles VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, [
            profile.source_file,
            profile.extracted_at,
            profile.location_city,
            profile.location_address,
            profile.asset_class.value,
            json.dumps([c.value for c in profile.conversion_potential]),
            profile.plot_size_sqm,
            profile.building_size_sqm,
            profile.estimated_value_eur,
            profile.value_threshold_met,
            json.dumps(profile.zoning_flags),
            json.dumps(profile.distress_signals),
            profile.sax_fit_score,
            profile.summary,
            profile.raw_source_text,
        ])


def _row_to_profile(row: tuple) -> AssetProfile:
    """Convert a raw DuckDB row back into a validated AssetProfile object."""
    return AssetProfile(
        source_file=row[0],
        extracted_at=row[1],
        location_city=row[2],
        location_address=row[3],
        asset_class=AssetClass(row[4]),
        conversion_potential=[ConversionPotential(c) for c in json.loads(row[5])],
        plot_size_sqm=row[6],
        building_size_sqm=row[7],
        estimated_value_eur=row[8],
        value_threshold_met=row[9],
        zoning_flags=json.loads(row[10]),
        distress_signals=json.loads(row[11]),
        sax_fit_score=row[12],
        summary=row[13],
        raw_source_text=row[14],
    )


def get_all() -> list[AssetProfile]:
    """Return every profile in the database, sorted by fit score descending."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM asset_profiles
            ORDER BY sax_fit_score DESC
        """).fetchall()
    return [_row_to_profile(row) for row in rows]


def get_top_n(n: int = 5) -> list[AssetProfile]:
    """Return the top N profiles by fit score — used for the dashboard highlights."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM asset_profiles
            ORDER BY sax_fit_score DESC
            LIMIT ?
        """, [n]).fetchall()
    return [_row_to_profile(row) for row in rows]


def filter_by_class(asset_class: AssetClass) -> list[AssetProfile]:
    """Return all profiles matching a specific asset class."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM asset_profiles
            WHERE asset_class = ?
            ORDER BY sax_fit_score DESC
        """, [asset_class.value]).fetchall()
    return [_row_to_profile(row) for row in rows]