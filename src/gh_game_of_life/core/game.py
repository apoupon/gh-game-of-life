"""Quad-Life simulation engine.

Implements Quad-Life rules (4-color cellular automaton) with configurable
boundary strategies for grid evolution.
"""

from enum import Enum

from .cell_state import CellState
from .grid import Grid
from .quad_rules import QuadLifeRules


class BoundaryStrategy(Enum):
    """Enum for different grid boundary behaviors."""

    VOID = "void"  # Cells outside grid are treated as dead
    LOOP = "loop"  # Grid wraps toroidally (edges connect)


class GameOfLife:
    """Quad-Life simulator for GitHub contribution grids.

    Evolves grids according to Quad-Life rules:
    - Any live cell with 2-3 neighbors survives (same color)
    - Any dead cell with exactly 3 neighbors births with determined color
    - All other cells die/stay dead
    - Birth color determined by neighbor color majority or tiebreaker

    Supports multiple boundary strategies for edge handling.
    """

    def __init__(self, strategy: BoundaryStrategy = BoundaryStrategy.LOOP) -> None:
        """Initialize Game of Life simulator.

        Args:
            strategy: Boundary behavior (VOID or LOOP).
                     Defaults to VOID (cells outside grid are dead).
        """
        if not isinstance(strategy, BoundaryStrategy):
            raise TypeError(f"strategy must be BoundaryStrategy, got {type(strategy)}")
        self.strategy = strategy

    def count_neighbors(self, grid: Grid, row: int, col: int) -> int:
        """Count alive neighbors for a cell.

        Args:
            grid: The current grid state.
            row: Cell row index.
            col: Cell column index.

        Returns:
            Number of alive neighbors (0-8).
        """
        count = 0

        # Check all 8 adjacent cells
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the cell itself

                neighbor_row = row + dr
                neighbor_col = col + dc

                # Apply boundary strategy
                if self.strategy == BoundaryStrategy.VOID:
                    # Out-of-bounds cells are treated as dead
                    if not (
                        0 <= neighbor_row < Grid.ROWS and 0 <= neighbor_col < Grid.COLS
                    ):
                        continue
                    neighbor_state = grid.get_cell(neighbor_row, neighbor_col)

                elif self.strategy == BoundaryStrategy.LOOP:
                    # Wrap edges toroidally
                    neighbor_row = neighbor_row % Grid.ROWS
                    neighbor_col = neighbor_col % Grid.COLS
                    neighbor_state = grid.get_cell(neighbor_row, neighbor_col)

                # Count if alive (any state except DEAD)
                if neighbor_state != CellState.DEAD:
                    count += 1

        return count

    def next_generation(self, grid: Grid) -> Grid:
        """Compute next generation of the grid.

        Applies Quad-Life rules:
        1. Live cell with 2-3 neighbors → survives with same color
        2. Dead cell with exactly 3 neighbors → births with determined color
        3. All other cells die/stay dead

        Args:
            grid: Current grid state.

        Returns:
            New Grid representing next generation.
        """
        new_cells = [[CellState.DEAD] * Grid.COLS for _ in range(Grid.ROWS)]

        for row in range(Grid.ROWS):
            for col in range(Grid.COLS):
                alive_neighbors = self.count_neighbors(grid, row, col)
                current_state = grid.get_cell(row, col)

                # Apply Quad-Life rules
                if current_state != CellState.DEAD:
                    # Cell is alive
                    if QuadLifeRules.should_survive(alive_neighbors):
                        # Survives with same color
                        new_cells[row][col] = current_state
                    else:
                        # Dies
                        new_cells[row][col] = CellState.DEAD
                else:
                    # Cell is dead
                    if QuadLifeRules.should_birth(alive_neighbors):
                        # Births with determined color
                        new_cells[row][col] = QuadLifeRules.determine_birth_color(
                            grid, row, col, self.strategy.value
                        )
                    else:
                        # Stays dead
                        new_cells[row][col] = CellState.DEAD

        return Grid(new_cells)

    def evolve(self, grid: Grid, generations: int) -> list[Grid]:
        """Evolve grid for multiple generations.

        Args:
            grid: Starting grid state.
            generations: Number of generations to evolve.
                        Must be >= 0.

        Returns:
            List of grids, starting with the input grid,
            including all intermediate generations.
            Total length is generations + 1.

        Raises:
            ValueError: If generations < 0.
        """
        if generations < 0:
            raise ValueError(f"generations must be >= 0, got {generations}")

        history = [grid]
        current = grid

        for _ in range(generations):
            current = self.next_generation(current)
            history.append(current)

        return history

    def simulate(self, grid: Grid, generations: int) -> Grid:
        """Simulate game for N generations, returning final state.

        Convenience method that returns only the final grid
        (equivalent to evolve()[-1]).

        Args:
            grid: Starting grid state.
            generations: Number of generations to simulate.

        Returns:
            Final grid state after N generations.
        """
        if generations < 0:
            raise ValueError(f"generations must be >= 0, got {generations}")

        current = grid
        for _ in range(generations):
            current = self.next_generation(current)
        return current

    def __repr__(self) -> str:
        """String representation of the simulator."""
        return f"GameOfLife({self.strategy.value})"
