from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QLineF
from PyQt5.QtGui import QPainter, QPen
from GUI.blocks import Block
from GUI.wires import Wire


class DiagramCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Set up the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Wire Drawing State
        self.wire_start_port = None
        self.temp_line = None

    def add_block(self, name="Block", x=0, y=0):
        """Add a draggable block to the canvas."""
        block = Block(name)
        block.setPos(x, y)
        block.set_canvas(self)  # Pass canvas to block for wire drawing
        self.scene.addItem(block)

    def start_wire(self, port):
        """Start drawing a wire from a port."""
        self.wire_start_port = port
        port_center = port.scenePos() + QPointF(port.rect().width() / 2, port.rect().height() / 2)
        self.temp_line = QGraphicsLineItem(QLineF(port_center, port_center))
        self.temp_line.setPen(QPen(Qt.black, 2, Qt.DashLine))
        self.scene.addItem(self.temp_line)

    def update_wire(self, mouse_pos):
        """Update the temporary wire line as the mouse moves."""
        if self.temp_line:
            line = self.temp_line.line()
            line.setP2(mouse_pos)
            self.temp_line.setLine(line)

    def finish_wire(self, port):
        """Finish drawing a wire and connect it to another port."""
        if self.wire_start_port and port != self.wire_start_port:
            wire = Wire(self.wire_start_port, port)
            self.scene.addItem(wire)

        # Reset wire drawing state
        self.cancel_wire()

    def cancel_wire(self):
        """Cancel the current wire drawing."""
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
        self.temp_line = None
        self.wire_start_port = None
