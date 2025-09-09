from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt
from ui.record_dialog import RecordDialog


class DetailDialog(QDialog):
    def __init__(self, data, parent=None):
        """
        data: {
            "summary_info": {
                "汇总ID": str,
                "汇总名称": str,
                "汇总备注": str,
                "汇总时间": str,
                "是否报销": str
            },
            "related_records": list[dict]  # 相关记录列表
        }
        """
        super().__init__(parent)
        self.setWindowTitle("汇总详情")
        self.setMinimumWidth(800)
        self.resize(1000, 600)
        self.setup_ui(data)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'table'):
            self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def on_add_record(self):
        """添加新记录"""
        dialog = RecordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "提示", "记录添加成功")
            # 刷新表格数据
            if hasattr(self.parent(), 'load_data'):
                self.parent().load_data()

    def setup_ui(self, data):
        layout = QVBoxLayout(self)
        
        # 汇总信息区域
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel(f"<b>汇总名称:</b> {data['summary_info']['汇总名称']}"))
        summary_layout.addWidget(QLabel(f"<b>汇总时间:</b> {data['summary_info']['汇总时间']}"))
        summary_layout.addWidget(QLabel(f"<b>是否报销:</b> {data['summary_info']['是否报销']}"))
        layout.addLayout(summary_layout)
        
        if data['summary_info']['汇总备注']:
            layout.addWidget(QLabel(f"<b>备注:</b> {data['summary_info']['汇总备注']}"))

        # 记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "记录ID", "物品", "用途", "平台", "总价", 
            "数量", "是否收到", "是否开票", "购买日期"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 填充记录数据（按购买日期降序排序）
        records = []
        current_summary_id = str(data['summary_info']['汇总ID']).strip()
        # print(f"DEBUG: 当前对话框汇总ID: {current_summary_id}")
        
        for r in data['related_records']:
            record_summary_id = str(r.get("汇总ID", "")).strip()
            # print(f"DEBUG: 检查记录 {r['记录ID']} - 汇总ID: {record_summary_id}")
            if record_summary_id == current_summary_id:
                records.append(r)
                # print(f"DEBUG: 匹配记录 {r['记录ID']} - 汇总ID: {record_summary_id}")
        
        records = sorted(records, key=lambda x: x.get("购买日期", ""), reverse=True)
        # print(f"DEBUG: 最终展示 {len(records)} 条记录 (期望汇总ID: {current_summary_id})")
        if len(records) == 0:
            print("DEBUG: 警告：没有找到匹配的记录！")
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

        # 底部按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.on_add_record)
        btn_layout.addWidget(add_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)