from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
import uuid
import csv
from datetime import datetime


class SummaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建汇总")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 汇总名称
        layout.addWidget(QLabel("汇总名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入汇总名称")
        layout.addWidget(self.name_input)

        # 汇总备注
        layout.addWidget(QLabel("备注:"))
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("可选")
        layout.addWidget(self.note_input)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "错误", "汇总名称不能为空")
            return
        self.accept()

    def get_summary_data(self):
        return {
            "summary_id": str(uuid.uuid4()),
            "name": self.name_input.text().strip(),
            "note": self.note_input.text().strip(),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reimbursed": "否"
        }