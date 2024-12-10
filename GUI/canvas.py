from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5.QtGui import QPainter

class DiagramCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Set up the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Wire Drawing State
        self.wire_start_block = None
        self.temp_line = None

    def add_block(self, name="Block", x=0, y=0):
        """Add a draggable block to the canvas."""
        block = Block(name)
        block.setPos(x, y)
        block.setCanvas(self)  # Pass canvas to block for wire drawing
        self.scene.addItem(block)

    def start_wire(self, block, port_pos):
        """Start drawing a wire from a block."""
        self.wire_start_block = block
        self.temp_line = QGraphicsLineItem(QLineF(port_pos, port_pos))
        self.temp_line.setPen(Qt.black)
        self.scene.addItem(self.temp_line)

    def update_wire(self, mouse_pos):
        """Update the temporary wire line as the mouse moves."""
        if self.temp_line:
            line = self.temp_line.line()
            line.setP2(mouse_pos)
            self.temp_line.setLine(line)

    def mouseMoveEvent(self, event):
        """Update the temporary wire line as the mouse moves."""
        if self.temp_line:
            mouse_pos = self.mapToScene(event.pos())
            self.update_wire(mouse_pos)
        super().mouseMoveEvent(event)


    def finish_wire(self, block, port_pos):
        """Finish drawing a wire and connect it to another block."""
        if self.wire_start_block and block != self.wire_start_block:
            # Create a permanent wire
            wire = Wire(self.wire_start_block, block, self.temp_line.line())
            self.scene.addItem(wire)

        # Reset wire drawing state
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
        self.temp_line = None
        self.wire_start_block = None

class Block(QGraphicsRectItem):
    """A draggable block."""
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

    def setCanvas(self, canvas):
        """Set the canvas for wire drawing."""
        self.canvas = canvas

    def mousePressEvent(self, event):
        """Handle mouse press for starting or finishing wire drawing."""
        if event.button() == Qt.LeftButton and self.canvas:
            port_pos = self.scenePos() + QPointF(self.rect().width() / 2, self.rect().height() / 2)
            if not self.canvas.wire_start_block:
                # Start wire drawing
                self.canvas.start_wire(self, port_pos)
            else:
                # Finish wire drawing
                self.canvas.finish_wire(self, port_pos)
        super().mousePressEvent(event)

class Wire(QGraphicsLineItem):
    """Represents a wire connecting two blocks."""
    def __init__(self, start_block, end_block, line):
        super().__init__(line)
        self.start_block = start_block
        self.end_block = end_block
        self.setPen(Qt.black)
