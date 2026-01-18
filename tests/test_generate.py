"""Tests for End-to-End GIF Generation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gh_game_of_life.core.game import BoundaryStrategy
from gh_game_of_life.core.grid import Grid
from gh_game_of_life.generate import generate_gif


class TestGenerateGifOrchestration:
    """Test the complete orchestration flow."""

    def test_orchestration_flow_with_mock_data(self):
        """Test complete flow: fetch → simulate → render."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            # Mock the GitHub client and game
            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        # Setup mocks
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client

                        initial_grid = Grid.empty()
                        mock_client.fetch_and_convert.return_value = initial_grid

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game

                        grid_sequence = [Grid.empty() for _ in range(5)]
                        mock_game.evolve.return_value = grid_sequence

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        # Call the orchestration function
                        result = generate_gif("testuser", output_path, frames=5)

                        # Verify the flow
                        assert result == output_path
                        mock_client.fetch_and_convert.assert_called_once_with(
                            "testuser"
                        )
                        mock_game.evolve.assert_called_once_with(initial_grid, 5)
                        mock_renderer.render_gif.assert_called_once_with(
                            grid_sequence, output_path
                        )

    def test_returns_path_object(self):
        """Orchestration returns Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        result = generate_gif("user", output_path)

                        assert isinstance(result, Path)


class TestGenerateGifParameters:
    """Test parameter validation and handling."""

    def test_accepts_string_output_path(self):
        """Accepts string output path and converts to Path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path_str = str(Path(tmpdir) / "test.gif")

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        result = generate_gif("user", output_path_str)

                        assert isinstance(result, Path)
                        assert str(result) == output_path_str

    def test_accepts_path_output_path(self):
        """Accepts Path object output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        result = generate_gif("user", output_path)

                        assert result == output_path

    def test_creates_output_directory(self):
        """Creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "nested" / "dirs" / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        assert not nested_path.parent.exists()

                        generate_gif("user", nested_path)

                        assert nested_path.parent.exists()

    def test_default_frames_is_50(self):
        """Default frames parameter is 50."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()] * 50

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        # Call without frames parameter
                        generate_gif("user", output_path)

                        # Verify frames=50 was used
                        mock_game.evolve.assert_called_once()
                        call_args = mock_game.evolve.call_args
                        assert call_args[0][1] == 50

    def test_custom_frames_parameter(self):
        """Custom frames parameter is passed through."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()] * 100

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        generate_gif("user", output_path, frames=100)

                        call_args = mock_game.evolve.call_args
                        assert call_args[0][1] == 100

    def test_boundary_strategy_loop_default(self):
        """Default boundary strategy is LOOP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game_class.return_value = Mock()
                        mock_renderer_class.return_value = Mock()

                        generate_gif("user", output_path)

                        # Verify LOOP strategy was passed
                        call_kwargs = mock_game_class.call_args[1]
                        assert call_kwargs["strategy"] == BoundaryStrategy.LOOP

    def test_custom_boundary_strategy(self):
        """Custom boundary strategy is passed through."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game_class.return_value = Mock()
                        mock_renderer_class.return_value = Mock()

                        generate_gif(
                            "user",
                            output_path,
                            boundary_strategy=BoundaryStrategy.VOID,
                        )

                        call_kwargs = mock_game_class.call_args[1]
                        assert call_kwargs["strategy"] == BoundaryStrategy.VOID

    def test_custom_cell_size(self):
        """Custom cell size is passed through."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer_class.return_value = Mock()

                        generate_gif("user", output_path, cell_size=20)

                        call_kwargs = mock_renderer_class.call_args[1]
                        assert call_kwargs["cell_size"] == 20

    def test_custom_frame_delay(self):
        """Custom frame delay is passed through."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer_class.return_value = Mock()

                        generate_gif("user", output_path, frame_delay_ms=1000)

                        call_kwargs = mock_renderer_class.call_args[1]
                        assert call_kwargs["frame_delay_ms"] == 1000


