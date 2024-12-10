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
        self.update_position()

    def update_position(self):
        """Update the wire's position."""
        start = self.start_port.scenePos() + QPointF(5, 5)
        end = self.end_port.scenePos() + QPointF(5, 5)
        self.setLine(QLineF(start, end))

    def create_bdsim_connection(self, bdsim_model):
        """Connect bdsim blocks via ports."""
        start_block = self.start_port.parentItem()
        end_block = self.end_port.parentItem()
        if (
            start_block.bdsim_instance
            and end_block.bdsim_instance
            and self.start_port.port_type == "output"
            and self.end_port.port_type == "input"
        ):
            bdsim_model.connect(start_block.bdsim_instance, end_block.bdsim_instance)
