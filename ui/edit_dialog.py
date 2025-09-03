from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QDateEdit, QCheckBox, QPushButton, QMessageBox,
                             QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import QDate
from typing import Dict, Any

class EditDialog(QDialog):
    def __init__(self, record_data, record_manager=None, parent=None):
        super().__init__(parent)
        self.record_manager = record_manager
        self.record_data = record_data.copy()
        # 确保记录有ID
        if '记录ID' not in self.record_data:
            self.record_data['记录ID'] = str(hash(frozenset(record_data.items())) % (10 ** 8))
        self.init_ui()
        self.populate_form()
        
    def get_record_data(self):
        """获取表单数据"""
        data = {
            '记录ID': self.record_data.get('记录ID', ''),
            '用途': self.purpose_combo.currentText(),
            '平台': self.platform_combo.currentText(),
            '物品': self.item_input.text().strip(),
            '数量': str(self.quantity_spin.value()),
            '总价': str(self.total_price_spin.value()),
            '购买日期': self.date_edit.date().toString('yyyy-MM-dd'),
            '是否收到': '是' if self.received_check.isChecked() else '否',
            '是否开票': '是' if self.invoice_check.isChecked() else '否'
        }
        # 确保所有字段都有值
        for key in data:
            if data[key] is None:
                data[key] = ''
        return data
    
    def init_ui(self):
        self.setWindowTitle('编辑购物记录')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 用途选择
        self.purpose_combo = QComboBox()
        self.purpose_combo.addItems(['转正仪式', '晋级仪式', '生日礼物', '微信转账', '其他'])
        form_layout.addRow('用途:', self.purpose_combo)
        
        # 平台选择
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['京东', '淘宝', '拼多多', '天猫', '线下', '其他'])
        form_layout.addRow('平台:', self.platform_combo)
        
        # 物品名称
        self.item_input = QLineEdit()
        form_layout.addRow('物品:', self.item_input)
        
        # 数量
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999)
        form_layout.addRow('数量:', self.quantity_spin)
        
        # 总价
        self.total_price_spin = QDoubleSpinBox()
        self.total_price_spin.setRange(0, 999999)
        self.total_price_spin.setDecimals(2)
        self.total_price_spin.setPrefix('¥ ')
        form_layout.addRow('总价:', self.total_price_spin)
        
        # 购买日期
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow('购买日期:', self.date_edit)
        
        # 是否收到
        self.received_check = QCheckBox('是')
        form_layout.addRow('是否收到:', self.received_check)
        
        # 是否开票
        self.invoice_check = QCheckBox('是')
        form_layout.addRow('是否开票:', self.invoice_check)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def populate_form(self):
        """填充表单数据"""
        self.purpose_combo.setCurrentText(self.record_data.get('用途', ''))
        self.platform_combo.setCurrentText(self.record_data.get('平台', ''))
        self.item_input.setText(self.record_data.get('物品', ''))
        self.quantity_spin.setValue(int(self.record_data.get('数量', 1)))
        self.total_price_spin.setValue(float(self.record_data.get('总价', 0)))
        
        # 处理日期
        date_str = self.record_data.get('购买日期', '')
        if date_str:
            try:
                year, month, day = map(int, date_str.split('-'))
                self.date_edit.setDate(QDate(year, month, day))
            except:
                self.date_edit.setDate(QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())
        
        # 处理复选框
        self.received_check.setChecked(self.record_data.get('是否收到', '') == '是')
        self.invoice_check.setChecked(self.record_data.get('是否开票', '') == '是')

    def accept(self):
        """保存数据并关闭对话框"""
        try:
            # 获取表单数据
            new_data = self.get_record_data()
            
            # 基本数据验证
            if not new_data['物品'].strip():
                QMessageBox.warning(self, "警告", "物品名称不能为空")
                return
                
            if float(new_data['总价']) <= 0:
                QMessageBox.warning(self, "警告", "总价必须大于0")
                return
                
            # 保存到记录管理器
            if self.record_manager:
                if '记录ID' in self.record_data and self.record_data['记录ID']:
                    # 更新现有记录
                    success, message = self.record_manager.update_record(
                        self.record_data['记录ID'], new_data
                    )
                    if not success:
                        raise Exception(message)
                else:
                    # 添加新记录
                    success, message = self.record_manager.add_record(new_data)
                    if not success:
                        raise Exception(message)
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")