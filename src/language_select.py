"""Language selection management module.

Manages persistent storage of the selected programming language,
allowing users to filter exercises by language across commands.
"""
import os
import yaml

SELECTED_LANG_FILE = os.path.expanduser("~/.trainer/selected_language.yml")


def _load() -> dict:
    """Load selected language from the configuration file.

    Returns:
        dict: The loaded configuration data, or empty dict if file doesn't exist or on error.
    """
    if not os.path.isfile(SELECTED_LANG_FILE):
        return {}
    try:
        with open(SELECTED_LANG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception:
        return {}


def _save(data: dict):
    """Save selected language to the configuration file.

    Args:
        data: Dictionary containing the selected language configuration to save.
    """
    os.makedirs(os.path.dirname(SELECTED_LANG_FILE), exist_ok=True)
    with open(SELECTED_LANG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def set_language(language: str):
    """Set the selected programming language.

    Args:
        language: The programming language to select (e.g., 'python', 'javascript', 'C').
    """
    data = _load()
    data["language"] = language
    _save(data)


def get_language() -> str | None:
    """Get the currently selected programming language.

    Returns:
        str or None: The selected language, or None if no language has been selected.
    """
    data = _load()
    return data.get("language")


def clear_language():
    """Clear the selected programming language."""
    data = _load()
    if "language" in data:
        del data["language"]
    _save(data)


def selectRun(args):
    """Handle the select command to choose a programming language.

    Args:
        args: Command-line arguments containing the language to select.
              Use 'none' to clear the language filter.
              Language is stored with original casing (e.g., C, C++, Python, JavaScript).
    """
    language = args.language.strip()

    if not language:
        print("Error: Language cannot be empty")
        return

    if language.lower() == "none":
        clear_language()
        print("Language filter cleared")
    else:
        set_language(language)
        print(f"Selected language: {language}")


def get_language_filter() -> str | None:
    """Get the language filter string for use in queries.

    Returns:
        str or None: The selected language in lowercase, or None if no language is selected.
    """
    lang = get_language()
    return lang.lower() if lang else None

