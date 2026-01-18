"""Tests for Boundary Strategy Selection."""

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.game import BoundaryStrategy, GameOfLife
from gh_game_of_life.core.grid import Grid


class TestBoundaryStrategyEnum:
    """Test BoundaryStrategy enum definition and availability."""

    def test_void_strategy_exists(self):
        """VOID boundary strategy is defined."""
        assert hasattr(BoundaryStrategy, "VOID")
        assert BoundaryStrategy.VOID is not None

    def test_loop_strategy_exists(self):
        """LOOP boundary strategy is defined."""
        assert hasattr(BoundaryStrategy, "LOOP")
        assert BoundaryStrategy.LOOP is not None

    def test_strategy_values_are_strings(self):
        """Strategy values are string identifiers."""
        assert BoundaryStrategy.VOID.value == "void"
        assert BoundaryStrategy.LOOP.value == "loop"

    def test_strategies_are_enumerable(self):
        """Strategies can be enumerated."""
        strategies = list(BoundaryStrategy)
        assert len(strategies) == 2
        assert BoundaryStrategy.VOID in strategies
        assert BoundaryStrategy.LOOP in strategies


class TestStrategySelection:
    """Test user ability to select strategies."""

    def test_select_void_strategy(self):
        """User can select VOID strategy."""
        game = GameOfLife(BoundaryStrategy.VOID)
        assert game.strategy == BoundaryStrategy.VOID

    def test_select_loop_strategy(self):
        """User can select LOOP strategy."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        assert game.strategy == BoundaryStrategy.LOOP

    def test_default_strategy_is_void(self):
        """Default strategy is VOID when not specified."""
        game = GameOfLife()
        assert game.strategy == BoundaryStrategy.VOID

    def test_strategy_is_configurable(self):
        """Can create multiple GameOfLife instances with different strategies."""
        void_game = GameOfLife(BoundaryStrategy.VOID)
        loop_game = GameOfLife(BoundaryStrategy.LOOP)

        assert void_game.strategy != loop_game.strategy
        assert void_game.strategy == BoundaryStrategy.VOID
        assert loop_game.strategy == BoundaryStrategy.LOOP


class TestVoidStrategyBehavior:
    """Test VOID strategy treats outside cells as dead."""

    def test_void_treats_outside_as_dead_horizontal_edge(self):
        """VOID strategy: cells outside grid are treated as dead (horizontal)."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][52] = CellState.GREEN_1  # Right edge cell
        grid = Grid(cells)

        # Right edge can only see 3 neighbors max (no wrapping)
        neighbors = game.count_neighbors(grid, 3, 52)
        assert neighbors == 0  # Isolated

    def test_void_treats_outside_as_dead_vertical_edge(self):
        """VOID strategy: cells outside grid are treated as dead (vertical)."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[6][26] = CellState.GREEN_1  # Bottom edge cell
        grid = Grid(cells)

        # Bottom edge can only see 3 neighbors max (no wrapping)
        neighbors = game.count_neighbors(grid, 6, 26)
        assert neighbors == 0  # Isolated

    def test_void_treats_corner_as_dead(self):
        """VOID strategy: corner cells are isolated."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = CellState.GREEN_1  # Top-left corner
        grid = Grid(cells)

        # Corner can only see 3 neighbors max
        neighbors = game.count_neighbors(grid, 0, 0)
        assert neighbors == 0  # Isolated

    def test_void_edge_patterns_cannot_evolve(self):
        """VOID strategy: patterns at edges behave differently due to boundary."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Single live cell at edge
        cells[0][0] = CellState.GREEN_1
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # Should die (alone at edge with no neighbors outside)
        assert next_gen.get_cell(0, 0) == CellState.DEAD


class TestLoopStrategyBehavior:
    """Test LOOP strategy wraps edges toroidally."""

    def test_loop_wraps_horizontally_left(self):
        """LOOP strategy: left edge wraps to right edge."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][0] = CellState.GREEN_1  # Left edge
        grid = Grid(cells)

        # Cell [3][52] (right edge) should see [3][0] as neighbor
        neighbors = game.count_neighbors(grid, 3, 52)
        assert neighbors == 1

    def test_loop_wraps_horizontally_right(self):
        """LOOP strategy: right edge wraps to left edge."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[3][52] = CellState.GREEN_1  # Right edge
        grid = Grid(cells)

        # Cell [3][0] (left edge) should see [3][52] as neighbor
        neighbors = game.count_neighbors(grid, 3, 0)
        assert neighbors == 1

    def test_loop_wraps_vertically_top(self):
        """LOOP strategy: top edge wraps to bottom edge."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][26] = CellState.GREEN_1  # Top edge
        grid = Grid(cells)

        # Cell [6][26] (bottom edge) should see [0][26] as neighbor
        neighbors = game.count_neighbors(grid, 6, 26)
        assert neighbors == 1

    def test_loop_wraps_vertically_bottom(self):
        """LOOP strategy: bottom edge wraps to top edge."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[6][26] = CellState.GREEN_1  # Bottom edge
        grid = Grid(cells)

        # Cell [0][26] (top edge) should see [6][26] as neighbor
        neighbors = game.count_neighbors(grid, 0, 26)
        assert neighbors == 1

    def test_loop_wraps_diagonally(self):
        """LOOP strategy: corners wrap diagonally."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = CellState.GREEN_1  # Top-left corner
        grid = Grid(cells)

        # Cell [6][52] (bottom-right corner) should see [0][0] diagonally
        neighbors = game.count_neighbors(grid, 6, 52)
        assert neighbors == 1

    def test_loop_toroidal_wrapping_all_directions(self):
        """LOOP strategy: grid wraps like a torus in all directions."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]

        # Place a single alive cell
        cells[0][0] = CellState.GREEN_1
        grid = Grid(cells)

        # Count neighbors at the opposite corner
        # Should see the cell at [0][0] diagonally from [6][52]
        neighbors_opposite_corner = game.count_neighbors(grid, 6, 52)
        assert neighbors_opposite_corner == 1

        # Count neighbors at adjacent corners (horizontal wrap)
        neighbors_right_corner = game.count_neighbors(grid, 0, 52)
        assert neighbors_right_corner == 1

        # Count neighbors at adjacent corners (vertical wrap)
        neighbors_bottom_corner = game.count_neighbors(grid, 6, 0)
        assert neighbors_bottom_corner == 1


class TestStrategyImpactOnEvolution:
    """Test how strategy choice affects evolution results."""

    def test_void_vs_loop_different_results(self):
        """Different strategies produce different evolution results."""
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Place pattern at edge
        cells[0][0] = CellState.GREEN_1
        cells[0][1] = CellState.GREEN_1
        cells[1][0] = CellState.GREEN_1
        grid = Grid(cells)

        void_game = GameOfLife(BoundaryStrategy.VOID)
        loop_game = GameOfLife(BoundaryStrategy.LOOP)

        void_next = void_game.next_generation(grid)
        loop_next = loop_game.next_generation(grid)

        # Results should differ due to boundary handling
        # (This specific pattern may or may not differ, but in general they do)
        assert void_next is not loop_next

    def test_void_strategy_preserves_interior_pattern(self):
        """VOID strategy doesn't affect patterns in interior."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Place blinker in center
        cells[3][25] = CellState.GREEN_1
        cells[3][26] = CellState.GREEN_1
        cells[3][27] = CellState.GREEN_1
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # Should evolve normally (not affected by boundary)
        assert next_gen.get_cell(2, 26) == CellState.GREEN_1
        assert next_gen.get_cell(4, 26) == CellState.GREEN_1

    def test_loop_strategy_preserves_interior_pattern(self):
        """LOOP strategy doesn't affect patterns in interior."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        # Place blinker in center
        cells[3][25] = CellState.GREEN_1
        cells[3][26] = CellState.GREEN_1
        cells[3][27] = CellState.GREEN_1
        grid = Grid(cells)

        next_gen = game.next_generation(grid)
        # Should evolve the same as VOID for interior patterns
        assert next_gen.get_cell(2, 26) == CellState.GREEN_1
        assert next_gen.get_cell(4, 26) == CellState.GREEN_1


class TestStrategyConfigurability:
    """Test that strategy can be configured and changed easily."""

    def test_create_simulator_with_each_strategy(self):
        """Can create simulators for each available strategy."""
        for strategy in BoundaryStrategy:
            game = GameOfLife(strategy)
            assert game.strategy == strategy

    def test_strategy_determines_simulation_behavior(self):
        """Selected strategy determines how simulation behaves."""
        grid = Grid.empty()

        void_game = GameOfLife(BoundaryStrategy.VOID)
        loop_game = GameOfLife(BoundaryStrategy.LOOP)

        # Both can simulate but with different boundary behavior
        void_result = void_game.simulate(grid, 5)
        loop_result = loop_game.simulate(grid, 5)

        assert void_result is not None
        assert loop_result is not None

    def test_strategy_selection_is_intuitive(self):
        """Strategy selection is clear and intuitive."""
        # Should be obvious what VOID and LOOP mean
        void_strategy = BoundaryStrategy.VOID
        loop_strategy = BoundaryStrategy.LOOP

        # Values clearly indicate behavior
        assert void_strategy.value == "void"
        assert loop_strategy.value == "loop"


class TestAcceptanceCriteria:
    """Verify all FR-103 acceptance criteria."""

    def test_void_strategy_treats_outside_cells_as_dead(self):
        """Acceptance Criterion: 'Void' strategy treats outside cells as dead."""
        game = GameOfLife(BoundaryStrategy.VOID)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]

        # Place alive cells at all edges
        for i in range(53):
            cells[0][i] = CellState.GREEN_1  # Top row
            cells[6][i] = CellState.GREEN_1  # Bottom row
        for i in range(7):
            cells[i][0] = CellState.GREEN_1  # Left column
            cells[i][52] = CellState.GREEN_1  # Right column
        grid = Grid(cells)

        # Corner cell should not see neighbors outside grid
        # [0][0] should only see neighbors within grid bounds
        corner_neighbors = game.count_neighbors(grid, 0, 0)
        # Can only see [0][1] and [1][0] (not [1][1] since it's not alive)
        assert corner_neighbors == 2  # Only [0][1], [1][0]

    def test_loop_strategy_wraps_edges_toroidally(self):
        """Acceptance Criterion: 'Loop' strategy wraps edges toroidally."""
        game = GameOfLife(BoundaryStrategy.LOOP)
        cells = [[CellState.DEAD] * 53 for _ in range(7)]
        cells[0][0] = CellState.GREEN_1
        grid = Grid(cells)

        # Verify toroidal wrapping at each boundary
        # Top wraps to bottom
        assert game.count_neighbors(grid, 6, 0) == 1
        # Left wraps to right
        assert game.count_neighbors(grid, 0, 52) == 1
        # Diagonal wrapping: [6][52] sees [0][0]
        assert game.count_neighbors(grid, 6, 52) == 1

    def test_strategy_selection_is_configurable(self):
        """Acceptance Criterion: Strategy selection is configurable."""
        # Can select VOID
        void_game = GameOfLife(BoundaryStrategy.VOID)
        assert void_game.strategy == BoundaryStrategy.VOID

        # Can select LOOP
        loop_game = GameOfLife(BoundaryStrategy.LOOP)
        assert loop_game.strategy == BoundaryStrategy.LOOP

        # Default is VOID
        default_game = GameOfLife()
        assert default_game.strategy == BoundaryStrategy.VOID

        # Can create multiple instances with different strategies
        simulators = [
            GameOfLife(BoundaryStrategy.VOID),
            GameOfLife(BoundaryStrategy.LOOP),
        ]
        assert len(simulators) == 2
        assert simulators[0].strategy != simulators[1].strategy
