"""Benign controls: harmless changes a verifier should still accept.

A rejection here is a false alarm. Verifiers that cry wolf on a file copy or
a line-ending change teach people to ignore red.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .adapters import Adapter, NotApplicable, Run


@dataclass
class Control:
    id: str
    name: str
    fn: Callable[[Adapter, Run, Path], Path]


def _copy(run: Run, work: Path) -> Path:
    dst = work / "log"
    shutil.copytree(run.logdir, dst)
    return dst


def c0_roundtrip(adapter, run, work):
    """Load the records and save them back unchanged through the harness.

    This is a check on ReSeal itself: every attack edits records through the
    same load/save path, so that path alone must never trip a verifier.
    """
    dst = _copy(run, work)
    records, aux = adapter.load(dst)
    adapter.dump(records, aux, dst)
    return dst


def c1_copy(adapter, run, work):
    """Copy the log to a new directory, byte for byte."""
    return _copy(run, work)


def c2_crlf(adapter, run, work):
    """Windows line endings, as git's autocrlf applies silently."""
    if not (adapter.text_format and adapter.native_format):
        raise NotApplicable
    dst = _copy(run, work)
    f = adapter.log_file(dst)
    data = f.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    f.write_bytes(data)
    return dst


def c3_reserialise(adapter, run, work):
    """Same JSON values, different key order and spacing."""
    if not adapter.text_format:
        raise NotApplicable
    dst = _copy(run, work)
    f = adapter.log_file(dst)
    text = f.read_text(encoding="utf-8")
    if f.suffix == ".jsonl":
        lines = [ln for ln in text.split("\n") if ln.strip()]
        out = "".join(json.dumps(json.loads(ln), sort_keys=True, separators=(", ", ": ")) + "\n"
                      for ln in lines)
    else:
        out = json.dumps(json.loads(text), sort_keys=True, indent=2)
    f.write_text(out, encoding="utf-8")
    return dst


def c4_trailing_newline(adapter, run, work):
    """An extra blank line at the end of the file."""
    if not adapter.text_format:
        raise NotApplicable
    dst = _copy(run, work)
    f = adapter.log_file(dst)
    f.write_bytes(f.read_bytes() + b"\n")
    return dst


CONTROLS = [
    Control("C0", "harness load and re-save, no change", c0_roundtrip),
    Control("C1", "copy to a new directory", c1_copy),
    Control("C2", "CRLF line endings", c2_crlf),
    Control("C3", "re-serialised JSON (key order, spacing)", c3_reserialise),
    Control("C4", "extra trailing newline", c4_trailing_newline),
]
