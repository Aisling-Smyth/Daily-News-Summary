from pathlib import Path


PROMPTS_DIR = Path("prompts")


def load_prompt(name: str) -> str:
    """
    Load a prompt template from the prompts directory.

    Args:
        name:
            Prompt filename without extension.

    Returns:
        Prompt template text.

    Raises:
        FileNotFoundError:
            If the prompt file does not exist.
    """

    path = PROMPTS_DIR / name

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}"
        )

    return path.read_text(
        encoding="utf-8"
    )