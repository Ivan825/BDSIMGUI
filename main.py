from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QToolBar,
    QComboBox, QLabel, QAction, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from GUI.canvas import DiagramCanvas
from GUI.properties import PropertiesEditor
from backend.simulate import run_bdsim_simulation
import json
from PyQt5.QtWidgets import QFileDialog


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BDSim GUI")
        self.resize(1200, 800)

        # Create the main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Toolbar
        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)

        # Block Type Selector
        self.block_type_label = QLabel("Block Type:")
        self.block_type_selector = QComboBox()
        self.block_type_selector.addItems(["STEP", "GAIN", "SUM", "SCOPE", "RAMP", "WAVEFORM", "CONSTANT", "LTI"])
        self.block_type_selector.currentTextChanged.connect(self.set_block_type)

        self.toolbar.addWidget(self.block_type_label)
        self.toolbar.addWidget(self.block_type_selector)

        # Add "Add Block" Button
        add_block_action = QAction("Add Block", self)
        add_block_action.triggered.connect(self.add_block)
        self.toolbar.addAction(add_block_action)

        # Delete Button
        delete_action = QAction("Delete Selected", self)
        delete_action.triggered.connect(self.delete_selected)
        self.toolbar.addAction(delete_action)

        # Simulation Time Input
        self.sim_time_label = QLabel("Simulation Time:")
        self.sim_time_input = QLineEdit("5")  # Default value is 5 seconds
        self.toolbar.addWidget(self.sim_time_label)
        self.toolbar.addWidget(self.sim_time_input)

        # Simulate Button
        simulate_action = QAction("Simulate", self)
        simulate_action.triggered.connect(self.simulate)
        self.toolbar.addAction(simulate_action)

        # Save Button
        save_action = QAction("Save Diagram", self)
        save_action.triggered.connect(self.save_to_file)  # Pass function reference without parentheses
        self.toolbar.addAction(save_action)

        # Load Button
        load_action = QAction("Load Diagram", self)
        load_action.triggered.connect(self.load_from_file)  # Pass function reference without parentheses
        self.toolbar.addAction(load_action)

        # Properties Editor
        self.properties_editor = PropertiesEditor()

        # Diagram Canvas
        self.canvas = DiagramCanvas(properties_editor=self.properties_editor)

        # Layouts
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.canvas)

        # Right Panel (Properties)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.properties_editor)
        self.right_panel.setLayout(self.right_layout)

        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([800, 400])  # Initial splitter sizes

        self.layout.addWidget(self.splitter)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Set default block type
        self.current_block_type = self.block_type_selector.currentText()

    def set_block_type(self, block_type):
        """Set the current block type from the dropdown menu."""
        self.current_block_type = block_type

    def add_block(self):
        """Add a block of the selected type to the canvas."""
        x, y = 100, 100  # Default position
        self.canvas.add_block(self.current_block_type, x, y)

    def delete_selected(self):
        """Delete all selected items (blocks, wires, or groups)."""
        for item in self.canvas.scene.selectedItems():
            self.canvas.scene.removeItem(item)

    def validate_blocks_and_wires(self, blocks, wires):
        """Validate blocks and wires before simulation."""
        # Ensure there is at least one SCOPE block
        scope_present = any(block["type"] == "SCOPE" for block in blocks)
        if not scope_present:
            self.show_error_message("Simulation Error: No SCOPE block present.")
            return False

        # Ensure all wires connect valid blocks
        block_names = {block["name"] for block in blocks}
        for wire in wires:
            if wire["start"] not in block_names or wire["end"] not in block_names:
                self.show_error_message(
                    f"Simulation Error: Invalid connection {wire['start']} -> {wire['end']}."
                )
                return False

        return True

    def simulate(self):
        """Run the simulation using bdsim."""
        blocks, wires = self.canvas.get_blocks_and_wires()

        try:
            # Validate blocks and wires before simulation
            if not self.validate_blocks_and_wires(blocks, wires):
                return

            # Get simulation time
            try:
                sim_time = float(self.sim_time_input.text())
                if sim_time <= 0:
                    raise ValueError("Simulation time must be greater than zero.")
            except ValueError as e:
                self.show_error_message(f"Invalid simulation time: {e}")
                return

            # Run simulation with updated logic
            run_bdsim_simulation(blocks, wires, T=sim_time)

        except Exception as e:
            self.show_error_message(str(e))

    def save_to_file(self):
        """Save the current block diagram to a file."""
        blocks, wires = self.canvas.get_blocks_and_wires()

        # Serialize the block diagram
        diagram_data = {
            "blocks": blocks,
            "wires": wires
        }

        # Open a save dialog
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Diagram", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)

        if file_name:
            try:
                with open(file_name, "w") as file:
                    json.dump(diagram_data, file, indent=4)
                QMessageBox.information(self, "Success", f"Diagram saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def load_from_file(self):
        """Load a block diagram from a file."""
        # Open a load dialog
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Diagram", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)

        if file_name:
            try:
                with open(file_name, "r") as file:
                    diagram_data = json.load(file)

                # Clear the canvas
                self.canvas.scene.clear()

                # Add blocks
                for block in diagram_data["blocks"]:
                    block_type = block["type"]
                    x, y = block["x"], block["y"]
                    block_instance = self.canvas.add_block(block_type, x, y)

                    # Set block properties
                    for prop, value in block["properties"].items():
                        block_instance.properties[prop] = value

                # Add wires
                for wire in diagram_data["wires"]:
                    start_block_name = wire["start"]
                    start_port_index = wire.get("start_port", 0)
                    end_block_name = wire["end"]
                    end_port_index = wire.get("end_port", 0)
                    self.canvas.add_wire(start_block_name, start_port_index, end_block_name, end_port_index)

                QMessageBox.information(self, "Success", f"Diagram loaded from {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {e}")

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
