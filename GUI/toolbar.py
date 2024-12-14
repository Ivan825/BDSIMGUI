from PyQt5.QtWidgets import QToolBar, QAction, QComboBox, QLabel,QMenu
from PyQt5.QtGui import QIcon

class Toolbar(QToolBar):
    def __init__(self):
        def __init__(self):
            super().__init__()
            self.canvas = None

            # File Operations
            file_menu = QMenu("File Operations", self)
            save_action = QAction("Save Diagram", self)
            save_action.triggered.connect(self.save_to_file)
            load_action = QAction("Load Diagram", self)
            load_action.triggered.connect(self.load_from_file)
            file_menu.addAction(save_action)
            file_menu.addAction(load_action)
            self.addAction(file_menu.menuAction())

            # Edit Operations
            edit_menu = QMenu("Edit Operations", self)
            undo_action = QAction("Undo", self)
            undo_action.triggered.connect(self.undo)
            redo_action = QAction("Redo", self)
            redo_action.triggered.connect(self.redo)
            delete_action = QAction("Delete Selected", self)
            delete_action.triggered.connect(self.delete_selected)
            edit_menu.addAction(undo_action)
            edit_menu.addAction(redo_action)
            edit_menu.addAction(delete_action)
            self.addAction(edit_menu.menuAction())

            # Block Options
            block_label = QLabel("Block Type:")
            self.addWidget(block_label)
            self.block_type_selector = QComboBox()
            self.block_type_selector.addItems(["STEP", "GAIN", "SUM", "SCOPE", "RAMP", "WAVEFORM", "CONSTANT", "LTI"])
            self.addWidget(self.block_type_selector)

            add_block_action = QAction("Add Block", self)
            add_block_action.triggered.connect(self.add_block)
            self.addAction(add_block_action)

            # Simulation Controls
            simulation_menu = QMenu("Simulation Controls", self)
            run_simulation_action = QAction("Run Simulation", self)
            run_simulation_action.triggered.connect(self.run_simulation)
            simulation_menu.addAction(run_simulation_action)
            self.addAction(simulation_menu.menuAction())

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
            # Call add_block without fixed coordinates to let the canvas logic handle placement
            self.canvas.add_block(block_type)

    def set_canvas(self, canvas):
        """Connect the toolbar to the diagram canvas."""
        self.canvas = canvas
        print("Toolbar connected to canvas.")  # Debugging output

    def run_simulation(self):
        """Run the simulation and display results."""
        if self.plot_canvas:
            import numpy as np
            # Generate some placeholder data
            t = np.linspace(0, 5, 500)
            y = np.sin(2 * np.pi * t)
            print("Running simulation...")
            self.plot_canvas.plot(t, y)
