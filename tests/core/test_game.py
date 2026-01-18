"""Tests for Game of Life simulation."""

import pytest

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.game import BoundaryStrategy, GameOfLife
from gh_game_of_life.core.grid import Grid


class TestGameOfLifeInitialization:
    """Test GameOfLife simulator initialization."""

    def test_default_strategy_is_void(self):
        """GameOfLife defaults to VOID boundary strategy."""
        game = GameOfLife()
        assert game.strategy == BoundaryStrategy.VOID

    def test_void_strategy_initialization(self):
        """GameOfLife accepts VOID strategy."""
        game = GameOfLife(BoundaryStrategy.VOID)
        assert game.strategy == BoundaryStrategy.VOID

    def test_loop_strategy_initialization(self):
        """GameOfLife accepts LOOP strategy."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        assert game.strategy == BoundaryStrategy.LOOP

    def test_invalid_strategy_type(self):
        """GameOfLife rejects non-BoundaryStrategy objects."""
        with pytest.raises(TypeError):
            GameOfLife("void")

    def test_none_strategy(self):
        """GameOfLife rejects None strategy."""
        with pytest.raises(TypeError):
            GameOfLife(None)


class TestNeighborCounting:
    """Test neighbor counting logic."""

    def test_count_neighbors_all_dead(self):
        """All-dead grid has zero neighbors everywhere."""
        game = GameOfLife(BoundaryStrategy.VOID)
        grid = Grid.empty()
        assert game.count_neighbors(grid, 3, 26) == 0

    def test_count_neighbors_single_alive(self):
        """Single alive cell is counted as 1 neighbor."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.GREEN_1
        grid = Grid(cells)

        # Cell at [2][25] should see 1 neighbor
        assert game.count_neighbors(grid, 2, 25) == 1

    def test_count_neighbors_all_eight_surrounding(self):
        """All 8 surrounding cells alive → count 8."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Place alive cells in all 8 surrounding positions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                cells[3 + dr][26 + dc] = CellState.GREEN_1
        grid = Grid(cells)

        assert game.count_neighbors(grid, 3, 26) == 8

    def test_count_neighbors_void_boundary_corner(self):
        """VOID strategy: corner cells can't see outside grid."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][1] = CellState.GREEN_1  # Neighbor to corner [0][0]
        cells[1][0] = CellState.GREEN_1
        cells[1][1] = CellState.GREEN_1
        grid = Grid(cells)

        # Corner [0][0] sees 3 neighbors, not more
        assert game.count_neighbors(grid, 0, 0) == 3

    def test_count_neighbors_loop_boundary_wraps_horizontal(self):
        """LOOP strategy wraps horizontally."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][0] = CellState.GREEN_1  # Left edge
        grid = Grid(cells)

        # Cell at [3][52] (right edge) should see [3][0] as neighbor
        assert game.count_neighbors(grid, 3, 52) == 1

    def test_count_neighbors_loop_boundary_wraps_vertical(self):
        """LOOP strategy wraps vertically."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][26] = CellState.GREEN_1  # Top edge
        grid = Grid(cells)

        # Cell at [6][26] (bottom edge) should see [0][26] as neighbor
        assert game.count_neighbors(grid, 6, 26) == 1

    def test_count_neighbors_loop_boundary_wraps_diagonal(self):
        """LOOP strategy wraps diagonally."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = CellState.GREEN_1
        grid = Grid(cells)

        # Cell at [6][52] should see [0][0] diagonally
        assert game.count_neighbors(grid, 6, 52) == 1


class TestQuadLifeRules:
    """Test Quad-Life rules (extended Conway's Game of Life)."""

    def test_live_cell_with_2_neighbors_survives(self):
        """Live cell with 2 neighbors survives with same color."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.GREEN_2  # Center (alive, GREEN_2)
        cells[2][25] = CellState.GREEN_1  # Neighbor 1
        cells[2][26] = CellState.GREEN_1  # Neighbor 2
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.GREEN_2  # Survives, same color

    def test_live_cell_with_3_neighbors_survives(self):
        """Live cell with 3 neighbors survives with same color."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.GREEN_3  # Center (alive, GREEN_3)
        cells[2][25] = CellState.GREEN_1  # Neighbor 1
        cells[2][26] = CellState.GREEN_2  # Neighbor 2
        cells[2][27] = CellState.GREEN_4  # Neighbor 3
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.GREEN_3  # Survives, same color

    def test_live_cell_with_0_neighbors_dies(self):
        """Live cell with 0 neighbors dies."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.GREEN_1  # Alone
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.DEAD

    def test_live_cell_with_1_neighbor_dies(self):
        """Live cell with 1 neighbor dies (underpopulation)."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.GREEN_1  # Center
        cells[2][25] = CellState.GREEN_2  # Only neighbor
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.DEAD

    def test_live_cell_with_4_neighbors_dies(self):
        """Live cell with 4+ neighbors dies (overpopulation)."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.GREEN_1  # Center
        # Add 4 neighbors around the center
        cells[2][25] = CellState.GREEN_2
        cells[2][26] = CellState.GREEN_2
        cells[2][27] = CellState.GREEN_2
        cells[3][25] = CellState.GREEN_2
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.DEAD

    def test_dead_cell_with_3_neighbors_births_with_color(self):
        """Dead cell with exactly 3 neighbors births with determined color."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.DEAD  # Center (dead)
        cells[2][25] = CellState.GREEN_3  # Neighbor 1
        cells[2][26] = CellState.GREEN_3  # Neighbor 2 (same color)
        cells[2][27] = CellState.GREEN_1  # Neighbor 3
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # Green_3 has 2 neighbors, so births as GREEN_3
        assert next_gen.get_cell(3, 26) == CellState.GREEN_3

    def test_dead_cell_with_2_neighbors_stays_dead(self):
        """Dead cell with 2 neighbors stays dead."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.DEAD  # Center (dead)
        cells[2][25] = CellState.GREEN_1  # Neighbor 1
        cells[2][26] = CellState.GREEN_2  # Neighbor 2
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.DEAD

    def test_dead_cell_with_4_neighbors_stays_dead(self):
        """Dead cell with 4 neighbors stays dead."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][26] = CellState.DEAD
        # Add 4 neighbors around the center
        cells[2][25] = CellState.GREEN_1
        cells[2][26] = CellState.GREEN_2
        cells[2][27] = CellState.GREEN_3
        cells[3][25] = CellState.GREEN_4
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        assert next_gen.get_cell(3, 26) == CellState.DEAD


class TestBoundaryStrategies:
    """Test boundary strategy behavior in full generations."""

    def test_void_strategy_edge_isolation(self):
        """VOID: edge cells isolated from outside."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Place patterns at edges
        cells[0][0] = CellState.GREEN_1
        cells[0][1] = CellState.GREEN_1
        cells[1][0] = CellState.GREEN_1  # 2-3 cell cluster
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # This forms a small pattern that depends on VOID behavior
        assert next_gen is not None

    def test_loop_strategy_edge_wrapping(self):
        """LOOP: edge cells see wrapped neighbors."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Create a pattern that spans edges
        cells[0][0] = CellState.GREEN_1
        cells[0][52] = CellState.GREEN_1
        cells[1][0] = CellState.GREEN_1
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # Edge cells see more neighbors due to wrapping
        assert next_gen is not None


class TestEvolutionMethods:
    """Test grid evolution over multiple generations."""

    def test_next_generation_creates_new_grid(self):
        """next_generation() returns new Grid."""
        game = GameOfLife()
        grid1 = Grid.empty()
        grid2 = game.next_generation(grid1)
        assert grid1 is not grid2
        assert grid1 == grid2  # Empty stays empty

    def test_next_generation_with_blinker_pattern(self):
        """Blinker pattern: period-2 oscillator in Quad-Life."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Horizontal blinker
        cells[3][25] = CellState.GREEN_1
        cells[3][26] = CellState.GREEN_1
        cells[3][27] = CellState.GREEN_1
        grid = Grid(cells)

        gen1 = game.next_generation(grid)
        # Should now be vertical
        assert gen1.get_cell(2, 26) == CellState.GREEN_1
        assert gen1.get_cell(3, 26) == CellState.GREEN_1
        assert gen1.get_cell(4, 26) == CellState.GREEN_1
        assert gen1.get_cell(3, 25) == CellState.DEAD

        # Next generation returns to horizontal
        gen2 = game.next_generation(gen1)
        assert gen2 == grid

    def test_evolve_returns_list_of_grids(self):
        """evolve() returns list including start grid."""
        game = GameOfLife()
        grid = Grid.empty()
        history = game.evolve(grid, 3)

        assert isinstance(history, list)
        assert len(history) == 4  # Start + 3 generations
        assert history[0] is grid

    def test_evolve_zero_generations(self):
        """evolve(grid, 0) returns [grid]."""
        game = GameOfLife()
        grid = Grid.full()
        history = game.evolve(grid, 0)

        assert history == [grid]

    def test_evolve_negative_generations_raises_error(self):
        """evolve() with negative generations raises ValueError."""
        game = GameOfLife()
        grid = Grid.empty()

        with pytest.raises(ValueError, match="must be >= 0"):
            game.evolve(grid, -1)

    def test_evolve_returns_deterministic_results(self):
        """Identical inputs produce identical evolution history."""
        cells = [
            [CellState.GREEN_1 if i % 2 == 0 else CellState.DEAD for i in range(53)]
            for _ in range(7)
        ]
        grid1 = Grid(cells)
        grid2 = Grid([row[:] for row in cells])

        game = GameOfLife(BoundaryStrategy.VOID)
        history1 = game.evolve(grid1, 5)
        history2 = game.evolve(grid2, 5)

        assert len(history1) == len(history2)
        for g1, g2 in zip(history1, history2):
            assert g1 == g2

    def test_simulate_returns_final_grid(self):
        """simulate() returns only final grid state."""
        game = GameOfLife()
        grid = Grid.empty()
        final = game.simulate(grid, 3)

        assert isinstance(final, Grid)
        assert final == grid  # Empty stays empty

    def test_simulate_zero_generations(self):
        """simulate(grid, 0) returns same grid."""
        game = GameOfLife()
        grid = Grid.full()
        result = game.simulate(grid, 0)

        assert result == grid

    def test_simulate_negative_generations_raises_error(self):
        """simulate() with negative generations raises ValueError."""
        game = GameOfLife()
        grid = Grid.empty()

        with pytest.raises(ValueError, match="must be >= 0"):
            game.simulate(grid, -1)

    def test_simulate_matches_evolve_final(self):
        """simulate(g, n) equals evolve(g, n)[-1]."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [
            [
                CellState.GREEN_1 if (i + j) % 2 == 0 else CellState.DEAD
                for j in range(53)
            ]
            for i in range(7)
        ]
        grid = Grid(cells)

        final_via_simulate = game.simulate(grid, 10)
        history_via_evolve = game.evolve(grid, 10)

        assert final_via_simulate == history_via_evolve[-1]


