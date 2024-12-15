from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import Qt
from GUI.blocks import Block, Port
from GUI.wires import Wire
from PyQt5.QtGui import QPainter
import json
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItemGroup


class DiagramCanvas(QGraphicsView):
    GRID_SIZE = 20  # Size of each grid cell
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


        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.current_group = None  # Store the current active group

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

    def drawBackground(self, painter, rect):
        """Draw a grid on the canvas."""
        super().drawBackground(painter, rect)

        # Set up the painter for the grid
        grid_pen = QPen(QColor(200, 200, 200), 0.5)  # Light gray grid
        painter.setPen(grid_pen)

        left = int(rect.left()) - (int(rect.left()) % self.GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % self.GRID_SIZE)

        # Draw vertical lines
        x = left
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += self.GRID_SIZE

        # Draw horizontal lines
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += self.GRID_SIZE

    def add_block(self, block_type, x=None, y=None, name=None):
        """Add a block of the specified type to the canvas."""
        if x is None or y is None:
            # Get the center of the visible area in the scene
            visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
            x, y = visible_rect.center().x(), visible_rect.center().y()
            print(f"Spawning block at scene center: x={x}, y={y}")  # Debugging output

        # Create the block
        if name:
            block = Block(block_type, name=name)
        else:
            block = Block(block_type)

        block.setPos(x, y)  # Position the block
        self.scene.addItem(block)
        # Push action to Undo stack
        self.undo_stack.append(("add_block", block))
        self.redo_stack.clear()  # Clear Redo stack
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

        # Push action to Undo stack
        self.undo_stack.append(("add_wire", wire))
        self.redo_stack.clear()  # Clear Redo stack

    def delete_selected(self):
        """Delete all selected items (blocks, wires, or groups)."""
        for item in self.scene.selectedItems():
            try:
                if isinstance(item, Block):
                    # Save state for Undo
                    self.undo_stack.append(("delete_block", item))
                    # Remove wires connected to the block
                    for port in item.input_ports + item.output_ports:
                        if hasattr(port, "remove_connected_wires"):
                            port.remove_connected_wires()
                    self.scene.removeItem(item)
                elif isinstance(item, Wire):
                    # Save state for Undo
                    wire_data = {
                        "start_block": item.start_port.parentItem(),
                        "start_port": item.start_port,
                        "end_block": item.end_port.parentItem(),
                        "end_port": item.end_port,
                        "wire": item,
                    }
                    self.undo_stack.append(("delete_wire", wire_data))
                    self.scene.removeItem(item)

            except Exception as e:
                print(f"Error during block deletion: {e}")

        self.redo_stack.clear()  # Clear Redo stack

    def clear(self):
        """Clear all blocks and wires from the canvas."""
        # Save current state for Undo
        self.undo_stack.append(("clear", self.get_blocks_and_wires()))
        for item in self.scene.items():
            self.scene.removeItem(item)

        self.redo_stack.clear()  # Clear Redo stack

    def group_selected_items(self):
        """Group selected items into a QGraphicsItemGroup."""
        selected_items = self.scene.selectedItems()

        if not selected_items:
            print("No items selected for grouping.")
            return

        group = QGraphicsItemGroup()

        for item in selected_items:
            group.addToGroup(item)
            item.setSelected(False)  # Deselect items

        group.setFlag(QGraphicsItem.ItemIsMovable, True)
        group.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.scene.addItem(group)

        # Add the group to the undo stack
        self.undo_stack.append(("group", group, selected_items))
        print("Grouped items successfully.")

    def ungroup_selected_items(self):
        """Ungroup selected QGraphicsItemGroup and ensure wires remain visually connected."""
        selected_items = self.scene.selectedItems()

        for group in selected_items:
            if isinstance(group, QGraphicsItemGroup):
                items_in_group = group.childItems()

                # Remove items from group and reset their positions
                for item in items_in_group:
                    group.removeFromGroup(item)
                    item.setSelected(True)

                    if isinstance(item, Wire):
                        item.update_position()  # Refresh wire endpoints visually

                self.scene.removeItem(group)  # Remove the group container

                # Reconnect wires and update their visual positions
                for item in items_in_group:
                    if isinstance(item, Block):
                        for port in item.input_ports + item.output_ports:
                            for wire in port.connected_wires:
                                wire.update_position()

                # Add to undo stack
                self.undo_stack.append(("ungroup", group, items_in_group))
                self.redo_stack.clear()
                print("Ungrouped items successfully.")

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

    def undo_action(self):
        """Undo the last action."""
        if not self.undo_stack:
            return

        action, *args = self.undo_stack.pop()
        if action == "group":
            group, items = args
            self.scene.removeItem(group)
            for item in items:
                item.setSelected(True)
        elif action == "ungroup":
            group, items = args
            self.scene.addItem(group)
            for item in items:
                group.addToGroup(item)
        elif action == "add_block":
            self.scene.removeItem(args[0])
        elif action == "delete_block":
            self.scene.addItem(args[0])
        elif action == "add_wire":
            self.scene.removeItem(args[0])
        elif action == "delete_wire":
            wire_data = args[0]
            new_wire = Wire(wire_data["start_port"], wire_data["end_port"])
            self.scene.addItem(new_wire)
        elif action == "clear":
            blocks, wires = args[0]
            for block_data in blocks:
                self.add_block(block_data["type"], block_data["x"], block_data["y"], block_data["name"])
            for wire_data in wires:
                self.add_wire(wire_data["start"], wire_data["start_port_index"],
                              wire_data["end"], wire_data["end_port_index"])

        self.redo_stack.append((action, *args))

    def redo_action(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            return

        action, *args = self.redo_stack.pop()
        if action == "group":
            group, items = args
            self.scene.addItem(group)
            for item in items:
                group.addToGroup(item)
        elif action == "ungroup":
            group, items = args
            self.scene.removeItem(group)
            for item in items:
                item.setSelected(True)
        elif action == "add_block":
            self.scene.addItem(args[0])
        elif action == "delete_block":
            self.scene.removeItem(args[0])
        elif action == "add_wire":
            self.scene.addItem(args[0])
        elif action == "delete_wire":
            self.scene.removeItem(args[0]["wire"])
        elif action == "clear":
            self.clear()

        self.undo_stack.append((action, *args))
