from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit


class PropertiesEditor(QWidget):
    """Widget for editing block properties."""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Properties")
        self.layout.addWidget(self.title_label)

        # Dynamically populated inputs
        self.property_inputs = {}

    def set_block(self, block):
        """Set the block whose properties to edit."""
        # Clear existing properties
        for widget in self.property_inputs.values():
            self.layout.removeWidget(widget)
            widget.deleteLater()

        self.property_inputs.clear()

        # Populate new properties
        if block and block.properties:
            self.title_label.setText(block.name)
            for prop_name, prop_value in block.properties.items():
                label = QLabel(prop_name)
                input_field = QLineEdit(str(prop_value))
                input_field.editingFinished.connect(
                    lambda pn=prop_name, field=input_field: self.update_property(block, pn, field)
                )
                self.layout.addWidget(label)
                self.layout.addWidget(input_field)
                self.property_inputs[prop_name] = input_field

    def update_property(self, block, prop_name, input_field):
        """Update the property of the block."""
        block.properties[prop_name] = input_field.text()
