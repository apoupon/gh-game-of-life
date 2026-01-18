"""End-to-end GIF generation orchestration.

Provides single orchestration function that combines GitHub data acquisition,
simulation, and GIF rendering into a unified flow.
"""

from pathlib import Path

from gh_game_of_life.core.game import BoundaryStrategy, GameOfLife
from gh_game_of_life.github_client import GitHubClient
from gh_game_of_life.render.gif import GifRenderer


def generate_gif(
    username: str,
    output_path: Path | str,
    frames: int = 50,
    boundary_strategy: BoundaryStrategy = BoundaryStrategy.LOOP,
    cell_size: int = 10,
    frame_delay_ms: int = 500,
) -> Path:
    """Generate a Game of Life GIF from GitHub contribution data.

    Orchestrates the complete flow:
    1. Fetch GitHub contribution data for user
    2. Convert contributions to binary grid
    3. Run Game of Life simulation for specified frames
    4. Render all frames to animated GIF

    Args:
        username: GitHub username to fetch data for.
        output_path: Path to save the output GIF file.
        frames: Number of simulation frames to render (default 50).
        boundary_strategy: How to handle grid edges - LOOP (wrap) or VOID (dead).
                          Defaults to LOOP.
        cell_size: Pixel size for each cell in output (default 10).
        frame_delay_ms: Milliseconds per frame in GIF (default 500).

    Returns:
        Path object pointing to the created GIF file.

    Raises:
        ValueError: If username is invalid or user not found.
        IOError: If unable to fetch GitHub data or write GIF.
        TypeError: If parameters have wrong types.

    Example:
        >>> from pathlib import Path
        >>> output = generate_gif("torvalds", Path("linux.gif"), frames=100)
        >>> print(output.exists())
        True
    """
    # Validate parameters
    if not isinstance(username, str):
        raise TypeError(f"username must be str, got {type(username).__name__}")

    if not username.strip():
        raise ValueError("username cannot be empty")

    if not isinstance(frames, int) or frames <= 0:
        raise ValueError(f"frames must be positive integer, got {frames}")

    if not isinstance(boundary_strategy, BoundaryStrategy):
        raise TypeError(
            f"boundary_strategy must be BoundaryStrategy, "
            f"got {type(boundary_strategy).__name__}"
        )

    if not isinstance(cell_size, int) or cell_size <= 0:
        raise ValueError(f"cell_size must be positive integer, got {cell_size}")

    if not isinstance(frame_delay_ms, int) or frame_delay_ms <= 0:
        raise ValueError(
            f"frame_delay_ms must be positive integer, got {frame_delay_ms}"
        )

    # Convert output_path to Path object
    output_path = Path(output_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Fetch GitHub contributions
    client = GitHubClient()
    initial_grid = client.fetch_and_convert(username)

    # Step 2: Run simulation
    game = GameOfLife(strategy=boundary_strategy)
    grid_sequence = game.evolve(initial_grid, frames)

    # Step 3: Render to GIF
    renderer = GifRenderer(
        cell_size=cell_size,
        frame_delay_ms=frame_delay_ms,
    )
    renderer.render_gif(grid_sequence, output_path)

    return output_path
