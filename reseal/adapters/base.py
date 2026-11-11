"""Adapter contract: how ReSeal talks to one audit-log tool.

An adapter does four things, always through the tool's own public code:

1. ``record``  - write an event list with the tool's recording API.
2. ``verify``  - run the tool's own verifier and normalise the verdict.
3. ``load`` / ``dump`` - read and write the tool's stored records so attacks
   can change them.
4. field hooks - tell the attack library where an argument, a policy verdict,
   a timestamp and the integrity fields live in one stored record.

Two setups are supported for every tool:

* ``default``: what a user gets by following the tool's quick start.
* ``strong`` : the strongest verification the tool documents (pinned keys,
  expected head, external witness, ...). Anything the verifier relies on in
  this setup lives in ``Run.external`` - state held outside the attacker's
  reach. Attacks never touch it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ACCEPTED = "accepted"          # verifier says the log is fine
REJECTED = "rejected"          # verifier says the log was tampered with
INCONCLUSIVE = "inconclusive"  # verifier refuses to vouch (e.g. unwitnessed)
ERROR = "error"                # verifier crashed (counted separately)


@dataclass
class Verdict:
    status: str
    detail: str = ""

    @property
    def detected(self) -> bool:
        """An attack counts as detected unless the verifier accepts the log."""
        return self.status != ACCEPTED


@dataclass
class Run:
    """One recorded log plus everything around it."""

    logdir: Path                                   # what the attacker can write
    external: dict = field(default_factory=dict)   # trusted state held outside
    secrets: dict = field(default_factory=dict)    # operator-only key material


class NotApplicable(Exception):
    """Raised by a hook when an attack has no meaning for this tool."""


class Adapter:
    name: str = "base"
    package: str = ""            # distribution name, for version pinning
    text_format: bool = True     # is the native log a text file?
    native_format: bool = True   # does the tool define the on-disk format?
    signed: bool = False         # does the tool sign records?
    # What the two setups mean for this tool, in one line each (for reports).
    default_setup: str = ""
    strong_setup: str = ""

    # -- recording and verifying -------------------------------------------
    def record(self, events: list[dict], logdir: Path, *, strong: bool,
               secrets: dict | None = None) -> Run:
        """Record ``events``. ``secrets`` lets the operator reuse their keys
        (tier 2 rewrite); ``None`` means generate fresh keys."""
        raise NotImplementedError

    def verify(self, logdir: Path, external: dict, *, strong: bool) -> Verdict:
        raise NotImplementedError

    # -- stored records ----------------------------------------------------
    def log_file(self, logdir: Path) -> Path:
        raise NotImplementedError

    def load(self, logdir: Path) -> tuple[list[dict], Any]:
        """Return (records, aux). ``aux`` is whatever else the file holds."""
        raise NotImplementedError

    def dump(self, records: list[dict], aux: Any, logdir: Path) -> None:
        raise NotImplementedError

    # -- field hooks (mutate one stored record in place) ---------------------
    def edit_arg(self, rec: dict) -> None:
        raise NotApplicable

    def flip_verdict(self, rec: dict) -> None:
        raise NotApplicable

    def backdate(self, rec: dict) -> None:
        raise NotApplicable

    def edit_uncovered(self, rec: dict) -> None:
        """Change a stored field the tool's integrity check may not cover."""
        raise NotApplicable

    def strip_integrity(self, rec: dict) -> None:
        """Downgrade: remove or blank the signature / integrity fields."""
        raise NotApplicable

    def fresh_identity(self, rec: dict) -> None:
        """Give a copied record a new id so an insert is not a plain replay."""
        raise NotApplicable
