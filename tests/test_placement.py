"""Έλεγχοι δύο οθονών, αρνητικών θέσεων και αλλαγής διάταξης."""
import pytest
from tooldock.core.placement import place

@pytest.mark.parametrize("bounds,dock,position,expected", [
    ((0,0,1920,1040), "right", (100,100), (1520,100,400,500)),
    ((-1920,0,1920,1040), "left", (200,100), (-1920,100,400,500)),
    ((1920,0,1920,1040), "right", (2000,100), (3440,100,400,500)),
    ((0,0,1920,1040), "floating", (4000,-900), (1520,0,400,500)),
    ((0,0,1920,1040), "bottom", (30,90), (30,540,400,500)),
    ((0,-1080,1920,1080), "top", (30,90), (30,-1080,400,500)),
])
def test_placement(bounds, dock, position, expected):
    assert place(bounds, (400,500), position, dock) == expected

def test_oversized():
    assert place((0,0,320,200), (400,500), (90,90), "floating") == (0,0,320,200)
