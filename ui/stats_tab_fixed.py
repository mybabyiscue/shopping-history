from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QPushButton,
                             QComboBox, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtChart import (QChart, QChartView, QBarSeries, QBarSet, 
                          QPieSeries, QBarCategoryAxis, QValueAxis)
from PyQt5.QtGui import QPainter, QFont
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
        
        # 添加图表区域
        chart_group = QGroupBox("消费分析")
        chart_layout = QVBoxLayout()
        
        # 图表类型选择
        chart_type_layout = QHBoxLayout()
        chart_type_label = QLabel("图表类型:")
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["柱状图", "饼图"])
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart_display)
        chart_type_layout.addWidget(chart_type_label)
        chart_type_layout.addWidget(self.chart_type_combo)
        chart_layout.addLayout(chart_type_layout)

        # 图表堆叠布局
        self.chart_stack = QStackedWidget()
        
        # 柱状图
        self.bar_chart_view = QChartView()
        self.bar_chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_stack.addWidget(self.bar_chart_view)
        
        # 饼图
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_stack.addWidget(self.pie_chart_view)
        
        chart_layout.addWidget(self.chart_stack)
        self.chart_stack.setCurrentIndex(0)  # 默认显示柱状图
        
        chart_group.setLayout(chart_layout)
        table_layout.addWidget(chart_group)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        self.setLayout(layout)
    
    def update_chart_display(self):
        """更新图表显示"""
        index = self.chart_type_combo.currentIndex()
        self.chart_stack.setCurrentIndex(index)

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
            
            # 更新柱状图
            bar_series = QBarSeries()
            bar_set = QBarSet("消费金额")
            
            purposes = []
            for purpose, stats in purpose_stats.items():
                bar_set.append(stats['amount'])
                purposes.append(purpose)
            
            bar_series.append(bar_set)
            
            bar_chart = QChart()
            bar_chart.addSeries(bar_series)
            bar_chart.setTitle("各用途消费金额分布")
            bar_chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
            bar_chart.setAnimationOptions(QChart.SeriesAnimations)
            
            axis_x = QBarCategoryAxis()
            axis_x.append(purposes)
            bar_chart.createDefaultAxes()
            bar_chart.setAxisX(axis_x, bar_series)
            bar_chart.legend().setVisible(True)
            bar_chart.legend().setAlignment(Qt.AlignBottom)
            bar_chart.legend().setFont(QFont("Arial", 10))
            
            # 设置Y轴标签
            axis_y = QValueAxis()
            axis_y.setTitleText("金额(¥)")
            axis_y.setTitleFont(QFont("Arial", 12))
            axis_y.setLabelsFont(QFont("Arial", 12))
            bar_chart.setAxisY(axis_y, bar_series)
            
            # 设置X轴标签
            axis_x.setTitleText("消费用途")
            axis_x.setTitleFont(QFont("Arial", 12))
            axis_x.setLabelsFont(QFont("Arial", 12))
            axis_x.setLabelsAngle(-45)  # 倾斜标签避免重叠
            
            self.bar_chart_view.setChart(bar_chart)
            
            # 更新饼图
            pie_series = QPieSeries()
            for purpose, stats in purpose_stats.items():
                pie_series.append(f"{purpose} ¥{stats['amount']:.2f}", stats['amount'])
            
            pie_chart = QChart()
            pie_chart.addSeries(pie_series)
            pie_chart.setTitle("消费用途占比")
            pie_chart.setTitleFont(QFont("Arial", 12, QFont.Bold))
            pie_chart.legend().setVisible(True)
            pie_chart.legend().setAlignment(Qt.AlignBottom)
            pie_chart.legend().setFont(QFont("Arial", 10))
            
            self.pie_chart_view.setChart(pie_chart)
                
        except Exception as e:
            print(f"加载统计数据时出错: {e}")