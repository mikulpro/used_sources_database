import sys

import requests
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
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
        self.initUI()

    def initUI(self):
        # Layout
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

        # Request Body Input
        self.request_body = QTextEdit(self)
        layout.addWidget(QLabel("Request Body:"))
        layout.addWidget(self.request_body)

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

    def sendRequest(self):
        url = self.url_input.text()
        method = self.method_selector.currentText()
        data = self.request_body.toPlainText()

        try:
            response = getattr(requests, method.lower())(url, data=data)
            self.response_display.setText(response.text)
        except Exception as e:
            self.response_display.setText(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HttpRequestTester()
    ex.show()
    sys.exit(app.exec_())
