class GameEngine:
    """
    A simple implementation of Conway's Game of Life engine.
    """
    def __init__(self, initial_grid):
        self.grid = initial_grid
        self.rows = len(initial_grid)
        self.cols = len(initial_grid[0])
        self.history = []

    def get_neighbors(self, r, c):
        """
        Count the number of live neighbors for a cell at position (r, c).
        """
        pass

    def step(self):
        """
        Advance the game by one generation.
        """
        pass

    def is_stable(self):
        """
        Check if the current grid is stable (no changes from previous state).
        """
        pass