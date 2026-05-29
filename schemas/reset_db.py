import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.storage import DB_PATH, init_db


def reset():
    """
    Drop and recreate the asset_profiles table.
    Use this when change the schema and need a clean slate.
    """
    if not DB_PATH.exists():
        print("[reset] No database found — running init instead.")
        init_db()
        return

    import duckdb
    with duckdb.connect(str(DB_PATH)) as conn:
        conn.execute("DROP TABLE IF EXISTS asset_profiles")
        print("[reset] Dropped asset_profiles table.")

    init_db()
    print("[reset] Recreated clean. Ready for a fresh pipeline run.")


if __name__ == "__main__":
    reset()