"""Smoke tests to ensure packages import correctly."""

import importlib

MODULES = [
    "core",
    "core.neus_system",
    "core.consciousness",
    "core.consciousness.self_model.self_model_engine",
    "core.reasoning",
    "core.reasoning.causal.causal_reasoning_engine",
]


def test_imports():
    for mod in MODULES:
        module = importlib.import_module(mod)
        assert module is not None
