from PyQt5.QtWidgets import QToolBar, QAction, QComboBox, QLabel
from PyQt5.QtGui import QIcon

class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.canvas = None
        self.plot_canvas = None

        # Add Block Type Selector
        self.block_type_label = QLabel("Block Type:")
        self.block_type_selector = QComboBox()
        self.block_type_selector.addItems(["STEP", "GAIN", "SUM", "SCOPE", "RAMP", "WAVEFORM", "CONSTANT", "LTI"])
        self.addWidget(self.block_type_label)
        self.addWidget(self.block_type_selector)

        # Add Block Action
        self.add_block_action = QAction(QIcon(None), "Add Block", self)
        self.add_block_action.triggered.connect(self.add_block)
        self.addAction(self.add_block_action)

        # Run Simulation Action
        self.run_simulation_action = QAction(QIcon(None), "Run Simulation", self)
        self.run_simulation_action.triggered.connect(self.run_simulation)
        self.addAction(self.run_simulation_action)

        # Toolbar for Save and Load
        save_action = QAction("Save Diagram", self)
        save_action.triggered.connect(self.save_to_file)
        self.toolbar.addAction(save_action)

        # New Diagram
        new_diagram_action = QAction("New Diagram", self)
        new_diagram_action.triggered.connect(self.new_diagram)
        self.toolbar.addAction(new_diagram_action)

        load_action = QAction("Load Diagram", self)
        load_action.triggered.connect(self.load_from_file)
        self.toolbar.addAction(load_action)

    def set_canvas(self, canvas):
        """Connect the toolbar to the diagram canvas."""
        self.canvas = canvas

    def set_plot_canvas(self, plot_canvas):
        """Connect the toolbar to the plot canvas."""
        self.plot_canvas = plot_canvas

    def add_block(self):
        """Add a block to the diagram canvas."""
        if self.canvas:
            block_type = self.block_type_selector.currentText()
            print(f"Adding block: {block_type}")
            self.canvas.add_block(block_type, 100, 100)

    def run_simulation(self):
        """Run the simulation and display results."""
        if self.plot_canvas:
            import numpy as np
            # Generate some placeholder data
            t = np.linspace(0, 5, 500)
            y = np.sin(2 * np.pi * t)
            print("Running simulation...")
            self.plot_canvas.plot(t, y)
