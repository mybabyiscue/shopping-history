import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QDialogButtonBox, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
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

        # 报销状态
        self.reimbursement_check = QCheckBox("是否报销")
        layout.addWidget(self.reimbursement_check)

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
        # 生成自增ID
        new_id = 1  # 默认ID
        summary_path = os.path.join("data", "summary.csv")
        
        try:
            if os.path.exists(summary_path):
                with open(summary_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames and "汇总ID" in reader.fieldnames:
                        valid_ids = []
                        for row in reader:
                            if row.get("汇总ID", "").isdigit():
                                valid_ids.append(int(row["汇总ID"]))
                        if valid_ids:
                            new_id = max(valid_ids) + 1
        except Exception:
            pass  # 如果出现任何错误，使用默认ID
            
        return {
            "summary_id": str(new_id),
            "name": self.name_input.text().strip(),
            "note": self.note_input.text().strip(),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reimbursed": self.reimbursement_check.isChecked()  # 返回布尔值，由调用方处理格式
        }