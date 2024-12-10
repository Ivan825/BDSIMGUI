from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem
from PyQt5.QtCore import QPointF, Qt


class Block(QGraphicsRectItem):
    """A draggable block with connection ports."""
    def __init__(self, name, width=100, height=50):
        super().__init__(0, 0, width, height)
        self.setBrush(Qt.lightGray)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.name = name
        self.canvas = None

        # Add ports to the block
        self.input_port = Port(self, "input")
        self.output_port = Port(self, "output")
        self.update_ports()

    def set_canvas(self, canvas):
        """Set the canvas for wire drawing."""
        self.canvas = canvas
        self.input_port.set_canvas(canvas)
        self.output_port.set_canvas(canvas)

    def update_ports(self):
        """Update port positions relative to the block."""
        rect = self.rect()
        self.input_port.setPos(rect.left() - 10, rect.top() + rect.height() / 2 - 5)
        self.output_port.setPos(rect.right() - 5, rect.top() + rect.height() / 2 - 5)

    def itemChange(self, change, value):
        """Handle block movement and update port and wire positions."""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Only proceed if the block is part of a scene
            self.update_ports()
            for wire in self.scene().items():
                if isinstance(wire, QGraphicsItem) and hasattr(wire, "update_position"):
                    wire.update_position()
        return super().itemChange(change, value)


class Port(QGraphicsEllipseItem):
    """A connection port on a block."""
    def __init__(self, parent, port_type, radius=10):
        super().__init__(-radius / 2, -radius / 2, radius, radius, parent)
        self.setBrush(Qt.darkGray)
        self.port_type = port_type
        self.canvas = None

    def set_canvas(self, canvas):
        """Set the canvas for wire drawing."""
        self.canvas = canvas

    def mousePressEvent(self, event):
        """Handle mouse press for starting or finishing wire drawing."""
        if event.button() == Qt.LeftButton and self.canvas:
            if not self.canvas.wire_start_port:
                # Start wire drawing
                self.canvas.start_wire(self)
            else:
                # Finish wire drawing
                self.canvas.finish_wire(self)
        super().mousePressEvent(event)
