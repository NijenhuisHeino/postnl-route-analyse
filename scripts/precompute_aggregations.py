"""Pre-compute zware aggregaties op de full-year data, save naar parquet.

Compute one-off `compute_weighted_edges` en `compute_road_heatmap_points`
op de hele dataset. Resultaten cachen in `.cache/agg_*_full.parquet`.

App.py probeert deze parquet bestanden eerst te laden bij "geen filters"
state — dat scheelt 3-5 min compute bij elke streamlit-restart.

Run:
    .venv/bin/python scripts/precompute_aggregations.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.road_usage import compute_road_heatmap_points, compute_weighted_edges  # noqa: E402
from src.routing import load_cached_routes, unique_segments  # noqa: E402

PARQUET = Path(".cache/postnl_csv_Rittendata.parquet")
EDGES_OUT = Path(".cache/agg_weighted_edges_full.parquet")
HEAT_OUT = Path(".cache/agg_road_heatmap_full.parquet")


def main() -> None:
    if not PARQUET.exists():
        print(f"Geen dataset op {PARQUET}", flush=True)
        sys.exit(1)

    print(f"[{time.strftime('%H:%M:%S')}] Inlezen {PARQUET}...", flush=True)
    df = pd.read_parquet(PARQUET)
    print(f"  {len(df):,} stops, {df['trip_id'].nunique():,} trips", flush=True)

    print(f"[{time.strftime('%H:%M:%S')}] Unieke segmenten...", flush=True)
    segs = unique_segments(df)
    routes, missing = load_cached_routes(segs)
    print(
        f"  {len(routes):,} cached, {missing} missing "
        f"(missing → straight-line fallback)",
        flush=True,
    )

    t0 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Weighted edges berekenen...", flush=True)
    edges = compute_weighted_edges(df, routes)
    print(f"  {len(edges):,} unique edges in {time.time()-t0:.0f}s", flush=True)

    edges_df = pd.DataFrame(
        [
            {
                "lat1": p1[0],
                "lon1": p1[1],
                "lat2": p2[0],
                "lon2": p2[1],
                "n_wagens": n,
            }
            for p1, p2, n in edges
        ]
    )
    edges_df.to_parquet(EDGES_OUT, index=False)
    print(
        f"  → {EDGES_OUT.name} ({EDGES_OUT.stat().st_size / 1024**2:.1f} MB)",
        flush=True,
    )

    t0 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Road heatmap points...", flush=True)
    heat = compute_road_heatmap_points(df, routes)
    print(f"  {len(heat):,} grid cells in {time.time()-t0:.0f}s", flush=True)

    heat_df = pd.DataFrame(heat, columns=["lat", "lon", "weight"])
    heat_df.to_parquet(HEAT_OUT, index=False)
    print(
        f"  → {HEAT_OUT.name} ({HEAT_OUT.stat().st_size / 1024**2:.1f} MB)",
        flush=True,
    )

    print(f"[{time.strftime('%H:%M:%S')}] Backup naar Drive...", flush=True)
    try:
        from scripts.sync_cache import backup as sync_backup

        sync_backup()
    except Exception as e:
        print(f"  Backup faalde (lokaal wel veilig): {e}", flush=True)

    print(f"[{time.strftime('%H:%M:%S')}] KLAAR.", flush=True)


if __name__ == "__main__":
    main()
