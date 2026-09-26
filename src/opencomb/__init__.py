"""
OpenComb – Everything developers need.

>>> import opencomb
>>> opencomb.__version__
'0.19.1'
"""

from __future__ import annotations

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer
from opencomb.pak import PackageManager
from opencomb.project import ProjectHelper
from opencomb.check import Checker
from opencomb.builder import interactive_build, run_build_ids, all_targets
from opencomb.drill import start_drill, DrillShell
from opencomb.templates_catalog import list_templates, apply_template, BUILDERS
from opencomb.scaffold import (
    STACKS, COMPONENTS, list_stacks, list_components,
    apply_stack, add_component, run_wizard, project_doctor,
    print_doctor_report, suggest_structure,
)
from opencomb.tools import (
    Searcher, TodoExtractor, ProjectStats, Differ, Hasher,
    OutdatedChecker, ReportServer, Watcher,
)
from opencomb.devtools import (
    GitHelper, SecretScanner, HttpClient, Bench,
    JsonYamlQuery, PortProbe, GitClone, SiteCloner,
)
from opencomb.occ import (
    SSHTarget, parse_target_string,
    connect as occ_connect,
    run_interactive as occ_interactive,
    list_profiles as occ_list_profiles,
    load_profile as occ_load_profile,
    save_profile as occ_save_profile,
)
from opencomb.codec import encode, decode, encode_file, decode_file, encode_chunks, decode_chunks
from opencomb.api import (
    combine, merge_configs, merge_env, generate_combos,
    render_template, build_prompt, run_recipe, new_project,
    search, todos, stats, doctor,
)

__version__ = "0.19.1"

__all__ = [
    "__version__",
    "CodeCombiner", "ConfigMerger", "CombinatorialGenerator",
    "PromptCombiner", "TemplateRenderer", "RecipeRunner",
    "EnvMerger", "CodeFormatter", "ReportGenerator",
    "PackageManager", "ProjectHelper", "Checker",
    "interactive_build", "run_build_ids", "all_targets",
    "DrillShell", "start_drill",
    "list_templates", "apply_template", "BUILDERS",
    "STACKS", "COMPONENTS", "list_stacks", "list_components",
    "apply_stack", "add_component", "run_wizard",
    "project_doctor", "print_doctor_report", "suggest_structure",
    "Searcher", "TodoExtractor", "ProjectStats", "Differ", "Hasher",
    "OutdatedChecker", "ReportServer", "Watcher",
    "GitHelper", "SecretScanner", "HttpClient", "Bench",
    "JsonYamlQuery", "PortProbe", "GitClone", "SiteCloner",
    "SSHTarget", "parse_target_string",
    "occ_connect", "occ_interactive", "occ_list_profiles",
    "occ_load_profile", "occ_save_profile",
    "combine", "merge_configs", "merge_env", "generate_combos",
    "render_template", "build_prompt", "run_recipe", "new_project",
    "search", "todos", "stats", "doctor",
    "encode", "decode", "encode_file", "decode_file", "encode_chunks", "decode_chunks",
]
