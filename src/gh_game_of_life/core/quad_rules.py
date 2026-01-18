"""Quad-Life cellular automaton rules.

Implements Quad-Life, a 4-color variant of cellular automata where:
- Cells have 4 living states (GREEN_1, GREEN_2, GREEN_3, GREEN_4) + 1 dead state (DEAD)
- Cells survive with 2-3 neighbors (Conway's rules)
- Dead cells birth with exactly 3 neighbors
- Birth color determined by neighbor color majority (2+ same color) or 4th color for deadlock
- When multiple colors have equal neighbors, uses RGB value as tiebreaker
"""

from .cell_state import CellState, ColorQuad
from .grid import Grid


class QuadLifeRules:
    """Quad-Life cellular automaton rules engine.

    Extends Conway's Game of Life to support 4 living colors.
    """

    @staticmethod
    def get_neighbor_color_counts(
        grid: Grid, row: int, col: int, boundary_strategy: str = "void"
    ) -> dict[CellState, int]:
        """Count neighbors by color (alive only, excludes DEAD).

        Args:
            grid: The current grid state.
            row: Cell row index.
            col: Cell column index.
            boundary_strategy: "void" (out-of-bounds = DEAD) or "loop" (toroidal wrapping).

        Returns:
            Dictionary mapping CellState to count of neighbors in that state.
            Only includes alive states (GREEN_1-4), DEAD is excluded.
        """
        color_counts: dict[CellState, int] = {
            CellState.GREEN_1: 0,
            CellState.GREEN_2: 0,
            CellState.GREEN_3: 0,
            CellState.GREEN_4: 0,
        }

        # Check all 8 adjacent cells
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the cell itself

                neighbor_row = row + dr
                neighbor_col = col + dc

                # Boundary handling
                if boundary_strategy == "loop":
                    # Toroidal wrapping
                    neighbor_row = neighbor_row % Grid.ROWS
                    neighbor_col = neighbor_col % Grid.COLS
                else:
                    # VOID strategy: out-of-bounds = DEAD
                    if not (
                        0 <= neighbor_row < Grid.ROWS and 0 <= neighbor_col < Grid.COLS
                    ):
                        continue

                neighbor_state = grid.get_cell(neighbor_row, neighbor_col)
                if neighbor_state != CellState.DEAD:
                    color_counts[neighbor_state] += 1

        return color_counts

    @staticmethod
    def count_alive_neighbors(grid: Grid, row: int, col: int) -> int:
        """Count total alive neighbors (all colors, excludes DEAD).

        Args:
            grid: The current grid state.
            row: Cell row index.
            col: Cell column index.

        Returns:
            Total count of alive neighbors (0-8).
        """
        color_counts = QuadLifeRules.get_neighbor_color_counts(grid, row, col)
        return sum(color_counts.values())

    @staticmethod
    def determine_birth_color(
        grid: Grid, row: int, col: int, boundary_strategy: str = "void"
    ) -> CellState:
        """Determine color for newly born cell.

        Rules:
        1. If 2+ neighbors are same color → born that color
        2. If 3 different colors → born 4th color (deadlock breaker)
        3. If no clear majority → use RGB value as tiebreaker

        Args:
            grid: The current grid state.
            row: Cell row index.
            col: Cell column index.
            boundary_strategy: "void" (out-of-bounds = DEAD) or "loop" (toroidal wrapping).

        Returns:
            CellState for the newly born cell.

        Raises:
            ValueError: If no alive neighbors found (shouldn't happen in birth context).
        """
        color_counts = QuadLifeRules.get_neighbor_color_counts(
            grid, row, col, boundary_strategy
        )

        # Remove colors with 0 neighbors
        active_colors = {
            color: count for color, count in color_counts.items() if count > 0
        }

        if not active_colors:
            raise ValueError(
                f"determine_birth_color called with no alive neighbors at ({row}, {col})"
            )

        # Rule 1: If any color has 2+ neighbors, born that color
        for color, count in active_colors.items():
            if count >= 2:
                return color

        # Rule 2: If 3 different colors present → born 4th color
        if len(active_colors) == 3:
            # Find the color not present
            all_green = {
                CellState.GREEN_1,
                CellState.GREEN_2,
                CellState.GREEN_3,
                CellState.GREEN_4,
            }
            missing_color = (all_green - set(active_colors.keys())).pop()
            return missing_color

        # Rule 3: No clear majority - use RGB tiebreaker
        # If 2 colors with 1 neighbor each, or some other tie:
        # Return the color with highest RGB value
        best_color = max(active_colors.keys(), key=lambda c: ColorQuad.get_color(c))
        return best_color

    @staticmethod
    def should_survive(alive_neighbors: int) -> bool:
        """Determine if a live cell survives.

        Conway's rules: live cell survives with 2-3 neighbors.

        Args:
            alive_neighbors: Total count of alive neighbors.

        Returns:
            True if cell survives, False otherwise.
        """
        return alive_neighbors in (2, 3)

    @staticmethod
    def should_birth(alive_neighbors: int) -> bool:
        """Determine if a dead cell births.

        Conway's rules: dead cell births with exactly 3 neighbors.

        Args:
            alive_neighbors: Total count of alive neighbors.

        Returns:
            True if cell should birth, False otherwise.
        """
        return alive_neighbors == 3
