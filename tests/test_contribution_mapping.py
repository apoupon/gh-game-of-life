"""Tests for Contribution-to-Grid Mapping."""

import pytest

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.grid import Grid
from gh_game_of_life.github_client import GitHubClient


class TestContributionMapping:
    """Test contribution count to cell state mapping."""

    def test_zero_contribution_is_dead(self):
        """Contribution count of 0 maps to DEAD cell."""
        client = GitHubClient()
        contributions = [[0] * 53 for _ in range(7)]

        grid = client.to_quad_grid(contributions)

        # All cells should be DEAD
        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.DEAD

    def test_one_contribution_is_green1(self):
        """Contribution count of 1 maps to GREEN_1 cell."""
        client = GitHubClient()
        contributions = [[1] * 53 for _ in range(7)]

        grid = client.to_quad_grid(contributions)

        # All cells should be GREEN_1
        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.GREEN_1

    def test_large_contribution_is_green4(self):
        """Large contribution counts map to GREEN_4 cell."""
        client = GitHubClient()
        contributions = [[100] * 53 for _ in range(7)]

        grid = client.to_quad_grid(contributions)

        # All cells should be GREEN_4
        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.GREEN_4

    def test_mixed_contributions_mapped_correctly(self):
        """Mixed contribution counts mapped to correct cell states."""
        client = GitHubClient()
        # Create pattern: odd columns get contribution 1, even columns get 0
        contributions = [[1 if i % 2 == 1 else 0 for i in range(53)] for _ in range(7)]

        grid = client.to_quad_grid(contributions)

        # Check mapping: odd columns (1, 3, 5, ...) should be GREEN_1 (contribution=1)
        for row in range(7):
            for col in range(53):
                if col % 2 == 1:  # Odd columns have contribution 1
                    assert grid.get_cell(row, col) == CellState.GREEN_1
                else:  # Even columns have contribution 0
                    assert grid.get_cell(row, col) == CellState.DEAD


class TestGridInvariant:
    """Test that output grid maintains 53×7 invariant."""

    def test_output_grid_is_53_by_7(self):
        """Output grid is exactly 53 columns × 7 rows."""
        client = GitHubClient()

        # Test with various contribution patterns
        for test_pattern in [
            [[0] * 53 for _ in range(7)],
            [[1] * 53 for _ in range(7)],
            [[i for i in range(53)] for _ in range(7)],
        ]:
            grid = client.to_quad_grid(test_pattern)

            # Verify dimensions
            assert grid.ROWS == 7
            assert grid.COLS == 53

            # Verify all cells are accessible
            for row in range(7):
                for col in range(53):
                    grid.get_cell(row, col)  # Should not raise

    def test_rejects_wrong_row_count(self):
        """Rejects contributions with wrong number of rows."""
        client = GitHubClient()

        # 8 rows instead of 7
        contributions = [[0] * 53 for _ in range(8)]

        with pytest.raises(ValueError, match="must have 7 rows"):
            client.to_quad_grid(contributions)

    def test_rejects_wrong_col_count(self):
        """Rejects contributions with wrong number of columns."""
        client = GitHubClient()

        # 54 columns instead of 53
        contributions = [[0] * 54 for _ in range(7)]

        with pytest.raises(ValueError, match="must have 53 columns"):
            client.to_quad_grid(contributions)

    def test_rejects_variable_col_count(self):
        """Rejects contributions with variable column counts per row."""
        client = GitHubClient()

        contributions = [[0] * 53 for _ in range(7)]
        contributions[3] = [0] * 50  # One row with fewer columns

        with pytest.raises(ValueError, match="must have 53 columns"):
            client.to_quad_grid(contributions)


