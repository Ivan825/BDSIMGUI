from PyQt5.QtWidgets import QToolBar, QAction, QComboBox, QLabel, QMenu, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon

class Toolbar(QToolBar):
    def __init__(self):
        super().__init__()

        self.canvas = None

        # Adjust toolbar height for two rows of tools
        self.setFixedHeight(80)

        # Main container for two rows
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        # ----- First Row: File and Edit Operations -----
        row1 = QToolBar("Row 1")
        file_menu = QMenu("File Operations", self)
        save_action = QAction("Save Diagram", self)
        save_action.triggered.connect(self.save_to_file)
        load_action = QAction("Load Diagram", self)
        load_action.triggered.connect(self.load_from_file)
        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        row1.addAction(file_menu.menuAction())

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
        row1.addAction(edit_menu.menuAction())

        # Grouping Buttons
        group_action = QAction("Group", self)
        group_action.triggered.connect(self.group_selected_items)
        row1.addAction(group_action)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.triggered.connect(self.ungroup_selected_items)
        row1.addAction(ungroup_action)

        layout.addWidget(row1)

        # ----- Second Row: Block Controls and Simulation -----
        row2 = QToolBar("Row 2")
        # Block type selection
        block_label = QLabel("Block Type:")
        row2.addWidget(block_label)

        self.block_type_selector = QComboBox()
        self.block_type_selector.addItems(["STEP", "GAIN", "SUM", "SCOPE", "RAMP", "WAVEFORM", "CONSTANT", "LTI"])
        row2.addWidget(self.block_type_selector)

        add_block_action = QAction("Add Block", self)
        add_block_action.triggered.connect(self.add_block)
        row2.addAction(add_block_action)

        # Simulation Controls
        simulation_menu = QMenu("Simulation Controls", self)
        run_simulation_action = QAction("Run Simulation", self)
        run_simulation_action.triggered.connect(self.run_simulation)
        simulation_menu.addAction(run_simulation_action)
        row2.addAction(simulation_menu.menuAction())

        layout.addWidget(row2)

        # Set layout
        container.setLayout(layout)
        self.addWidget(container)

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
