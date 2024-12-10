from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from GUI.blocks import Block, Port, Wire
from PyQt5.QtGui import QPainter


class DiagramCanvas(QGraphicsView):
    def __init__(self, properties_editor=None):
        super().__init__()

        # Set up the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Reference to the properties editor
        self.properties_editor = properties_editor

        # Wire drawing
        self.start_port = None

    def add_block(self, block_type, x=100, y=100):
        """Add a block of the specified type to the canvas."""
        block = Block(block_type)
        block.setPos(x, y)
        self.scene.addItem(block)

    def mousePressEvent(self, event):
        """Handle mouse press for selecting or starting a wire."""
        item = self.itemAt(event.pos())
        if isinstance(item, Port) and item.port_type == "output":
            self.start_port = item  # Start wire drawing
        elif self.start_port and isinstance(item, Port) and item.port_type == "input":
            # Finish wire if connected to a valid input port
            wire = Wire(self.start_port, item)
            self.scene.addItem(wire)
            self.start_port = None
        elif isinstance(item, Block):
            # Pass the selected block to the properties editor
            if self.properties_editor:
                self.properties_editor.set_block(item)
        else:
            # Reset wire drawing if no valid connection
            self.start_port = None
        super().mousePressEvent(event)
