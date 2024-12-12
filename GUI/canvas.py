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

        # Wire drawing state
        self.start_port = None
        self.temp_wire = None

    def get_blocks_and_wires(self):
        """Retrieve all blocks and wires from the canvas for simulation."""
        blocks = []
        wires = []

        for item in self.scene.items():
            if isinstance(item, Block):
                block_data = {
                    "type": item.block_type,
                    "name": item.name,
                    "properties": item.properties
                }
                blocks.append(block_data)
            elif isinstance(item, Wire):
                wire_data = {
                    "start": item.start_port.parentItem().name,
                    "end": item.end_port.parentItem().name
                }
                wires.append(wire_data)

        return blocks, wires

        return blocks, wires
    def add_block(self, block_type, x=100, y=100):
        """Add a block of the specified type to the canvas."""
        block = Block(block_type)
        block.setPos(x, y)
        self.scene.addItem(block)

    def delete_selected(self):
        """Delete all selected items (blocks, wires, or groups)."""
        for item in self.scene.selectedItems():
            if isinstance(item, Block):
                # Remove wires connected to the block
                for port in item.input_ports + item.output_ports:
                    port.remove_connected_wires()
            self.scene.removeItem(item)

    def mousePressEvent(self, event):
        """Handle mouse press for selecting or starting a wire."""
        item = self.itemAt(event.pos())

        if isinstance(item, Block):
            # Pass the selected block to the properties editor
            if self.properties_editor:
                self.properties_editor.set_block(item)

        elif isinstance(item, Port) and item.port_type == "output":
            # Start wire drawing from an output port
            self.start_port = item
            self.temp_wire = Wire(self.start_port)
            self.scene.addItem(self.temp_wire)

        elif self.start_port and isinstance(item, Port) and item.port_type == "input":
            # Complete the wire connection to a valid input port
            if self.temp_wire:
                self.temp_wire.set_end_port(item)  # Dynamically set the end_port
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

    def keyPressEvent(self, event):
        """Handle key presses for operations like deletion."""
        if event.key() == Qt.Key_Delete:
            # Delete selected items (blocks or wires)
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)
        super().keyPressEvent(event)
