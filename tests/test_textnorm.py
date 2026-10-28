"""Tests για κανονικοποίηση κειμένου."""
from tooldock.core.textnorm import normalize


def test_lowercase_and_accents():
    assert normalize("ΕΞΕΡΕΎΝΗΣΗ") == "εξερευνηση"


def test_whitespace():
    assert normalize("  α   β  ") == "α β"
