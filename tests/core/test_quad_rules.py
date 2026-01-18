"""Tests for Quad-Life rules."""

import pytest

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.grid import Grid
from gh_game_of_life.core.quad_rules import QuadLifeRules


class TestNeighborColorCounting:
    """Test neighbor color counting logic."""

    def test_all_dead_neighbors(self):
        """All-dead grid has no colored neighbors."""
        grid = Grid.empty()
        color_counts = QuadLifeRules.get_neighbor_color_counts(grid, 3, 26)
        assert color_counts == {
            CellState.GREEN_1: 0,
            CellState.GREEN_2: 0,
            CellState.GREEN_3: 0,
            CellState.GREEN_4: 0,
        }

    def test_single_green1_neighbor(self):
        """Counts single GREEN_1 neighbor correctly."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][25] = CellState.GREEN_1  # Neighbor to (3, 26)
        grid = Grid(cells)
        color_counts = QuadLifeRules.get_neighbor_color_counts(grid, 3, 26)
        assert color_counts[CellState.GREEN_1] == 1
        assert color_counts[CellState.GREEN_2] == 0

    def test_multiple_colors_neighbors(self):
        """Counts multiple colors correctly."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Set 3 neighbors around (3, 26)
        cells[2][25] = CellState.GREEN_1
        cells[2][26] = CellState.GREEN_2
        cells[2][27] = CellState.GREEN_3
        grid = Grid(cells)
        color_counts = QuadLifeRules.get_neighbor_color_counts(grid, 3, 26)
        assert color_counts[CellState.GREEN_1] == 1
        assert color_counts[CellState.GREEN_2] == 1
        assert color_counts[CellState.GREEN_3] == 1
        assert color_counts[CellState.GREEN_4] == 0

    def test_eight_neighbors_all_green4(self):
        """Counts all 8 neighbors when all are GREEN_4."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                cells[3 + dr][26 + dc] = CellState.GREEN_4
        grid = Grid(cells)
        color_counts = QuadLifeRules.get_neighbor_color_counts(grid, 3, 26)
        assert color_counts[CellState.GREEN_4] == 8
        assert sum(color_counts.values()) == 8

    def test_boundary_edge_cell(self):
        """Edge cell only counts valid in-bounds neighbors."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Set neighbors for corner cell (0, 0)
        cells[0][1] = CellState.GREEN_1
        cells[1][0] = CellState.GREEN_2
        cells[1][1] = CellState.GREEN_3
        grid = Grid(cells)
        color_counts = QuadLifeRules.get_neighbor_color_counts(grid, 0, 0)
        assert color_counts[CellState.GREEN_1] == 1
        assert color_counts[CellState.GREEN_2] == 1
        assert color_counts[CellState.GREEN_3] == 1
        assert sum(color_counts.values()) == 3  # Only 3 neighbors possible


class TestAliveNeighborCounting:
    """Test total alive neighbor counting."""

    def test_zero_alive_neighbors(self):
        """Empty grid has zero alive neighbors."""
        grid = Grid.empty()
        assert QuadLifeRules.count_alive_neighbors(grid, 3, 26) == 0

    def test_mixed_colors_count(self):
        """Count alive neighbors regardless of color."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][25] = CellState.GREEN_1
        cells[2][26] = CellState.GREEN_2
        cells[2][27] = CellState.GREEN_4
        grid = Grid(cells)
        assert QuadLifeRules.count_alive_neighbors(grid, 3, 26) == 3

    def test_ignores_dead_neighbors(self):
        """Dead cells are not counted."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][25] = CellState.DEAD  # Explicitly set to DEAD
        cells[2][26] = CellState.GREEN_1
        grid = Grid(cells)
        assert QuadLifeRules.count_alive_neighbors(grid, 3, 26) == 1


