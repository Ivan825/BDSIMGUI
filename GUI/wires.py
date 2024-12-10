from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsItem
from PyQt5.QtCore import QLineF, QPointF
from PyQt5.QtGui import QPen, QColor


class Wire(QGraphicsLineItem):
    """Represents a wire connecting two ports."""
    def __init__(self, start_port, end_port):
        super().__init__()

        self.start_port = start_port
        self.end_port = end_port

        # Initialize wire
        self.update_position()
        self.setPen(QPen(QColor("black"), 2))
        self.setFlags(
            QGraphicsItem.ItemIsSelectable  # Make wire selectable
        )

    def update_position(self):
        """Update the wire's position to stay connected to ports."""
        start_pos = self.start_port.scenePos() + QPointF(
            self.start_port.rect().width() / 2, self.start_port.rect().height() / 2
        )
        end_pos = self.end_port.scenePos() + QPointF(
            self.end_port.rect().width() / 2, self.end_port.rect().height() / 2
        )
        self.setLine(QLineF(start_pos, end_pos))
