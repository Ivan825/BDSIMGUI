from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import QLineF, QPointF
from PyQt5.QtGui import QPen, QColor


class Wire(QGraphicsLineItem):
    """Represents a wire connecting two ports."""
    def __init__(self, start_port, end_port=None):
        super().__init__()
        self.start_port = start_port
        self.end_port = None  # Set end_port to None by default
        self.setPen(QPen(QColor("black"), 2))
        self.setZValue(-1)  # Ensure wires are drawn behind blocks

        # Add this wire to the start_port's connected wires
        if not hasattr(self.start_port, "connected_wires"):
            self.start_port.connected_wires = []
        self.start_port.connected_wires.append(self)

        # If an end_port is provided at initialization, connect to it
        if end_port is not None:
            self.set_end_port(end_port)

        # Set properties for interactivity
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        self.selected_color = QColor("red")
        self.default_color = QColor("black")

        # Update wire position
        self.update_position()

    def set_end_port(self, end_port):
        """Set the end port and connect the wire to it."""
        self.end_port = end_port
        if not hasattr(self.end_port, "connected_wires"):
            self.end_port.connected_wires = []
        self.end_port.connected_wires.append(self)
        self.update_position()  # Update wire position after connecting to end_port

    def update_position(self):
        """Update the wire's position based on connected ports."""
        if self.start_port and self.end_port:
            start = self.start_port.scenePos()
            end = self.end_port.scenePos()
            self.setLine(QLineF(start, end))
        elif self.start_port:
            # Wire is being drawn, update to cursor position
            start = self.start_port.scenePos()
            self.setLine(QLineF(start, start))

    def update_temp_position(self, cursor_pos):
        """Update the position of the wire during drawing."""
        if self.start_port:
            start = self.start_port.scenePos()
            self.setLine(QLineF(start, cursor_pos))

    def mousePressEvent(self, event):
        """Highlight wire when selected."""
        self.setPen(QPen(self.selected_color, 2))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Reset wire color when deselected."""
        if not self.isSelected():
            self.setPen(QPen(self.default_color, 2))
        super().mouseReleaseEvent(event)

    def create_bdsim_connection(self, bdsim_model):
        """Connect bdsim blocks via ports."""
        if not self.start_port or not self.end_port:
            print("Invalid wire: Missing start or end port.")
            return

        start_block = self.start_port.parentItem()
        end_block = self.end_port.parentItem()

        if (
            start_block.bdsim_instance
            and end_block.bdsim_instance
            and self.start_port.port_type == "output"
            and self.end_port.port_type == "input"
        ):
            bdsim_model.connect(start_block.bdsim_instance, end_block.bdsim_instance)
        else:
            print(f"Invalid connection between {start_block.name} and {end_block.name}.")

    def remove_wire(self):
        """Safely remove the wire from the scene."""
        if self.scene():  # Check if the wire is still in a valid scene
            self.scene().removeItem(self)  # Remove the wire from the scene