class TestMappingLogic:
    """Test the specific mapping logic: contribution > 0 → alive, == 0 → dead."""

    def test_mapping_rule_greater_than_zero_is_alive(self):
        """Mapping rule: contribution > 0 → alive (various CellState levels)."""
        client = GitHubClient()

        # Test that all contributions > 0 map to some GREEN state, not DEAD
        test_cases = [
            (1, CellState.GREEN_1),
            (2, CellState.GREEN_1),
            (3, CellState.GREEN_2),
            (5, CellState.GREEN_3),
            (8, CellState.GREEN_4),
            (100, CellState.GREEN_4),
        ]

        for value, expected_state in test_cases:
            contributions = [[value] * 53 for _ in range(7)]
            grid = client.to_quad_grid(contributions)

            # All cells should map to expected state
            for row in range(7):
                for col in range(53):
                    assert grid.get_cell(row, col) == expected_state, (
                        f"Contribution {value} should map to {expected_state}"
                    )

    def test_mapping_rule_zero_is_dead(self):
        """Mapping rule: contribution == 0 → dead."""
        client = GitHubClient()

        contributions = [[0] * 53 for _ in range(7)]
        grid = client.to_quad_grid(contributions)

        # All cells should be dead
        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.DEAD, (
                    "Contribution 0 should map to dead"
                )

    def test_mapping_uses_cellstate_values(self):
        """Mapping produces CellState values according to contribution thresholds."""
        client = GitHubClient()

        # Test with various contribution levels mapped to different states
        test_cases = [
            (0, CellState.DEAD),
            (1, CellState.GREEN_1),
            (2, CellState.GREEN_1),
            (3, CellState.GREEN_2),
            (5, CellState.GREEN_3),
            (8, CellState.GREEN_4),
            (100, CellState.GREEN_4),
        ]
        for test_value, expected_state in test_cases:
            contributions = [[test_value] * 53 for _ in range(7)]
            grid = client.to_quad_grid(contributions)

            for row in range(7):
                for col in range(53):
                    cell_state = grid.get_cell(row, col)
                    # Should be CellState, not numeric
                    assert isinstance(cell_state, CellState)
                    # Should match expected mapping
                    assert cell_state == expected_state, (
                        f"Contribution {test_value} should map to {expected_state}"
                    )


class TestEdgeCases:
    """Test edge cases in contribution mapping."""

    def test_single_cell_alive(self):
        """Single alive cell in contribution grid."""
        client = GitHubClient()
        contributions = [[0] * 53 for _ in range(7)]
        contributions[3][26] = 1  # Single contribution

        grid = client.to_quad_grid(contributions)

        assert grid.get_cell(3, 26) == CellState.GREEN_1
        # All other cells should be dead
        for row in range(7):
            for col in range(53):
                if row == 3 and col == 26:
                    continue
                assert grid.get_cell(row, col) == CellState.DEAD

    def test_corner_contributions(self):
        """Contributions at grid corners map correctly."""
        client = GitHubClient()
        contributions = [[0] * 53 for _ in range(7)]
        contributions[0][0] = 1  # Top-left -> GREEN_1
        contributions[0][52] = 2  # Top-right -> GREEN_1
        contributions[6][0] = 3  # Bottom-left -> GREEN_2
        contributions[6][52] = 8  # Bottom-right -> GREEN_4

        grid = client.to_quad_grid(contributions)

        # Check corners map correctly
        assert grid.get_cell(0, 0) == CellState.GREEN_1
        assert grid.get_cell(0, 52) == CellState.GREEN_1
        assert grid.get_cell(6, 0) == CellState.GREEN_2
        assert grid.get_cell(6, 52) == CellState.GREEN_4

    def test_boundary_between_dead_and_alive(self):
        """Test boundary between dead (0) and alive (1+)."""
        client = GitHubClient()

        # Create checkerboard pattern: 0 and 1
        contributions = [[(i + j) % 2 for j in range(53)] for i in range(7)]

        grid = client.to_quad_grid(contributions)

        for row in range(7):
            for col in range(53):
                if (row + col) % 2 == 1:  # Contribution = 1 -> GREEN_1
                    assert grid.get_cell(row, col) == CellState.GREEN_1
                else:  # Contribution = 0 -> DEAD
                    assert grid.get_cell(row, col) == CellState.DEAD


class TestNormalization:
    """Test that mapping normalizes different contribution scales."""

    def test_normalizes_high_contributions_to_alive(self):
        """High contribution counts normalize to GREEN states, not DEAD."""
        client = GitHubClient()

        # GitHub's max contribution in a day is typically hundreds
        max_contributions = [[300] * 53 for _ in range(7)]
        low_contributions = [[1] * 53 for _ in range(7)]

        grid_max = client.to_quad_grid(max_contributions)
        grid_low = client.to_quad_grid(low_contributions)

        # Both should produce all GREEN states (no DEAD cells)
        for row in range(7):
            for col in range(53):
                max_state = grid_max.get_cell(row, col)
                low_state = grid_low.get_cell(row, col)
                # Both should be GREEN (not DEAD)
                assert max_state != CellState.DEAD
                assert low_state != CellState.DEAD
                # Max should be higher green level than low
                assert max_state.value > low_state.value

    def test_preserves_temporal_patterns(self):
        """Mapping preserves temporal patterns in data."""
        client = GitHubClient()

        # Create a pattern: weekday contributions, weekend off
        contributions = [[0] * 53 for _ in range(7)]
        for col in range(53):  # For each week
            for row in range(7):  # For each day
                # Mon-Fri (0-4): contributions, Sat-Sun (5-6): no contributions
                contributions[row][col] = 1 if row < 5 else 0

        grid = client.to_quad_grid(contributions)

        # Verify pattern: Mon-Fri alive, Sat-Sun dead
        for row in range(7):
            for col in range(53):
                if row < 5:  # Mon-Fri
                    assert grid.get_cell(row, col) == CellState.GREEN_1
                else:  # Sat-Sun
                    assert grid.get_cell(row, col) == CellState.DEAD