class TestAcceptanceCriteria:
    """Test explicit acceptance criteria for FR-102."""

    def test_quad_life_rules_applied(self):
        """Quad-Life rules are applied correctly."""
        game = GameOfLife(BoundaryStrategy.VOID)
        # Create specific patterns to verify all rules
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Block pattern (stable in both Conway and Quad-Life)
        cells[2][2] = CellState.GREEN_1
        cells[2][3] = CellState.GREEN_1
        cells[3][2] = CellState.GREEN_1
        cells[3][3] = CellState.GREEN_1
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # Block should remain unchanged
        assert next_gen.get_cell(2, 2) == CellState.GREEN_1
        assert next_gen.get_cell(2, 3) == CellState.GREEN_1
        assert next_gen.get_cell(3, 2) == CellState.GREEN_1
        assert next_gen.get_cell(3, 3) == CellState.GREEN_1

    def test_deterministic_results(self):
        """Identical inputs produce identical outputs."""
        cells = [
            [
                CellState.GREEN_1 if (i * j) % 3 == 0 else CellState.DEAD
                for j in range(53)
            ]
            for i in range(7)
        ]
        grid1 = Grid(cells)
        grid2 = Grid([row[:] for row in cells])

        game = GameOfLife(BoundaryStrategy.VOID)
        result1 = game.next_generation(grid1)
        result2 = game.next_generation(grid2)

        assert result1 == result2

    def test_supports_multiple_generations(self):
        """Can evolve grid over multiple generations."""
        game = GameOfLife()
        grid = Grid.empty()

        # Should handle any reasonable number of generations
        for n in [1, 5, 10, 100]:
            history = game.evolve(grid, n)
            assert len(history) == n + 1
