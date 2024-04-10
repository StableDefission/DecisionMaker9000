import sys
import os
import json
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QSpinBox, QPushButton, QLabel, QSlider, QComboBox, QFormLayout, QDialog, QListWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QIntValidator

class SettingsDialog(QDialog):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        
        layout = QFormLayout()

        self.duration_input = QLineEdit("5")
        self.duration_input.setValidator(QIntValidator(1, 3600))
        layout.addRow("Duration (seconds):", self.duration_input)

        self.theme_selection = QComboBox()
        self.theme_selection.addItems(["Dark", "Light"])
        layout.addRow("Theme:", self.theme_selection)

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        layout.addRow(save_button)

        self.setLayout(layout)

        # Call apply_theme after the layout is set
        self.apply_theme(theme)

        self.load_settings()

    def apply_theme(self, theme):
        if theme == "Dark":
            self.setPalette(self.parent().dark_palette)
            # Set text color to white for all labels in the form layout
            for i in range(self.layout().rowCount()):
                item = self.layout().itemAt(i, QFormLayout.LabelRole)
                if item is not None and item.widget() is not None:
                    item.widget().setStyleSheet("color: white;")
        elif theme == "Light":
            self.setPalette(self.parent().light_palette)
            for i in range(self.layout().rowCount()):
                item = self.layout().itemAt(i, QFormLayout.LabelRole)
                if item is not None and item.widget() is not None:
                    item.widget().setStyleSheet("color: black;")  # Assuming default text color for light theme

    def save_settings(self):
        settings = {
            'duration': int(self.duration_input.text() or 5),
            'theme': self.theme_selection.currentText()
        }
        with open('settings.json', 'w') as file:
            json.dump(settings, file)
        self.parent().apply_settings(settings)  # Apply settings immediately
        self.accept()  # Close the dialog

    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.duration_input.setText(str(settings.get('duration', 5)))
                self.theme_selection.setCurrentText(settings.get('theme', 'Dark'))
        except FileNotFoundError:
            pass

