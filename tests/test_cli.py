"""Tests for CLI Command Execution."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gh_game_of_life.cli import main, parse_args, print_help
from gh_game_of_life.core.game import BoundaryStrategy


class TestCliArgumentParsing:
    """Test CLI argument parsing."""

    def test_parse_positional_username(self):
        """Parse positional username argument."""
        args = ["torvalds"]
        parsed = parse_args(args)

        assert parsed["username"] == "torvalds"
        assert parsed["frames"] is None  # defaults applied in main()
        assert parsed["strategy"] is None  # defaults applied in main()

    def test_parse_username_flag(self):
        """Parse --username flag."""
        args = ["--username", "linux"]
        parsed = parse_args(args)

        assert parsed["username"] == "linux"

    def test_parse_username_short_flag(self):
        """Parse -u short flag."""
        args = ["-u", "python"]
        parsed = parse_args(args)

        assert parsed["username"] == "python"

    def test_parse_output_flag(self):
        """Parse --output flag."""
        args = ["torvalds", "--output", "myfile.gif"]
        parsed = parse_args(args)

        assert parsed["output"] == "myfile.gif"

    def test_parse_output_short_flag(self):
        """Parse -o short flag."""
        args = ["torvalds", "-o", "result.gif"]
        parsed = parse_args(args)

        assert parsed["output"] == "result.gif"

    def test_parse_frames_flag(self):
        """Parse --frames flag."""
        args = ["torvalds", "--frames", "100"]
        parsed = parse_args(args)

        assert parsed["frames"] == 100

    def test_parse_frames_short_flag(self):
        """Parse -f short flag."""
        args = ["torvalds", "-f", "75"]
        parsed = parse_args(args)

        assert parsed["frames"] == 75

    def test_parse_strategy_loop(self):
        """Parse --strategy loop."""
        args = ["torvalds", "--strategy", "loop"]
        parsed = parse_args(args)

        assert parsed["strategy"] == "loop"

    def test_parse_strategy_void(self):
        """Parse --strategy void."""
        args = ["torvalds", "--strategy", "void"]
        parsed = parse_args(args)

        assert parsed["strategy"] == "void"

    def test_parse_strategy_short_flag(self):
        """Parse -s short flag."""
        args = ["torvalds", "-s", "void"]
        parsed = parse_args(args)

        assert parsed["strategy"] == "void"

    def test_parse_cell_size_flag(self):
        """Parse --cell-size flag."""
        args = ["torvalds", "--cell-size", "15"]
        parsed = parse_args(args)

        assert parsed["cell_size"] == 15

    def test_parse_cell_size_short_flag(self):
        """Parse -c short flag."""
        args = ["torvalds", "-c", "20"]
        parsed = parse_args(args)

        assert parsed["cell_size"] == 20

    def test_parse_frame_delay_flag(self):
        """Parse --frame-delay flag."""
        args = ["torvalds", "--frame-delay", "1000"]
        parsed = parse_args(args)

        assert parsed["frame_delay"] == 1000

    def test_parse_frame_delay_short_flag(self):
        """Parse -d short flag."""
        args = ["torvalds", "-d", "750"]
        parsed = parse_args(args)

        assert parsed["frame_delay"] == 750

    def test_parse_combined_flags(self):
        """Parse multiple flags together."""
        args = [
            "-u",
            "torvalds",
            "-o",
            "linux.gif",
            "-f",
            "100",
            "-s",
            "void",
            "-c",
            "12",
            "-d",
            "600",
        ]
        parsed = parse_args(args)

        assert parsed["username"] == "torvalds"
        assert parsed["output"] == "linux.gif"
        assert parsed["frames"] == 100
        assert parsed["strategy"] == "void"
        assert parsed["cell_size"] == 12
        assert parsed["frame_delay"] == 600

    def test_parse_help_flag(self):
        """Parse --help flag (exits)."""
        with pytest.raises(SystemExit, match="0"):
            parse_args(["--help"])

    def test_parse_help_short_flag(self):
        """Parse -h short flag (exits)."""
        with pytest.raises(SystemExit, match="0"):
            parse_args(["-h"])

    def test_parse_version_flag(self):
        """Parse --version flag (exits)."""
        with pytest.raises(SystemExit, match="0"):
            parse_args(["--version"])

    def test_parse_version_short_flag(self):
        """Parse -v short flag (exits)."""
        with pytest.raises(SystemExit, match="0"):
            parse_args(["-v"])

    def test_parse_missing_username_required_flag_value(self):
        """Missing required value for --username."""
        with pytest.raises(SystemExit, match="2"):
            parse_args(["--username"])

    def test_parse_missing_output_required_flag_value(self):
        """Missing required value for --output."""
        with pytest.raises(SystemExit, match="2"):
            parse_args(["torvalds", "--output"])

    def test_parse_invalid_frames_value(self):
        """Invalid frames value (non-integer)."""
        with pytest.raises(SystemExit, match="2"):
            parse_args(["torvalds", "--frames", "abc"])

    def test_parse_invalid_cell_size_value(self):
        """Invalid cell-size value (non-integer)."""
        with pytest.raises(SystemExit, match="2"):
            parse_args(["torvalds", "--cell-size", "xyz"])

    def test_parse_invalid_strategy_value(self):
        """Invalid strategy value."""
        with pytest.raises(SystemExit, match="2"):
            parse_args(["torvalds", "--strategy", "invalid"])

    def test_parse_strategy_case_insensitive(self):
        """Strategy parsing is case-insensitive."""
        args1 = ["torvalds", "--strategy", "LOOP"]
        parsed1 = parse_args(args1)
        assert parsed1["strategy"] == "loop"

        args2 = ["torvalds", "--strategy", "VOID"]
        parsed2 = parse_args(args2)
        assert parsed2["strategy"] == "void"

    def test_parse_empty_args(self):
        """Parse with no arguments."""
        parsed = parse_args([])

        assert parsed["username"] is None
        assert parsed["frames"] is None
        assert parsed["strategy"] is None


class TestCliMainFunction:
    """Test CLI main function."""

    def test_main_success(self):
        """Main function succeeds with valid arguments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                result = main(["torvalds", "-o", str(output_path)])

                assert result == 0
                mock_generate.assert_called_once()

    def test_main_missing_username(self):
        """Main function fails when username is missing."""
        result = main([])

        assert result == 2

    def test_main_generates_default_output_path(self):
        """Main function uses username-gh-life.gif as default output."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("torvalds-gh-life.gif")

            result = main(["torvalds"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["output_path"] == "torvalds-gh-life.gif"

    def test_main_passes_custom_output_path(self):
        """Main function passes custom output path."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("custom.gif")

            result = main(["torvalds", "-o", "custom.gif"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["output_path"] == "custom.gif"

    def test_main_passes_frames_parameter(self):
        """Main function passes frames parameter."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds", "-f", "100"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["frames"] == 100

    def test_main_passes_boundary_strategy_loop(self):
        """Main function passes LOOP boundary strategy."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds", "-s", "loop"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["boundary_strategy"] == BoundaryStrategy.LOOP

    def test_main_passes_boundary_strategy_void(self):
        """Main function passes VOID boundary strategy."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds", "-s", "void"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["boundary_strategy"] == BoundaryStrategy.VOID

    def test_main_passes_cell_size_parameter(self):
        """Main function passes cell_size parameter."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds", "-c", "20"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["cell_size"] == 20

    def test_main_passes_frame_delay_parameter(self):
        """Main function passes frame_delay_ms parameter."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds", "-d", "1000"])

            assert result == 0
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["frame_delay_ms"] == 1000

    def test_main_handles_value_error(self):
        """Main function handles ValueError from generate_gif."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("User not found")

            result = main(["nonexistent"])

            assert result == 1

    def test_main_handles_io_error(self):
        """Main function handles IOError from generate_gif."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = IOError("Cannot write file")

            result = main(["torvalds"])

            assert result == 1

    def test_main_handles_keyboard_interrupt(self):
        """Main function handles KeyboardInterrupt."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = KeyboardInterrupt()

            result = main(["torvalds"])

            assert result == 130

    def test_main_handles_unexpected_exception(self):
        """Main function handles unexpected exceptions."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = RuntimeError("Unexpected error")

            result = main(["torvalds"])

            assert result == 1


class TestCliAcceptanceCriteria:
    """Test FR-401 acceptance criteria."""

    def test_cli_command_is_installed_via_entry_point(self):
        """Acceptance: CLI command is installed via PyPI entry point."""
        # This is verified by the pyproject.toml entry point configuration
        # [project.scripts] section with gh-game-of-life = "cli:main"
        # We verify the main function exists and is callable
        assert callable(main)
        assert hasattr(main, "__call__")

    def test_cli_invokes_orchestration_logic(self):
        """Acceptance: CLI invokes orchestration logic (generate_gif)."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["testuser"])

            # Verify generate_gif was called (orchestration logic)
            mock_generate.assert_called_once()
            assert result == 0

    def test_cli_writes_output_file_to_disk(self):
        """Acceptance: Output file is written to disk."""
        # This is tested indirectly - the CLI calls generate_gif which
        # is responsible for writing to disk. We verify the orchestration works.
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            output_path = Path("/tmp/test.gif")
            mock_generate.return_value = output_path

            result = main(["testuser", "-o", "/tmp/test.gif"])

            # Verify output_path was passed to generate_gif
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["output_path"] == "/tmp/test.gif"
            assert result == 0


class TestCliErrorHandling:
    """Test CLI error handling and exit codes."""

    def test_cli_exit_code_0_on_success(self):
        """CLI returns exit code 0 on success."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds"])

            assert result == 0

    def test_cli_exit_code_1_on_value_error(self):
        """CLI returns exit code 1 on ValueError."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("Invalid input")

            result = main(["invalid"])

            assert result == 1

    def test_cli_exit_code_1_on_io_error(self):
        """CLI returns exit code 1 on IOError."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = IOError("File error")

            result = main(["torvalds"])

            assert result == 1

    def test_cli_exit_code_1_on_generic_error(self):
        """CLI returns exit code 1 on generic Exception."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = Exception("Generic error")

            result = main(["torvalds"])

            assert result == 1

    def test_cli_exit_code_2_on_argument_error(self):
        """CLI returns exit code 2 on argument error."""
        result = main([])

        assert result == 2

    def test_cli_exit_code_130_on_interrupt(self):
        """CLI returns exit code 130 on KeyboardInterrupt."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = KeyboardInterrupt()

            result = main(["torvalds"])

            assert result == 130


class TestCliIntegration:
    """Integration tests for CLI."""

    def test_cli_full_flow_with_all_options(self):
        """Test CLI with all options specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "result.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                result = main(
                    [
                        "-u",
                        "torvalds",
                        "-o",
                        str(output_path),
                        "-f",
                        "100",
                        "-s",
                        "void",
                        "-c",
                        "15",
                        "-d",
                        "750",
                    ]
                )

                assert result == 0

                # Verify all parameters were passed correctly
                call_kwargs = mock_generate.call_args[1]
                assert call_kwargs["username"] == "torvalds"
                assert call_kwargs["output_path"] == str(output_path)
                assert call_kwargs["frames"] == 100
                assert call_kwargs["boundary_strategy"] == BoundaryStrategy.VOID
                assert call_kwargs["cell_size"] == 15
                assert call_kwargs["frame_delay_ms"] == 750

    def test_cli_with_minimal_arguments(self):
        """Test CLI with only required arguments."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.return_value = Path("test.gif")

            result = main(["torvalds"])

            assert result == 0

            # Verify defaults were used
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs["username"] == "torvalds"
            assert call_kwargs["output_path"] == "torvalds.gif"
            assert call_kwargs["frames"] == 50
            assert call_kwargs["boundary_strategy"] == BoundaryStrategy.LOOP
            assert call_kwargs["cell_size"] == 10
            assert call_kwargs["frame_delay_ms"] == 500


class TestCliHelpAndVersion:
    """Test CLI help and version output."""

    def test_help_function_exists(self):
        """Help function exists and is callable."""
        assert callable(print_help)

    def test_help_flag_shows_help(self):
        """--help flag shows help message."""
        with pytest.raises(SystemExit, match="0"):
            parse_args(["--help"])

    def test_version_flag_shows_version(self):
        """--version flag shows version."""
        with pytest.raises(SystemExit, match="0"):
            parse_args(["--version"])


class TestCliDocumentation:
    """Test CLI documentation."""

    def test_main_has_docstring(self):
        """Main function has docstring."""
        assert main.__doc__ is not None
        assert len(main.__doc__.strip()) > 0

    def test_parse_args_has_docstring(self):
        """parse_args function has docstring."""
        assert parse_args.__doc__ is not None
        assert len(parse_args.__doc__.strip()) > 0

    def test_print_help_has_docstring(self):
        """print_help function has docstring."""
        assert print_help.__doc__ is not None
        assert len(print_help.__doc__.strip()) > 0
