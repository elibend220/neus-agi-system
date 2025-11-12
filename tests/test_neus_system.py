"""Tests for the NeusSystem placeholder."""

from core.neus_system import NeusSystem


def test_neus_system_start(capsys):
    s = NeusSystem()
    s.start()
    captured = capsys.readouterr()
    assert "NeusSystem started" in captured.out
