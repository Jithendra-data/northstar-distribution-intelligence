"""Shared helpers for deterministic synthetic data generation."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")


def write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    def clean(value: Any) -> Any:
        if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)): return [clean(v) for v in value]
        if hasattr(value, "item") and callable(value.item): value = value.item()
        if hasattr(value, "isoformat") and callable(value.isoformat): return value.isoformat()
        if isinstance(value, float) and not math.isfinite(value): return None
        return value
    path.write_text(json.dumps(clean(payload), indent=2, default=str, allow_nan=False), encoding="utf-8")
