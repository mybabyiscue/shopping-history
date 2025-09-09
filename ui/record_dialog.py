from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QLabel, QHBoxLayout,
    QDateEdit, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt, QDate
import csv
import os


class RecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加记录")
        self.setMinimumSize(800, 600)
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.setup_ui()
        # 初始化时自动加载记录
        QtCore.QTimer.singleShot(0, self.load_records)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 日期查询
        date_layout = QHBoxLayout()
        date_layout.setSpacing(5)
        date_layout.addWidget(QLabel("开始时间:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(120)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("结束时间:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(120)
        date_layout.addWidget(self.end_date)
        
        search_btn = QPushButton("查询")
        search_btn.clicked.connect(self.load_records)
        search_btn.setFixedWidth(80)  # 设置按钮宽度
        date_layout.addWidget(search_btn)
        
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_dates)
        reset_btn.setFixedWidth(80)  # 设置按钮宽度
        date_layout.addWidget(reset_btn)
        
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.accept)
        add_btn.setFixedWidth(80)  # 设置按钮宽度
        date_layout.addWidget(add_btn)
        
        layout.addLayout(date_layout)

        # 记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "", "记录ID", "物品", "总价", "购买日期"
        ])
        self.table.setColumnWidth(0, 30)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # 分页控件和取消按钮
        footer_layout = QHBoxLayout()
        
        # 分页控件
        page_layout = QHBoxLayout()
        page_layout.setSpacing(5)
        
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setFixedWidth(80)
        page_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setFixedWidth(80)
        page_layout.addWidget(self.next_btn)
        
        page_layout.addWidget(QLabel("页码:"))
        self.page_label = QLabel("1")
        self.page_label.setStyleSheet("font-weight: bold;")
        self.page_label.setFixedWidth(30)
        page_layout.addWidget(self.page_label)
        
        page_layout.addWidget(QLabel("/"))
        self.total_pages_label = QLabel("1")
        self.total_pages_label.setStyleSheet("font-weight: bold;")
        self.total_pages_label.setFixedWidth(30)
        page_layout.addWidget(self.total_pages_label)
        
        page_layout.addWidget(QLabel("每页:"))
        self.items_per_page_combo = QComboBox()
        self.items_per_page_combo.addItems(["10", "30", "60"])
        self.items_per_page_combo.setCurrentIndex(0)
        self.items_per_page_combo.currentTextChanged.connect(self.on_items_per_page_changed)
        self.items_per_page_combo.setFixedWidth(60)
        page_layout.addWidget(self.items_per_page_combo)
        
        footer_layout.addLayout(page_layout)
        
        # 添加弹簧将取消按钮推到右侧
        footer_layout.addStretch()
        
        # 关闭按钮
        cancel_btn = QPushButton("关闭")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setFixedWidth(80)
        footer_layout.addWidget(cancel_btn)
        
        layout.addLayout(footer_layout)

    def reset_dates(self):
        """重置日期范围"""
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        self.load_records()

    def accept(self):
        """保存选中的记录到当前汇总"""
        try:
            selected_records = []
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).checkState() == Qt.Checked:
                    record_id = self.table.item(row, 1).text()
                    selected_records.append(record_id)

            if not selected_records:
                QMessageBox.information(self, "提示", "请先选择要添加的记录")
                return

            # 更新records.csv文件
            records_path = os.path.join("data", "records.csv")
            if not os.path.exists(records_path):
                QMessageBox.information(self, "提示", "没有找到记录文件")
                return

            # 从父窗口获取当前汇总ID
            if hasattr(self.parent(), 'current_summary_id'):
                summary_id = self.parent().current_summary_id
            else:
                # 添加详细调试信息
                parent_info = "无父窗口" if not self.parent() else f"父窗口类型: {type(self.parent()).__name__}"
                has_attr = hasattr(self.parent(), 'current_summary_id') if self.parent() else False
                debug_msg = f"""无法获取当前汇总ID"""
                QMessageBox.warning(self, "调试信息", debug_msg)
                return

            # 更新选中的记录
            updated_records = []
            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for record in reader:
                    if record["记录ID"] in selected_records:
                        record["汇总ID"] = summary_id
                    updated_records.append(record)

            # 写回文件
            with open(records_path, "w", encoding="utf-8", newline="") as f:
                fieldnames = reader.fieldnames or []
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_records)

            QMessageBox.information(self, "提示", f"成功添加 {len(selected_records)} 条记录到汇总")
            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存记录失败: {str(e)}")

    def on_items_per_page_changed(self, text):
        self.items_per_page = int(text)
        self.current_page = 1
        self.load_records()
        
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_records()
            
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_records()
            
    def update_page_controls(self):
        self.page_label.setText(str(self.current_page))
        self.total_pages_label.setText(str(self.total_pages))
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        
    def load_records(self):
        """加载指定日期范围内的记录"""
        try:
            records_path = os.path.join("data", "records.csv")
            if not os.path.exists(records_path):
                QMessageBox.information(self, "提示", "没有找到记录文件")
                return

            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)

            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            # 筛选汇总ID为空的记录并按购买日期降序排列
            filtered_records = [
                r for r in records 
                if not r.get("汇总ID", "").strip()
            ]
            filtered_records = sorted(filtered_records, 
                                   key=lambda x: x.get("购买日期", ""), 
                                   reverse=True)

            # 计算分页
            self.total_pages = max(1, (len(filtered_records) + self.items_per_page - 1) // self.items_per_page)
            self.update_page_controls()
            
            start = (self.current_page - 1) * self.items_per_page
            end = start + self.items_per_page
            page_records = filtered_records[start:end]
            
            self.table.setRowCount(len(page_records))
            for row, record in enumerate(page_records):
                # 添加复选框
                chk = QtWidgets.QTableWidgetItem()
                chk.setCheckState(Qt.Unchecked)
                self.table.setItem(row, 0, chk)
                
                # 设置数据列（注意列索引+1）
                columns = ["记录ID", "物品", "总价", "购买日期"]
                for col, key in enumerate(columns):
                    item = QTableWidgetItem(record.get(key, ""))
                    self.table.setItem(row, col+1, item)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载记录失败: {str(e)}")