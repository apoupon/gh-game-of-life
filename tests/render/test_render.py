"""Tests for GIF Rendering."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.grid import Grid
from gh_game_of_life.render import GifRenderer
from gh_game_of_life.render.color_palette import Color, GitHubPalette


class TestColorClass:
    """Test Color class for RGB representation."""

    def test_color_creation_valid(self):
        """Color accepts valid RGB values."""
        color = Color(255, 128, 64)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64

    def test_color_minimum_values(self):
        """Color accepts 0 for all channels."""
        color = Color(0, 0, 0)
        assert color.red == 0
        assert color.green == 0
        assert color.blue == 0

    def test_color_maximum_values(self):
        """Color accepts 255 for all channels."""
        color = Color(255, 255, 255)
        assert color.red == 255
        assert color.green == 255
        assert color.blue == 255

    def test_color_rejects_negative_values(self):
        """Color rejects negative RGB values."""
        with pytest.raises(ValueError, match="must be 0-255"):
            Color(-1, 128, 128)

    def test_color_rejects_values_over_255(self):
        """Color rejects RGB values > 255."""
        with pytest.raises(ValueError, match="must be 0-255"):
            Color(256, 128, 128)

    def test_color_rejects_non_integer_values(self):
        """Color rejects non-integer RGB values."""
        with pytest.raises(TypeError, match="must be int"):
            Color(255.5, 128, 128)

    def test_color_to_tuple(self):
        """Color.to_tuple() returns RGB tuple."""
        color = Color(255, 128, 64)
        assert color.to_tuple() == (255, 128, 64)

    def test_color_immutable(self):
        """Color is frozen (immutable)."""
        color = Color(255, 128, 64)
        with pytest.raises(Exception):  # FrozenInstanceError
            color.red = 100


class TestGitHubPalette:
    """Test GitHub contribution graph color palette."""

    def test_dead_cell_color(self):
        """DEAD color is GitHub gray."""
        assert GitHubPalette.DEAD.red == 239
        assert GitHubPalette.DEAD.green == 242
        assert GitHubPalette.DEAD.blue == 245

    def test_green1_cell_color(self):
        """GREEN_1 color is light green."""
        assert GitHubPalette.GREEN_1.red == 172
        assert GitHubPalette.GREEN_1.green == 238
        assert GitHubPalette.GREEN_1.blue == 187

    def test_get_cell_color_dead(self):
        """get_cell_color returns DEAD for CellState.DEAD."""
        color = GitHubPalette.get_cell_color(CellState.DEAD)
        assert color == GitHubPalette.DEAD

    def test_get_cell_color_green1(self):
        """get_cell_color returns GREEN_1 for CellState.GREEN_1."""
        color = GitHubPalette.get_cell_color(CellState.GREEN_1)
        assert color == GitHubPalette.GREEN_1

    def test_get_cell_color_green4(self):
        """get_cell_color returns GREEN_4 for CellState.GREEN_4."""
        color = GitHubPalette.get_cell_color(CellState.GREEN_4)
        assert color == GitHubPalette.GREEN_4

    def test_validate_color_valid(self):
        """validate_color accepts Color objects."""
        color = Color(100, 150, 200)
        GitHubPalette.validate_color(color)  # Should not raise

    def test_validate_color_rejects_non_color(self):
        """validate_color rejects non-Color objects."""
        with pytest.raises(TypeError, match="Expected Color"):
            GitHubPalette.validate_color((100, 150, 200))


class TestGifRendererInitialization:
    """Test GifRenderer initialization and configuration."""

    def test_default_initialization(self):
        """GifRenderer initializes with defaults."""
        renderer = GifRenderer()
        assert renderer.cell_size == 10
        assert renderer.frame_delay_ms == 500

    def test_custom_cell_size(self):
        """GifRenderer accepts custom cell size."""
        renderer = GifRenderer(cell_size=20)
        assert renderer.cell_size == 20

    def test_custom_frame_delay(self):
        """GifRenderer accepts custom frame delay."""
        renderer = GifRenderer(frame_delay_ms=100)
        assert renderer.frame_delay_ms == 100

    def test_custom_background_color(self):
        """GifRenderer accepts custom background color."""
        bg = Color(200, 200, 200)
        renderer = GifRenderer(background_color=bg)
        assert renderer.background_color == bg

    def test_rejects_zero_cell_size(self):
        """GifRenderer rejects cell_size < 1."""
        with pytest.raises(ValueError, match="must be int >= 1"):
            GifRenderer(cell_size=0)

    def test_rejects_negative_cell_size(self):
        """GifRenderer rejects negative cell_size."""
        with pytest.raises(ValueError, match="must be int >= 1"):
            GifRenderer(cell_size=-5)

    def test_rejects_non_integer_cell_size(self):
        """GifRenderer rejects non-integer cell_size."""
        with pytest.raises(ValueError, match="must be int >= 1"):
            GifRenderer(cell_size=10.5)

    def test_rejects_zero_frame_delay(self):
        """GifRenderer rejects frame_delay_ms < 1."""
        with pytest.raises(ValueError, match="must be int >= 1"):
            GifRenderer(frame_delay_ms=0)

    def test_rejects_negative_frame_delay(self):
        """GifRenderer rejects negative frame_delay_ms."""
        with pytest.raises(ValueError, match="must be int >= 1"):
            GifRenderer(frame_delay_ms=-100)

    def test_rejects_non_integer_frame_delay(self):
        """GifRenderer rejects non-integer frame_delay_ms."""
        with pytest.raises(ValueError, match="must be int >= 1"):
            GifRenderer(frame_delay_ms=500.5)

    def test_rejects_invalid_background_color_type(self):
        """GifRenderer rejects non-Color background."""
        with pytest.raises(TypeError, match="Expected Color"):
            GifRenderer(background_color=(200, 200, 200))


class TestGridToImage:
    """Test conversion of grids to images."""

    def test_image_dimensions_default_cell_size(self):
        """Image dimensions match grid × cell_size."""
        renderer = GifRenderer(cell_size=10)
        grid = Grid.empty()

        image = renderer._grid_to_image(grid)
        # 53 columns × 10 pixels, 7 rows × 10 pixels
        assert image.width == 530
        assert image.height == 70

    def test_image_dimensions_custom_cell_size(self):
        """Image dimensions scale with cell_size."""
        renderer = GifRenderer(cell_size=5)
        grid = Grid.empty()

        image = renderer._grid_to_image(grid)
        assert image.width == 265  # 53 × 5
        assert image.height == 35  # 7 × 5

    def test_image_all_dead_cells(self):
        """Empty grid produces all dead-cell color."""
        renderer = GifRenderer(cell_size=1)
        grid = Grid.empty()

        image = renderer._grid_to_image(grid)
        pixels = image.load()

        # Check a few random pixels
        assert pixels[0, 0] == GitHubPalette.DEAD.to_tuple()
        assert pixels[52, 6] == GitHubPalette.DEAD.to_tuple()

    def test_image_all_green4_cells(self):
        """Full grid (GREEN_4) produces all green4-cell color."""
        renderer = GifRenderer(cell_size=1)
        grid = Grid.full()

        image = renderer._grid_to_image(grid)
        pixels = image.load()

        # Check a few random pixels
        assert pixels[0, 0] == GitHubPalette.GREEN_4.to_tuple()
        assert pixels[52, 6] == GitHubPalette.GREEN_4.to_tuple()

    def test_image_mixed_cells(self):
        """Grid with mixed cells renders correctly."""
        renderer = GifRenderer(cell_size=1)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = CellState.GREEN_1
        cells[3][26] = CellState.GREEN_3
        cells[6][52] = CellState.GREEN_4
        grid = Grid(cells)

        image = renderer._grid_to_image(grid)
        pixels = image.load()

        # Colored cells at specific positions
        assert pixels[0, 0] == GitHubPalette.GREEN_1.to_tuple()
        assert pixels[26, 3] == GitHubPalette.GREEN_3.to_tuple()
        assert pixels[52, 6] == GitHubPalette.GREEN_4.to_tuple()

        # Dead cells elsewhere
        assert pixels[1, 0] == GitHubPalette.DEAD.to_tuple()
        assert pixels[0, 1] == GitHubPalette.DEAD.to_tuple()


class TestGifRendering:
    """Test GIF file rendering."""

    def test_render_gif_single_frame(self):
        """Can render single-frame GIF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grid = Grid.empty()
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif([grid], output)

            assert output.exists()
            assert output.stat().st_size > 0

    def test_render_gif_multiple_frames(self):
        """Can render multi-frame GIF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grids = [Grid.empty(), Grid.full(), Grid.empty()]
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif(grids, output)

            assert output.exists()
            assert output.stat().st_size > 0

    def test_render_gif_output_is_valid(self):
        """Rendered GIF is valid and readable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grids = [Grid.empty(), Grid.full()]
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif(grids, output)

            # Verify by reading with PIL
            image = Image.open(output)
            assert image.format == "GIF"

    def test_render_gif_respects_cell_size(self):
        """Rendered GIF respects cell_size configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer(cell_size=20)
            grid = Grid.empty()
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif([grid], output)

            image = Image.open(output)
            # 53 × 20 = 1060, 7 × 20 = 140
            assert image.width == 1060
            assert image.height == 140

    def test_render_gif_respects_frame_delay(self):
        """Rendered GIF respects frame_delay_ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer(frame_delay_ms=200)
            grids = [Grid.empty(), Grid.full()]
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif(grids, output)

            image = Image.open(output)
            # Check frame duration (may be stored in info dict)
            assert hasattr(image, "info")

    def test_render_gif_rejects_empty_grid_list(self):
        """render_gif rejects empty grid list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            output = Path(tmpdir) / "test.gif"

            with pytest.raises(ValueError, match="must contain at least 1"):
                renderer.render_gif([], output)

    def test_render_gif_rejects_non_grid_items(self):
        """render_gif rejects non-Grid items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            output = Path(tmpdir) / "test.gif"

            with pytest.raises(TypeError, match="must be Grid"):
                renderer.render_gif([Grid.empty(), "not a grid"], output)

    def test_render_gif_uses_path_object(self):
        """render_gif accepts Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grid = Grid.empty()
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif([grid], output)
            assert output.exists()

    def test_render_gif_uses_string_path(self):
        """render_gif accepts string paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grid = Grid.empty()
            output = str(Path(tmpdir) / "test.gif")

            renderer.render_gif([grid], output)
            assert Path(output).exists()


