from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QDateEdit, QCheckBox, QPushButton, QMessageBox,
                             QFormLayout, QGroupBox)
from PyQt5.QtCore import QDate
from core.record_manager import RecordManager
from core.utils import validate_fields

class RecordTab(QWidget):
    def __init__(self):
        super().__init__()
        self.record_manager = RecordManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 表单组
        form_group = QGroupBox("购物记录录入")
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
        self.item_input.setPlaceholderText('请输入物品名称')
        form_layout.addRow('物品:', self.item_input)
        
        # 数量
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999)
        self.quantity_spin.setValue(1)
        form_layout.addRow('数量:', self.quantity_spin)
        
        # 总价输入
        self.total_price_spin = QDoubleSpinBox()
        self.total_price_spin.setRange(0, 999999)
        self.total_price_spin.setDecimals(2)
        self.total_price_spin.setPrefix('¥ ')
        form_layout.addRow('总价:', self.total_price_spin)
        
        # 购买日期
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow('购买日期:', self.date_edit)
        
        # 是否收到
        self.received_check = QCheckBox('是')
        self.received_check.setChecked(False)
        form_layout.addRow('是否收到:', self.received_check)
        
        # 是否开票
        self.invoice_check = QCheckBox('是')
        self.invoice_check.setChecked(False)
        form_layout.addRow('是否开票:', self.invoice_check)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 保存按钮
        save_button = QPushButton('保存记录')
        save_button.setStyleSheet('font-size: 14px; padding: 10px;')
        save_button.clicked.connect(self.save_record)
        layout.addWidget(save_button)
        
        
        self.setLayout(layout)
    
    
    def save_record(self):
        """保存购物记录"""
        record_data = {
            '用途': self.purpose_combo.currentText(),
            '平台': self.platform_combo.currentText(),
            '物品': self.item_input.text().strip(),
            '数量': str(self.quantity_spin.value()),
            '总价': str(self.total_price_spin.value()),
            '购买日期': self.date_edit.date().toString('yyyy-MM-dd'),
            '是否收到': '是' if self.received_check.isChecked() else '否',
            '是否开票': '是' if self.invoice_check.isChecked() else '否'
        }
        
        # 验证必填字段
        required_fields = ['物品']
        valid, message = validate_fields(record_data, required_fields)
        if not valid:
            QMessageBox.warning(self, '输入错误', message)
            return
        
        # 保存记录
        success, message = self.record_manager.add_record(record_data)
        if success:
            QMessageBox.information(self, '成功', message)
            self.clear_form()
        else:
            QMessageBox.critical(self, '错误', message)
    
    def clear_form(self):
        """清空表单"""
        self.item_input.clear()
        self.quantity_spin.setValue(1)
        self.total_price_spin.setValue(0)
        self.date_edit.setDate(QDate.currentDate())
        self.received_check.setChecked(False)
        self.invoice_check.setChecked(False)