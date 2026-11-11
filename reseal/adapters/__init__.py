"""Tool adapters. Add a tool by writing one Adapter subclass and listing it here."""

from .base import (ACCEPTED, ERROR, INCONCLUSIVE, REJECTED, Adapter, NotApplicable, Run, Verdict)
from .halo import HaloAdapter
from .obsigna_ import ObsignaAdapter
from .tool_e import ToolEAdapter
from .signet import SignetAdapter
from .witnesskit_ import WitnessKitAdapter

ALL = [HaloAdapter, WitnessKitAdapter, SignetAdapter, ObsignaAdapter, ToolEAdapter]


def get(name: str) -> Adapter:
    for cls in ALL:
        if cls.name == name:
            return cls()
    raise KeyError(f"unknown tool {name!r}; known: {[c.name for c in ALL]}")


__all__ = ["ALL", "get", "Adapter", "Run", "Verdict", "NotApplicable",
           "ACCEPTED", "REJECTED", "INCONCLUSIVE", "ERROR"]
