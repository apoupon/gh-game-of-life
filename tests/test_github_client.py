"""Tests for GitHub Contribution Fetching."""

from unittest.mock import Mock, patch

import pytest

from gh_game_of_life.core.cell_state import CellState
from gh_game_of_life.core.grid import Grid
from gh_game_of_life.github_client import GitHubClient


class TestGitHubClientInitialization:
    """Test GitHubClient initialization."""

    def test_client_initialization_without_token(self):
        """GitHubClient initializes without token."""
        import os

        # Temporarily remove GITHUB_TOKEN from environment to test fallback
        original_token = os.environ.pop("GITHUB_TOKEN", None)
        try:
            client = GitHubClient()
            assert client.token is None
        finally:
            if original_token is not None:
                os.environ["GITHUB_TOKEN"] = original_token

    def test_client_initialization_with_token(self):
        """GitHubClient accepts optional token."""
        token = "ghp_test_token_12345"
        client = GitHubClient(token=token)
        assert client.token == token

    def test_rejects_non_string_token(self):
        """GitHubClient rejects non-string token."""
        with pytest.raises(TypeError, match="must be str or None"):
            GitHubClient(token=12345)

    def test_rejects_non_string_token_dict(self):
        """GitHubClient rejects dict as token."""
        with pytest.raises(TypeError):
            GitHubClient(token={"key": "value"})


class TestUsernameValidation:
    """Test username validation."""

    def test_fetch_contributions_accepts_valid_username(self):
        """Valid usernames are accepted."""
        client = GitHubClient()

        # Mock the API call
        with patch.object(client, "_fetch_from_github") as mock_fetch:
            mock_fetch.return_value = {
                "data": {
                    "user": {
                        "contributionsCollection": {
                            "contributionCalendar": {"weeks": []}
                        }
                    }
                }
            }

            # Should accept valid usernames
            for username in [
                "torvalds",
                "gvanrossum",
                "octocat",
                "test-user",
                "test_user",
            ]:
                result = client.fetch_contributions(username)
                assert result is not None

    def test_rejects_empty_username(self):
        """Empty username is rejected."""
        client = GitHubClient()
        with pytest.raises(ValueError, match="cannot be empty"):
            client.fetch_contributions("")

    def test_rejects_whitespace_only_username(self):
        """Whitespace-only username is rejected."""
        client = GitHubClient()
        with pytest.raises(ValueError, match="cannot be empty"):
            client.fetch_contributions("   ")

    def test_rejects_non_string_username(self):
        """Non-string username is rejected."""
        client = GitHubClient()
        with pytest.raises(TypeError, match="username must be str"):
            client.fetch_contributions(12345)

    def test_rejects_username_with_invalid_characters(self):
        """Username with invalid characters is rejected."""
        client = GitHubClient()
        invalid_usernames = [
            "user@name",
            "user name",
            "user.name",
            "user/name",
            "user\\name",
            "user:name",
        ]
        for username in invalid_usernames:
            with pytest.raises(ValueError, match="Invalid username"):
                client.fetch_contributions(username)

    def test_username_stripped_of_whitespace(self):
        """Username is stripped of leading/trailing whitespace."""
        client = GitHubClient()

        with patch.object(client, "_fetch_from_github") as mock_fetch:
            mock_fetch.return_value = {
                "data": {
                    "user": {
                        "contributionsCollection": {
                            "contributionCalendar": {"weeks": []}
                        }
                    }
                }
            }

            # Should accept and strip whitespace
            result = client.fetch_contributions("  octocat  ")
            assert result is not None
            # Check that stripped username was passed
            mock_fetch.assert_called_once_with("octocat")


