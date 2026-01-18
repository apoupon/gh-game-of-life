"""Tests for CellState and ColorQuad."""

import pytest

from gh_game_of_life.core.cell_state import CellState, ColorQuad


class TestCellState:
    """Test CellState enum."""

    def test_cell_state_values(self):
        """CellState values are correct."""
        assert CellState.DEAD == 0
        assert CellState.GREEN_1 == 1
        assert CellState.GREEN_2 == 2
        assert CellState.GREEN_3 == 3
        assert CellState.GREEN_4 == 4

    def test_cell_state_is_alive(self):
        """is_alive() correctly identifies live cells."""
        assert CellState.DEAD.is_alive() is False
        assert CellState.GREEN_1.is_alive() is True
        assert CellState.GREEN_2.is_alive() is True
        assert CellState.GREEN_3.is_alive() is True
        assert CellState.GREEN_4.is_alive() is True

    def test_cell_state_from_int(self):
        """CellState can be created from int values."""
        assert CellState(0) == CellState.DEAD
        assert CellState(1) == CellState.GREEN_1
        assert CellState(4) == CellState.GREEN_4

    def test_cell_state_repr(self):
        """CellState string representation."""
        assert repr(CellState.DEAD) == "DEAD"
        assert repr(CellState.GREEN_1) == "GREEN_1"
        assert repr(CellState.GREEN_4) == "GREEN_4"


class TestColorQuad:
    """Test ColorQuad color mapping."""

    def test_dead_color(self):
        """DEAD cell has correct color."""
        color = ColorQuad.get_color(CellState.DEAD)
        assert color == (235, 237, 240)  # #ebedf0

    def test_green1_color(self):
        """GREEN_1 cell has correct color."""
        color = ColorQuad.get_color(CellState.GREEN_1)
        assert color == (198, 228, 139)  # #c6e48b

    def test_green2_color(self):
        """GREEN_2 cell has correct color."""
        color = ColorQuad.get_color(CellState.GREEN_2)
        assert color == (126, 231, 135)  # #7ee787

    def test_green3_color(self):
        """GREEN_3 cell has correct color."""
        color = ColorQuad.get_color(CellState.GREEN_3)
        assert color == (38, 166, 65)  # #26a641

    def test_green4_color(self):
        """GREEN_4 cell has correct color."""
        color = ColorQuad.get_color(CellState.GREEN_4)
        assert color == (0, 109, 50)  # #006d32

    def test_get_color_rejects_invalid_state(self):
        """get_color() rejects non-CellState."""
        with pytest.raises(TypeError):
            ColorQuad.get_color(1)

    def test_is_alive_for_dead(self):
        """is_alive() returns False for DEAD."""
        assert ColorQuad.is_alive(CellState.DEAD) is False

    def test_is_alive_for_green_states(self):
        """is_alive() returns True for all GREEN states."""
        for state in [
            CellState.GREEN_1,
            CellState.GREEN_2,
            CellState.GREEN_3,
            CellState.GREEN_4,
        ]:
            assert ColorQuad.is_alive(state) is True

    def test_is_alive_rejects_invalid_state(self):
        """is_alive() rejects non-CellState."""
        with pytest.raises(TypeError):
            ColorQuad.is_alive(1)


class TestContributionMapping:
    """Test contribution count to cell state mapping."""

    def test_zero_contributions_dead(self):
        """0 contributions → DEAD."""
        assert ColorQuad.contribution_to_state(0) == CellState.DEAD

    def test_one_two_contributions_green1(self):
        """1-2 contributions → GREEN_1."""
        assert ColorQuad.contribution_to_state(1) == CellState.GREEN_1
        assert ColorQuad.contribution_to_state(2) == CellState.GREEN_1

    def test_three_four_contributions_green2(self):
        """3-4 contributions → GREEN_2."""
        assert ColorQuad.contribution_to_state(3) == CellState.GREEN_2
        assert ColorQuad.contribution_to_state(4) == CellState.GREEN_2

    def test_five_to_seven_contributions_green3(self):
        """5-7 contributions → GREEN_3."""
        assert ColorQuad.contribution_to_state(5) == CellState.GREEN_3
        assert ColorQuad.contribution_to_state(6) == CellState.GREEN_3
        assert ColorQuad.contribution_to_state(7) == CellState.GREEN_3

    def test_eight_plus_contributions_green4(self):
        """8+ contributions → GREEN_4."""
        assert ColorQuad.contribution_to_state(8) == CellState.GREEN_4
        assert ColorQuad.contribution_to_state(100) == CellState.GREEN_4

    def test_contribution_mapping_rejects_negative(self):
        """contribution_to_state() rejects negative values."""
        with pytest.raises(ValueError, match="must be >= 0"):
            ColorQuad.contribution_to_state(-1)

    def test_contribution_mapping_rejects_non_int(self):
        """contribution_to_state() rejects non-integer."""
        with pytest.raises(TypeError):
            ColorQuad.contribution_to_state("5")
        with pytest.raises(TypeError):
            ColorQuad.contribution_to_state(5.5)
        with pytest.raises(TypeError):
            ColorQuad.contribution_to_state(None)


class TestColorGradient:
    """Test color gradient properties."""

    def test_colors_are_increasing_intensity(self):
        """Colors increase in intensity from DEAD to GREEN_4."""
        colors = [
            ColorQuad.get_color(CellState.DEAD),
            ColorQuad.get_color(CellState.GREEN_1),
            ColorQuad.get_color(CellState.GREEN_2),
            ColorQuad.get_color(CellState.GREEN_3),
            ColorQuad.get_color(CellState.GREEN_4),
        ]

        # All colors should be tuples of 3 integers
        for color in colors:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(isinstance(c, int) for c in color)
            assert all(0 <= c <= 255 for c in color)

    def test_github_palette_mapping(self):
        """Verify mapping matches GitHub's actual colors."""
        # These are GitHub's actual contribution colors
        expected = {
            CellState.DEAD: (235, 237, 240),  # #ebedf0
            CellState.GREEN_1: (198, 228, 139),  # #c6e48b
            CellState.GREEN_2: (126, 231, 135),  # #7ee787
            CellState.GREEN_3: (38, 166, 65),  # #26a641
            CellState.GREEN_4: (0, 109, 50),  # #006d32
        }

        for state, expected_color in expected.items():
            assert ColorQuad.get_color(state) == expected_color
