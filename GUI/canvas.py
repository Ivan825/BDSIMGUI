from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from GUI.blocks import Block, Port
from GUI.wires import Wire
from PyQt5.QtGui import QPainter


class DiagramCanvas(QGraphicsView):
    """Canvas for the diagram editor."""
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
        self.temp_wire = None

    def add_block(self, block_type, x=100, y=100):
        """Add a block of the specified type to the canvas."""
        block = Block(block_type)
        block.setPos(x, y)
        self.scene.addItem(block)

    def mousePressEvent(self, event):
        """Handle mouse press for selecting or starting a wire."""
        item = self.itemAt(event.pos())

        if isinstance(item, Block):
            # Pass the selected block to the properties editor
            if self.properties_editor:
                self.properties_editor.set_block(item)
        elif isinstance(item, Port) and item.port_type == "output":
            # Start wire drawing
            self.start_port = item
            self.temp_wire = Wire(self.start_port, None)
            self.scene.addItem(self.temp_wire)
        elif self.start_port and isinstance(item, Port) and item.port_type == "input":
            # Complete the wire if connected to a valid input port
            self.temp_wire.end_port = item
            self.temp_wire.update_position()
            self.temp_wire = None
            self.start_port = None
        else:
            # Reset wire drawing if no valid connection
            if self.temp_wire:
                self.scene.removeItem(self.temp_wire)
                self.temp_wire = None
            self.start_port = None

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Update the temporary wire during wire drawing."""
        if self.start_port and self.temp_wire:
            cursor_pos = self.mapToScene(event.pos())
            self.temp_wire.update_temp_position(cursor_pos)
        super().mouseMoveEvent(event)
