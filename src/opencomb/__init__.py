"""
OpenComb – Smart Combiner for Code, Configs, Prompts and Combinatorial Generation.

A practical toolkit for developers that helps combine code snippets, merge
configuration files intelligently, and generate combinatorial parameter sets.
"""

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator

__version__ = "0.1.0"
__all__ = [
    "CodeCombiner",
    "ConfigMerger",
    "CombinatorialGenerator",
    "__version__",
]
