"""Combinatorial generation utilities – useful for testing and experiments."""

from __future__ import annotations

import itertools
import random
from collections.abc import Callable
from typing import Any, Iterator


class CombinatorialGenerator:
    """
    Generate combinations of parameters.

    Supports:
    - Full cartesian product
    - Efficient pairwise (all-pairs) testing
    - Random sampling
    - Constraints (filter invalid combinations)
    """

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def cartesian(
        self,
        parameters: dict[str, list[Any]],
        *,
        limit: int | None = None,
        constraints: list[Callable[[dict[str, Any]], bool]] | None = None,
    ) -> list[dict[str, Any]]:
        if not parameters:
            return [{}]

        keys = list(parameters.keys())
        value_lists = [parameters[k] for k in keys]

        combos = []
        for values in itertools.product(*value_lists):
            combo = dict(zip(keys, values))
            if constraints and not all(c(combo) for c in constraints):
                continue
            combos.append(combo)
            if limit is not None and len(combos) >= limit:
                break

        return combos

    def pairwise(
        self,
        parameters: dict[str, list[Any]],
        *,
        limit: int | None = None,
        constraints: list[Callable[[dict[str, Any]], bool]] | None = None,
    ) -> list[dict[str, Any]]:
        if not parameters:
            return [{}]

        keys = list(parameters.keys())
        if len(keys) == 1:
            combos = [{keys[0]: v} for v in parameters[keys[0]]]
            if constraints:
                combos = [c for c in combos if all(fn(c) for fn in constraints)]
            return combos

        required_pairs: set[tuple[tuple[str, Any], tuple[str, Any]]] = set()
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1 :]:
                for v1 in parameters[k1]:
                    for v2 in parameters[k2]:
                        required_pairs.add(((k1, v1), (k2, v2)))

        uncovered = required_pairs.copy()
        result: list[dict[str, Any]] = []

        product_size = 1
        for v in parameters.values():
            product_size *= max(1, len(v))
        seed_count = min(8, product_size)

        attempts = 0
        while len(result) < seed_count and attempts < seed_count * 20:
            attempts += 1
            combo = {k: self.rng.choice(parameters[k]) for k in keys}
            if constraints and not all(c(combo) for c in constraints):
                continue
            result.append(combo)
            self._cover(combo, uncovered)

        max_iterations = 2000
        iteration = 0
        while uncovered and iteration < max_iterations:
            iteration += 1
            best_combo = None
            best_cover = 0

            for _ in range(80):
                candidate = {k: self.rng.choice(parameters[k]) for k in keys}
                if constraints and not all(c(candidate) for c in constraints):
                    continue
                cover_count = self._count_cover(candidate, uncovered)
                if cover_count > best_cover:
                    best_cover = cover_count
                    best_combo = candidate

            if best_combo is None or best_cover == 0:
                break

            result.append(best_combo)
            self._cover(best_combo, uncovered)

            if limit is not None and len(result) >= limit:
                break

        return result

    def sample(
        self,
        parameters: dict[str, list[Any]],
        n: int,
        *,
        constraints: list[Callable[[dict[str, Any]], bool]] | None = None,
    ) -> list[dict[str, Any]]:
        if not parameters:
            return [{}] * n

        keys = list(parameters.keys())
        result = []
        attempts = 0
        max_attempts = n * 50

        while len(result) < n and attempts < max_attempts:
            attempts += 1
            combo = {k: self.rng.choice(parameters[k]) for k in keys}
            if constraints and not all(c(combo) for c in constraints):
                continue
            result.append(combo)

        return result

    def iterate(
        self,
        parameters: dict[str, list[Any]],
        method: str = "cartesian",
        *,
        constraints: list[Callable[[dict[str, Any]], bool]] | None = None,
    ) -> Iterator[dict[str, Any]]:
        if method == "cartesian":
            for combo in self.cartesian(parameters, constraints=constraints):
                yield combo
        else:
            for combo in self.pairwise(parameters, constraints=constraints):
                yield combo

    @staticmethod
    def _cover(
        combo: dict[str, Any],
        uncovered: set[tuple[tuple[str, Any], tuple[str, Any]]],
    ) -> None:
        keys = list(combo.keys())
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1 :]:
                pair = ((k1, combo[k1]), (k2, combo[k2]))
                uncovered.discard(pair)
                uncovered.discard(((k2, combo[k2]), (k1, combo[k1])))

    @staticmethod
    def _count_cover(
        combo: dict[str, Any],
        uncovered: set[tuple[tuple[str, Any], tuple[str, Any]]],
    ) -> int:
        count = 0
        keys = list(combo.keys())
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1 :]:
                pair = ((k1, combo[k1]), (k2, combo[k2]))
                if pair in uncovered or ((k2, combo[k2]), (k1, combo[k1])) in uncovered:
                    count += 1
        return count
