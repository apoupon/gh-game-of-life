"""GitHub contribution data fetching and grid conversion.

Provides client for fetching GitHub contribution data via GraphQL API
and converting to binary grid representation.
"""

import os
from typing import Optional

from dotenv import load_dotenv

from gh_game_of_life.core.cell_state import ColorQuad
from gh_game_of_life.core.grid import Grid

# Load environment variables from .env file
load_dotenv()


class GitHubClient:
    """Client for fetching GitHub contribution data.

    Uses GitHub GraphQL API to fetch contribution data for a user
    and converts to Quad-Life grid (53 columns × 7 rows).
    """

    GITHUB_API_URL = "https://api.github.com/graphql"

    # GraphQL query to fetch contribution data
    # Returns the last year of contribution calendar data
    CONTRIBUTION_QUERY = """
    query($userName:String!) {
        user(login: $userName) {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            contributionCount
                            date
                        }
                    }
                }
            }
        }
    }
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize GitHub client.

        Args:
            token: GitHub authentication token. If None, will attempt to read from
                   GITHUB_TOKEN environment variable. If still None, client will
                   work in unauthenticated mode (lower rate limits).

        Raises:
            TypeError: If token is not str or None.
        """
        if token is not None and not isinstance(token, str):
            raise TypeError(f"token must be str or None, got {type(token).__name__}")

        # Use provided token, or read from environment variable
        if token is None:
            token = os.environ.get("GITHUB_TOKEN")

        self.token = token

    def fetch_contributions(self, username: str) -> list[list[int]]:
        """Fetch contribution data for a GitHub user.

        Args:
            username: GitHub username to fetch data for.

        Returns:
            2D list of contribution counts (53 × 7), where:
            - Rows represent days of week (Monday-Sunday)
            - Columns represent weeks (current week backwards to 1 year ago)
            - Values are contribution counts for that day

        Raises:
            ValueError: If username is invalid or missing.
            TypeError: If username is not a string.
            IOError: If unable to reach GitHub API or request fails.
        """
        if not isinstance(username, str):
            raise TypeError(f"username must be str, got {type(username).__name__}")

        if not username or not username.strip():
            raise ValueError("username cannot be empty")

        username = username.strip()

        # Validate username format (alphanumeric, hyphens, underscores only)
        if not all(c.isalnum() or c in "-_" for c in username):
            raise ValueError(
                f"Invalid username '{username}': "
                "must contain only alphanumeric characters, hyphens, and underscores"
            )

        # Fetch from GitHub GraphQL API
        contribution_data = self._fetch_from_github(username)

        # Convert to grid format
        grid_data = self._convert_to_grid(contribution_data)

        return grid_data

    def _fetch_from_github(self, username: str) -> dict:
        """Fetch contribution data from GitHub GraphQL API.

        Args:
            username: GitHub username.

        Returns:
            Raw contribution data from GitHub.

        Raises:
            IOError: If API request fails.
            ValueError: If user not found or data invalid.
        """
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests library required for GitHub API calls. "
                "Install with: uv add requests"
            )

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        variables = {"userName": username}
        payload = {
            "query": self.CONTRIBUTION_QUERY,
            "variables": variables,
        }

        try:
            response = requests.post(
                self.GITHUB_API_URL,
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise IOError(f"GitHub API request timed out for user '{username}'")
        except requests.exceptions.RequestException as e:
            raise IOError(f"GitHub API request failed: {e}") from e

        data = response.json()

        # Check for GraphQL errors
        if "errors" in data:
            errors = data["errors"]
            error_msg = (
                errors[0].get("message", "Unknown error") if errors else "Unknown error"
            )

            if (
                "not found" in error_msg.lower()
                or "could not resolve" in error_msg.lower()
            ):
                raise ValueError(f"GitHub user '{username}' not found")

            raise IOError(f"GitHub API error: {error_msg}")

        # Check if user exists
        if not data.get("data", {}).get("user"):
            raise ValueError(f"GitHub user '{username}' not found")

        return data

    def _convert_to_grid(self, github_data: dict) -> list[list[int]]:
        """Convert GitHub contribution data to 53×7 grid.

        Args:
            github_data: Raw data from GitHub GraphQL API.

        Returns:
            2D list of contribution counts (7 rows × 53 columns).

        Raises:
            ValueError: If data format is invalid.
        """
        try:
            weeks = github_data["data"]["user"]["contributionsCollection"][
                "contributionCalendar"
            ]["weeks"]
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid GitHub response format: {e}") from e

        # Initialize 7×53 grid
        grid = [[0] * 53 for _ in range(7)]

        # Parse weeks (max 53 weeks in a year)
        for week_idx, week in enumerate(weeks):
            if week_idx >= 53:
                break

            try:
                days = week.get("contributionDays", [])
                for day_idx, day in enumerate(days):
                    if day_idx >= 7:  # 7 days per week
                        break

                    count = day.get("contributionCount", 0)
                    if not isinstance(count, int) or count < 0:
                        count = 0

                    grid[day_idx][week_idx] = count
            except (KeyError, TypeError, AttributeError):
                # Skip malformed entries
                continue

        return grid

    def to_quad_grid(self, contributions: list[list[int]]) -> Grid:
        """Convert contribution counts to Quad-Life grid.

        Uses GitHub contribution count thresholds to map to CellState values:
        - 0 contributions → DEAD
        - 1-2 contributions → GREEN_1
        - 3-4 contributions → GREEN_2
        - 5-7 contributions → GREEN_3
        - 8+ contributions → GREEN_4

        Args:
            contributions: 2D list of contribution counts.

        Returns:
            Grid with CellState values.

        Raises:
            ValueError: If contributions is wrong dimensions or invalid.
        """
        if len(contributions) != 7:
            raise ValueError(
                f"Contributions must have 7 rows, got {len(contributions)}"
            )

        quad_cells = []
        for row in contributions:
            if len(row) != 53:
                raise ValueError(f"Each row must have 53 columns, got {len(row)}")
            quad_row = [ColorQuad.contribution_to_state(count) for count in row]
            quad_cells.append(quad_row)

        return Grid(quad_cells)

    def fetch_and_convert(self, username: str) -> Grid:
        """Fetch GitHub contributions and convert to Quad-Life grid.

        Convenience method combining fetch + conversion.

        Args:
            username: GitHub username.

        Returns:
            Quad-Life Grid ready for simulation.

        Raises:
            ValueError: If username invalid or user not found.
            IOError: If unable to fetch data.
        """
        contributions = self.fetch_contributions(username)
        return self.to_quad_grid(contributions)
