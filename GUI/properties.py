''' Block properties editor '''
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit

class PropertiesEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Placeholder widgets
        self.block_label = QLabel("No block selected")
        self.param_editor = QLineEdit()

        self.layout.addWidget(self.block_label)
        self.layout.addWidget(self.param_editor)
        self.setLayout(self.layout)

    def update_properties(self, block_name, properties):
        self.block_label.setText(f"Editing: {block_name}")
        self.param_editor.setText(str(properties))
