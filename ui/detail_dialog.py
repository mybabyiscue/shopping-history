from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt


class DetailDialog(QDialog):
    def __init__(self, records, parent=None):
        super().__init__(parent)
        self.setWindowTitle("汇总详情")
        self.setMinimumWidth(800)
        self.resize(1000, 600)  # 设置初始窗口大小
        self.setup_ui(records)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'table'):
            self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def setup_ui(self, records):
        layout = QVBoxLayout(self)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "记录ID", "物品", "用途", "平台", "总价", 
            "数量", "是否收到", "是否开票", "购买日期"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        # 设置列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 填充数据
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            columns = [
                "记录ID", "物品", "用途", "平台", "总价", 
                "数量", "是否收到", "是否开票", "购买日期"
            ]
            for col, key in enumerate(columns):
                item = QTableWidgetItem(record.get(key, ""))
                if key in ["是否收到", "是否开票"]:
                    item.setTextAlignment(Qt.AlignCenter)
                    if record.get(key) == "否":
                        item.setForeground(QtGui.QColor(200, 0, 0))
                self.table.setItem(row, col, item)

        layout.addWidget(self.table)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, 0, Qt.AlignRight)