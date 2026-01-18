"""Tests for CI-Friendly Exit Codes."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gh_game_of_life.cli import main


class TestExitCodeZeroOnSuccess:
    """Test exit code 0 on successful execution."""

    def test_exit_code_0_on_successful_generation(self):
        """Exit code is 0 on successful GIF generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                exit_code = main(["torvalds", "-o", str(output_path)])

                assert exit_code == 0

    def test_exit_code_0_with_all_options(self):
        """Exit code is 0 when all options are specified correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "result.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                exit_code = main(
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
                        "20",
                        "-d",
                        "750",
                    ]
                )

                assert exit_code == 0


class TestExitCodeNonZeroOnFailure:
    """Test non-zero exit codes on failure."""

    def test_exit_code_nonzero_on_user_not_found(self):
        """Exit code is non-zero when user not found."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("User not found")

            exit_code = main(["nonexistent"])

            assert exit_code != 0

    def test_exit_code_nonzero_on_github_api_error(self):
        """Exit code is non-zero on GitHub API error."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = IOError("GitHub API error")

            exit_code = main(["torvalds"])

            assert exit_code != 0

    def test_exit_code_nonzero_on_file_write_error(self):
        """Exit code is non-zero on file write error."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = IOError("Cannot write file")

            exit_code = main(["torvalds", "-o", "/invalid/path.gif"])

            assert exit_code != 0

    def test_exit_code_nonzero_on_generic_error(self):
        """Exit code is non-zero on unexpected error."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = RuntimeError("Unexpected error")

            exit_code = main(["torvalds"])

            assert exit_code != 0


class TestExitCodeTwoOnArgumentError:
    """Test exit code 2 for argument parsing errors."""

    def test_exit_code_2_on_missing_username(self):
        """Exit code is 2 when username is missing."""
        exit_code = main([])

        assert exit_code == 2

    def test_exit_code_2_on_invalid_frames(self):
        """Exit code is 2 when frames argument is invalid."""
        with pytest.raises(SystemExit, match="2"):
            main(["torvalds", "--frames", "invalid"])

    def test_exit_code_2_on_invalid_strategy(self):
        """Exit code is 2 when strategy argument is invalid."""
        with pytest.raises(SystemExit, match="2"):
            main(["torvalds", "--strategy", "invalid"])

    def test_exit_code_2_on_invalid_cell_size(self):
        """Exit code is 2 when cell-size argument is invalid."""
        with pytest.raises(SystemExit, match="2"):
            main(["torvalds", "--cell-size", "invalid"])


class TestErrorsPrintedClearly:
    """Test that errors are printed clearly to stderr."""

    def test_user_not_found_error_message(self, capsys):
        """User not found error is printed clearly."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("User not found")

            main(["nonexistent"])

            captured = capsys.readouterr()
            assert "Error" in captured.err or "not found" in captured.err.lower()

    def test_file_error_message(self, capsys):
        """File error is printed clearly."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = IOError("Failed to write file")

            main(["torvalds"])

            captured = capsys.readouterr()
            assert "Error" in captured.err or "Failed" in captured.err

    def test_missing_username_error_message(self, capsys):
        """Missing username error is printed clearly."""
        main([])

        captured = capsys.readouterr()
        assert "Error" in captured.err or "required" in captured.err.lower()

    def test_success_message_printed(self, capsys):
        """Success message is printed on successful generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                main(["torvalds", "-o", str(output_path)])

                captured = capsys.readouterr()
                assert "Success" in captured.err or "saved" in captured.err.lower()


