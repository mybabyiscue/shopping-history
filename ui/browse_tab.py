from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QCheckBox, QHeaderView, QSizePolicy, 
    QComboBox, QLineEdit, QMessageBox, QDialog
)
from PyQt5.QtGui import QColor
from ui.summary_dialog import SummaryDialog
import csv
import os
from PyQt5.QtCore import Qt, QDate


class BrowseTab(QWidget):
    def __init__(self, record_manager, parent=None):
        super().__init__(parent)
        self.record_manager = record_manager
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QTableWidget {
                font-size: 14px;
                alternate-background-color: #f8f8f8;
            }
            QHeaderView::section {
                padding: 6px;
                background-color: #f0f0f0;
                border: none;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 5px;
                min-height: 28px;
            }
            QPushButton {
                padding: 5px 10px;
                min-width: 70px;
            }
        """)

        # --- 搜索区域 ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        search_layout.setContentsMargins(0, 0, 0, 15)

        # 时间选择
        time_group = QHBoxLayout()
        time_group.setSpacing(5)
        time_group.addWidget(QLabel("开始时间:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(2025, 1, 1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(120)
        time_group.addWidget(self.start_date)
        
        time_group.addSpacing(15)
        time_group.addWidget(QLabel("结束时间:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(120)
        time_group.addWidget(self.end_date)
        search_layout.addLayout(time_group)

        # 用途和平台
        combo_group = QHBoxLayout()
        combo_group.setSpacing(5)
        combo_group.addWidget(QLabel("用途:"))
        self.purpose_combo = self.create_checkable_combo(["转正仪式", "晋级仪式", "生日礼物", "微信转账", "其他"])
        self.purpose_combo.setFixedWidth(150)
        combo_group.addWidget(self.purpose_combo)
        
        combo_group.addSpacing(15)
        combo_group.addWidget(QLabel("平台:"))
        self.platform_combo = self.create_checkable_combo(["京东", "淘宝", "拼多多", "天猫", "线下"])
        self.platform_combo.setFixedWidth(150)
        combo_group.addWidget(self.platform_combo)
        search_layout.addLayout(combo_group)

        # 复选框
        check_group = QHBoxLayout()
        check_group.setSpacing(15)
        self.received_check = QCheckBox("已收到")
        self.invoiced_check = QCheckBox("已开票")
        check_group.addWidget(self.received_check)
        check_group.addWidget(self.invoiced_check)
        search_layout.addLayout(check_group)

        # 按钮
        btn_group = QHBoxLayout()
        btn_group.setSpacing(10)
        self.search_btn = QPushButton("查询")
        self.search_btn.setFixedWidth(80)
        self.search_btn.clicked.connect(self.load_data)
        btn_group.addWidget(self.search_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedWidth(80)
        self.reset_btn.clicked.connect(self.reset_filters)
        btn_group.addWidget(self.reset_btn)

        self.summary_btn = QPushButton("汇总")
        self.summary_btn.setFixedWidth(80)
        self.summary_btn.clicked.connect(self.show_summary_dialog)
        btn_group.addWidget(self.summary_btn)
        search_layout.addLayout(btn_group)

        search_layout.addStretch()
        main_layout.addLayout(search_layout)

        # --- 数据表格 ---
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 设置初始列数和表头
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "选择", "ID", "物品", "用途", "平台", "总价",
            "数量", "是否收到", "是否开票", "购买日期", "操作"
        ])
        
        # 设置第一列(复选框列)固定宽度
        self.table.setColumnWidth(0, 40)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)

        # 自动按列数均分宽度
        self.adjust_table_columns()

        # 添加表头全选复选框
        self.header_checkbox = QCheckBox()
        self.header_checkbox.stateChanged.connect(self.on_header_checkbox_changed)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.header_checkbox)
        header_widget.setLayout(header_layout)
        
        self.table.setCellWidget(0, 0, header_widget)

        main_layout.addWidget(self.table)

        # 创建底部布局（分页在左，总计在右）
        footer_layout = QHBoxLayout()
        
        # 添加分页控件到左侧
        pagination_layout = QHBoxLayout()
        
        # 页码导航
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.next_page)
        
        # 页码显示
        self.page_label = QLabel("总页数:")
        self.total_pages_label = QLabel("1")
        self.total_pages_label.setStyleSheet("font-weight: bold;")
        
        # 每页记录数选择
        self.items_per_page = QComboBox()
        self.items_per_page.addItems(["20", "50", "100"])
        self.items_per_page.setCurrentIndex(0)
        self.items_per_page.currentTextChanged.connect(self.load_data)
        
        # 布局调整
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.total_pages_label)
        pagination_layout.addWidget(QLabel("每页"))
        pagination_layout.addWidget(self.items_per_page)
        pagination_layout.addWidget(QLabel("条记录"))
        
        # 添加总计标签到右侧
        self.total_label = QLabel("查询结果总价: <b><font color='red'>¥0.00</font></b>")
        self.total_label.setStyleSheet("font-size: 14px;")
        
        # 将分页和总计添加到同一行
        footer_layout.addLayout(pagination_layout)
        footer_layout.addStretch()
        footer_layout.addWidget(self.total_label)
        
        main_layout.addLayout(footer_layout)

        # 分页相关变量
        self.current_page = 1
        self.filtered_records = []

    # --- 自动按列均分宽度 ---
    def adjust_table_columns(self):
        header = self.table.horizontalHeader()
        col_count = self.table.columnCount()
        if col_count == 0:
            return

        # 最后一列固定宽度
        last_col = col_count - 1
        header.setSectionResizeMode(last_col, QHeaderView.Fixed)
        self.table.setColumnWidth(last_col, 240)  # 操作按钮列宽度固定

        # 其他列均分剩余空间
        for col in range(col_count - 1):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        # 设置默认行高
        self.table.verticalHeader().setDefaultSectionSize(36)  # 每行高度36，可调节

    # --- 多选下拉框 ---
    def create_checkable_combo(self, items):
        class CheckableComboBox(QtWidgets.QComboBox):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setEditable(True)
                self.lineEdit().setReadOnly(True)
                self.lineEdit().setPlaceholderText("请选择...")

                self._model = QtGui.QStandardItemModel()
                self.setModel(self._model)

                self._view = QtWidgets.QListView()
                self._view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
                self.setView(self._view)

                for text in items:
                    item = QtGui.QStandardItem(text)
                    item.setCheckable(True)
                    item.setCheckState(Qt.Unchecked)
                    self._model.appendRow(item)

                self._view.pressed.connect(self._handleItemPressed)

            def _handleItemPressed(self, index):
                if index.isValid():
                    item = self._model.itemFromIndex(index)
                    if item.isCheckable():
                        new_state = Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked
                        item.setCheckState(new_state)
                        self.setCurrentIndex(-1)
                        self._updateText()
                        QtCore.QTimer.singleShot(10, self.showPopup)

            def _updateText(self):
                selected = [self._model.item(i).text()
                            for i in range(self._model.rowCount())
                            if self._model.item(i).checkState() == Qt.Checked]
                self.lineEdit().setText(", ".join(selected) if selected else "")

            def get_checked_items(self):
                return [self._model.item(i).text()
                        for i in range(self._model.rowCount())
                        if self._model.item(i).checkState() == Qt.Checked]

            def get_model(self):
                return self._model

        return CheckableComboBox()

    def get_checked_items(self, combo):
        return combo.get_checked_items()

    def reset_combo(self, combo):
        model = combo.get_model()
        for i in range(model.rowCount()):
            model.item(i).setCheckState(Qt.Unchecked)
        combo.lineEdit().setText("")

    # --- 数据加载与筛选 ---
    def load_data(self, reset_page=True):
        """加载数据并应用分页"""
        try:
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            purposes = self.get_checked_items(self.purpose_combo)
            platforms = self.get_checked_items(self.platform_combo)

            records = self.record_manager.get_all_records()
            self.filtered_records = []
            for record in records:
                if not (start_date <= record.get("购买日期", "") <= end_date):
                    continue
                if purposes and record.get("用途", "") not in purposes:
                    continue
                if platforms and record.get("平台", "") not in platforms:
                    continue
                if self.received_check.isChecked() and record.get("是否收到", "") != "是":
                    continue
                if self.invoiced_check.isChecked() and record.get("是否开票", "") != "是":
                    continue
                self.filtered_records.append(record)
            
            # 按购买日期降序排序
            self.filtered_records.sort(key=lambda x: x.get("购买日期", ""), reverse=True)

            if reset_page:
                self.current_page = 1
            
            self.update_page()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", f"加载数据失败: {str(e)}")

    def update_page(self):
        """更新当前页数据"""
        items_per_page = int(self.items_per_page.currentText())
        start_index = (self.current_page - 1) * items_per_page
        end_index = start_index + items_per_page
        page_records = self.filtered_records[start_index:end_index]

        self.table.setRowCount(len(page_records))
        for row, record in enumerate(page_records):
            self.fill_table_row(row, record)

        # 更新分页信息
        total_pages = max(1, (len(self.filtered_records) + items_per_page - 1) // items_per_page)
        self.total_pages_label.setText(str(total_pages))
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        # 计算总计
        total = sum(float(r.get("总价", 0)) for r in self.filtered_records)
        self.total_label.setText(f"查询结果总价: <b><font color='red'>¥{total:.2f}</font></b>")

        # 重新均分列宽
        self.adjust_table_columns()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page()

    def next_page(self):
        items_per_page = int(self.items_per_page.currentText())
        total_pages = max(1, (len(self.filtered_records) + items_per_page - 1) // items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_page()

    def jump_to_page(self):
        """跳转到指定页码"""
        try:
            items_per_page = int(self.items_per_page.currentText())
            total_pages = max(1, (len(self.filtered_records) + items_per_page - 1) // items_per_page)
            page_num = int(self.page_input.text())
            if 1 <= page_num <= total_pages:
                self.current_page = page_num
                self.update_page()
            else:
                QtWidgets.QMessageBox.warning(self, "提示", f"请输入1到{total_pages}之间的页码")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "错误", "请输入有效的页码数字")

    def reset_filters(self):
        """重置所有筛选条件并重新加载数据"""
        self.start_date.setDate(QDate(2025, 1, 1))
        self.end_date.setDate(QDate.currentDate())
        self.reset_combo(self.purpose_combo)
        self.reset_combo(self.platform_combo)
        self.received_check.setChecked(False)
        self.invoiced_check.setChecked(False)
        self.purpose_combo.lineEdit().setText("")
        self.platform_combo.lineEdit().setText("")
        self.load_data(reset_page=True)

    # --- 表格行操作 ---
    def on_edit_record(self, row):
        try:
            record_data = {
                "记录ID": self.table.item(row, 1).text(),
                "ID": self.table.item(row, 1).text(),
                "物品": self.table.item(row, 2).text(),
                "用途": self.table.item(row, 3).text(),
                "平台": self.table.item(row, 4).text(),
                "总价": float(self.table.item(row, 5).text()),
                "数量": int(self.table.item(row, 6).text()),
                "是否收到": self.table.item(row, 7).text(),
                "是否开票": self.table.item(row, 8).text(),
                "购买日期": self.table.item(row, 9).text()
            }
            from ui.edit_dialog import EditDialog
            dialog = EditDialog(record_data, self.record_manager, self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.load_data()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "错误",
                f"编辑记录时出错:\n{str(e)}\n请确保所有字段填写正确"
            )

    def on_delete_record(self, row):
        record_id = self.table.item(row, 1).text()  # 记录ID现在在第1列(索引1)
        reply = QtWidgets.QMessageBox.question(
            self, '确认删除',
            f'确定要删除记录ID {record_id} 吗?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.record_manager.delete_record(record_id)
            if success:
                self.load_data()
                QtWidgets.QMessageBox.information(self, "成功", message)
            else:
                QtWidgets.QMessageBox.warning(self, "错误", message)

    def fill_table_row(self, row, record):
        # 1. 行复选框
        checkbox = QCheckBox()
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_widget.setLayout(checkbox_layout)
        self.table.setCellWidget(row, 0, checkbox_widget)

        # 2. 数据列(所有内容居中)
        columns = [
            (1, "记录ID"), (2, "物品"), (3, "用途"), (4, "平台"),
            (5, "总价"), (6, "数量"), (7, "是否收到"), (8, "是否开票"), (9, "购买日期")
        ]
        for col, key in columns:
            # 显示时使用"ID"作为列名，但数据仍从"记录ID"获取
            display_key = "ID" if key == "记录ID" else key
            item = QTableWidgetItem(str(record.get(key, "")))
            item.setTextAlignment(Qt.AlignCenter)
            if key in ["是否收到", "是否开票"] and record.get(key) == "否":
                item.setForeground(QtGui.QColor(200, 0, 0))
            self.table.setItem(row, col, item)

        # 3. 操作按钮列（索引 10）
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(2, 2, 2, 2)
        btn_layout.setSpacing(10)

        edit_btn = QPushButton()
        edit_btn.setIcon(QtGui.QIcon("ui/icons/edit-solid.svg"))
        edit_btn.setIconSize(QtCore.QSize(16, 16))
        edit_btn.setFixedWidth(32)
        edit_btn.setToolTip("编辑")
        edit_btn.clicked.connect(lambda _, r=row: self.on_edit_record(r))

        del_btn = QPushButton()
        del_btn.setIcon(QtGui.QIcon("ui/icons/trash-solid.svg"))
        del_btn.setIconSize(QtCore.QSize(16, 16))
        del_btn.setFixedWidth(32)
        del_btn.setToolTip("删除")
        del_btn.clicked.connect(lambda _, r=row: self.on_delete_record(r))

        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        btn_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.table.setCellWidget(row, 10, btn_widget)


        # btn_widget = QWidget()
        # btn_layout = QHBoxLayout(btn_widget)
        # btn_layout.setContentsMargins(0, 0, 0, 0)

        # edit_btn = QPushButton("编辑")
        # edit_btn.clicked.connect(lambda _, r=row: self.on_edit_record(r))
        # del_btn = QPushButton("删除")
        # del_btn.clicked.connect(lambda _, r=row: self.on_delete_record(r))

        # btn_layout.addWidget(edit_btn)
        # btn_layout.addWidget(del_btn)
        # self.table.setCellWidget(row, 9, btn_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.table.resizeRowsToContents()
        self.adjust_table_columns()

    def show_summary_dialog(self):
        """显示汇总对话框并处理汇总操作"""
        # 获取勾选的记录
        selected_rows = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0).findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                record_id = self.table.item(row, 1).text()
                selected_rows.append(record_id)
        
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请至少勾选一条记录")
            return

        dialog = SummaryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            summary_data = dialog.get_summary_data()
            self.create_summary(summary_data, selected_rows)

    def create_summary(self, summary_data, selected_record_ids):
        """创建汇总记录"""
        try:
            # 检查记录是否已有汇总ID
            records_path = os.path.join("data", "records.csv")
            error_records = []
            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["记录ID"] in selected_record_ids and row.get("汇总ID"):
                        error_records.append(row)
            
            if error_records:
                error_ids = ", ".join([r["记录ID"] for r in error_records])

                class ErrorDialog(QDialog):
                    def __init__(self, ids, parent=None):
                        super().__init__(parent)
                        self.setWindowTitle("汇总失败")
                        self.setFixedSize(420, 220)
                        self.setStyleSheet("""
                            QDialog {
                                background-color: #ffffff;
                                border-radius: 8px;
                            }
                            QLabel {
                                font-size: 14px;
                                color: #333333;
                            }
                            QPushButton {
                                min-width: 80px;
                                min-height: 30px;
                                border-radius: 6px;
                                background-color: #0078d7;
                                color: white;
                                font-size: 14px;
                            }
                            QPushButton:hover {
                                background-color: #005a9e;
                            }
                        """)

                        layout = QVBoxLayout(self)
                        layout.setContentsMargins(20, 20, 20, 20)
                        layout.setSpacing(15)

                        # 标题
                        title_label = QLabel("⚠️ 以下记录已存在汇总中，无法再次汇总：")
                        title_label.setStyleSheet("font-size:16px; font-weight:bold; color:#d9534f;")
                        layout.addWidget(title_label)

                        # 记录ID
                        error_label = QLabel(f"<font color='red'><b><span style='font-size:18px'>{ids}</span></b></font>")
                        error_label.setTextFormat(Qt.RichText)
                        error_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                        layout.addWidget(error_label)

                        layout.addStretch()

                        # 按钮
                        btn_layout = QHBoxLayout()
                        btn_layout.addStretch()
                        ok_btn = QPushButton("确定")
                        ok_btn.clicked.connect(self.accept)
                        btn_layout.addWidget(ok_btn)
                        layout.addLayout(btn_layout)

                dlg = ErrorDialog(error_ids, self)
                dlg.exec_()
                return

            # 更新records.csv中的汇总ID
            updated_records = []
            with open(records_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row["记录ID"] in selected_record_ids:
                        row["汇总ID"] = summary_data["summary_id"]
                    updated_records.append(row)

            # 写入更新后的records.csv
            with open(records_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_records)

            # 在summary.csv中添加新记录
            summary_path = os.path.join("data", "summary.csv")
            fieldnames = ["汇总ID", "汇总名称", "汇总备注", "汇总时间", "是否报销"]
            
            # 读取现有数据
            rows = []
            if os.path.exists(summary_path):
                with open(summary_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames == fieldnames:  # 检查列名是否匹配
                        rows = list(reader)
            
            # 添加新记录
            rows.append({
                "汇总ID": summary_data["summary_id"],
                "汇总名称": summary_data["name"],
                "汇总备注": summary_data["note"],
                "汇总时间": summary_data["time"],
                "是否报销": "是" if summary_data.get("reimbursed", False) else "否"
            })
            
            # 写入更新后的数据
            with open(summary_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            QMessageBox.information(self, "成功", "汇总创建成功")
            self.load_data()  # 刷新表格

        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建汇总失败: {str(e)}")

    def on_header_checkbox_changed(self, state):
        """表头复选框状态变化时触发"""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0).findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(self.header_checkbox.isChecked())