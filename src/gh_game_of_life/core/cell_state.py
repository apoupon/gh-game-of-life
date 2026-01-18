"""Cell state representation for Quad-Life cellular automaton.

Defines the four color states used in Quad-Life and provides color mapping
to GitHub's green gradient palette.
"""

from enum import IntEnum
from typing import Tuple


class CellState(IntEnum):
    """Represents a cell state in Quad-Life.

    Values:
    - DEAD (0): No cell activity
    - GREEN_1 (1): Light green - low activity (1-2 contributions)
    - GREEN_2 (2): Medium green - moderate activity (3-4 contributions)
    - GREEN_3 (3): Darker green - high activity (5-7 contributions)
    - GREEN_4 (4): Darkest green - very high activity (8+ contributions)

    These values can be stored directly as integers in grids for efficiency.
    """

    DEAD = 0
    GREEN_1 = 1  # Light green
    GREEN_2 = 2  # Medium green
    GREEN_3 = 3  # Darker green
    GREEN_4 = 4  # Darkest green

    def is_alive(self) -> bool:
        """Check if this state represents a living cell."""
        return self != CellState.DEAD

    def __repr__(self) -> str:
        """String representation."""
        names = {
            CellState.DEAD: "DEAD",
            CellState.GREEN_1: "GREEN_1",
            CellState.GREEN_2: "GREEN_2",
            CellState.GREEN_3: "GREEN_3",
            CellState.GREEN_4: "GREEN_4",
        }
        return names.get(self, f"UNKNOWN({self.value})")


class ColorQuad:
    """GitHub green gradient color palette for Quad-Life.

    Provides RGB color values matching GitHub's contribution graph colors:
    - DEAD: Light gray background
    - GREEN_1: Lightest green (1-2 contributions)
    - GREEN_2: Light green (3-4 contributions)
    - GREEN_3: Medium green (5-7 contributions)
    - GREEN_4: Dark green (8+ contributions)
    """

    # RGB values matching GitHub's palette
    COLORS: dict[CellState, Tuple[int, int, int]] = {
        CellState.DEAD: (235, 237, 240),  # #ebedf0 - light gray
        CellState.GREEN_1: (198, 228, 139),  # #c6e48b - light green
        CellState.GREEN_2: (126, 231, 135),  # #7ee787 - medium green
        CellState.GREEN_3: (38, 166, 65),  # #26a641 - darker green
        CellState.GREEN_4: (0, 109, 50),  # #006d32 - darkest green
    }

    @classmethod
    def get_color(cls, state: CellState) -> Tuple[int, int, int]:
        """Get RGB color tuple for a cell state.

        Args:
            state: The cell state to get color for.

        Returns:
            Tuple of (R, G, B) values (0-255 each).

        Raises:
            ValueError: If state is not a valid CellState.
        """
        if not isinstance(state, CellState):
            raise TypeError(f"state must be CellState, got {type(state)}")

        return cls.COLORS[state]

    @classmethod
    def is_alive(cls, state: CellState) -> bool:
        """Check if cell state represents a living cell.

        Args:
            state: The cell state to check.

        Returns:
            True if state is GREEN_1, GREEN_2, GREEN_3, or GREEN_4.
            False if state is DEAD.
        """
        if not isinstance(state, CellState):
            raise TypeError(f"state must be CellState, got {type(state)}")

        return state.is_alive()

    @classmethod
    def contribution_to_state(cls, contribution_count: int) -> CellState:
        """Convert GitHub contribution count to cell state.

        Mapping:
        - 0 contributions → DEAD
        - 1-2 contributions → GREEN_1
        - 3-4 contributions → GREEN_2
        - 5-7 contributions → GREEN_3
        - 8+ contributions → GREEN_4

        Args:
            contribution_count: Number of contributions (0+).

        Returns:
            Corresponding CellState value.

        Raises:
            ValueError: If contribution_count is negative.
            TypeError: If contribution_count is not an integer.
        """
        if not isinstance(contribution_count, int):
            raise TypeError(
                f"contribution_count must be int, got {type(contribution_count)}"
            )

        if contribution_count < 0:
            raise ValueError(
                f"contribution_count must be >= 0, got {contribution_count}"
            )

        if contribution_count == 0:
            return CellState.DEAD
        elif contribution_count <= 2:
            return CellState.GREEN_1
        elif contribution_count <= 4:
            return CellState.GREEN_2
        elif contribution_count <= 7:
            return CellState.GREEN_3
        else:
            return CellState.GREEN_4