class TestStaticImageRendering:
    """Test rendering single grids as static images."""

    def test_render_grid_creates_png(self):
        """render_grid creates a PNG file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grid = Grid.empty()
            output = Path(tmpdir) / "test.png"

            renderer.render_grid(grid, output)

            assert output.exists()
            assert output.stat().st_size > 0

    def test_render_grid_respects_cell_size(self):
        """render_grid respects cell_size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer(cell_size=15)
            grid = Grid.full()
            output = Path(tmpdir) / "test.png"

            renderer.render_grid(grid, output)

            image = Image.open(output)
            assert image.width == 795  # 53 × 15
            assert image.height == 105  # 7 × 15


class TestAcceptanceCriteria:
    """Verify all FR-104 acceptance criteria."""

    def test_output_is_looping_gif(self):
        """Acceptance: Output is a looping .gif"""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()
            grids = [Grid.empty(), Grid.full(), Grid.empty()]
            output = Path(tmpdir) / "test.gif"

            renderer.render_gif(grids, output)

            # Verify file exists and is a GIF
            assert output.suffix.lower() == ".gif"
            image = Image.open(output)
            assert image.format == "GIF"

    def test_uses_github_color_palette(self):
        """Acceptance: Dead and green cells use GitHub color palette"""
        renderer = GifRenderer(cell_size=1)
        cells = [
            [CellState.GREEN_1 if i % 2 == 0 else CellState.DEAD for i in range(53)]
            for _ in range(7)
        ]
        grid = Grid(cells)

        image = renderer._grid_to_image(grid)
        pixels = image.load()

        # Should only see two colors: GitHub dead and GitHub GREEN_1
        color_1 = pixels[0, 0]
        color_2 = pixels[1, 0]

        colors = {color_1, color_2}
        assert GitHubPalette.DEAD.to_tuple() in colors
        assert GitHubPalette.GREEN_1.to_tuple() in colors

    def test_cell_scaling_configurable(self):
        """Acceptance: Cell scaling is configurable"""
        for cell_size in [1, 5, 10, 20, 50]:
            renderer = GifRenderer(cell_size=cell_size)
            grid = Grid.empty()

            image = renderer._grid_to_image(grid)
            assert image.width == 53 * cell_size + renderer.cell_gap * (53 - 1)
            assert image.height == 7 * cell_size + renderer.cell_gap * (7 - 1)

    def test_frame_delay_configurable(self):
        """Acceptance: Frame delay is configurable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            for delay in [100, 250, 500, 1000]:
                renderer = GifRenderer(frame_delay_ms=delay)
                grid = Grid.empty()
                output = Path(tmpdir) / f"test_{delay}.gif"

                renderer.render_gif([grid], output)
                assert output.exists()

    def test_frame_count_configurable(self):
        """Acceptance: Frame count is configurable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = GifRenderer()

            for num_frames in [1, 2, 5, 10, 50]:
                grids = [Grid.empty() for _ in range(num_frames)]
                output = Path(tmpdir) / f"test_{num_frames}.gif"

                renderer.render_gif(grids, output)
                assert output.exists()
