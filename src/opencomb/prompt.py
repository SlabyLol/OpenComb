"""Prompt combining and management for LLM workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PromptCombiner:
    """
    Combine system prompts, user prompts, few-shot examples and context
    into a single well-structured prompt.
    """

    def __init__(
        self,
        system_separator: str = "\n\n",
        example_header: str = "### Example {n}\n",
        section_header: str = "## {title}\n\n",
    ):
        self.system_separator = system_separator
        self.example_header = example_header
        self.section_header = section_header

    def combine(
        self,
        *,
        system: str | list[str] | None = None,
        instruction: str | None = None,
        context: str | list[str] | None = None,
        examples: list[dict[str, str]] | None = None,
        user: str | None = None,
        extra_sections: dict[str, str] | None = None,
    ) -> str:
        """
        Build a complete prompt from components.

        Args:
            system: One or more system messages.
            instruction: Main task instruction.
            context: Background information / retrieved documents.
            examples: List of {"input": ..., "output": ...} few-shot examples.
            user: The actual user query.
            extra_sections: Arbitrary named sections.

        Returns:
            Fully combined prompt string.
        """
        parts: list[str] = []

        # System
        if system:
            if isinstance(system, str):
                systems = [system]
            else:
                systems = system
            system_text = self.system_separator.join(s.strip() for s in systems if s.strip())
            if system_text:
                parts.append(self.section_header.format(title="System") + system_text)

        # Instruction
        if instruction and instruction.strip():
            parts.append(self.section_header.format(title="Instruction") + instruction.strip())

        # Context
        if context:
            if isinstance(context, str):
                contexts = [context]
            else:
                contexts = context
            ctx_text = "\n\n".join(c.strip() for c in contexts if c.strip())
            if ctx_text:
                parts.append(self.section_header.format(title="Context") + ctx_text)

        # Few-shot examples
        if examples:
            example_blocks = []
            for i, ex in enumerate(examples, 1):
                header = self.example_header.format(n=i)
                block = header
                if "input" in ex:
                    block += f"**Input:**\n{ex['input'].strip()}\n\n"
                if "output" in ex:
                    block += f"**Output:**\n{ex['output'].strip()}\n"
                example_blocks.append(block.strip())
            if example_blocks:
                parts.append(
                    self.section_header.format(title="Examples")
                    + "\n\n".join(example_blocks)
                )

        # Extra sections
        if extra_sections:
            for title, content in extra_sections.items():
                if content and content.strip():
                    parts.append(
                        self.section_header.format(title=title) + content.strip()
                    )

        # User query
        if user and user.strip():
            parts.append(self.section_header.format(title="User") + user.strip())

        return "\n\n".join(parts).strip() + "\n"

    def from_files(
        self,
        *,
        system_files: list[str | Path] | None = None,
        instruction_file: str | Path | None = None,
        context_files: list[str | Path] | None = None,
        examples_file: str | Path | None = None,
        user_file: str | Path | None = None,
    ) -> str:
        """Load components from files and combine them."""
        system = None
        if system_files:
            system = [Path(f).read_text(encoding="utf-8") for f in system_files]

        instruction = None
        if instruction_file:
            instruction = Path(instruction_file).read_text(encoding="utf-8")

        context = None
        if context_files:
            context = [Path(f).read_text(encoding="utf-8") for f in context_files]

        examples = None
        if examples_file:
            import yaml
            data = yaml.safe_load(Path(examples_file).read_text(encoding="utf-8"))
            if isinstance(data, list):
                examples = data

        user = None
        if user_file:
            user = Path(user_file).read_text(encoding="utf-8")

        return self.combine(
            system=system,
            instruction=instruction,
            context=context,
            examples=examples,
            user=user,
        )

    def save(self, prompt: str, path: str | Path) -> None:
        """Save the combined prompt to a file."""
        Path(path).write_text(prompt, encoding="utf-8")
