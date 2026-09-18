"""Combinatorial generation utilities – useful for testing and experiments."""

from __future__ import annotations

import itertools
import random
from typing import Any, Iterator


class CombinatorialGenerator:
    """
    Generate combinations of parameters.

    Supports full cartesian product and efficient pairwise (all-pairs) testing.
    """

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def cartesian(
        self,
        parameters: dict[str, list[Any]],
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate the full cartesian product of parameter values.

        Args:
            parameters: Mapping of parameter name → list of possible values.
            limit: Optional maximum number of combinations to return.

        Returns:
            List of dictionaries, each representing one combination.
        """
        if not parameters:
            return [{}]

        keys = list(parameters.keys())
        value_lists = [parameters[k] for k in keys]

        combos = []
        for values in itertools.product(*value_lists):
            combos.append(dict(zip(keys, values)))
            if limit is not None and len(combos) >= limit:
                break

        return combos

    def pairwise(
        self,
        parameters: dict[str, list[Any]],
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate a (near) minimal set of combinations that cover all pairwise
        interactions between parameters. Very useful for efficient testing.

        This is a simple greedy implementation – good enough for most practical cases.
        """
        if not parameters:
            return [{}]

        keys = list(parameters.keys())
        if len(keys) == 1:
            return [{keys[0]: v} for v in parameters[keys[0]]]

        # Generate all required pairs
        required_pairs: set[tuple[tuple[str, Any], tuple[str, Any]]] = set()
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1 :]:
                for v1 in parameters[k1]:
                    for v2 in parameters[k2]:
                        required_pairs.add(((k1, v1), (k2, v2)))

        # Greedy covering
        uncovered = required_pairs.copy()
        result: list[dict[str, Any]] = []

        # Start with a few random full combinations to seed
        for _ in range(min(5, len(list(itertools.product(*[parameters[k] for k in keys]))))):
            combo = {k: self.rng.choice(parameters[k]) for k in keys}
            result.append(combo)
            self._cover(combo, uncovered)

        # Keep adding combinations that cover the most remaining pairs
        max_iterations = 1000
        iteration = 0
        while uncovered and iteration < max_iterations:
            iteration += 1
            best_combo = None
            best_cover = 0

            # Try a limited number of candidates
            for _ in range(50):
                candidate = {k: self.rng.choice(parameters[k]) for k in keys}
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
    ) -> list[dict[str, Any]]:
        """Randomly sample n combinations (with replacement if necessary)."""
        if not parameters:
            return [{}] * n

        keys = list(parameters.keys())
        result = []
        for _ in range(n):
            result.append({k: self.rng.choice(parameters[k]) for k in keys})
        return result

    def iterate(
        self,
        parameters: dict[str, list[Any]],
        method: str = "cartesian",
    ) -> Iterator[dict[str, Any]]:
        """Lazy iterator over combinations."""
        if method == "cartesian":
            keys = list(parameters.keys())
            value_lists = [parameters[k] for k in keys]
            for values in itertools.product(*value_lists):
                yield dict(zip(keys, values))
        else:
            for combo in self.pairwise(parameters):
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
                # also the reverse order just in case
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
