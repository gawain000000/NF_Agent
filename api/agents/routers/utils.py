import importlib.resources
import json
from typing import Any, Callable, Dict

import yaml


def load_openapi_examples(target: str) -> dict[str, Any]:
    """
    Load an OpenAPI example from a resource file within the 'openapi_examples' directory.

    Tries various file extensions including no extension, '.yaml', '.yml', and '.json'.

    Args:
        target: The base name of the target file without an extension.

    Returns:
        The loaded data as a dictionary.

    Raises:
        FileNotFoundError: If none of the expected files can be found.
        ValueError: If a file with an unknown extension is encountered.
    """
    base = importlib.resources.files(__package__).joinpath("openapi_examples")
    # Map file extensions to their corresponding loader functions.
    loaders: Dict[str, Callable[[bytes], Any]] = {
        ".json": json.loads,
        ".yaml": yaml.safe_load,
        ".yml": yaml.safe_load,
    }

    # Try with different extensions.
    for ext in ("", ".yaml", ".yml", ".json"):
        path = base.joinpath(target + ext)
        if not path.is_file():
            continue

        name = path.name
        stem, dot, suffix = name.rpartition(".")
        if not dot:  # Skip files without an extension.
            continue

        suffix = "." + suffix.lower()
        loader = loaders.get(suffix)
        if loader is None:
            raise ValueError(f"Unknown file extension: {suffix!r}")

        with path.open("rb") as handle:
            return loader(handle.read())

    raise FileNotFoundError(f"Cannot locate: {target!r}")
