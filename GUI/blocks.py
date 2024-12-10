from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem
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
        self.properties = properties or {}
        self.bdsim_instance = None

        # Assign a unique name
        if block_type not in Block.instance_counter:
            Block.instance_counter[block_type] = 1
        else:
            Block.instance_counter[block_type] += 1
        self.name = f"{block_type} {Block.instance_counter[block_type]}"

        # Add ports dynamically based on block type
        self.input_ports = []
        self.output_ports = []
        self.add_ports()

    def add_ports(self):
        """Add ports to the block based on its type."""
        port_spacing = 20  # Space between ports

        # Define ports based on the block type
        if self.block_type == "STEP":
            num_inputs, num_outputs = 0, 1
        elif self.block_type == "GAIN":
            num_inputs, num_outputs = 1, 1
        elif self.block_type == "SUM":
            num_inputs, num_outputs = 2, 1
        elif self.block_type == "SCOPE":
            num_inputs, num_outputs = 1, 0
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

    def update_ports(self):
        """Update port positions when the block is moved."""
        for i, port in enumerate(self.input_ports):
            port.setPos(self.rect().left() - 10, self.rect().top() + i * 20 + 10)
        for i, port in enumerate(self.output_ports):
            port.setPos(self.rect().right(), self.rect().top() + i * 20 + 10)

    def itemChange(self, change, value):
        """Handle block movement and update port positions."""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.update_ports()
            for wire in self.scene().items():
                if isinstance(wire, Wire):
                    wire.update_position()
        return super().itemChange(change, value)


class Port(QGraphicsEllipseItem):
    """A port on a block."""
    def __init__(self, parent, port_type, radius=10):
        super().__init__(-radius / 2, -radius / 2, radius, radius, parent)
        self.setBrush(Qt.darkGray)
        self.port_type = port_type  # Either "input" or "output"
        self.setZValue(1)  # Ensure ports are always on top


class Wire(QGraphicsLineItem):
    """Represents a wire connecting two ports."""
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.setPen(QPen(QColor("black"), 2))
        self.update_position()

    def update_position(self):
        """Update the wire's position."""
        start = self.start_port.scenePos() + QPointF(self.start_port.rect().width() / 2, self.start_port.rect().height() / 2)
        end = self.end_port.scenePos() + QPointF(self.end_port.rect().width() / 2, self.end_port.rect().height() / 2)
        self.setLine(QLineF(start, end))

    def create_bdsim_connection(self, bdsim_model):
        """Connect bdsim blocks via ports."""
        start_block = self.start_port.parentItem()
        end_block = self.end_port.parentItem()
        if (
            start_block.bdsim_instance
            and end_block.bdsim_instance
            and self.start_port.port_type == "output"
            and self.end_port.port_type == "input"
        ):
            bdsim_model.connect(start_block.bdsim_instance, end_block.bdsim_instance)