class TestIntegrationWithFetch:
    """Test contribution mapping in context of fetching flow."""

    def test_fetch_result_maps_correctly(self):
        """Mapping works on data from fetch_contributions."""
        client = GitHubClient()

        # Create mock contribution data in the format that fetch_contributions returns
        contributions = [
            [0, 0, 1, 2, 0, 1, 0, 0] + [0] * 45,  # Row 0
            [1, 0, 0, 3, 1, 0, 1, 0] + [1] * 45,  # Row 1
            [0, 0, 0, 0, 0, 0, 0, 0] + [0] * 45,  # Row 2
            [2, 1, 1, 1, 1, 1, 1, 2] + [1] * 45,  # Row 3
            [0, 0, 0, 0, 0, 0, 0, 0] + [0] * 45,  # Row 4
            [1, 1, 1, 1, 1, 1, 1, 1] + [1] * 45,  # Row 5
            [0, 0, 0, 0, 0, 0, 0, 0] + [0] * 45,  # Row 6
        ]

        grid = client.to_quad_grid(contributions)

        # Verify specific mappings
        assert grid.get_cell(0, 2) == CellState.GREEN_1  # 1 -> alive
        assert grid.get_cell(0, 0) == CellState.DEAD  # 0 -> dead
        assert grid.get_cell(3, 0) == CellState.GREEN_1  # 2 -> alive
        assert grid.get_cell(4, 0) == CellState.DEAD  # 0 -> dead


class TestAcceptanceCriteria:
    """Verify FR-203 acceptance criteria."""

    def test_contribution_greater_than_zero_to_alive(self):
        """Acceptance: Contribution > 0 → alive (various GREEN levels)"""
        client = GitHubClient()

        test_cases = [
            (1, CellState.GREEN_1),
            (2, CellState.GREEN_1),
            (3, CellState.GREEN_2),
            (5, CellState.GREEN_3),
            (10, CellState.GREEN_4),
            (999, CellState.GREEN_4),
        ]

        for contribution_value, expected_state in test_cases:
            contributions = [[contribution_value] * 53 for _ in range(7)]
            grid = client.to_quad_grid(contributions)

            for row in range(7):
                for col in range(53):
                    assert grid.get_cell(row, col) == expected_state

    def test_contribution_zero_to_dead(self):
        """Acceptance: Contribution == 0 → dead"""
        client = GitHubClient()

        contributions = [[0] * 53 for _ in range(7)]
        grid = client.to_quad_grid(contributions)

        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.DEAD

    def test_output_grid_matches_invariant(self):
        """Acceptance: Output grid matches 53 × 7 invariant"""
        client = GitHubClient()

        # Test with various input patterns
        test_patterns = [
            [[0] * 53 for _ in range(7)],
            [[1] * 53 for _ in range(7)],
            [[i % 5 for i in range(53)] for _ in range(7)],
        ]

        for contributions in test_patterns:
            grid = client.to_quad_grid(contributions)

            # Must be Grid instance
            assert isinstance(grid, Grid)

            # Must have correct dimensions
            assert grid.ROWS == 7
            assert grid.COLS == 53

            # All cells must be accessible and be CellState
            for row in range(7):
                for col in range(53):
                    cell = grid.get_cell(row, col)
                    assert isinstance(cell, CellState)


class TestTypeSafety:
    """Test type safety of mapping."""

    def test_requires_list_of_lists(self):
        """Mapping requires 2D list input."""
        client = GitHubClient()

        # Single list instead of 2D
        with pytest.raises((TypeError, ValueError)):
            client.to_quad_grid([1, 2, 3])

    def test_handles_integer_contributions(self):
        """Accepts integer contribution values."""
        client = GitHubClient()

        contributions = [[int(i) for i in range(53)] for _ in range(7)]
        grid = client.to_quad_grid(contributions)

        assert isinstance(grid, Grid)

    def test_returns_grid_instance(self):
        """Mapping returns Grid instance, not plain list."""
        client = GitHubClient()

        contributions = [[0] * 53 for _ in range(7)]
        result = client.to_quad_grid(contributions)

        assert isinstance(result, Grid)
        assert not isinstance(result, list)
