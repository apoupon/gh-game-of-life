"""GitHub contribution graph color palette.

Provides standard GitHub colors for Quad-Life cells in Game of Life visualizations.
Maps CellState values to RGB colors matching GitHub's contribution graph.
"""

from dataclasses import dataclass

from gh_game_of_life.core.cell_state import CellState


@dataclass(frozen=True)
class Color:
    """Immutable RGB color representation.

    Attributes:
        red: Red channel (0-255)
        green: Green channel (0-255)
        blue: Blue channel (0-255)
    """

    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        """Validate RGB values."""
        for value, name in [
            (self.red, "red"),
            (self.green, "green"),
            (self.blue, "blue"),
        ]:
            if not isinstance(value, int):
                raise TypeError(f"{name} must be int, got {type(value).__name__}")
            if not (0 <= value <= 255):
                raise ValueError(f"{name} must be 0-255, got {value}")

    def to_tuple(self) -> tuple[int, int, int]:
        """Convert to RGB tuple for PIL."""
        return (self.red, self.green, self.blue)

    def __repr__(self) -> str:
        """String representation."""
        return f"Color(#{self.red:02x}{self.green:02x}{self.blue:02x})"


class GitHubPalette:
    """GitHub contribution graph color palette for Quad-Life.

    Defines standard colors for representing cell states:
    - DEAD: Gray (#ebedf0) - no contribution
    - GREEN_1: Light green (#c6e48b) - 1-2 contributions
    - GREEN_2: Medium green (#7ee787) - 3-4 contributions
    - GREEN_3: Dark green (#26a641) - 5-7 contributions
    - GREEN_4: Darkest green (#006d32) - 8+ contributions

    Reference: GitHub's actual contribution graph colors
    """

    BACKGROUND = Color(255, 255, 255)

    DEAD = Color(239, 242, 245)
    GREEN_1 = Color(172, 238, 187)
    GREEN_2 = Color(74, 194, 107)
    GREEN_3 = Color(46, 164, 78)
    GREEN_4 = Color(18, 99, 41)

    @classmethod
    def get_cell_color(cls, cell_state: CellState) -> Color:
        """Get color for a cell state.

        Args:
            cell_state: CellState value (DEAD, GREEN_1-4).

        Returns:
            Appropriate Color for the cell state.
        """
        color_map = {
            CellState.DEAD: cls.DEAD,
            CellState.GREEN_1: cls.GREEN_1,
            CellState.GREEN_2: cls.GREEN_2,
            CellState.GREEN_3: cls.GREEN_3,
            CellState.GREEN_4: cls.GREEN_4,
        }
        return color_map[cell_state]

    @classmethod
    def validate_color(cls, color: Color) -> None:
        """Validate color object.

        Args:
            color: Color to validate.

        Raises:
            TypeError: If color is not a Color instance.
        """
        if not isinstance(color, Color):
            raise TypeError(f"Expected Color, got {type(color).__name__}")