class TestApiMocking:
    """Test API calls with mocked responses."""

    def test_fetch_uses_graphql_api(self):
        """Fetch uses GitHub GraphQL API endpoint."""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "user": {
                        "contributionsCollection": {
                            "contributionCalendar": {"weeks": []}
                        }
                    }
                }
            }
            mock_post.return_value = mock_response

            client.fetch_contributions("test-user")

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "api.github.com/graphql" in call_args[0][0]

    def test_fetch_includes_token_in_header(self):
        """Fetch includes token in Authorization header."""
        token = "ghp_test_12345"
        client = GitHubClient(token=token)

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "user": {
                        "contributionsCollection": {
                            "contributionCalendar": {"weeks": []}
                        }
                    }
                }
            }
            mock_post.return_value = mock_response

            client.fetch_contributions("test-user")

            # Check Authorization header
            call_kwargs = mock_post.call_args[1]
            assert "Authorization" in call_kwargs["headers"]
            assert f"Bearer {token}" == call_kwargs["headers"]["Authorization"]

    def test_handles_api_timeout(self):
        """Handles API request timeout gracefully."""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            import requests

            mock_post.side_effect = requests.exceptions.Timeout()

            with pytest.raises(IOError, match="timed out"):
                client.fetch_contributions("test-user")

    def test_handles_api_connection_error(self):
        """Handles API connection error gracefully."""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            import requests

            mock_post.side_effect = requests.exceptions.ConnectionError(
                "Connection failed"
            )

            with pytest.raises(IOError, match="API request failed"):
                client.fetch_contributions("test-user")

    def test_handles_user_not_found(self):
        """Handles GitHub user not found."""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "errors": [
                    {
                        "message": "Could not resolve to a User with the login of 'nonexistent-user'."
                    }
                ]
            }
            mock_post.return_value = mock_response

            with pytest.raises(ValueError, match="not found"):
                client.fetch_contributions("nonexistent-user")

    def test_handles_null_user_response(self):
        """Handles null user in response."""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"data": {"user": None}}
            mock_post.return_value = mock_response

            with pytest.raises(ValueError, match="not found"):
                client.fetch_contributions("test-user")

    def test_handles_graphql_error(self):
        """Handles GraphQL API errors."""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"errors": [{"message": "Invalid query"}]}
            mock_post.return_value = mock_response

            with pytest.raises(IOError, match="API error"):
                client.fetch_contributions("test-user")


class TestContributionDataParsing:
    """Test parsing contribution data from GitHub response."""

    def test_convert_to_grid_empty_weeks(self):
        """Convert handles empty weeks list."""
        client = GitHubClient()
        github_data = {
            "data": {
                "user": {
                    "contributionsCollection": {"contributionCalendar": {"weeks": []}}
                }
            }
        }

        grid = client._convert_to_grid(github_data)
        assert len(grid) == 7
        assert all(len(row) == 53 for row in grid)
        assert all(all(count == 0 for count in row) for row in grid)

    def test_convert_to_grid_with_data(self):
        """Convert parses contribution data correctly."""
        client = GitHubClient()

        # Create mock weeks with some contribution data
        weeks = []
        for week_idx in range(2):  # Just 2 weeks for testing
            week = {
                "contributionDays": [
                    {
                        "contributionCount": (week_idx + 1) * (day_idx + 1),
                        "date": f"2024-01-{day_idx + 1}",
                    }
                    for day_idx in range(7)
                ]
            }
            weeks.append(week)

        github_data = {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {"weeks": weeks}
                    }
                }
            }
        }

        grid = client._convert_to_grid(github_data)

        # Verify dimensions
        assert len(grid) == 7
        assert all(len(row) == 53 for row in grid)

        # Verify data was parsed
        assert grid[0][0] == 1  # Week 0, Day 0
        assert grid[6][0] == 7  # Week 0, Day 6
        assert grid[0][1] == 2  # Week 1, Day 0

    def test_convert_to_grid_handles_malformed_data(self):
        """Convert handles malformed contribution data gracefully."""
        client = GitHubClient()

        github_data = {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "weeks": [
                                {"contributionDays": [{"contributionCount": 5}] * 7},
                                {"contributionDays": None},  # Malformed
                                {
                                    "contributionDays": [
                                        {"contributionCount": "invalid"}
                                    ]
                                },  # Invalid type
                            ]
                        }
                    }
                }
            }
        }

        grid = client._convert_to_grid(github_data)
        # Should not raise, just skip malformed entries
        assert len(grid) == 7


