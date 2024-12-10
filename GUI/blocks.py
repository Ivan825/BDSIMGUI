from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QLineF


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
        self.properties = properties or {}  # Editable properties
        self.bdsim_instance = None

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
        """Create a bdsim instance for this block."""
        if self.block_type == "STEP":
            self.bdsim_instance = bdsim_model.STEP(
                T=float(self.properties.get("Start Time", 0)),
                A=float(self.properties.get("Amplitude", 1)),
                name=self.name,
            )
        elif self.block_type == "GAIN":
            self.bdsim_instance = bdsim_model.GAIN(
                K=float(self.properties.get("Gain", 1)),
                name=self.name,
            )
        elif self.block_type == "SUM":
            self.bdsim_instance = bdsim_model.SUM(
                signs=self.properties.get("Signs", "+-"),
                name=self.name,
            )
        elif self.block_type == "SCOPE":
            self.bdsim_instance = bdsim_model.SCOPE(name=self.name)

    def add_ports(self):
        """Add ports to the block based on its type."""
        port_spacing = 20  # Space between ports

        # Define ports based on the block type
        if self.block_type == "STEP":
            num_inputs, num_outputs = 0, 1
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
        else:
            num_inputs, num_outputs = 0, 0  # Default for unknown types

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


class Port(QGraphicsEllipseItem):
    """A port on a block."""
    def __init__(self, parent, port_type, radius=10):
        super().__init__(-radius / 2, -radius / 2, radius, radius, parent)
        self.setBrush(Qt.darkGray)
        self.port_type = port_type  # Either "input" or "output"
        self.setZValue(1)  # Ensure ports are always on top
