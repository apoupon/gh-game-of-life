"""Tests for CLI Configuration Options."""

import tempfile
from pathlib import Path

import pytest

from gh_game_of_life.config import (
    get_final_config,
    load_config,
    merge_configs,
    validate_config,
)


class TestConfigLoading:
    """Test YAML configuration file loading."""

    def test_load_config_from_yaml_file(self):
        """Load configuration from valid YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""\
username: torvalds
frames: 100
strategy: loop
cell-size: 15
frame-delay: 750
output: test.gif
""")

            config = load_config(config_file)

            assert config["username"] == "torvalds"
            assert config["frames"] == 100
            assert config["strategy"] == "loop"
            assert config["cell_size"] == 15
            assert config["frame_delay"] == 750
            assert config["output"] == "test.gif"

    def test_load_config_with_none_returns_empty(self):
        """Loading None config returns empty dictionary."""
        config = load_config(None)

        assert config == {}

    def test_load_config_file_not_found(self):
        """Missing config file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_config("/nonexistent/path/config.yaml")

    def test_load_config_with_string_path(self):
        """Load config using string path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("username: test\n")

            config = load_config(str(config_file))

            assert config["username"] == "test"

    def test_load_config_with_path_object(self):
        """Load config using Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("username: test\n")

            config = load_config(config_file)

            assert config["username"] == "test"

    def test_load_config_empty_file(self):
        """Loading empty YAML file returns empty dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("")

            config = load_config(config_file)

            assert config == {}

    def test_load_config_invalid_yaml(self):
        """Invalid YAML raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("invalid: yaml: content: >>>")

            with pytest.raises(ValueError, match="Invalid YAML"):
                load_config(config_file)

    def test_load_config_not_dict(self):
        """YAML file not containing dict raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("- item1\n- item2\n")

            with pytest.raises(ValueError, match="must contain a YAML dictionary"):
                load_config(config_file)

    def test_load_config_normalizes_keys(self):
        """Configuration keys are normalized to lowercase with underscores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("CellSize: 20\nframe-delay: 500\n")

            config = load_config(config_file)

            assert config["cellsize"] == 20
            assert config["frame_delay"] == 500

    def test_load_config_non_string_keys(self):
        """Non-string keys in YAML raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("123: value\n")

            with pytest.raises(ValueError, match="keys must be strings"):
                load_config(config_file)


class TestConfigValidation:
    """Test configuration value validation."""

    def test_validate_valid_config(self):
        """Valid configuration passes validation."""
        config = {
            "username": "test",
            "frames": 100,
            "strategy": "loop",
            "cell_size": 15,
        }

        validated = validate_config(config)

        assert validated["username"] == "test"
        assert validated["frames"] == 100
        assert validated["strategy"] == "loop"
        assert validated["cell_size"] == 15

    def test_validate_unknown_key(self):
        """Unknown configuration key raises ValueError."""
        config = {"unknown_key": "value"}

        with pytest.raises(ValueError, match="Unknown configuration key"):
            validate_config(config)

    def test_validate_wrong_type_username(self):
        """Non-string username raises ValueError."""
        config = {"username": 123}

        with pytest.raises(ValueError, match="must be str or NoneType"):
            validate_config(config)

    def test_validate_wrong_type_frames(self):
        """Non-integer frames raises ValueError."""
        config = {"frames": "100"}

        with pytest.raises(ValueError, match="must be int or NoneType"):
            validate_config(config)

    def test_validate_negative_frames(self):
        """Negative frames raises ValueError."""
        config = {"frames": -5}

        with pytest.raises(ValueError, match="must be positive"):
            validate_config(config)

    def test_validate_zero_frames(self):
        """Zero frames raises ValueError."""
        config = {"frames": 0}

        with pytest.raises(ValueError, match="must be positive"):
            validate_config(config)

    def test_validate_invalid_strategy(self):
        """Invalid strategy value raises ValueError."""
        config = {"strategy": "invalid"}

        with pytest.raises(ValueError, match="must be 'loop' or 'void'"):
            validate_config(config)

    def test_validate_strategy_case_insensitive(self):
        """Strategy is normalized to lowercase."""
        config = {"strategy": "LOOP"}

        validated = validate_config(config)

        assert validated["strategy"] == "loop"

    def test_validate_negative_cell_size(self):
        """Negative cell size raises ValueError."""
        config = {"cell_size": -10}

        with pytest.raises(ValueError, match="must be positive"):
            validate_config(config)

    def test_validate_negative_frame_delay(self):
        """Negative frame delay raises ValueError."""
        config = {"frame_delay": -100}

        with pytest.raises(ValueError, match="must be positive"):
            validate_config(config)

    def test_validate_none_values_allowed(self):
        """None values are allowed (optional fields)."""
        config = {
            "username": None,
            "frames": None,
            "strategy": None,
        }

        validated = validate_config(config)

        # None values are not included in validated config
        assert "username" not in validated or validated["username"] is None

    def test_validate_hyphenated_keys_normalized(self):
        """Hyphenated keys are converted to underscores."""
        config = {
            "cell-size": 20,
            "frame-delay": 600,
        }

        validated = validate_config(config)

        assert validated["cell_size"] == 20
        assert validated["frame_delay"] == 600