class TestGenerateGifValidation:
    """Test parameter validation."""

    def test_rejects_empty_username(self):
        """Rejects empty username."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="empty"):
                generate_gif("", output_path)

    def test_rejects_whitespace_only_username(self):
        """Rejects whitespace-only username."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="empty"):
                generate_gif("   ", output_path)

    def test_rejects_non_string_username(self):
        """Rejects non-string username."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(TypeError, match="username must be str"):
                generate_gif(123, output_path)

    def test_rejects_zero_frames(self):
        """Rejects zero frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="frames must be positive"):
                generate_gif("user", output_path, frames=0)

    def test_rejects_negative_frames(self):
        """Rejects negative frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="frames must be positive"):
                generate_gif("user", output_path, frames=-5)

    def test_rejects_non_integer_frames(self):
        """Rejects non-integer frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="frames must be positive"):
                generate_gif("user", output_path, frames=5.5)

    def test_rejects_invalid_boundary_strategy_type(self):
        """Rejects invalid boundary strategy type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(
                TypeError, match="boundary_strategy must be BoundaryStrategy"
            ):
                generate_gif("user", output_path, boundary_strategy="invalid")

    def test_rejects_zero_cell_size(self):
        """Rejects zero cell size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="cell_size must be positive"):
                generate_gif("user", output_path, cell_size=0)

    def test_rejects_negative_cell_size(self):
        """Rejects negative cell size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="cell_size must be positive"):
                generate_gif("user", output_path, cell_size=-5)

    def test_rejects_non_integer_cell_size(self):
        """Rejects non-integer cell size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="cell_size must be positive"):
                generate_gif("user", output_path, cell_size=5.5)

    def test_rejects_zero_frame_delay(self):
        """Rejects zero frame delay."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="frame_delay_ms must be positive"):
                generate_gif("user", output_path, frame_delay_ms=0)

    def test_rejects_negative_frame_delay(self):
        """Rejects negative frame delay."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="frame_delay_ms must be positive"):
                generate_gif("user", output_path, frame_delay_ms=-100)

    def test_rejects_non_integer_frame_delay(self):
        """Rejects non-integer frame delay."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="frame_delay_ms must be positive"):
                generate_gif("user", output_path, frame_delay_ms=500.5)


class TestGenerateGifErrorHandling:
    """Test error handling and propagation."""

    def test_propagates_github_api_errors(self):
        """Propagates errors from GitHub API."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.fetch_and_convert.side_effect = ValueError("User not found")

                with pytest.raises(ValueError, match="User not found"):
                    generate_gif("nonexistent", output_path)

    def test_propagates_simulation_errors(self):
        """Propagates errors from simulation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    mock_client = Mock()
                    mock_client_class.return_value = mock_client
                    mock_client.fetch_and_convert.return_value = Grid.empty()

                    mock_game = Mock()
                    mock_game_class.return_value = mock_game
                    mock_game.evolve.side_effect = RuntimeError("Simulation failed")

                    with pytest.raises(RuntimeError, match="Simulation failed"):
                        generate_gif("user", output_path)

    def test_propagates_rendering_errors(self):
        """Propagates errors from rendering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer
                        mock_renderer.render_gif.side_effect = IOError(
                            "Cannot write file"
                        )

                        with pytest.raises(IOError, match="Cannot write file"):
                            generate_gif("user", output_path)


