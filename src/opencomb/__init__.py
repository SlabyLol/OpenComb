"""
OpenComb – Smart Combiner for Code, Configs, Prompts, Templates, Recipes,
Environment files, Reports and Combinatorial Generation.

A practical toolkit for developers.
"""

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer

__version__ = "0.3.0"
__all__ = [
    "CodeCombiner",
    "ConfigMerger",
    "CombinatorialGenerator",
    "PromptCombiner",
    "TemplateRenderer",
    "RecipeRunner",
    "EnvMerger",
    "CodeFormatter",
    "ReportGenerator",
    "__version__",
]
