from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QAction
from PyQt5.QtCore import Qt
from GUI.toolbar import Toolbar
from GUI.canvas import DiagramCanvas
from GUI.properties import PropertiesEditor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        self.toolbar = Toolbar()
        self.addToolBar(self.toolbar)

        # Add "Delete" button to the toolbar
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected)
        self.toolbar.addAction(delete_action)

        # Splitter for resizability
        self.splitter = QSplitter(Qt.Horizontal)

        # Diagram Canvas (on the left)
        self.canvas = DiagramCanvas()
        self.splitter.addWidget(self.canvas)

        # Properties Editor + Plot Area (on the right)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()

        # Properties Editor
        self.properties_editor = PropertiesEditor()
        self.right_layout.addWidget(self.properties_editor)

        # Plotting Area
        self.plot_canvas = PlotCanvas(self, width=8, height=6)
        self.right_layout.addWidget(self.plot_canvas)

        self.right_panel.setLayout(self.right_layout)
        self.splitter.addWidget(self.right_panel)

        # Add the splitter to the layout
        self.layout.addWidget(self.splitter)

        # Set central layout
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Toolbar to access canvas and plot
        self.toolbar.set_canvas(self.canvas)
        self.toolbar.set_plot_canvas(self.plot_canvas)

    def delete_selected(self):
        """Delete all selected items (blocks, wires, or groups)."""
        for item in self.canvas.scene.selectedItems():
            self.canvas.scene.removeItem(item)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
