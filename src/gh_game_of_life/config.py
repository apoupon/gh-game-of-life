"""Configuration file handling for CLI.

Supports loading configuration from YAML files and merging with command-line arguments.
"""

from pathlib import Path
from typing import Any, Optional


def load_config(config_path: Path | str | None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file. If None, returns empty config.

    Returns:
        Dictionary with configuration values.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file is invalid or malformed.
        IOError: If unable to read config file.

    Example:
        >>> config = load_config("config.yaml")
        >>> config["frames"]
        100
    """
    if config_path is None:
        return {}

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML library required for configuration file support. "
            "Install with: uv add pyyaml"
        )

    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
    except IOError as e:
        raise IOError(f"Failed to read configuration file: {e}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in configuration file: {e}") from e

    # Handle empty file
    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Configuration file must contain a YAML dictionary, got {type(data).__name__}"
        )

    # Normalize keys: snake_case → snake_case
    normalized = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError(
                f"Configuration keys must be strings, got {type(key).__name__}"
            )

        # Convert hyphenated keys to underscores
        normalized_key = key.replace("-", "_").lower()
        normalized[normalized_key] = value

    return normalized


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize configuration values.

    Args:
        config: Configuration dictionary.

    Returns:
        Normalized configuration dictionary.

    Raises:
        ValueError: If configuration values are invalid.

    Allowed keys:
        - username: str
        - output: str
        - frames: int
        - strategy: str ('loop' or 'void')
        - cell_size: int
        - frame_delay: int
    """
    validated = {}

    # Define allowed keys and their types
    allowed_keys = {
        "username": (str, type(None)),
        "output": (str, type(None)),
        "frames": (int, type(None)),
        "strategy": (str, type(None)),
        "cell_size": (int, type(None)),
        "cell-size": (int, type(None)),
        "frame_delay": (int, type(None)),
        "frame-delay": (int, type(None)),
    }

    for key, value in config.items():
        if key not in allowed_keys:
            raise ValueError(f"Unknown configuration key: '{key}'")

        expected_types = allowed_keys[key]
        if not isinstance(value, expected_types):
            type_names = " or ".join(t.__name__ for t in expected_types)
            raise ValueError(
                f"Configuration key '{key}' must be {type_names}, got {type(value).__name__}"
            )

        # Normalize key names (hyphenated to underscored)
        normalized_key = key.replace("-", "_")

        # Validate specific values
        if normalized_key == "strategy" and value is not None:
            if value.lower() not in ["loop", "void"]:
                raise ValueError(f"Strategy must be 'loop' or 'void', got '{value}'")
            validated[normalized_key] = value.lower()

        elif normalized_key == "frames" and value is not None:
            if value <= 0:
                raise ValueError(f"Frames must be positive, got {value}")
            validated[normalized_key] = value

        elif normalized_key == "cell_size" and value is not None:
            if value <= 0:
                raise ValueError(f"Cell size must be positive, got {value}")
            validated[normalized_key] = value

        elif normalized_key == "frame_delay" and value is not None:
            if value <= 0:
                raise ValueError(f"Frame delay must be positive, got {value}")
            validated[normalized_key] = value

        else:
            if value is not None:
                validated[normalized_key] = value

    return validated


def merge_configs(
    file_config: dict[str, Any], cli_config: dict[str, Any]
) -> dict[str, Any]:
    """Merge file configuration with CLI configuration.

    CLI arguments override file configuration (CLI has priority).

    Args:
        file_config: Configuration loaded from file.
        cli_config: Configuration from CLI arguments.

    Returns:
        Merged configuration with CLI taking precedence.

    Example:
        >>> file_cfg = {"frames": 50, "strategy": "loop"}
        >>> cli_cfg = {"frames": 100}
        >>> merge_configs(file_cfg, cli_cfg)
        {"frames": 100, "strategy": "loop"}
    """
    merged = {}

    # Start with file config
    merged.update(file_config)

    # Override with CLI config (CLI arguments override file)
    for key, value in cli_config.items():
        if value is not None:
            merged[key] = value

    return merged


def get_final_config(
    file_config: Optional[dict[str, Any]], cli_config: dict[str, Any]
) -> dict[str, Any]:
    """Get final configuration after loading, validating, and merging.

    Args:
        file_config: Configuration loaded from file (or None).
        cli_config: Configuration from CLI arguments.

    Returns:
        Final merged and validated configuration.

    Raises:
        ValueError: If configuration is invalid.
    """
    if file_config is None:
        file_config = {}

    # Validate both configs
    validated_file = validate_config(file_config)
    validated_cli = validate_config(cli_config)

    # Merge with CLI taking precedence
    merged = merge_configs(validated_file, validated_cli)

    return merged
