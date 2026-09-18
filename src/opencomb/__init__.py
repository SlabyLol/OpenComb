"""
OpenComb – Smart Combiner for Code, Configs, Prompts, Templates, Recipes,
Environment files, Packages, Reports and Combinatorial Generation.
"""

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.pak import PackageManager
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer

__version__ = "0.4.0"
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
    "PackageManager",
    "__version__",
]
