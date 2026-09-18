"""OpenComb – Developer Swiss Army Knife."""

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
from opencomb.tools import (
    Differ,
    Hasher,
    OutdatedChecker,
    ProjectStats,
    ReportServer,
    Searcher,
    TodoExtractor,
    Watcher,
)

__version__ = "0.7.0"
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
    "Searcher",
    "TodoExtractor",
    "ProjectStats",
    "Differ",
    "Hasher",
    "OutdatedChecker",
    "ReportServer",
    "Watcher",
    "__version__",
]
