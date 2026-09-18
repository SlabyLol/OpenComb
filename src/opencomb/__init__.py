"""
OpenComb – Smart Combiner for Code, Configs, Prompts, Templates, Recipes
and Combinatorial Generation.

A practical toolkit for developers.
"""

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.template import TemplateRenderer

__version__ = "0.2.0"
__all__ = [
    "CodeCombiner",
    "ConfigMerger",
    "CombinatorialGenerator",
    "PromptCombiner",
    "TemplateRenderer",
    "RecipeRunner",
    "__version__",
]
