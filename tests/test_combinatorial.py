"""Tests for CombinatorialGenerator."""

from opencomb.combinatorial import CombinatorialGenerator


def test_cartesian():
    gen = CombinatorialGenerator()
    params = {
        "a": [1, 2],
        "b": ["x", "y"],
    }
    combos = gen.cartesian(params)
    assert len(combos) == 4
    assert {"a": 1, "b": "x"} in combos
    assert {"a": 2, "b": "y"} in combos


def test_cartesian_limit():
    gen = CombinatorialGenerator()
    params = {"a": list(range(10)), "b": list(range(10))}
    combos = gen.cartesian(params, limit=5)
    assert len(combos) == 5


def test_pairwise():
    gen = CombinatorialGenerator(seed=42)
    params = {
        "os": ["linux", "windows", "macos"],
        "python": ["3.10", "3.11", "3.12"],
        "arch": ["x64", "arm64"],
    }
    combos = gen.pairwise(params)
    # Should be significantly smaller than full cartesian (3*3*2 = 18)
    assert len(combos) < 18
    assert len(combos) >= 6  # at least some coverage


def test_sample():
    gen = CombinatorialGenerator(seed=123)
    params = {"x": [1, 2, 3], "y": ["a", "b"]}
    samples = gen.sample(params, n=5)
    assert len(samples) == 5
    for s in samples:
        assert s["x"] in [1, 2, 3]
        assert s["y"] in ["a", "b"]


def test_empty():
    gen = CombinatorialGenerator()
    assert gen.cartesian({}) == [{}]
    assert gen.pairwise({}) == [{}]
