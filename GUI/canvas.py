from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from GUI.blocks import Block, Port
from GUI.wires import Wire
from PyQt5.QtGui import QPainter
import json


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
        """Retrieve all blocks and wires from the canvas for simulation or saving."""
        blocks = []
        wires = []

        for item in self.scene.items():
            if isinstance(item, Block):
                block_data = {
                    "type": item.block_type,
                    "name": item.name,
                    "properties": item.properties,
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                }
                blocks.append(block_data)
            elif isinstance(item, Wire):
                wire_data = {
                    "start": item.start_port.parentItem().name,
                    "end": item.end_port.parentItem().name,
                    "start_port_index": self.get_port_index(item.start_port),
                    "end_port_index": self.get_port_index(item.end_port),
                }
                wires.append(wire_data)

        return blocks, wires

    def add_block(self, block_type, x=100, y=100, name=None):
        """Add a block of the specified type to the canvas."""
        if name:
            block = Block(block_type,name=name)

        else:
            block = Block(block_type)
        block.setPos(x, y)
        self.scene.addItem(block)
        return block

    def add_wire(self, start_block_name, start_port_index, end_block_name, end_port_index):
        """Add a wire between two ports on the canvas."""
        # Find the blocks by their names
        start_block = self.find_block_by_name(start_block_name)
        end_block = self.find_block_by_name(end_block_name)

        if not start_block or not end_block:
            print(f"Error: Could not find blocks {start_block_name} or {end_block_name} for wire.")
            return

        # Get the specified ports
        start_port = start_block.output_ports[start_port_index]
        end_port = end_block.input_ports[end_port_index]

        # Create and connect the wire
        wire = Wire(start_port, end_port)
        self.scene.addItem(wire)

    def delete_selected(self):
        """Delete all selected items (blocks, wires, or groups)."""
        for item in self.scene.selectedItems():
            try:
                if isinstance(item, Block):
                    # Remove wires connected to the block
                    for port in item.input_ports + item.output_ports:
                        if hasattr(port, "remove_connected_wires"):
                            port.remove_connected_wires()
                    self.scene.removeItem(item)
                elif isinstance(item, Wire):
                    # If it's a wire, remove it directly
                    self.scene.removeItem(item)
            except Exception as e:
                print(f"Error during block deletion: {e}")

    def clear(self):
        """Clear all blocks and wires from the canvas."""
        for item in self.scene.items():
            self.scene.removeItem(item)

    def save_to_file(self, file_path):
        """Save the current diagram to a file."""
        blocks, wires = self.get_blocks_and_wires()
        diagram_data = {"blocks": blocks, "wires": wires}

        try:
            with open(file_path, "w") as file:
                json.dump(diagram_data, file, indent=4)
            print(f"Diagram saved to {file_path}")
        except Exception as e:
            print(f"Error saving diagram: {e}")

    def load_from_file(self, file_path):
        """Load a diagram from a file."""
        try:
            with open(file_path, "r") as file:
                diagram_data = json.load(file)

            # Clear the current canvas
            self.clear()

            # Add blocks
            for block_data in diagram_data["blocks"]:
                block = self.add_block(
                    block_type=block_data["type"],
                    x=block_data["x"],
                    y=block_data["y"],
                    name=block_data["name"],  # Pass the name to preserve it
                )
                block.properties.update(block_data["properties"])

            # Add wires
            for wire_data in diagram_data["wires"]:
                self.add_wire(
                    start_block_name=wire_data["start"],
                    start_port_index=wire_data["start_port_index"],
                    end_block_name=wire_data["end"],
                    end_port_index=wire_data["end_port_index"],
                )
            print(f"Diagram loaded from {file_path}")
        except Exception as e:
            print(f"Error loading diagram: {e}")

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

    def find_block_by_name(self, name):
        """Find a block by its name."""
        for item in self.scene.items():
            if isinstance(item, Block) and item.name == name:
                return item
        return None

    def get_port_index(self, port):
        """Return the index of a port."""
        if port.port_type == "input":
            return port.parentItem().input_ports.index(port)
        elif port.port_type == "output":
            return port.parentItem().output_ports.index(port)
        return None