class TestGenerateGifAcceptanceCriteria:
    """Test acceptance criteria for FR-301."""

    def test_fetches_contributions(self):
        """Acceptance: Fetches contributions for user."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        mock_game.evolve.return_value = [Grid.empty()]

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        generate_gif("testuser", output_path)

                        # Verify contributions were fetched
                        mock_client.fetch_and_convert.assert_called_once_with(
                            "testuser"
                        )

    def test_runs_simulation_for_configured_frames(self):
        """Acceptance: Runs simulation for configured frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        initial_grid = Grid.empty()
                        mock_client.fetch_and_convert.return_value = initial_grid

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        grid_sequence = [Grid.empty() for _ in range(42)]
                        mock_game.evolve.return_value = grid_sequence

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        generate_gif("user", output_path, frames=42)

                        # Verify simulation was run with correct frames
                        mock_game.evolve.assert_called_once_with(initial_grid, 42)

    def test_produces_gif_output(self):
        """Acceptance: Produces a GIF output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        grid_sequence = [Grid.empty()]
                        mock_game.evolve.return_value = grid_sequence

                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        result = generate_gif("user", output_path)

                        # Verify GIF rendering was called
                        mock_renderer.render_gif.assert_called_once_with(
                            grid_sequence, output_path
                        )
                        assert result == output_path

    def test_has_no_cli_dependencies(self):
        """Acceptance: Has no CLI dependencies."""
        # This test verifies the function works without CLI imports
        import ast
        import inspect

        source = inspect.getsource(generate_gif)
        tree = ast.parse(source)

        # Check that no CLI-related imports are in the function
        cli_keywords = ["argparse", "click", "typer", "fire"]

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.lower())
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.lower() if node.module else "")

        for cli_keyword in cli_keywords:
            assert cli_keyword not in imports, (
                f"Found CLI dependency '{cli_keyword}' in generate_gif"
            )

    def test_has_no_http_dependencies(self):
        """Acceptance: Has no HTTP/web dependencies (delegated to GitHubClient)."""
        # This test verifies the function doesn't directly do HTTP
        import ast
        import inspect

        source = inspect.getsource(generate_gif)
        tree = ast.parse(source)

        # Check that no HTTP-related imports are in the function
        http_keywords = ["requests", "httpx", "aiohttp", "urllib"]

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.lower())
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.lower() if node.module else "")

        for http_keyword in http_keywords:
            assert http_keyword not in imports, (
                f"Found HTTP dependency '{http_keyword}' in generate_gif"
            )


class TestGenerateGifIntegration:
    """Integration tests with mocked components."""

    def test_full_orchestration_flow_with_mocks(self):
        """Test full orchestration with all components mocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "result.gif"

            with patch("gh_game_of_life.generate.GitHubClient") as mock_client_class:
                with patch("gh_game_of_life.generate.GameOfLife") as mock_game_class:
                    with patch(
                        "gh_game_of_life.generate.GifRenderer"
                    ) as mock_renderer_class:
                        # Setup mock GitHubClient
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client
                        mock_client.fetch_and_convert.return_value = Grid.empty()

                        # Setup mock GameOfLife
                        mock_game = Mock()
                        mock_game_class.return_value = mock_game
                        frames = [Grid.empty() for _ in range(10)]
                        mock_game.evolve.return_value = frames

                        # Setup mock GifRenderer
                        mock_renderer = Mock()
                        mock_renderer_class.return_value = mock_renderer

                        # Call orchestration
                        result = generate_gif(
                            "testuser",
                            output_path,
                            frames=10,
                            boundary_strategy=BoundaryStrategy.VOID,
                            cell_size=15,
                            frame_delay_ms=750,
                        )

                        # Verify complete flow
                        assert result == output_path
                        mock_client.fetch_and_convert.assert_called_once_with(
                            "testuser"
                        )
                        mock_game_class.assert_called_once_with(
                            strategy=BoundaryStrategy.VOID
                        )
                        mock_game.evolve.assert_called_once()
                        mock_renderer_class.assert_called_once_with(
                            cell_size=15,
                            frame_delay_ms=750,
                        )
                        mock_renderer.render_gif.assert_called_once()


class TestGenerateGifDocumentation:
    """Test that function has proper documentation."""

    def test_has_docstring(self):
        """Function has a docstring."""
        assert generate_gif.__doc__ is not None
        assert len(generate_gif.__doc__.strip()) > 0

    def test_docstring_includes_usage_example(self):
        """Docstring includes usage example."""
        assert "Example:" in generate_gif.__doc__
