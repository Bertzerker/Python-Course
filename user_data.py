import sys
import json
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QFileDialog
)


class DataEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Person Data Editor")

        self.data = []
        self.current_index = -1

        # UI Elements
        self.person_selector = QComboBox()
        self.person_selector.currentIndexChanged.connect(self.on_person_changed)

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.food_input = QLineEdit()

        # Main buttons
        self.add_button = QPushButton("Add Person")
        self.add_button.clicked.connect(self.add_person)

        self.delete_button = QPushButton("Delete Person")
        self.delete_button.clicked.connect(self.delete_person)

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_current_data)

        self.show_button = QPushButton("Show All Data")
        self.show_button.clicked.connect(self.show_all_data)

        # File buttons
        self.save_file_button = QPushButton("Save to File")
        self.save_file_button.clicked.connect(self.save_to_file)

        self.load_file_button = QPushButton("Load from File")
        self.load_file_button.clicked.connect(self.load_from_file)

        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)

        # Layouts
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Person:"))
        layout.addWidget(self.person_selector)

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Age:"))
        layout.addWidget(self.age_input)

        layout.addWidget(QLabel("Favorite Food:"))
        layout.addWidget(self.food_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.show_button)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.save_file_button)
        file_layout.addWidget(self.load_file_button)
        file_layout.addWidget(self.export_csv_button)

        layout.addLayout(btn_layout)
        layout.addLayout(file_layout)
        self.setLayout(layout)

        self.add_person()  # Start with one person

    def on_person_changed(self, new_index):
        if 0 <= self.current_index < len(self.data):
            self.save_fields_to_data(self.current_index)
        self.current_index = new_index
        self.load_person_data()

    def add_person(self):
        self.data.append({"name": "", "age": "", "favorite_food": ""})
        self.person_selector.addItem(f"Person {len(self.data)}")
        self.person_selector.setCurrentIndex(len(self.data) - 1)

    def delete_person(self):
        if not self.data:
            QMessageBox.warning(self, "Warning", "No persons to delete.")
            return

        idx = self.person_selector.currentIndex()
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete Person {idx + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            del self.data[idx]
            self.person_selector.removeItem(idx)
            for i in range(self.person_selector.count()):
                self.person_selector.setItemText(i, f"Person {i + 1}")

            if self.data:
                self.person_selector.setCurrentIndex(0)
                self.current_index = 0
                self.load_person_data()
            else:
                self.clear_inputs()
                self.current_index = -1

    def load_person_data(self):
        if 0 <= self.current_index < len(self.data):
            person = self.data[self.current_index]
            self.name_input.setText(person["name"])
            self.age_input.setText(person["age"])
            self.food_input.setText(person["favorite_food"])
        else:
            self.clear_inputs()

    def save_fields_to_data(self, idx):
        if 0 <= idx < len(self.data):
            self.data[idx]["name"] = self.name_input.text()
            self.data[idx]["age"] = self.age_input.text()
            self.data[idx]["favorite_food"] = self.food_input.text()

    def validate_inputs(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        food = self.food_input.text().strip()

        if not name or not food:
            QMessageBox.warning(self, "Validation Error", "Name and favorite food cannot be empty.")
            return False
        if not age.isdigit():
            QMessageBox.warning(self, "Validation Error", "Age must be a number.")
            return False
        return True

    def save_current_data(self):
        if not self.validate_inputs():
            return
        if 0 <= self.current_index < len(self.data):
            self.save_fields_to_data(self.current_index)
            QMessageBox.information(self, "Saved", f"Data for Person {self.current_index + 1} saved.")
        else:
            QMessageBox.warning(self, "Warning", "No person selected to save.")

    def show_all_data(self):
        if not self.data:
            QMessageBox.information(self, "All Data", "No data to display.")
            return

        self.save_current_data()

        msg = "--- All Data ---\n"
        for i, person in enumerate(self.data, start=1):
            msg += f"Person {i}: Name: {person['name']}, Age: {person['age']}, Favorite Food: {person['favorite_food']}\n"
        QMessageBox.information(self, "All Data", msg)

    def save_to_file(self):
        self.save_current_data()
        path, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4)
                QMessageBox.information(self, "Saved", f"Data saved to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)

                self.person_selector.clear()
                for i in range(len(self.data)):
                    self.person_selector.addItem(f"Person {i + 1}")
                if self.data:
                    self.person_selector.setCurrentIndex(0)
                    self.current_index = 0
                    self.load_person_data()
                else:
                    self.clear_inputs()
                    self.current_index = -1

                QMessageBox.information(self, "Loaded", f"Loaded data from {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file:\n{str(e)}")

    def export_to_csv(self):
        self.save_current_data()
        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=["name", "age", "favorite_food"])
                    writer.writeheader()
                    writer.writerows(self.data)
                QMessageBox.information(self, "Exported", f"Data exported to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export to CSV:\n{str(e)}")

    def clear_inputs(self):
        self.name_input.clear()
        self.age_input.clear()
        self.food_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataEditor()
    window.show()
    sys.exit(app.exec())
