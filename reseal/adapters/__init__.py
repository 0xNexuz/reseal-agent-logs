"""Tool adapters. Add a tool by writing one Adapter subclass and listing it here."""

import importlib.util
from pathlib import Path

from .base import (ACCEPTED, ERROR, INCONCLUSIVE, REJECTED, Adapter, NotApplicable, Run, Verdict)
from .halo import HaloAdapter
from .obsigna_ import ObsignaAdapter
from .signet import SignetAdapter
from .witnesskit_ import WitnessKitAdapter

ALL = [HaloAdapter, WitnessKitAdapter, SignetAdapter, ObsignaAdapter]


def _load_withheld():
    """Load the adapter for the unnamed fifth tool, if this checkout has it.

    That adapter is kept out of the public repository until the tool's
    maintainer has been told about its result (README, "The unnamed tool").
    Without it everything else runs on the four named tools.
    """
    path = Path(__file__).resolve().parents[2] / "private" / "tool_e.py"
    if not path.exists():
        return
    spec = importlib.util.spec_from_file_location("reseal_private_tool_e", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return
    ALL.append(module.ToolEAdapter)


_load_withheld()


def get(name: str) -> Adapter:
    for cls in ALL:
        if cls.name == name:
            return cls()
    raise KeyError(f"unknown tool {name!r}; known: {[c.name for c in ALL]}")


__all__ = ["ALL", "get", "Adapter", "Run", "Verdict", "NotApplicable",
           "ACCEPTED", "REJECTED", "INCONCLUSIVE", "ERROR"]