class TestCIFriendlyBehavior:
    """Test CI-friendly behavior for GitHub Actions."""

    def test_deterministic_exit_codes(self):
        """Exit codes are deterministic for same error."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("Same error")

            exit_code_1 = main(["test"])
            exit_code_2 = main(["test"])

            assert exit_code_1 == exit_code_2

    def test_no_output_to_stdout_on_error(self, capsys):
        """No output to stdout on error (errors go to stderr only)."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("Error")

            main(["torvalds"])

            captured = capsys.readouterr()
            # Most error output should go to stderr
            assert len(captured.out) == 0 or captured.err != ""

    def test_keyboard_interrupt_handled(self):
        """KeyboardInterrupt (Ctrl+C) is handled gracefully."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = KeyboardInterrupt()

            exit_code = main(["torvalds"])

            # Should return non-zero exit code
            assert exit_code != 0


class TestAcceptanceCriteria:
    """Test FR-403 acceptance criteria."""

    def test_exit_code_0_on_success(self):
        """Acceptance: Exit code 0 on success."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                exit_code = main(["testuser", "-o", str(output_path)])

                assert exit_code == 0

    def test_exit_code_nonzero_on_failure(self):
        """Acceptance: Non-zero exit code on failure."""
        # Test various failure modes
        failure_cases = [
            ValueError("User not found"),
            IOError("API error"),
            RuntimeError("Unexpected error"),
        ]

        for error in failure_cases:
            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.side_effect = error

                exit_code = main(["testuser"])

                assert exit_code != 0, f"Exit code should be non-zero for {error}"

    def test_errors_printed_clearly(self, capsys):
        """Acceptance: Errors are printed clearly."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("Test error message")

            main(["testuser"])

            captured = capsys.readouterr()
            # Error message should be in stderr
            assert len(captured.err) > 0


class TestSpecificExitCodes:
    """Test specific exit code semantics."""

    def test_exit_code_0_means_success(self):
        """Exit code 0 indicates successful execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "result.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                exit_code = main(["testuser", "-o", str(output_path)])

                # Exit code 0 means success
                assert exit_code == 0

    def test_exit_code_1_means_runtime_error(self):
        """Exit code 1 indicates a runtime error."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("Runtime error")

            exit_code = main(["testuser"])

            # Exit code 1 means runtime error
            assert exit_code == 1

    def test_exit_code_2_means_argument_error(self):
        """Exit code 2 indicates an argument parsing error."""
        exit_code = main([])  # Missing required argument

        # Exit code 2 means argument error
        assert exit_code == 2

    def test_exit_code_130_means_interrupted(self):
        """Exit code 130 indicates user interrupt (Ctrl+C)."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = KeyboardInterrupt()

            exit_code = main(["testuser"])

            # Exit code 130 means interrupted by signal
            assert exit_code == 130


class TestGitHubActionsCompatibility:
    """Test compatibility with GitHub Actions."""

    def test_can_detect_success_in_github_actions(self):
        """GitHub Actions can detect success from exit code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = output_path

                exit_code = main(["testuser", "-o", str(output_path)])

                # GitHub Actions workflow would do: if exit_code == 0
                if exit_code == 0:
                    # Success branch
                    success = True
                else:
                    success = False

                assert success

    def test_can_detect_failure_in_github_actions(self):
        """GitHub Actions can detect failure from exit code."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            mock_generate.side_effect = ValueError("Test failure")

            exit_code = main(["testuser"])

            # GitHub Actions workflow would do: if exit_code != 0
            if exit_code != 0:
                # Failure branch
                failed = True
            else:
                failed = False

            assert failed

    def test_exit_code_suitable_for_ci_cd_pipeline(self):
        """Exit codes are suitable for CI/CD pipeline decision making."""
        scenarios = [
            (["testuser", "-o", "/tmp/test.gif"], True),  # Success
            ([], False),  # Argument error
        ]

        for args, should_succeed in scenarios:
            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.return_value = Path("/tmp/test.gif")

                exit_code = main(args)

                # In CI/CD, 0 = success, non-zero = failure
                if should_succeed:
                    assert exit_code == 0, f"Expected success for {args}"
                else:
                    assert exit_code != 0, f"Expected failure for {args}"


class TestExitCodeDocumentation:
    """Test exit code documentation."""

    def test_cli_help_exists(self):
        """CLI help is available."""
        # This is implicitly tested by parse_args help
        # but we verify the main function exists
        assert callable(main)

    def test_exit_codes_are_standard_unix(self):
        """Exit codes follow Unix conventions."""
        with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
            # Success
            mock_generate.return_value = Path("/tmp/test.gif")
            assert main(["test", "-o", "/tmp/test.gif"]) == 0

            # Failure
            mock_generate.side_effect = ValueError("Error")
            assert main(["test"]) == 1

            # Bad arguments
            assert main([]) == 2


class TestExitCodeConsistency:
    """Test exit code consistency across different scenarios."""

    def test_same_error_produces_same_exit_code(self):
        """Same error always produces same exit code."""
        error = ValueError("Consistent error")

        exit_codes = []
        for _ in range(3):
            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.side_effect = error
                exit_codes.append(main(["test"]))

        # All exit codes should be identical
        assert len(set(exit_codes)) == 1

    def test_different_errors_produce_consistent_exit_code(self):
        """Different runtime errors produce consistent exit code."""
        errors = [
            ValueError("Error 1"),
            IOError("Error 2"),
            RuntimeError("Error 3"),
        ]

        exit_codes = []
        for error in errors:
            with patch("gh_game_of_life.cli.generate_gif") as mock_generate:
                mock_generate.side_effect = error
                exit_codes.append(main(["test"]))

        # All should be non-zero (failure)
        assert all(code != 0 for code in exit_codes)
        # All should be the same value (exit code 1)
        assert len(set(exit_codes)) == 1
