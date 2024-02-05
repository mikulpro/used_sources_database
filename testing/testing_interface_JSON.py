import json
import sys

import requests
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class HttpRequestTester(QWidget):
    def __init__(self):
        super().__init__()
        self.response_display = None
        self.select_file_btn = None
        self.file_path_label = None
        self.method_selector = None
        self.url_input = None
        self.url_input = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # URL Input
        self.url_input = QLineEdit(self)
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(self.url_input)

        # Method Selection
        self.method_selector = QComboBox(self)
        self.method_selector.addItems(["GET", "POST", "PUT", "DELETE"])
        layout.addWidget(QLabel("Method:"))
        layout.addWidget(self.method_selector)

        # File Selection for JSON
        self.file_path_label = QLabel("No file selected")
        self.select_file_btn = QPushButton("Select JSON File", self)
        self.select_file_btn.clicked.connect(self.selectFile)
        layout.addWidget(self.select_file_btn)
        layout.addWidget(self.file_path_label)

        # Send Button
        send_btn = QPushButton("Send Request", self)
        send_btn.clicked.connect(self.sendRequest)
        layout.addWidget(send_btn)

        # Response Display
        self.response_display = QTextEdit(self)
        self.response_display.setReadOnly(True)
        layout.addWidget(QLabel("Response:"))
        layout.addWidget(self.response_display)

        self.setLayout(layout)
        self.setWindowTitle("HTTP Request Tester")

    def selectFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select JSON file", "", "JSON Files (*.json)"
        )
        if file_path:
            self.file_path_label.setText(file_path)

    def sendRequest(self):
        url = self.url_input.text()
        method = self.method_selector.currentText()
        file_path = self.file_path_label.text()

        try:
            data = {}
            if file_path and file_path != "No file selected":
                with open(file_path, "r") as file:
                    data = json.load(file)

            response = getattr(requests, method.lower())(url, json=data)
            self.response_display.setText(response.text)
        except Exception as e:
            self.response_display.setText(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HttpRequestTester()
    ex.show()
    sys.exit(app.exec_())
