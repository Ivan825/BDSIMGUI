from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea


class PropertiesEditor(QWidget):
    """Widget to display and edit block properties."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add a scroll area for better usability
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QFormLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)

        self.layout.addWidget(self.scroll_area)

    def set_block(self, block):
        """Set the properties of the selected block."""
        # Clear the previous properties
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add properties for the selected block
        block_label = QLabel(f"{block.name}")
        self.scroll_layout.addRow(block_label)

        for prop, value in block.properties.items():
            label = QLabel(prop)
            input_field = QLineEdit(str(value))

            # Use lambda with default argument to avoid reference issues
            input_field.editingFinished.connect(
                lambda p=prop, field=input_field: self.update_property(block, p, field.text())
            )
            self.scroll_layout.addRow(label, input_field)

    def update_property(self, block, prop, value):
        """Update the property of the block."""
        try:
            # Convert value to its original type
            block.properties[prop] = type(block.properties[prop])(value)
        except ValueError:
            block.properties[prop] = value

    def update_properties(self, block):
        """Update properties based on the selected block."""
        self.clear()  # Remove existing property fields
        self.block = block

        if not self.block:
            return

        self.add_item(QLabel(f"Properties for {block.name}"))
        for prop_name, prop_value in block.properties.items():
            label = QLabel(prop_name)
            input_field = QLineEdit(str(prop_value))
            input_field.editingFinished.connect(
                lambda name=prop_name, field=input_field: self.update_block_property(name, field)
            )
            self.add_item(label)
            self.add_item(input_field)

