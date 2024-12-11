from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import QLineF, QPointF
from PyQt5.QtGui import QPen, QColor


class Wire(QGraphicsLineItem):
    """Represents a wire connecting two ports."""
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.setPen(QPen(QColor("black"), 2))
        self.setZValue(-1)  # Ensure wires are behind blocks
        self.update_position()

        # Set properties to identify as a wire
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        self.selected_color = QColor("red")
        self.default_color = QColor("black")

    def update_position(self):
        """Update the wire's position."""
        if self.start_port and self.end_port:
            start = self.start_port.scenePos() + QPointF(self.start_port.rect().width() / 2, self.start_port.rect().height() / 2)
            end = self.end_port.scenePos() + QPointF(self.end_port.rect().width() / 2, self.end_port.rect().height() / 2)
            self.setLine(QLineF(start, end))

    def update_temp_position(self, cursor_pos):
        """Update the position of the wire during drawing."""
        if self.start_port:
            start = self.start_port.scenePos() + QPointF(self.start_port.rect().width() / 2, self.start_port.rect().height() / 2)
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
        # Ensure both ports are valid
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

