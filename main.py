import sys
import os
import json
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QHeaderView, QTableWidget, QTableWidgetItem, QInputDialog, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QLineEdit, QSpinBox, QPushButton, QLabel, QSlider, QComboBox, QFormLayout, QDialog, QListWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QIntValidator
import subprocess


class MultiRollDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Multi-Roll")
        self.resize(800, 400)
        self.layout = QVBoxLayout(self)

        # Initialize table and buttons
        self.init_ui()

        # Apply dark theme from parent if available
        if parent and hasattr(parent, 'apply_dark_theme_to_dialog'):
            parent.apply_dark_theme_to_dialog(self)

    def init_ui(self):
        # Table for lists and results
        self.table = QTableWidget(0, 4)  # Start with no rows
        self.table.setHorizontalHeaderLabels(['List Name', 'Result', 'Delete', 'Lock'])
        self.layout.addWidget(self.table)
        
        self.init_table()
        
        # Button to add new rows
        self.add_button = QPushButton("Add Row", self)
        self.add_button.clicked.connect(self.add_row)
        self.layout.addWidget(self.add_button)

        # Button to start the roll process
        self.start_button = QPushButton("Start Roll", self)
        self.start_button.clicked.connect(self.start_roll)
        self.layout.addWidget(self.start_button)

    def init_table(self):
        self.add_row()  # Start with one row
        
        # Setting fixed column widths for 'List Name' and 'Delete'
        self.table.setColumnWidth(0, 250)  # 'List Name'
        self.table.setColumnWidth(2, 150)  # 'Delete'
        self.table.setColumnWidth(3, 150)  # 'Lock'
        
        # Setting the 'Result' column to dynamically resize with the window
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 'Result' column stretches

        # Adjust the height of the rows
        default_row_height = 30
        self.table.verticalHeader().setDefaultSectionSize(default_row_height)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStyleSheet(self.get_header_style())

    def get_header_style(self):
        # Ensure the font size can be retrieved from the main window settings or set a default
        font_size = self.parent().current_font_size if hasattr(self.parent(), 'current_font_size') else 12
        return f"""
        QHeaderView::section {{
            background-color: #353535;  # Dark gray background
            color: white;               # White text
            border: none;
            padding-left: 4px;
            font-size: {font_size}px;   # Use dynamic or default font size
        }}
        """

    
    @staticmethod
    def apply_dark_theme_to_combobox(combobox):
        combobox.setStyleSheet("""
            QComboBox, QAbstractItemView {
                color: white;
                background-color: #353535; /* Dark background */
                selection-background-color: #6a6ea9; /* Color for selected items */
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: url('path/to/your/down_arrow_icon.png'); /* Path to the icon */
            }
        """)

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Adding a combo box with list selections
        list_selector = QComboBox()
        MultiRollDialog.apply_dark_theme_to_combobox(list_selector)
        list_selector.addItems(self.parent().get_saved_lists())
        self.table.setCellWidget(row_position, 0, list_selector)

        # Placeholder for result display
        self.table.setItem(row_position, 1, QTableWidgetItem(""))

        # Delete button for the row
        delete_btn = QPushButton("X")
        delete_btn.clicked.connect(lambda: self.delete_row(row_position))
        self.table.setCellWidget(row_position, 2, delete_btn)

        # Checkbox for locking the row
        lock_checkbox = QCheckBox()
        checkbox_container = QWidget()  # Create a container widget
        checkbox_layout = QHBoxLayout(checkbox_container)  # Create a horizontal box layout
        checkbox_layout.addWidget(lock_checkbox)  # Add the checkbox to the layout
        checkbox_layout.setAlignment(Qt.AlignCenter)  # Center the checkbox in the layout
        checkbox_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to ensure it stays centered
        self.table.setCellWidget(row_position, 3, checkbox_container)  # Add the container to the table

    def delete_row(self, row):
        if self.table.rowCount() > 1:
            self.table.removeRow(row)

    def start_roll(self):
        for row in range(self.table.rowCount()):
            checkbox_container = self.table.cellWidget(row, 3)  # Get the container widget
            checkbox = checkbox_container.layout().itemAt(0).widget()  # Access the QCheckBox from the layout
            if not checkbox.isChecked():  # Check if the lock checkbox is not checked
                self.finish_roll(row)


    def finish_roll(self, row):
        list_name = self.table.cellWidget(row, 0).currentText()
        result = self.roll_for_list(list_name)
        self.table.item(row, 1).setText(result)

    def roll_for_list(self, list_name):
        weighted_options = self.fetch_list_data(list_name)
        if not weighted_options:
            return "No data available"
        options, weights = zip(*weighted_options)  # Separate the options and weights
        result = random.choices(options, weights=weights, k=1)[0]  # Use random.choices to consider weights
        return result



    def fetch_list_data(self, list_name):
        path = os.path.join(self.parent().lists_directory, f"{list_name}.json")
        try:
            with open(path, 'r') as file:
                data = json.load(file)
                return [(item[0], item[1]) for item in data]  # Adjust to handle new data format
        except FileNotFoundError:
            return []



class HandCursorButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCursor(Qt.PointingHandCursor)
        
class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setPalette(parent.dark_palette)  # Apply the dark palette from the parent
        self.setStyleSheet("""
            QWidget {
                color: white;
                background-color: #232323;
            }
            QPushButton {
                background-color: #464646;
                color: white;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                padding: 6px;
                min-width: 80px;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
                border-style: inset;
            }
            QComboBox, QLineEdit, QSpinBox, QLabel {
                color: white;
                background-color: #2c2c2c;
            }
        """)  # Apply consistent styling

        layout = QFormLayout(self)


        # Duration setting
        self.duration_input = QLineEdit("5")
        self.duration_input.setValidator(QIntValidator(1, 3600))
        layout.addRow("Duration (seconds):", self.duration_input)

        # Sort Order Selection
        self.sort_order_selection = QComboBox()
        self.sort_order_selection.addItems(["Alphabetical", "Weight"])
        layout.addRow("Sort Order:", self.sort_order_selection)

        # Font Size Setting
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 30)
        self.font_size_input.setValue(14)
        layout.addRow("Font Size:", self.font_size_input)

        # Save settings button
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        layout.addRow(save_button)

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
            'duration': int(self.duration_input.text()),
            'sort_order': self.sort_order_selection.currentText(),
            'font_size': self.font_size_input.value()
        }

        # Save the settings to a JSON file
        with open('settings.json', 'w') as file:
            json.dump(settings, file)

        self.parent().apply_settings(settings)
        self.accept()  # Close the dialog after saving settings

    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.duration_input.setText(str(settings.get('duration', 5)))
                self.sort_order_selection.setCurrentText(settings.get('sort_order', 'Alphabetical'))
                self.font_size_input.setValue(settings.get('font_size', 14))
        except FileNotFoundError:
            pass  # If the file is not found, default settings will be used


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

        # Set up dark palette
        self.dark_palette = self.get_dark_palette()
        self.setPalette(self.dark_palette)
        self.setStyleSheet(self.get_dark_style_sheet())

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
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_option)
        option_layout.addWidget(self.add_button)
        layout.addLayout(option_layout)

        self.save_button = QPushButton('Save List')
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_options)

        self.load_combobox = QComboBox()
        self.load_combobox.addItem("Select a list to load")
        self.load_combobox.addItems(self.get_saved_lists())
        self.load_combobox.activated[str].connect(self.load_options)

        self.delete_list_button = QPushButton('Delete List')
        self.delete_list_button.setCursor(Qt.PointingHandCursor)
        self.delete_list_button.clicked.connect(self.delete_list)

        self.new_list_button = QPushButton('New List')
        self.new_list_button.setCursor(Qt.PointingHandCursor)
        self.new_list_button.clicked.connect(self.new_list)

        save_load_layout = QHBoxLayout()
        save_load_layout.addWidget(self.load_combobox)
        save_load_layout.addWidget(self.save_button)
        save_load_layout.addWidget(self.new_list_button)
        save_load_layout.addWidget(self.delete_list_button)
        layout.addLayout(save_load_layout)

        self.display_area = QLabel("Your options will appear here!")
        self.display_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.display_area)

        self.options_list = QListWidget()
        self.options_list.setSelectionMode(QListWidget.MultiSelection)
        self.options_list.itemDoubleClicked.connect(self.edit_option)
        layout.addWidget(self.options_list)

        self.start_button = QPushButton('Start')
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self.start_decision_process)
        layout.addWidget(self.start_button)

        action_buttons_layout = QHBoxLayout()
        self.selectAllCheckBox = QCheckBox("Select/Deselect All")
        self.selectAllCheckBox.stateChanged.connect(self.toggle_select_all)
        action_buttons_layout.addWidget(self.selectAllCheckBox)

        self.delete_button = QPushButton('Delete Option(s)')
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self.delete_selected_options)
        action_buttons_layout.addWidget(self.delete_button)

        layout.addLayout(action_buttons_layout) 

        # Add Multi-Roll button
        self.multi_roll_button = QPushButton("Multi-Roll", self)
        self.multi_roll_button.setCursor(Qt.PointingHandCursor)
        self.multi_roll_button.clicked.connect(self.open_multi_roll_dialog)
        layout.addWidget(self.multi_roll_button)  # Add the Multi-Roll button to the layout

        self.settings_button = QPushButton('Settings')
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.clicked.connect(self.show_settings_dialog)
        layout.addWidget(self.settings_button)

        central_widget.setLayout(layout)

    def open_multi_roll_dialog(self):
        dialog = MultiRollDialog(self)
        dialog.exec_()

    def new_list(self):
        self.options = []  # Clear current options
        self.refresh_options_list()
        self.load_combobox.setCurrentIndex(0)  # Reset to the default "Select a list to load"


    def toggle_select_all(self, state):
        is_checked = state == Qt.Checked
        for index in range(self.options_list.count()):
            item = self.options_list.item(index)
            item.setSelected(is_checked)
            
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
            options = [opt.strip() for opt in option_text.split(',') if opt.strip()]
            for opt in options:
                self.options.append((opt, weight))
            self.option_input.clear()
            self.weight_input.setValue(1)
            self.refresh_options_list()

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
                
    def refresh_options_list(self):
        if self.sort_order == 'Weight':
            # Sort by weight (highest first) and then alphabetically
            self.options.sort(key=lambda x: (-x[1], x[0]))
        else:
            # Default alphabetical sort
            self.options.sort(key=lambda x: x[0])

        self.options_list.clear()
        for option_text, weight in self.options:
            self.options_list.addItem(f"{option_text} (Weight: {weight})")

    def load_options(self, list_name):
        if list_name == "Select a list to load" or not list_name.strip():
            return
        file_path = os.path.join(self.lists_directory, f"{list_name}.json")
        try:
            with open(file_path, 'r') as file:
                self.options = json.load(file)
                self.refresh_options_list()
        except FileNotFoundError:
            print(f"No saved list file found for {file_path}.")

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)  # Remove the current_theme argument
        dialog.exec_()

    def apply_settings(self, settings):
        self.duration = settings.get('duration', 5) * 1000
        theme = settings.get('theme', 'Dark')
        self.current_theme = settings.get('theme', 'Dark')  # Update current theme

        # Check if the theme has changed and apply the new theme
        current_theme = "Dark" if self.palette() == self.dark_palette else "Light"
        if theme != current_theme:
            if theme == "Light":
                self.apply_light_theme()
            else:
                self.apply_dark_theme()

        self.sort_order = settings.get('sort_order', 'Alphabetical')
        self.refresh_options_list()  # Refresh the list to apply new sort order

        font_size = settings.get('font_size', 14)
        self.apply_font_size(font_size)

    def apply_font_size(self, font_size):
        self.current_font_size = font_size

        # Update the font for the application
        app_font = QApplication.instance().font()
        app_font.setPointSize(font_size)
        QApplication.instance().setFont(app_font)

        # Update the display_area font to be font_size + 10
        display_font = self.display_area.font()
        display_font.setPointSize(font_size + 10)  # Increase the font size for display_area
        self.display_area.setFont(display_font)

        # Update the styles to reflect the new font size
        if self.palette() == self.dark_palette:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def update_widget_fonts(self, widget, font):
        if isinstance(widget, QWidget):  # Ensure widget is an instance of QWidget
            widget.setFont(font)
            for child in widget.children():
                self.update_widget_fonts(child, font)

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

        # Update the style for the checkbox text color
        self.selectAllCheckBox.setStyleSheet("QCheckBox { color: white; }")

        # Apply the palette to the application
        self.setPalette(palette)

        # Update the label style directly
        self.display_area.setStyleSheet("QLabel { color : yellow;}")
        
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
                padding: 8px;
            }}
            QPushButton:pressed {{
                background-color: {buttonColor.lighter().name()};
                border-style: inset;
            }}
        """
        self.setStyleSheet(button_style)
        self.set_custom_style(self.dark_palette, self.current_font_size, QColor(70, 70, 70), QColor(Qt.white))
            
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

    def get_dark_style_sheet(self):
        return """
            QPushButton {
                background-color: #464646;
                color: white;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                padding: 6px;
                min-width: 80px;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
                border-style: inset;
            }
            QComboBox, QLineEdit, QSpinBox, QLabel, QCheckBox, QTableWidget {
                color: white;
                background-color: #2c2c2c;
            }
            QHeaderView::section {
                background-color: #353535;
                color: white;
                padding-left: 4px;
                border: none;
            }
        """

    def apply_dark_theme_to_dialog(self, dialog):
        # Set the palette for dark theme
        dialog.setPalette(self.dark_palette)
        # Apply a consistent style sheet for the dialog
        dialog.setStyleSheet("""
            QWidget {
                color: white;
                background-color: #232323;
            }
            QPushButton {
                background-color: #464646;
                color: white;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                padding: 6px;
                min-width: 80px;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
                border-style: inset;
            }
            QComboBox, QLineEdit, QSpinBox {
                color: white;
                background-color: #2c2c2c;
            }
        """)
            
    def apply_light_theme(self):
        self.setPalette(QApplication.style().standardPalette())

        self.display_area.setStyleSheet("QLabel { color: red;}")

        self.selectAllCheckBox.setStyleSheet("QCheckBox { color: black; }")
        self.set_custom_style(QApplication.style().standardPalette(), self.current_font_size, QColor(255, 255, 255), QColor(0, 0, 0))

    def set_custom_style(self, palette, font_size, button_color, text_color):
        self.setPalette(palette)
        # Dynamically setting the font size in the style sheet
        button_style = f"""
            QPushButton {{
                font-size: {font_size}px;
                background-color: {button_color.name()};
                color: {text_color.name()};
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                padding: 8px;
            }}
            QPushButton:pressed {{
                background-color: {button_color.lighter().name()};
                border-style: inset;
            }}
        """
        self.setStyleSheet(button_style)
def main():
    app = QApplication(sys.argv)
    main_window = DecisionMaker9000()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()