class TestQuadGridConversion:
    """Test conversion of contribution counts to Quad-Life grid."""

    def test_to_quad_grid_all_zeros(self):
        """All-zero contributions become DEAD cells."""
        client = GitHubClient()
        contributions = [[0] * 53 for _ in range(7)]

        grid = client.to_quad_grid(contributions)

        assert isinstance(grid, Grid)
        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.DEAD

    def test_to_quad_grid_contribution_mapping(self):
        """Contribution counts map to correct CellState values."""
        client = GitHubClient()
        # Test all mapping thresholds: 0->DEAD, 1-2->GREEN_1, 3-4->GREEN_2, 5-7->GREEN_3, 8+->GREEN_4
        contributions = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8] + [0] * 44,
            [0] * 53,
            [0] * 53,
            [0] * 53,
            [0] * 53,
            [0] * 53,
            [0] * 53,
        ]

        grid = client.to_quad_grid(contributions)

        assert isinstance(grid, Grid)
        # Check first row mappings
        assert grid.get_cell(0, 0) == CellState.DEAD  # 0 -> DEAD
        assert grid.get_cell(0, 1) == CellState.GREEN_1  # 1 -> GREEN_1
        assert grid.get_cell(0, 2) == CellState.GREEN_1  # 2 -> GREEN_1
        assert grid.get_cell(0, 3) == CellState.GREEN_2  # 3 -> GREEN_2
        assert grid.get_cell(0, 4) == CellState.GREEN_2  # 4 -> GREEN_2
        assert grid.get_cell(0, 5) == CellState.GREEN_3  # 5 -> GREEN_3
        assert grid.get_cell(0, 6) == CellState.GREEN_3  # 6 -> GREEN_3
        assert grid.get_cell(0, 7) == CellState.GREEN_3  # 7 -> GREEN_3
        assert grid.get_cell(0, 8) == CellState.GREEN_4  # 8 -> GREEN_4

    def test_to_quad_grid_high_contributions(self):
        """High contributions map to GREEN_4."""
        client = GitHubClient()
        contributions = [[20] * 53 for _ in range(7)]

        grid = client.to_quad_grid(contributions)

        for row in range(7):
            for col in range(53):
                assert grid.get_cell(row, col) == CellState.GREEN_4

    def test_to_quad_grid_rejects_wrong_rows(self):
        """Rejects contribution grid with wrong number of rows."""
        client = GitHubClient()

        with pytest.raises(ValueError, match="must have 7 rows"):
            client.to_quad_grid([[0] * 53 for _ in range(8)])

    def test_to_quad_grid_rejects_wrong_cols(self):
        """Rejects contribution grid with wrong number of columns."""
        client = GitHubClient()

        with pytest.raises(ValueError, match="must have 53 columns"):
            client.to_quad_grid([[0] * 54 for _ in range(7)])


class TestFetchAndConvert:
    """Test full fetch and conversion pipeline."""

    def test_fetch_and_convert_returns_grid(self):
        """fetch_and_convert returns a Grid."""
        client = GitHubClient()

        with patch.object(client, "fetch_contributions") as mock_fetch:
            mock_fetch.return_value = [[0] * 53 for _ in range(7)]

            result = client.fetch_and_convert("test-user")

            assert isinstance(result, Grid)

    def test_fetch_and_convert_propagates_errors(self):
        """fetch_and_convert propagates errors from fetch."""
        client = GitHubClient()

        with patch.object(client, "fetch_contributions") as mock_fetch:
            mock_fetch.side_effect = ValueError("User not found")

            with pytest.raises(ValueError, match="not found"):
                client.fetch_and_convert("nonexistent-user")


class TestAcceptanceCriteria:
    """Verify FR-201 acceptance criteria."""

    def test_uses_github_graphql_api(self):
        """Acceptance: Uses GitHub GraphQL API"""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "user": {
                        "contributionsCollection": {
                            "contributionCalendar": {"weeks": []}
                        }
                    }
                }
            }
            mock_post.return_value = mock_response

            client.fetch_contributions("test-user")

            # Verify GraphQL endpoint is used
            assert mock_post.called
            call_url = mock_post.call_args[0][0]
            assert "graphql" in call_url

    def test_supports_username_input(self):
        """Acceptance: Supports username input"""
        client = GitHubClient()

        with patch.object(client, "_fetch_from_github") as mock_fetch:
            mock_fetch.return_value = {
                "data": {
                    "user": {
                        "contributionsCollection": {
                            "contributionCalendar": {"weeks": []}
                        }
                    }
                }
            }

            # Should accept username input
            result = client.fetch_contributions("torvalds")
            assert result is not None

    def test_handles_invalid_users_gracefully(self):
        """Acceptance: Handles missing or invalid users gracefully"""
        client = GitHubClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "errors": [{"message": "Could not resolve to a User"}]
            }
            mock_post.return_value = mock_response

            # Should raise clear error, not crash
            with pytest.raises(ValueError) as exc_info:
                client.fetch_contributions("invalid-user-xyz-12345")

            assert "not found" in str(exc_info.value).lower()
