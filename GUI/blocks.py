from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QLineF
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


class Block(QGraphicsRectItem):
    """A draggable block with connection ports and editable properties."""
    instance_counter = {}  # Keeps track of instance numbers per block type

    def __init__(self, block_type, width=100, height=50, properties=None):
        super().__init__(0, 0, width, height)
        self.setBrush(Qt.lightGray)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.block_type = block_type
        self.properties = properties or {}

        # Assign a unique name
        if block_type not in Block.instance_counter:
            Block.instance_counter[block_type] = 1
        else:
            Block.instance_counter[block_type] += 1
        self.name = f"{block_type} {Block.instance_counter[block_type]}"

        # Display the block name
        self.name_label = QGraphicsTextItem(self.name, self)
        self.name_label.setDefaultTextColor(Qt.white)
        self.name_label.setFont(QFont("Arial", 10))
        self.name_label.setPos(10, -20)  # Position above the block

        # Add ports dynamically based on block type
        self.input_ports = []
        self.output_ports = []
        self.add_ports()

    def create_bdsim_instance(self, bdsim_model):
        """Create a bdsim block instance for this block."""
        try:
            if self.block_type == "STEP":
                self.bdsim_instance = bdsim_model.STEP(
                    A=self.properties.get("Amplitude", 1),
                    T=self.properties.get("Start Time", 0),
                    name=self.name,
                )
            elif self.block_type == "GAIN":
                self.bdsim_instance = bdsim_model.GAIN(
                    K=self.properties.get("Gain", 1),
                    name=self.name,
                )
            elif self.block_type == "SUM":
                self.bdsim_instance = bdsim_model.SUM(
                    gains=self.properties.get("Inputs", "+-"),
                    name=self.name,
                )
            elif self.block_type == "SCOPE":
                self.bdsim_instance = bdsim_model.SCOPE(
                    styles=[self.properties.get("Style", "Line")],
                    name=self.name,
                )
            elif self.block_type == "RAMP":
                self.bdsim_instance = bdsim_model.RAMP(
                    T=self.properties.get("Start Time", 0),
                    slope=self.properties.get("Slope", 1),
                    name=self.name,
                )
            elif self.block_type == "WAVEFORM":
                self.bdsim_instance = bdsim_model.WAVEFORM(
                    wave=self.properties.get("Wave Type", "square"),
                    freq=self.properties.get("Frequency", 1),
                    amplitude=self.properties.get("Amplitude", 1),
                    offset=self.properties.get("Offset", 0),
                    phase=self.properties.get("Phase", 0),
                    name=self.name,
                )
            elif self.block_type == "CONSTANT":
                self.bdsim_instance = bdsim_model.CONSTANT(
                    value=self.properties.get("Value", 0),
                    name=self.name,
                )
            elif self.block_type == "LTI":
                self.bdsim_instance = bdsim_model.LTI_SISO(
                    N=self.properties.get("Numerator", [1]),
                    D=self.properties.get("Denominator", [1, 1]),
                    name=self.name,
                )
            else:
                print(f"Unsupported block type: {self.block_type}")
        except Exception as e:
            print(f"Error creating bdsim instance for {self.name}: {e}")

    def add_ports(self):
        """Add ports to the block based on its type."""
        port_spacing = 20  # Space between ports

        # Define ports based on the block type
        if self.block_type == "STEP":
            num_inputs, num_outputs = 0, 1  # STEP block only has an output port
            self.properties = {"Amplitude": 1, "Start Time": 0}
        elif self.block_type == "GAIN":
            num_inputs, num_outputs = 1, 1
            self.properties = {"Gain": 1}
        elif self.block_type == "SUM":
            num_inputs, num_outputs = 2, 1
            self.properties = {"Inputs": "+-"}
        elif self.block_type == "SCOPE":
            num_inputs, num_outputs = 1, 0
            self.properties = {"Style": "Line"}
        elif self.block_type == "RAMP":
            num_inputs, num_outputs = 0, 1
            self.properties = {"Start Time": 0, "Slope": 1}
        elif self.block_type == "WAVEFORM":
            num_inputs, num_outputs = 0, 1
            self.properties = {
                "Wave Type": "square",
                "Frequency": 1,
                "Amplitude": 1,
                "Offset": 0,
                "Phase": 0,
            }
        elif self.block_type == "CONSTANT":
            num_inputs, num_outputs = 0, 1
            self.properties = {"Value": 0}
        elif self.block_type == "LTI":
            num_inputs, num_outputs = 1, 1
            self.properties = {"Numerator": [1], "Denominator": [1, 1]}
        else:
            num_inputs, num_outputs = 0, 0  # Default for unknown types

        # Clear existing ports
        self.input_ports = []
        self.output_ports = []

        # Create input ports
        for i in range(num_inputs):
            port = Port(self, "input")
            port.setPos(self.rect().left() - 10, self.rect().top() + i * port_spacing + 10)
            self.input_ports.append(port)

        # Create output ports
        for i in range(num_outputs):
            port = Port(self, "output")
            port.setPos(self.rect().right(), self.rect().top() + i * port_spacing + 10)
            self.output_ports.append(port)

    def __del__(self):
        """Ensure all connected wires are removed when the block is deleted."""
        for port in self.input_ports + self.output_ports:
            port.remove_connected_wires()

    def itemChange(self, change, value):
        """Update ports when block is moved."""
        if change == QGraphicsItem.ItemPositionChange:
            try:
                for port in self.input_ports + self.output_ports:
                    if port:  # Check if port is valid
                        port.notify_wires()
            except Exception as e:
                print(f"Error updating port wires: {e}")
        return super().itemChange(change, value)


class Port(QGraphicsEllipseItem):
    def __init__(self, parent, port_type, radius=5):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius, parent)
        self.port_type = port_type
        self.setBrush(Qt.darkGray)
        self.connected_wires = []  # Track wires connected to this port

    def notify_wires(self):
        """Safely notify connected wires to update their positions."""
        try:
            for wire in self.connected_wires:
                if wire:  # Check if wire is valid
                    wire.update_position()
        except Exception as e:
            print(f"Error notifying wires: {e}")

    def remove_connected_wires(self):
        """Remove all wires connected to this port."""
        for wire in list(self.connected_wires):  # Use a copy of the list
            if wire:  # Check if wire is not None
                wire.remove_wire()
        self.connected_wires.clear()  # Clear the list

    def __del__(self):
        """Safely clean up ports and wires."""
        try:
            for port in self.input_ports + self.output_ports:
                if port:  # Check if port is valid
                    port.remove_connected_wires()
        except Exception as e:
            logging.error(f"Error during block deletion: {e}")


