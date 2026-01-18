"""Core Grid Representation for Quad-Life cellular automaton.

This module implements the fixed-size, immutable grid that represents
the GitHub contribution layout (53 columns × 7 rows) with Quad-Life cell states.
"""

from .cell_state import CellState


class Grid:
    """Immutable 53×7 grid representing GitHub contribution graph in Quad-Life.

    The grid maintains four-color cell states (DEAD, GREEN_1, GREEN_2, GREEN_3, GREEN_4)
    corresponding to contribution activity levels. Grid dimensions are strictly enforced
    as invariants and cannot be modified after creation.

    Attributes:
        ROWS: Fixed number of rows (7 - days of week)
        COLS: Fixed number of columns (53 - weeks in a year)
    """

    ROWS = 7
    COLS = 53

    def __init__(self, cells: list[list[CellState]]) -> None:
        """Initialize a grid with Quad-Life cell states.

        Args:
            cells: 2D list of CellState values representing cell states.
                   Each cell must be DEAD, GREEN_1, GREEN_2, GREEN_3, or GREEN_4.
                   Must be exactly ROWS × COLS.

        Raises:
            ValueError: If dimensions don't match 53×7 or cells is invalid.
            TypeError: If cells contains non-CellState values.
        """
        if not isinstance(cells, (list, tuple)):
            raise TypeError(f"cells must be a list or tuple, got {type(cells)}")

        if len(cells) != self.ROWS:
            raise ValueError(f"Grid must have {self.ROWS} rows, got {len(cells)}")

        for row_idx, row in enumerate(cells):
            if not isinstance(row, (list, tuple)):
                raise TypeError(
                    f"Row {row_idx} must be a list or tuple, got {type(row)}"
                )
            if len(row) != self.COLS:
                raise ValueError(
                    f"Row {row_idx} must have {self.COLS} columns, got {len(row)}"
                )
            for col_idx, cell in enumerate(row):
                if not isinstance(cell, CellState):
                    raise TypeError(
                        f"Cell [{row_idx}][{col_idx}] must be CellState, "
                        f"got {type(cell).__name__}"
                    )

        # Store as immutable tuple of tuples
        self._cells: tuple[tuple[CellState, ...], ...] = tuple(
            tuple(row) for row in cells
        )

    def get_cell(self, row: int, col: int) -> CellState:
        """Get the state of a cell.

        Args:
            row: Row index (0-6)
            col: Column index (0-52)

        Returns:
            CellState value (DEAD, GREEN_1, GREEN_2, GREEN_3, or GREEN_4).

        Raises:
            IndexError: If row or col is out of bounds.
        """
        if not (0 <= row < self.ROWS):
            raise IndexError(f"Row {row} out of bounds [0, {self.ROWS - 1}]")
        if not (0 <= col < self.COLS):
            raise IndexError(f"Col {col} out of bounds [0, {self.COLS - 1}]")
        return self._cells[row][col]

    def to_list(self) -> list[list[int]]:
        """Export grid as mutable 2D list of integer values.

        Returns:
            2D list of integers (0-4) representing grid state.
            This is a copy; modifications do not affect the grid.
            0=DEAD, 1=GREEN_1, 2=GREEN_2, 3=GREEN_3, 4=GREEN_4
        """
        return [[int(cell) for cell in row] for row in self._cells]

    @classmethod
    def empty(cls) -> "Grid":
        """Create an empty grid (all cells dead).

        Returns:
            A new Grid with all cells set to DEAD.
        """
        return cls([[CellState.DEAD] * cls.COLS for _ in range(cls.ROWS)])

    @classmethod
    def full(cls) -> "Grid":
        """Create a full grid (all cells at maximum state).

        Returns:
            A new Grid with all cells set to GREEN_4.
        """
        return cls([[CellState.GREEN_4] * cls.COLS for _ in range(cls.ROWS)])

    @classmethod
    def from_color_values(cls, values: list[list[int]]) -> "Grid":
        """Create a grid from integer color values.

        Args:
            values: 2D list of integers (0-4) representing cell states.
                   0=DEAD, 1=GREEN_1, 2=GREEN_2, 3=GREEN_3, 4=GREEN_4

        Returns:
            A new Grid with cells initialized from the values.

        Raises:
            ValueError: If any value is not in range 0-4.
            TypeError: If values contain non-integers.
        """
        cells = []
        for row_idx, row in enumerate(values):
            cell_row = []
            for col_idx, val in enumerate(row):
                if not isinstance(val, int):
                    raise TypeError(
                        f"Cell [{row_idx}][{col_idx}] must be int, got {type(val)}"
                    )
                if not 0 <= val <= 4:
                    raise ValueError(
                        f"Cell [{row_idx}][{col_idx}] must be 0-4, got {val}"
                    )
                cell_row.append(CellState(val))
            cells.append(cell_row)

        return cls(cells)

    def __repr__(self) -> str:
        """String representation of the grid."""
        return f"Grid({self.ROWS}×{self.COLS})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Grid.

        Args:
            other: Object to compare with.

        Returns:
            True if both grids have identical cell states.
        """
        if not isinstance(other, Grid):
            return NotImplemented
        return self._cells == other._cells
