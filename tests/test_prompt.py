"""Tests for PromptCombiner."""

from opencomb.prompt import PromptCombiner


def test_basic_combine():
    pc = PromptCombiner()
    result = pc.combine(
        system="You are a helpful assistant.",
        instruction="Answer the question.",
        user="What is 2+2?",
    )
    assert "System" in result
    assert "You are a helpful assistant." in result
    assert "What is 2+2?" in result


def test_with_examples():
    pc = PromptCombiner()
    result = pc.combine(
        system="Be concise.",
        examples=[
            {"input": "Hi", "output": "Hello!"},
            {"input": "Bye", "output": "Goodbye!"},
        ],
        user="How are you?",
    )
    assert "Examples" in result
    assert "Hello!" in result
    assert "Goodbye!" in result


def test_extra_sections():
    pc = PromptCombiner()
    result = pc.combine(
        system="Sys",
        extra_sections={"Constraints": "Keep it short.", "Style": "Friendly"},
        user="Hello",
    )
    assert "Constraints" in result
    assert "Keep it short." in result
