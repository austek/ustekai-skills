from __future__ import annotations

import json
import os
from pathlib import Path


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def new_state(units: list[str], budget: dict) -> dict:
    return {"budget": budget, "spent": 0, "units": {u: "pending" for u in units}}


def mark(state: dict, unit: str, status: str, spent: float) -> dict:
    units = {**state["units"], unit: status}
    return {**state, "spent": state["spent"] + spent, "units": units}


def pending(state: dict) -> list[str]:
    return [u for u, s in state["units"].items() if s == "pending"]


def mark_lane(state: dict, lane: str, spent: float) -> dict:
    done = [*state.get("lanes_done", []), lane]
    return {**state, "spent": state["spent"] + spent, "lanes_done": sorted(set(done))}
