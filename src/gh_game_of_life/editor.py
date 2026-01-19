import ipywidgets as widgets
from IPython.display import clear_output, display

# Your specific GitHub Palette
HEX_COLORS = {0: "#EFF2F5", 1: "#aceebb", 2: "#4ac26b", 3: "#2ea44e", 4: "#126329"}


class QuadLifeGridEditor:
    def __init__(self):
        self.rows, self.cols = 7, 53
        # Initialize internal state as a 7x53 matrix of 0s
        self.state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # 1. Create the buttons
        grid_items = []
        for r in range(self.rows):
            for c in range(self.cols):
                btn = widgets.Button(
                    description="",
                    layout=widgets.Layout(width="12px", height="12px", margin="0px"),
                    style={"button_color": HEX_COLORS[0]},
                )
                btn.indices = (r, c)
                btn.on_click(self.on_cell_click)
                grid_items.append(btn)

        # 2. Setup the Grid with the requested column/row padding
        self.grid = widgets.GridBox(
            grid_items,
            layout=widgets.Layout(
                grid_template_columns=f"repeat({self.cols}, 12px)",
                grid_gap="3px",  # Margin between cells
                width="max-content",
            ),
        )

        # 3. Output UI
        self.gen_button = widgets.Button(
            description="Generate Grid Data",
            button_style="success",
            layout=widgets.Layout(margin="20px 0 0 0"),
        )
        self.gen_button.on_click(self.display_values)
        self.output = widgets.Output()

    def on_cell_click(self, b):
        r, c = b.indices
        # Cycle state 0-4
        self.state[r][c] = (self.state[r][c] + 1) % 5
        b.style.button_color = HEX_COLORS[self.state[r][c]]

    def get_values(self) -> list[list[int]]:
        """Returns the full 7x53 matrix of integers."""
        return self.state

    def display_values(self, b):
        """Prints the 2D list in a format ready for from_color_values."""
        with self.output:
            clear_output()
            values = self.get_values()
            print("my_grid = [")
            for row in values:
                # Print each row on a new line for readability
                print(f"    {row},")
            print("]")
            print("\nYou can copy-paste this in the cell below !")

    def show(self):
        display(
            widgets.HTML("<h3>Quad-Life Grid Designer</h3>"),
            self.grid,
            self.gen_button,
            self.output,
        )
