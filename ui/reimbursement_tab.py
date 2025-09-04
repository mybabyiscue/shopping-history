from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLabel, QDialog
)
from PyQt5.QtCore import Qt
import csv
import os


class ReimbursementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "汇总名称", "汇总备注", "汇总时间", "是否报销", "操作"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        # 设置自适应列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 汇总名称
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 汇总备注
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 汇总时间
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 是否报销
        
        # 操作列固定宽度
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 360)
        
        # 设置默认行高
        self.table.verticalHeader().setDefaultSectionSize(36)
        
        # 启用交替行颜色
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f8f8f8;
            }
        """)

        main_layout.addWidget(self.table)

    def load_data(self):
        """加载汇总数据"""
        try:
            summary_path = os.path.join("data", "summary.csv")
            if not os.path.exists(summary_path):
                self.table.setRowCount(0)
                return

            with open(summary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summaries = list(reader)
            
            summaries.sort(key=lambda x: x["汇总时间"], reverse=True)

            self.table.setRowCount(len(summaries))
            for row, summary in enumerate(summaries):
                item = QTableWidgetItem(summary["汇总名称"])
                item.setData(Qt.UserRole, summary["汇总ID"])  # 存储汇总ID
                self.table.setItem(row, 0, item)
                self.table.setItem(row, 1, QTableWidgetItem(summary["汇总备注"]))
                self.table.setItem(row, 2, QTableWidgetItem(summary["汇总时间"]))
                
                # 是否报销列
                item = QTableWidgetItem(summary["是否报销"])
                item.setTextAlignment(Qt.AlignCenter)
                if summary["是否报销"] == "否":
                    item.setForeground(QtGui.QColor(200, 0, 0))
                self.table.setItem(row, 3, item)

                # 操作列
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(5)

                view_btn = QPushButton("查看")
                view_btn.setFixedWidth(80)
                view_btn.clicked.connect(lambda _, r=row: 
                    self.view_details(self.table.item(r, 0).data(Qt.UserRole)))
                btn_layout.addWidget(view_btn)

                edit_btn = QPushButton("编辑")
                edit_btn.setFixedWidth(80)
                edit_btn.clicked.connect(lambda _, r=row: 
                    self.edit_summary(self.table.item(r, 0).data(Qt.UserRole)))
                btn_layout.addWidget(edit_btn)

                delete_btn = QPushButton("删除")
                delete_btn.setFixedWidth(80)
                delete_btn.clicked.connect(lambda _, r=row: 
                    self.delete_summary(self.table.item(r, 0).data(Qt.UserRole)))
                btn_layout.addWidget(delete_btn)

                # 将汇总ID存储在表格项的用户数据中
                self.table.item(row, 0).setData(Qt.UserRole, summary["汇总ID"])

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(row, 4, btn_widget)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")

    def view_details(self, summary_id):
        """查看汇总详情"""
        try:
            # 首先从summary.csv获取汇总基本信息
            summary_path = os.path.join("data", "summary.csv")
            if not os.path.exists(summary_path):
                QMessageBox.information(self, "提示", "没有找到汇总记录")
                return

            with open(summary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summary_info = next((s for s in reader if s["汇总ID"] == summary_id), None)
            
            if not summary_info:
                QMessageBox.information(self, "提示", "找不到指定的汇总记录")
                return

            # 然后从records.csv获取相关记录
            records_path = os.path.join("data", "records.csv")
            if not os.path.exists(records_path):
                QMessageBox.information(self, "提示", "没有找到相关记录")
                return

            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                related_records = []
                for r in reader:
                    record_summary_id = str(r.get("汇总ID", "")).strip()
                    current_summary_id = str(summary_id).strip()
                    if record_summary_id == current_summary_id:
                        related_records.append(r)

            # 创建详情窗口并传递汇总信息和相关记录（确保使用原始汇总ID）
            from ui.detail_dialog import DetailDialog
            dialog = DetailDialog({
                "summary_info": summary_info,
                "related_records": [r for r in related_records 
                                  if str(r.get('汇总ID', '')).strip() == str(summary_id).strip()]
            }, self)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看详情失败: {str(e)}")

    def edit_summary(self, summary_id):
        """编辑汇总信息"""
        try:
            summary_path = os.path.join("data", "summary.csv")
            with open(summary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summaries = list(reader)
            
            summary = next((s for s in summaries if s["汇总ID"] == summary_id), None)
            if not summary:
                QMessageBox.warning(self, "错误", "找不到指定的汇总记录")
                return

            from ui.summary_dialog import SummaryDialog
            dialog = SummaryDialog(self)
            dialog.name_input.setText(summary["汇总名称"])
            dialog.note_input.setText(summary["汇总备注"])
            dialog.reimbursement_check.setChecked(summary["是否报销"] == "是")
            dialog.setWindowTitle("编辑汇总")

            if dialog.exec_() == QDialog.Accepted:
                summary_data = dialog.get_summary_data()
                summary["汇总名称"] = summary_data["name"]
                summary["汇总备注"] = summary_data["note"]
                summary["是否报销"] = "是" if summary_data.get("reimbursed", False) else "否"
                
                # 更新文件
                with open(summary_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writer.writerows(summaries)

                QMessageBox.information(self, "成功", "汇总信息已更新")
                self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"编辑汇总失败: {str(e)}")

    def delete_summary(self, summary_id):
        """删除汇总记录"""
        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这条汇总记录吗?原始记录不会被删除。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            # 从summary.csv中删除记录
            summary_path = os.path.join("data", "summary.csv")
            with open(summary_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summaries = [s for s in reader if s["汇总ID"] != summary_id]

            with open(summary_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(summaries)

            # 将records.csv中对应的汇总ID置空
            records_path = os.path.join("data", "records.csv")
            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)

            for record in records:
                if record.get("汇总ID") == summary_id:
                    record["汇总ID"] = ""

            with open(records_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(records)

            QMessageBox.information(self, "成功", "汇总记录已删除")
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除汇总失败: {str(e)}")