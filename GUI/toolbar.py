from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon

class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.canvas = None
        self.plot_canvas = None

        # Add Block Action
        self.add_block_action = QAction(QIcon(None), "Add Block", self)
        self.add_block_action.triggered.connect(self.add_block)
        self.addAction(self.add_block_action)

        # Run Simulation Action
        self.run_simulation_action = QAction(QIcon(None), "Run Simulation", self)
        self.run_simulation_action.triggered.connect(self.run_simulation)
        self.addAction(self.run_simulation_action)

    def set_canvas(self, canvas):
        """Connect the toolbar to the diagram canvas."""
        self.canvas = canvas

    def set_plot_canvas(self, plot_canvas):
        """Connect the toolbar to the plot canvas."""
        self.plot_canvas = plot_canvas

    def add_block(self):
        """Add a block to the diagram canvas."""
        if self.canvas:
            print("Adding a block to the canvas...")
            # Add the block at a fixed position (customize as needed)
            self.canvas.add_block(name="New Block", x=100, y=100)

    def run_simulation(self):
        """Run the simulation and display results."""
        if self.plot_canvas:
            import numpy as np
            # Generate some placeholder data
            t = np.linspace(0, 5, 500)
            y = np.sin(2 * np.pi * t)
            print("Running simulation...")
            self.plot_canvas.plot(t, y)