class TestBirthColorDetermination:
    """Test birth color determination logic."""

    def test_majority_single_color_two_neighbors(self):
        """Two neighbors same color → born that color."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][25] = CellState.GREEN_3
        cells[2][26] = CellState.GREEN_3
        cells[2][27] = CellState.GREEN_1
        grid = Grid(cells)
        # Cell at (3, 26) has 3 neighbors: 2 GREEN_3, 1 GREEN_1
        born_color = QuadLifeRules.determine_birth_color(grid, 3, 26)
        assert born_color == CellState.GREEN_3

    def test_three_different_colors_births_fourth(self):
        """Three different colors present → born 4th color (deadlock)."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][25] = CellState.GREEN_1
        cells[2][26] = CellState.GREEN_2
        cells[2][27] = CellState.GREEN_3
        grid = Grid(cells)
        # Cell at (3, 26) has 3 neighbors: GREEN_1, GREEN_2, GREEN_3 (missing GREEN_4)
        born_color = QuadLifeRules.determine_birth_color(grid, 3, 26)
        assert born_color == CellState.GREEN_4

    def test_deadlock_missing_green2(self):
        """Three different colors (missing GREEN_2) → born GREEN_2."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[2][25] = CellState.GREEN_1
        cells[2][26] = CellState.GREEN_3
        cells[2][27] = CellState.GREEN_4
        grid = Grid(cells)
        born_color = QuadLifeRules.determine_birth_color(grid, 3, 26)
        assert born_color == CellState.GREEN_2

    def test_tiebreaker_rgb_value(self):
        """When no clear majority, use RGB value as tiebreaker."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Set two neighbors with different colors (1 each)
        cells[2][25] = CellState.GREEN_1  # RGB: (198, 228, 139)
        cells[2][27] = CellState.GREEN_4  # RGB: (0, 109, 50)
        grid = Grid(cells)
        # GREEN_1 has higher RGB values, so should win tiebreaker
        born_color = QuadLifeRules.determine_birth_color(grid, 3, 26)
        assert born_color == CellState.GREEN_1

    def test_no_neighbors_raises_error(self):
        """Called with no alive neighbors raises ValueError."""
        grid = Grid.empty()
        with pytest.raises(ValueError, match="no alive neighbors"):
            QuadLifeRules.determine_birth_color(grid, 3, 26)


class TestSurvivalRules:
    """Test cell survival logic."""

    def test_survives_with_2_neighbors(self):
        """Alive cell with 2 neighbors survives."""
        assert QuadLifeRules.should_survive(2) is True

    def test_survives_with_3_neighbors(self):
        """Alive cell with 3 neighbors survives."""
        assert QuadLifeRules.should_survive(3) is True

    def test_dies_with_0_neighbors(self):
        """Alive cell with 0 neighbors dies."""
        assert QuadLifeRules.should_survive(0) is False

    def test_dies_with_1_neighbor(self):
        """Alive cell with 1 neighbor dies."""
        assert QuadLifeRules.should_survive(1) is False

    def test_dies_with_4_neighbors(self):
        """Alive cell with 4 neighbors dies."""
        assert QuadLifeRules.should_survive(4) is False

    def test_dies_with_8_neighbors(self):
        """Alive cell with 8 neighbors dies."""
        assert QuadLifeRules.should_survive(8) is False


class TestBirthRules:
    """Test cell birth logic."""

    def test_births_with_3_neighbors(self):
        """Dead cell with exactly 3 neighbors births."""
        assert QuadLifeRules.should_birth(3) is True

    def test_no_birth_with_0_neighbors(self):
        """Dead cell with 0 neighbors stays dead."""
        assert QuadLifeRules.should_birth(0) is False

    def test_no_birth_with_1_neighbor(self):
        """Dead cell with 1 neighbor stays dead."""
        assert QuadLifeRules.should_birth(1) is False

    def test_no_birth_with_2_neighbors(self):
        """Dead cell with 2 neighbors stays dead."""
        assert QuadLifeRules.should_birth(2) is False

    def test_no_birth_with_4_neighbors(self):
        """Dead cell with 4 neighbors stays dead."""
        assert QuadLifeRules.should_birth(4) is False

    def test_no_birth_with_8_neighbors(self):
        """Dead cell with 8 neighbors stays dead."""
        assert QuadLifeRules.should_birth(8) is False
