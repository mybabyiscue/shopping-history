from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt
from ui.record_dialog import RecordDialog
import csv
import os
from functools import partial  # 修复闭包问题

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
            "related_records": list[dict],  # 相关记录列表
            "parent_tab": ReimbursementTab # 父级报销记录Tab
        }
        """
        super().__init__(parent)
        self.parent_tab = data.get("parent_tab")
        self.setWindowTitle("汇总详情")
        self.setMinimumWidth(800)
        self.resize(1000, 600)
        self.setup_ui(data)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 移除自动调整策略，避免影响按钮布局

    def refresh_data(self):
        """刷新表格数据"""
        try:
            # 重新加载当前汇总的记录
            records_path = os.path.join("data", "records.csv")
            if not os.path.exists(records_path):
                QMessageBox.information(self, "提示", "没有找到记录文件")
                return

            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)

            # 筛选当前汇总的记录
            current_summary_id = str(self.parent_tab.current_summary_id).strip()
            filtered_records = [
                r for r in records 
                if str(r.get("汇总ID", "")).strip() == current_summary_id
            ]
            filtered_records = sorted(filtered_records, key=lambda x: x.get("购买日期", ""), reverse=True)

            # 更新表格数据
            self.table.setRowCount(len(filtered_records))
            for row, record in enumerate(filtered_records):
                columns = [
                    "记录ID", "物品", "用途", "平台", "总价", "数量", "是否收到", "是否开票", "购买日期"
                ]
                for col, key in enumerate(columns):
                    item = QTableWidgetItem(record.get(key, ""))
                    if key in ["是否收到", "是否开票"]:
                        item.setTextAlignment(Qt.AlignCenter)
                        if record.get(key) == "否":
                            item.setForeground(QtGui.QColor(200, 0, 0))
                    self.table.setItem(row, col, item)

                # 更新删除按钮
                btn_widget = QtWidgets.QWidget()
                btn_layout = QtWidgets.QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                delete_btn = QPushButton("删除")
                delete_btn.setFixedSize(60, 32)
                delete_btn.clicked.connect(partial(self.delete_record, record["记录ID"]))
                btn_layout.addWidget(delete_btn)
                btn_layout.setAlignment(Qt.AlignCenter)
                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(row, 9, btn_widget)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据失败: {str(e)}")

    def delete_record(self, record_id):
        """从当前汇总移除记录(清空汇总ID)"""
        reply = QMessageBox.question(
            self, '确认移除',
            '确定要将此记录从当前汇总移除吗?\n(记录不会被删除，只是不再属于此汇总)',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            records_path = os.path.join("data", "records.csv")
            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)
            # 更新指定记录的汇总ID为空
            for record in records:
                if record["记录ID"] == record_id:
                    record["汇总ID"] = ""
            with open(records_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(records)
            QMessageBox.information(self, "成功", "记录已从当前汇总移除")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"移除记录失败: {str(e)}")

    def on_add_record(self):
        """添加新记录"""
        dialog = RecordDialog(self.parent_tab if self.parent_tab else self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "提示", "记录添加成功")
            self.refresh_data()

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
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "记录ID", "物品", "用途", "平台", "总价", "数量", "是否收到", "是否开票", "购买日期", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(9, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 填充记录数据（按购买日期降序排序）
        records = []
        current_summary_id = str(data['summary_info']['汇总ID']).strip()
        for r in data['related_records']:
            record_summary_id = str(r.get("汇总ID", "")).strip()
            if record_summary_id == current_summary_id:
                records.append(r)
        records = sorted(records, key=lambda x: x.get("购买日期", ""), reverse=True)

        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            columns = [
                "记录ID", "物品", "用途", "平台", "总价", "数量", "是否收到", "是否开票", "购买日期"
            ]
            for col, key in enumerate(columns):
                item = QTableWidgetItem(record.get(key, ""))
                if key in ["是否收到", "是否开票"]:
                    item.setTextAlignment(Qt.AlignCenter)
                    if record.get(key) == "否":
                        item.setForeground(QtGui.QColor(200, 0, 0))
                self.table.setItem(row, col, item)

            # 在操作列(第10列)添加删除按钮(使用QWidget包装)
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            delete_btn = QPushButton("删除")
            delete_btn.setFixedSize(60, 32)
            # 修复 lambda 闭包问题
            delete_btn.clicked.connect(partial(self.delete_record, record["记录ID"]))
            btn_layout.addWidget(delete_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 9, btn_widget)

        layout.addWidget(self.table)

        # 底部按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_data)
        btn_layout.addWidget(refresh_btn)

        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.on_add_record)
        btn_layout.addWidget(add_btn)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
