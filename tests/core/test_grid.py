"""Tests for Grid."""

import pytest

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.grid import Grid


class TestGridCreation:
    """Test grid creation with valid inputs."""

    def test_create_grid_with_valid_dimensions(self):
        """Grid creation succeeds with exactly 53×7."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        grid = Grid(cells)
        assert grid is not None

    def test_create_grid_with_mixed_states(self):
        """Grid accepts mix of different CellState values."""
        cells = [
            [
                CellState.GREEN_1 if (i + j) % 2 == 0 else CellState.DEAD
                for j in range(53)
            ]
            for i in range(7)
        ]
        grid = Grid(cells)
        assert grid.get_cell(0, 0) == CellState.GREEN_1
        assert grid.get_cell(0, 1) == CellState.DEAD

    def test_empty_factory_method(self):
        """Grid.empty() creates all-DEAD grid."""
        grid = Grid.empty()
        for i in range(7):
            for j in range(53):
                assert grid.get_cell(i, j) == CellState.DEAD

    def test_full_factory_method(self):
        """Grid.full() creates all-GREEN_4 grid."""
        grid = Grid.full()
        for i in range(7):
            for j in range(53):
                assert grid.get_cell(i, j) == CellState.GREEN_4


class TestGridDimensionValidation:
    """Test grid rejects invalid dimensions."""

    def test_reject_wrong_row_count(self):
        """Grid rejects incorrect number of rows."""
        cells = [[CellState.DEAD] * 53 for _ in range(8)]  # 8 rows instead of 7
        with pytest.raises(ValueError, match="must have 7 rows"):
            Grid(cells)

    def test_reject_wrong_col_count(self):
        """Grid rejects incorrect number of columns."""
        cells = [[CellState.DEAD] * 54 for _ in range(7)]  # 54 cols instead of 53
        with pytest.raises(ValueError, match="must have 53 columns"):
            Grid(cells)

    def test_reject_too_many_rows(self):
        """Grid rejects grid with too many rows."""
        cells = [[False] * 53 for _ in range(10)]
        with pytest.raises(ValueError):
            Grid(cells)

    def test_reject_too_few_rows(self):
        """Grid rejects grid with too few rows."""
        cells = [[False] * 53 for _ in range(3)]
        with pytest.raises(ValueError):
            Grid(cells)

    def test_reject_too_many_cols_in_row(self):
        """Grid rejects row with too many columns."""
        cells = [[False] * 53 for _ in range(7)]
        cells[0] = [False] * 100
        with pytest.raises(ValueError, match="must have 53 columns"):
            Grid(cells)

    def test_reject_too_few_cols_in_row(self):
        """Grid rejects row with too few columns."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3] = [CellState.DEAD] * 20
        with pytest.raises(ValueError, match="must have 53 columns"):
            Grid(cells)


class TestGridStateValidation:
    """Test grid validates cell states as CellState values."""

    def test_reject_non_boolean_cell_values(self):
        """Grid rejects non-CellState cell values."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][10] = 1  # Integer instead of CellState
        with pytest.raises(TypeError, match="must be CellState"):
            Grid(cells)

    def test_reject_none_cell_value(self):
        """Grid rejects None as cell value."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = None
        with pytest.raises(TypeError):
            Grid(cells)

    def test_reject_string_cell_value(self):
        """Grid rejects string as cell value."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[5][25] = "alive"
        with pytest.raises(TypeError):
            Grid(cells)

    def test_reject_non_list_input(self):
        """Grid rejects non-list input."""
        with pytest.raises(TypeError):
            Grid("not a list")

    def test_reject_non_list_row(self):
        """Grid rejects row that is not a list/tuple."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[1] = "not a list"
        with pytest.raises(TypeError):
            Grid(cells)


