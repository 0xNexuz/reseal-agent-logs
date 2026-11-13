"""Checks on the claims-versus-behaviour labelling."""

from reseal.analyze import claim_for, label, outcome


def row(strength, tier="T1", notes=""):
    return {"strength": strength, "tier": tier, "notes": notes, "quote": "q", "setup_needed": ""}


def test_specific_claim_beats_slogan():
    claims = {("t", "edit"): [row("claims", "any", "general slogan"), row("disclaims", "T2")]}
    assert claim_for(claims, "t", "edit", "T2")[:2] == ("disclaims", "specific")
    assert claim_for(claims, "t", "edit", "T1")[:2] == ("claims", "slogan")
    assert claim_for(claims, "t", "delete", "T1")[:2] == ("silent", "none")


def test_most_cautious_statement_governs():
    claims = {("t", "rewrite"): [row("claims", "T2"), row("claims_with_setup", "T2")]}
    assert claim_for(claims, "t", "rewrite", "T2")[0] == "claims_with_setup"


def test_outcome():
    mk = lambda d: {"applicable": True, "detected": d}
    assert outcome([mk(True), mk(True)]) == ("caught", 2, 2)
    assert outcome([mk(False), mk(False)]) == ("missed", 0, 2)
    assert outcome([mk(True), mk(False)]) == ("partial", 1, 2)
    assert outcome([{"applicable": False, "detected": False}]) == ("n/a", 0, 0)


def test_labels():
    assert label("claims", "specific", "default", "caught") == "holds"
    assert label("claims", "specific", "default", "missed") == "claim not met"
    assert label("claims", "specific", "default", "partial") == "claim not met"
    assert label("claims", "slogan", "default", "missed") == "headline not met"
    assert label("claims_with_setup", "specific", "default", "missed") == "needs setup (disclosed)"
    assert label("claims_with_setup", "specific", "strong", "caught") == "holds with setup"
    assert label("claims_with_setup", "specific", "strong", "missed") == "claim not met"
    assert label("claims_with_setup", "specific", "strong", "missed", wired=False) == "setup left to the user (disclosed)"
    assert label("disclaims", "specific", "default", "missed") == "disclosed limit"
    assert label("disclaims", "specific", "strong", "caught") == "better than stated"
    assert label("silent", "none", "default", "missed") == "silent miss"
    assert label("silent", "none", "default", "caught") == "caught (unstated)"