class TestConfigMerging:
    """Test configuration merging (file + CLI)."""

    def test_merge_file_and_cli_configs(self):
        """File config is overridden by CLI config."""
        file_config = {"frames": 50, "strategy": "loop"}
        cli_config = {"frames": 100}

        merged = merge_configs(file_config, cli_config)

        assert merged["frames"] == 100  # CLI overrides
        assert merged["strategy"] == "loop"  # From file

    def test_merge_empty_file_config(self):
        """Merging with empty file config uses CLI only."""
        file_config = {}
        cli_config = {"username": "test", "frames": 100}

        merged = merge_configs(file_config, cli_config)

        assert merged["username"] == "test"
        assert merged["frames"] == 100

    def test_merge_empty_cli_config(self):
        """Merging with empty CLI config uses file only."""
        file_config = {"username": "test", "frames": 100}
        cli_config = {}

        merged = merge_configs(file_config, cli_config)

        assert merged["username"] == "test"
        assert merged["frames"] == 100

    def test_merge_cli_none_values_not_override(self):
        """CLI None values don't override file config."""
        file_config = {"frames": 50}
        cli_config = {"frames": None, "username": "test"}

        merged = merge_configs(file_config, cli_config)

        assert merged["frames"] == 50  # File value preserved
        assert merged["username"] == "test"

    def test_merge_preserves_all_fields(self):
        """Merge preserves all fields from both configs."""
        file_config = {"frames": 50, "strategy": "loop", "cell_size": 10}
        cli_config = {"username": "test", "frames": 100}

        merged = merge_configs(file_config, cli_config)

        assert merged["username"] == "test"
        assert merged["frames"] == 100
        assert merged["strategy"] == "loop"
        assert merged["cell_size"] == 10


class TestFinalConfig:
    """Test final config assembly."""

    def test_get_final_config_from_file_only(self):
        """Final config from file only."""
        file_config = {"username": "test", "frames": 100}
        cli_config = {}

        final = get_final_config(file_config, cli_config)

        assert final["username"] == "test"
        assert final["frames"] == 100

    def test_get_final_config_cli_overrides(self):
        """Final config with CLI overriding file."""
        file_config = {"username": "test", "frames": 50}
        cli_config = {"frames": 100}

        final = get_final_config(file_config, cli_config)

        assert final["username"] == "test"
        assert final["frames"] == 100

    def test_get_final_config_none_file(self):
        """Final config with None file config."""
        file_config = None
        cli_config = {"username": "test"}

        final = get_final_config(file_config, cli_config)

        assert final["username"] == "test"

    def test_get_final_config_validation_error(self):
        """Final config raises error on invalid config."""
        file_config = {"frames": -5}
        cli_config = {}

        with pytest.raises(ValueError):
            get_final_config(file_config, cli_config)


class TestAcceptanceCriteria:
    """Test FR-402 acceptance criteria."""

    def test_supports_frames_configuration(self):
        """Supports frames configuration option."""
        config = {"frames": 200}

        validated = validate_config(config)

        assert validated["frames"] == 200

    def test_supports_strategy_configuration(self):
        """Supports strategy configuration option."""
        config = {"strategy": "void"}

        validated = validate_config(config)

        assert validated["strategy"] == "void"

    def test_supports_output_path_configuration(self):
        """Supports output path configuration option."""
        config = {"output": "/tmp/custom.gif"}

        validated = validate_config(config)

        assert validated["output"] == "/tmp/custom.gif"

    def test_provides_sensible_defaults_via_cli(self):
        """Sensible defaults are applied (in CLI main)."""
        # This is tested in test_cli.py where defaults are applied
        # The config module just validates and merges
        pass

    def test_supports_optional_yaml_config_file(self):
        """Supports loading optional YAML config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""\
frames: 150
strategy: void
output: custom.gif
""")

            config = load_config(config_file)
            validated = validate_config(config)

            assert validated["frames"] == 150
            assert validated["strategy"] == "void"
            assert validated["output"] == "custom.gif"


class TestConfigIntegration:
    """Integration tests for configuration."""

    def test_full_config_flow_yaml_and_cli(self):
        """Complete flow: load YAML, merge with CLI, validate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""\
username: torvalds
frames: 50
strategy: loop
cell-size: 10
output: base.gif
""")

            # Load file config
            file_config = load_config(config_file)

            # Simulate CLI overrides
            cli_config = {"frames": 100, "output": "override.gif"}

            # Merge and validate
            final = get_final_config(file_config, cli_config)

            assert final["username"] == "torvalds"
            assert final["frames"] == 100  # CLI overrides
            assert final["strategy"] == "loop"
            assert final["cell_size"] == 10
            assert final["output"] == "override.gif"  # CLI overrides

    def test_yaml_with_various_formats(self):
        """YAML supports various key formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""\
username: test
frames: 100
strategy: loop
cell-size: 15
frame-delay: 750
output: test.gif
""")

            config = load_config(config_file)
            validated = validate_config(config)

            # All keys should be normalized and present
            assert "username" in validated
            assert "frames" in validated
            assert "strategy" in validated
            assert "cell_size" in validated
            assert "frame_delay" in validated
            assert "output" in validated


class TestConfigDocumentation:
    """Test configuration documentation."""

    def test_load_config_has_docstring(self):
        """load_config function has docstring."""
        assert load_config.__doc__ is not None

    def test_validate_config_has_docstring(self):
        """validate_config function has docstring."""
        assert validate_config.__doc__ is not None

    def test_merge_configs_has_docstring(self):
        """merge_configs function has docstring."""
        assert merge_configs.__doc__ is not None

    def test_get_final_config_has_docstring(self):
        """get_final_config function has docstring."""
        assert get_final_config.__doc__ is not None
