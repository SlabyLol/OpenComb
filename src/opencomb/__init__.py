"""
OpenComb – Everything developers need:
Code combine, configs, prompts, templates, recipes, env, packages (oc-pak),
project init, checks, version bump, drill mode, reports and more.
"""

from opencomb.check import Checker
from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.drill import DrillShell, start_drill
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.pak import PackageManager
from opencomb.project import ProjectHelper
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer

__version__ = "0.6.0"
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
    "ProjectHelper",
    "Checker",
    "DrillShell",
    "start_drill",
    "__version__",
]
