"""GIF rendering for Game of Life simulations.

Converts grid evolution history to animated GIF with configurable cell scaling,
cell gap and frame delay.
"""

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

from gh_game_of_life.core.grid import Grid

from .color_palette import Color, GitHubPalette


class GifRenderer:
    """Renders Game of Life grids as GitHub-style animated GIFs."""

    PADDING = 10
    CORNER_RADIUS = 2

    def __init__(
        self,
        cell_size: int = 10,
        cell_gap: int = 3,
        frame_delay_ms: int = 500,
        background_color: Optional[Color] = None,
    ) -> None:
        if not isinstance(cell_size, int) or cell_size < 1:
            raise ValueError(f"cell_size must be int >= 1, got {cell_size}")

        if not isinstance(cell_gap, int) or cell_gap < 0:
            raise ValueError(f"cell_gap must be int >= 0, got {cell_gap}")

        if not isinstance(frame_delay_ms, int) or frame_delay_ms < 1:
            raise ValueError(f"frame_delay_ms must be int >= 1, got {frame_delay_ms}")

        if background_color is not None:
            GitHubPalette.validate_color(background_color)

        self.cell_size = cell_size
        self.cell_gap = cell_gap
        self.frame_delay_ms = frame_delay_ms
        self.background_color = (
            background_color
            if background_color is not None
            else GitHubPalette.BACKGROUND
        )

    def _grid_to_image(self, grid: Grid) -> Image.Image:
        slot = self.cell_size + self.cell_gap

        grid_width = Grid.COLS * slot - self.cell_gap
        grid_height = Grid.ROWS * slot - self.cell_gap

        width = grid_width + 2 * self.PADDING
        height = grid_height + 2 * self.PADDING

        image = Image.new(
            "RGB",
            (width, height),
            self.background_color.to_tuple(),
        )
        draw = ImageDraw.Draw(image)

        for row in range(Grid.ROWS):
            for col in range(Grid.COLS):
                state = grid.get_cell(row, col)
                color = GitHubPalette.get_cell_color(state)

                x0 = self.PADDING + col * slot
                y0 = self.PADDING + row * slot
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size

                draw.rounded_rectangle(
                    [x0, y0, x1, y1],
                    radius=self.CORNER_RADIUS,
                    fill=color.to_tuple(),
                )

        return image

    def render_gif(self, grids: list[Grid], output_path: str | Path) -> None:
        if not grids:
            raise ValueError("grids must contain at least 1 grid")

        for i, grid in enumerate(grids):
            if not isinstance(grid, Grid):
                raise TypeError(f"grids[{i}] must be Grid, got {type(grid).__name__}")

        images = [self._grid_to_image(grid) for grid in grids]

        images = [img.convert("P", palette=Image.ADAPTIVE, colors=16) for img in images]

        output_path = Path(output_path)

        try:
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                duration=self.frame_delay_ms,
                loop=0,
                optimize=False,
            )
        except Exception as e:
            raise IOError(f"Failed to write GIF to {output_path}: {e}") from e

    def render_grid(self, grid: Grid, output_path: str | Path) -> None:
        image = self._grid_to_image(grid)
        output_path = Path(output_path)

        try:
            image.save(output_path)
        except Exception as e:
            raise IOError(f"Failed to write image to {output_path}: {e}") from e

    def __repr__(self) -> str:
        return (
            f"GifRenderer(cell_size={self.cell_size}, "
            f"cell_gap={self.cell_gap}, "
            f"frame_delay_ms={self.frame_delay_ms})"
        )