class DecisionMaker9000(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DecisionMaker9000')
        self.setGeometry(100, 100, 800, 600)
        
        self.lists_directory = 'lists'
        os.makedirs(self.lists_directory, exist_ok=True)
        
        self.options = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)

        self.dark_palette = self.get_dark_palette()
        self.light_palette = QApplication.style().standardPalette()

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.option_input = QLineEdit()
        self.weight_input = QSpinBox()
        self.weight_input.setMinimum(1)
        self.weight_input.setValue(1)
        option_layout = QHBoxLayout()
        option_layout.addWidget(self.option_input)
        option_layout.addWidget(self.weight_input)
        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_option)
        option_layout.addWidget(self.add_button)
        layout.addLayout(option_layout)

        self.save_button = QPushButton('Save List')
        self.save_button.clicked.connect(self.save_options)

        self.load_combobox = QComboBox()
        self.load_combobox.addItem("Select a list to load")
        self.load_combobox.addItems(self.get_saved_lists())
        self.load_combobox.activated[str].connect(self.load_options)

        self.delete_list_button = QPushButton('Delete List')  # New delete button for the list
        self.delete_list_button.clicked.connect(self.delete_list)  # Connect to the delete_list method

        save_load_layout = QHBoxLayout()
        save_load_layout.addWidget(self.save_button)
        save_load_layout.addWidget(self.load_combobox)
        save_load_layout.addWidget(self.delete_list_button)  # Add the delete button to the layout
        layout.addLayout(save_load_layout)

        self.display_area = QLabel("Your options will appear here!")
        self.display_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.display_area)

        self.options_list = QListWidget()
        self.options_list.setSelectionMode(QListWidget.MultiSelection)  # Enable multiple selection
        self.options_list.itemDoubleClicked.connect(self.edit_option)
        layout.addWidget(self.options_list)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_decision_process)
        layout.addWidget(self.start_button)

        self.delete_button = QPushButton('Delete Option(s)')
        self.delete_button.clicked.connect(self.delete_selected_options)  # Connect the delete button
        layout.addWidget(self.delete_button)

        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.show_settings_dialog)
        layout.addWidget(self.settings_button)

        central_widget.setLayout(layout)

    def delete_list(self):
        list_name = self.load_combobox.currentText()
        if list_name and list_name != "Select a list to load":
            reply = QMessageBox.question(self, 'Delete List',
                                         f'Are you sure you want to delete the list "{list_name}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                file_path = os.path.join(self.lists_directory, f"{list_name}.json")
                try:
                    os.remove(file_path)
                    self.load_combobox.removeItem(self.load_combobox.currentIndex())
                    QMessageBox.information(self, 'Deleted', f'List "{list_name}" deleted successfully.')
                except FileNotFoundError:
                    QMessageBox.warning(self, 'Error', f'List "{list_name}" not found.')

    def add_option(self):
        option_text = self.option_input.text().strip()
        weight = self.weight_input.value()
        if option_text:
            # Split the input by commas to support multiple options
            options = [opt.strip() for opt in option_text.split(',') if opt.strip()]
            for opt in options:
                self.options.append((opt, weight))
                self.options_list.addItem(f"{opt} (Weight: {weight})")
            self.option_input.clear()
            self.weight_input.setValue(1)

    def edit_option(self, item):
        index = self.options_list.row(item)
        option_text, _ = self.options[index]
        new_weight, ok = QInputDialog.getInt(self, "Edit Weight", "Set new weight for option:", min=1)
        if ok:
            self.options[index] = (option_text, new_weight)
            item.setText(f"{option_text} (Weight: {new_weight})")

    def delete_selected_options(self):
        selected_items = self.options_list.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, 'Confirm Deletion', 'Are you sure you want to delete the selected options?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            while selected_items:
                item = selected_items.pop()
                index = self.options_list.row(item)
                del self.options[index]  # Remove from the options list
                self.options_list.takeItem(index)  # Remove from the QListWidget

    def start_decision_process(self):
        self.timer.start(100)
        QTimer.singleShot(self.duration, self.timer.stop)

    def update_display(self):
        if not self.options:
            self.display_area.setText("No options to display")
            return
        weighted_options = [opt for opt, weight in self.options for _ in range(weight)]
        random_option = random.choice(weighted_options)
        self.display_area.setText(random_option)

    def get_saved_lists(self):
        return [os.path.splitext(file)[0] for file in os.listdir(self.lists_directory) if file.endswith('.json')]

    def set_dialog_dark_theme(self, dialog):
        dialog.setPalette(self.dark_palette)
        dialog.setStyleSheet("color: white; background-color: {0};".format(self.dark_palette.color(QPalette.Window).name()))


    def save_options(self):
        # Get the currently loaded list name, but only use it to pre-fill the dialog
        current_list_name = self.load_combobox.currentText()
        if current_list_name == "Select a list to load":
            current_list_name = ""

        dialog = QInputDialog(self)
        dialog.setWindowTitle('Save List')
        dialog.setLabelText('Enter name for the list:')
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setTextValue(current_list_name)  # Pre-fill the dialog with the current list name, if any

        if self.palette() == self.dark_palette:
            self.set_dialog_dark_theme(dialog)

        result = dialog.exec_()
        list_name = dialog.textValue()

        if result == QDialog.Accepted and list_name:
            file_path = os.path.join(self.lists_directory, f"{list_name}.json")

            # Check if the list with the entered name already exists and prompt for overwrite
            if os.path.exists(file_path):
                reply = QMessageBox.question(
                    self, 'Overwrite List',
                    f'The list "{list_name}" already exists. Do you want to overwrite it?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return  # Do not proceed with saving if the user decides not to overwrite

            # Proceed with saving the list
            with open(file_path, 'w') as file:
                json.dump(self.options, file)

            # Update the combo box if the list name is not already present
            if list_name not in [self.load_combobox.itemText(i) for i in range(self.load_combobox.count())]:
                self.load_combobox.addItem(list_name)
            else:
                # If the list is being overwritten, we might need to update the list in the UI or other data structures as needed
                pass
                
    def load_options(self, list_name):
        if list_name == "Select a list to load" or not list_name.strip():
            return
        file_path = os.path.join(self.lists_directory, f"{list_name}.json")
        try:
            with open(file_path, 'r') as file:
                self.options = json.load(file)
                self.options_list.clear()
                for option_text, weight in self.options:
                    self.options_list.addItem(f"{option_text} (Weight: {weight})")
        except FileNotFoundError:
            print(f"No saved list file found for {file_path}.")

    def show_settings_dialog(self):
        current_theme = "Dark" if self.palette() == self.dark_palette else "Light"
        dialog = SettingsDialog(self, current_theme)
        dialog.exec_()

    def apply_settings(self, settings):
        self.duration = settings.get('duration', 5) * 1000
        theme = settings.get('theme', 'Dark')
        if theme == "Light":
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.apply_settings(settings)
        except FileNotFoundError:
            self.apply_dark_theme()  # Default to dark theme

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(50, 50, 50))
        palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        
        # Update the button color and text color for better contrast
        buttonColor = QColor(70, 70, 70)  # Dark grey
        textColor = QColor(Qt.white)  # White text color
        
        palette.setColor(QPalette.Button, buttonColor)
        palette.setColor(QPalette.ButtonText, textColor)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, textColor)
        
        # Apply the palette to the application
        self.setPalette(palette)

        # Update the label style directly
        self.display_area.setStyleSheet("QLabel { color : yellow; font: bold 24px;}")
        
        # Additional styling to improve button readability
        button_style = f"""
            QPushButton {{
                background-color: {buttonColor.name()};
                color: {textColor.name()};
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                font: bold 14px;
                min-width: 10em;
                padding: 6px;
            }}
            QPushButton:pressed {{
                background-color: {buttonColor.lighter().name()};
                border-style: inset;
            }}
        """
        self.setStyleSheet(button_style)
        
    def get_dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(50, 50, 50))
        palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(70, 70, 70))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        return palette
    
    def apply_light_theme(self):
        self.setPalette(QApplication.style().standardPalette())

def main():
    app = QApplication(sys.argv)
    main_window = DecisionMaker9000()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
