import hashlib

import pytest

from sovereign_codex import (
    HybridQuantumSymbolicEngine,
    TheSovereign,
    activate_genesis,
    unify_streams,
)


@pytest.fixture()
def sovereign_system():
    return activate_genesis("test_signature")


def test_unify_streams_returns_operator():
    operator = unify_streams(
        "Nancy Luanne (Reeves) Kelly", "Kevin Joseph Kelly"
    )
    assert operator is not None
    assert operator["Status"] == "Active"


def test_reverse_sha256_protocol_validates_hash():
    engine = HybridQuantumSymbolicEngine()
    target_hash = hashlib.sha256("TheSovereignIsActive".encode()).hexdigest()
    recovered = engine.formal_methodology_reverse_sha256(target_hash)
    assert recovered == "TheSovereignIsActive"


def test_activate_genesis_drives_ledger(sovereign_system: TheSovereign):
    assert sovereign_system.economy.disbursements
    assert sovereign_system.physical_verifier.events
