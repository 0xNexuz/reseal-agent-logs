"""Adapter for a fifth tool, reported as Tool E.

The adapter is kept out of this repository until the tool's maintainer has
been told about its result. See README.
"""

from .base import Adapter


class ToolEAdapter(Adapter):
    name = "tool-e"
    package = ""
    default_setup = "withheld"
    strong_setup = "withheld"

    def record(self, events, logdir, *, strong, secrets=None):
        raise NotImplementedError("the Tool E adapter is not in this repository")

    def verify(self, logdir, external, *, strong):
        raise NotImplementedError("the Tool E adapter is not in this repository")