class TestGridImmutability:
    """Test grid is immutable after creation."""

    def test_grid_is_immutable(self):
        """Grid cannot be modified after creation."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        grid = Grid(cells)

        # Attempting to modify original list should not affect grid
        cells[0][0] = CellState.GREEN_1
        assert grid.get_cell(0, 0) == CellState.DEAD

    def test_exported_list_is_separate(self):
        """to_list() returns independent copy."""
        grid = Grid.empty()
        exported = grid.to_list()

        # Modifying exported list should not affect grid
        exported[0][0] = 1
        assert grid.get_cell(0, 0) == CellState.DEAD


class TestGridCellAccess:
    """Test cell access methods."""

    def test_get_cell_valid_indices(self):
        """get_cell() returns correct value for valid indices."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][25] = CellState.GREEN_1
        grid = Grid(cells)

        assert grid.get_cell(3, 25) == CellState.GREEN_1
        assert grid.get_cell(0, 0) == CellState.DEAD
        assert grid.get_cell(6, 52) == CellState.DEAD

    def test_get_cell_boundary_indices(self):
        """get_cell() works at grid boundaries."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = CellState.GREEN_1
        cells[6][52] = CellState.GREEN_1
        grid = Grid(cells)

        assert grid.get_cell(0, 0) == CellState.GREEN_1
        assert grid.get_cell(6, 52) == CellState.GREEN_1

    def test_get_cell_row_out_of_bounds(self):
        """get_cell() raises IndexError for invalid row."""
        grid = Grid.empty()
        with pytest.raises(IndexError, match="Row .* out of bounds"):
            grid.get_cell(7, 0)

    def test_get_cell_col_out_of_bounds(self):
        """get_cell() raises IndexError for invalid column."""
        grid = Grid.empty()
        with pytest.raises(IndexError, match="Col .* out of bounds"):
            grid.get_cell(0, 53)

    def test_get_cell_negative_row(self):
        """get_cell() raises IndexError for negative row."""
        grid = Grid.empty()
        with pytest.raises(IndexError):
            grid.get_cell(-1, 0)

    def test_get_cell_negative_col(self):
        """get_cell() raises IndexError for negative column."""
        grid = Grid.empty()
        with pytest.raises(IndexError):
            grid.get_cell(0, -1)


class TestGridEquality:
    """Test grid equality comparison."""

    def test_equal_grids(self):
        """Two grids with same state are equal."""
        cells = [[CellState.GREEN_1] * 53 for _ in range(7)]
        grid1 = Grid(cells)
        grid2 = Grid([row[:] for row in cells])
        assert grid1 == grid2

    def test_unequal_grids_different_cells(self):
        """Grids with different cell states are not equal."""
        cells1 = [[CellState.DEAD] * 53 for _ in range(7)]
        cells2 = [[CellState.GREEN_4] * 53 for _ in range(7)]
        grid1 = Grid(cells1)
        grid2 = Grid(cells2)
        assert grid1 != grid2

    def test_not_equal_to_non_grid(self):
        """Grid is not equal to non-Grid objects."""
        grid = Grid.empty()
        assert grid != []
        assert grid != "grid"
        assert grid is not None


class TestGridExport:
    """Test grid export functionality."""

    def test_to_list_returns_correct_dimensions(self):
        """to_list() returns 7×53 list."""
        grid = Grid.empty()
        exported = grid.to_list()
        assert len(exported) == 7
        assert all(len(row) == 53 for row in exported)

    def test_to_list_preserves_state(self):
        """to_list() preserves cell states as integer values."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][10] = CellState.GREEN_1
        cells[5][50] = CellState.GREEN_4
        grid = Grid(cells)

        exported = grid.to_list()
        assert exported[2][10] == 1  # GREEN_1
        assert exported[5][50] == 4  # GREEN_4
        assert exported[0][0] == 0  # DEAD

    def test_to_list_returns_copy(self):
        """to_list() returns independent copy."""
        grid = Grid.full()
        exported = grid.to_list()
        exported[0][0] = 0

        # Original grid unchanged
        assert grid.get_cell(0, 0) == CellState.GREEN_4
        assert Grid.COLS == 53
