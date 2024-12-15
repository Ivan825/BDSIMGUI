from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QToolBar,
    QComboBox, QLabel, QAction, QLineEdit, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt
import json

from GUI.canvas import DiagramCanvas
from GUI.properties import PropertiesEditor
from GUI.blocks import Block
from backend.simulate import run_bdsim_simulation


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BDSim GUI")
        self.resize(1200, 800)

        # Initialize UI components
        self.setup_ui()

        # Set default block type
        self.current_block_type = self.block_type_selector.currentText()

    def setup_ui(self):
        """Setup the main UI components."""
        # Create the central layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Create the toolbars
        self.setup_toolbars()

        # Create the properties editor
        self.properties_editor = PropertiesEditor()

        # Create the diagram canvas
        self.canvas = DiagramCanvas(properties_editor=self.properties_editor)

        # Create and configure the splitter layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.canvas)

        # Add the properties editor panel
        self.setup_properties_panel()

        # Add the splitter to the main layout
        self.layout.addWidget(self.splitter)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def setup_toolbars(self):
        """Setup toolbars with grouped actions split into two rows."""
        # First Toolbar: Block Operations and Edit Operations
        self.block_toolbar = QToolBar("Block Operations")
        self.addToolBar(Qt.TopToolBarArea, self.block_toolbar)

        # Block Operations
        block_label = QLabel("Block Type:")
        self.block_toolbar.addWidget(block_label)

        self.block_type_selector = QComboBox()
        self.block_type_selector.addItems(["STEP", "GAIN", "SUM", "SCOPE", "RAMP", "WAVEFORM", "CONSTANT", "LTI"])
        self.block_type_selector.currentTextChanged.connect(self.set_block_type)
        self.block_toolbar.addWidget(self.block_type_selector)

        add_block_action = QAction("Add Block", self)
        add_block_action.triggered.connect(self.add_block)
        self.block_toolbar.addAction(add_block_action)

        delete_action = QAction("Delete Selected", self)
        delete_action.triggered.connect(self.delete_selected)
        self.block_toolbar.addAction(delete_action)

        # Group and Ungroup Buttons
        group_action = QAction("Group", self)
        group_action.triggered.connect(self.group_selected_items)
        self.block_toolbar.addAction(group_action)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.triggered.connect(self.ungroup_selected_items)
        self.block_toolbar.addAction(ungroup_action)

        # Second Toolbar: File and Simulation Operations
        self.main_toolbar = QToolBar("Main Operations")
        self.addToolBar(Qt.TopToolBarArea, self.main_toolbar)

        # File Actions
        save_action = QAction("Save Diagram", self)
        save_action.triggered.connect(self.save_to_file)
        self.main_toolbar.addAction(save_action)

        load_action = QAction("Load Diagram", self)
        load_action.triggered.connect(self.load_from_file)
        self.main_toolbar.addAction(load_action)

        new_diagram_action = QAction("New Diagram", self)
        new_diagram_action.triggered.connect(self.new_diagram)
        self.main_toolbar.addAction(new_diagram_action)

        # Simulation Actions
        self.sim_time_label = QLabel("Simulation Time:")
        self.main_toolbar.addWidget(self.sim_time_label)

        self.sim_time_input = QLineEdit("5")
        self.main_toolbar.addWidget(self.sim_time_input)

        simulate_action = QAction("Simulate", self)
        simulate_action.triggered.connect(self.simulate)
        self.main_toolbar.addAction(simulate_action)

        # Undo/Redo Actions
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo_action)
        self.main_toolbar.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.redo_action)
        self.main_toolbar.addAction(redo_action)

    def setup_properties_panel(self):
        """Setup the properties panel."""
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.properties_editor)
        self.right_panel.setLayout(self.right_layout)

        # Add the properties panel to the splitter
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([800, 400])  # Initial sizes for splitter sections

    # Event Handlers
    def set_block_type(self, block_type):
        """Set the current block type from the dropdown menu."""
        self.current_block_type = block_type

    def add_block(self):
        """Add a block of the selected type to the canvas."""
        self.canvas.add_block(self.current_block_type)

    def delete_selected(self):
        """Delete all selected items (blocks, wires, or groups)."""
        self.canvas.delete_selected()

    def group_selected_items(self):
        """Group selected items."""
        self.canvas.group_selected_items()

    def ungroup_selected_items(self):
        """Ungroup selected items."""
        self.canvas.ungroup_selected_items()

    def undo_action(self):
        """Perform undo action."""
        self.canvas.undo_action()

    def redo_action(self):
        """Perform redo action."""
        self.canvas.redo_action()

    def simulate(self):
        """Run the simulation using bdsim."""
        blocks, wires = self.canvas.get_blocks_and_wires()

        try:
            if not self.validate_blocks_and_wires(blocks, wires):
                return

            # Get simulation time
            sim_time = self.get_simulation_time()
            if sim_time is None:
                return

            # Run the simulation
            run_bdsim_simulation(blocks, wires, T=sim_time)

        except Exception as e:
            self.show_error_message(str(e))

    def validate_blocks_and_wires(self, blocks, wires):
        """Validate blocks and wires before simulation."""
        scope_present = any(block["type"] == "SCOPE" for block in blocks)
        if not scope_present:
            self.show_error_message("Simulation Error: No SCOPE block present.")
            return False

        block_names = {block["name"] for block in blocks}
        for wire in wires:
            if wire["start"] not in block_names or wire["end"] not in block_names:
                self.show_error_message(
                    f"Simulation Error: Invalid connection {wire['start']} -> {wire['end']}."
                )
                return False

        return True

    def get_simulation_time(self):
        """Retrieve and validate the simulation time."""
        try:
            sim_time = float(self.sim_time_input.text())
            if sim_time <= 0:
                raise ValueError("Simulation time must be greater than zero.")
            return sim_time
        except ValueError as e:
            self.show_error_message(f"Invalid simulation time: {e}")
            return None

    def save_to_file(self):
        """Save the current block diagram to a file."""
        blocks, wires = self.canvas.get_blocks_and_wires()
        diagram_data = {"blocks": blocks, "wires": wires}

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Diagram", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_name:
            try:
                with open(file_name, "w") as file:
                    json.dump(diagram_data, file, indent=4)
                QMessageBox.information(self, "Success", f"Diagram saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def load_from_file(self):
        """Load a block diagram from a file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Diagram", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_name:
            try:
                Block.reset_instance_counter()
                self.canvas.load_from_file(file_name)
                QMessageBox.information(self, "Success", f"Diagram loaded from {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {e}")

    def new_diagram(self):
        """Start a new diagram with a fresh canvas."""
        Block.reset_instance_counter()
        self.canvas.clear()
        QMessageBox.information(self, "New Diagram", "Started a new diagram!")

    def show_error_message(self, message):
        """Display an error message in a dialog box."""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Simulation Error")
        error_dialog.setText(message)
        error_dialog.exec_()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
