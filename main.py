from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QToolBar, QComboBox, QLabel, QAction
)
from PyQt5.QtCore import Qt
from GUI.canvas import DiagramCanvas
from GUI.properties import PropertiesEditor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from bdsim import BDSim


class PlotCanvas(FigureCanvas):
    """A Matplotlib-based widget for plotting simulation results."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def plot(self, x, y):
        """Clear the canvas and plot new data."""
        self.ax.clear()
        self.ax.plot(x, y, label="Simulation Data")
        self.ax.set_title("Simulation Results")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        self.ax.legend()
        self.draw()


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
        self.block_type_selector.addItems(["STEP", "GAIN", "SUM", "SCOPE"])
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

        # Simulate Button
        simulate_action = QAction("Simulate", self)
        simulate_action.triggered.connect(self.simulate)
        self.toolbar.addAction(simulate_action)

        # Properties Editor
        self.properties_editor = PropertiesEditor()

        # Diagram Canvas
        self.canvas = DiagramCanvas(properties_editor=self.properties_editor)

        # Plotting Canvas
        self.plot_canvas = PlotCanvas()

        # Layouts
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.canvas)

        # Right Panel (Properties + Plot)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.properties_editor)
        self.right_layout.addWidget(self.plot_canvas)
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

    def simulate(self):
        """Compile the current diagram into a bdsim model and simulate."""
        from bdsim import BDSim

        sim = BDSim()
        bdsim_model = sim.blockdiagram()

        # Create blocks
        for item in self.canvas.scene.items():
            if hasattr(item, "create_bdsim_instance"):
                item.create_bdsim_instance(bdsim_model)

        # Create connections
        for item in self.canvas.scene.items():
            if hasattr(item, "create_bdsim_connection"):
                item.create_bdsim_connection(bdsim_model)

        # Compile and run simulation
        try:
            bdsim_model.compile()
            results = sim.run(bdsim_model, 5)

            # Ensure results contain a SCOPE block
            if "scope.0" in results["out"]:
                scope_data = results["out"]["scope.0"]
                self.plot_canvas.plot(scope_data.t, scope_data.y)
            else:
                print("No valid SCOPE block found in the diagram.")
                self.show_error_message(
                    "No valid SCOPE block found in the diagram. Add a SCOPE block and connect it properly.")
        except Exception as e:
            print(f"Simulation Error: {e}")
            self.show_error_message(f"Simulation Error: {e}")

    def show_error_message(self, message):
        """Display an error message in a dialog box."""
        from PyQt5.QtWidgets import QMessageBox
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
