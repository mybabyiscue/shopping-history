from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt
from core.record_manager import RecordManager

class StatsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.record_manager = RecordManager()
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 总消费金额
        total_group = QGroupBox("总消费统计")
        total_layout = QHBoxLayout()
        self.total_label = QLabel('总消费金额: ¥ 0.00')
        self.total_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #e74c3c;')
        total_layout.addWidget(self.total_label)
        
        # 刷新按钮
        refresh_button = QPushButton('刷新统计')
        refresh_button.clicked.connect(self.load_statistics)
        total_layout.addWidget(refresh_button)
        
        total_group.setLayout(total_layout)
        layout.addWidget(total_group)
        
        # 消费记录表格
        table_group = QGroupBox("消费记录统计")
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['用途', '消费次数', '总金额'])
        table_layout.addWidget(self.table)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        self.setLayout(layout)
    
    def load_statistics(self):
        """加载统计数据"""
        try:
            records = self.record_manager.get_all_records()
            
            # 计算总消费金额
            total_amount = sum(float(record.get('总价', 0)) for record in records)
            self.total_label.setText(f'总消费金额: ¥ {total_amount:.2f}')
            
            # 按用途统计
            purpose_stats = {}
            for record in records:
                purpose = record.get('用途', '其他')
                amount = float(record.get('总价', 0))
                
                if purpose not in purpose_stats:
                    purpose_stats[purpose] = {'count': 0, 'amount': 0}
                
                purpose_stats[purpose]['count'] += 1
                purpose_stats[purpose]['amount'] += amount
            
            # 更新表格
            self.table.setRowCount(len(purpose_stats))
            for row, (purpose, stats) in enumerate(purpose_stats.items()):
                self.table.setItem(row, 0, QTableWidgetItem(purpose))
                self.table.setItem(row, 1, QTableWidgetItem(str(stats['count'])))
                self.table.setItem(row, 2, QTableWidgetItem(f'¥ {stats["amount"]:.2f}'))
                
        except Exception as e:
            print(f"加载统计数据时出错: {e}")