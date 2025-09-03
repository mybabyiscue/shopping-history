from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.font_manager as fm
from core.record_manager import RecordManager

class StatsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.record_manager = RecordManager()
        # 设置中文字体
        try:
            # 尝试使用系统中可用的中文字体
            chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            for font in chinese_fonts:
                if font in available_fonts:
                    plt.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
                    break
            else:
                # 如果没有找到中文字体，使用默认字体
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
                
            plt.rcParams['axes.unicode_minus'] = False
        except:
            # 如果字体设置失败，使用默认设置
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
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
        
        # 图表区域
        charts_layout = QHBoxLayout()
        
        # 月度消费趋势
        monthly_group = QGroupBox("月度消费趋势")
        monthly_layout = QVBoxLayout()
        self.monthly_figure = Figure(figsize=(8, 4))
        self.monthly_canvas = FigureCanvas(self.monthly_figure)
        monthly_layout.addWidget(self.monthly_canvas)
        monthly_group.setLayout(monthly_layout)
        charts_layout.addWidget(monthly_group)
        
        # 平台消费占比
        platform_group = QGroupBox("平台消费占比")
        platform_layout = QVBoxLayout()
        self.platform_figure = Figure(figsize=(8, 4))
        self.platform_canvas = FigureCanvas(self.platform_figure)
        platform_layout.addWidget(self.platform_canvas)
        platform_group.setLayout(platform_layout)
        charts_layout.addWidget(platform_group)
        
        layout.addLayout(charts_layout)
        
        # 分类统计表格
        table_group = QGroupBox("分类详细统计")
        table_layout = QVBoxLayout()
        
        # 平台统计表格
        platform_table_label = QLabel("平台消费统计:")
        table_layout.addWidget(platform_table_label)
        
        self.platform_table = QTableWidget()
        self.platform_table.setColumnCount(2)
        self.platform_table.setHorizontalHeaderLabels(['平台', '消费金额'])
        table_layout.addWidget(self.platform_table)
        
        # 用途统计表格
        category_table_label = QLabel("用途消费统计:")
        table_layout.addWidget(category_table_label)
        
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(2)
        self.category_table.setHorizontalHeaderLabels(['用途', '消费金额'])
        table_layout.addWidget(self.category_table)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        self.setLayout(layout)
    
    def load_statistics(self):
        """加载统计信息"""
        stats = self.record_manager.get_statistics()
        
        # 更新总金额
        self.total_label.setText(f'总消费金额: ¥ {stats["total_amount"]:,.2f}')
        
        # 更新月度趋势图表
        self.update_monthly_chart(stats['monthly_data'])
        
        # 更新平台占比图表
        self.update_platform_chart(stats['platform_data'])
        
        # 更新统计表格
        self.update_statistics_tables(stats)
    
    def update_monthly_chart(self, monthly_data):
        """更新月度消费趋势图表"""
        self.monthly_figure.clear()
        ax = self.monthly_figure.add_subplot(111)
        
        # 按月份排序
        sorted_months = sorted(monthly_data.keys())
        months = []
        amounts = []
        
        for month in sorted_months:
            months.append(month)
            amounts.append(monthly_data[month])
        
        if amounts:
            ax.plot(months, amounts, marker='o', linestyle='-', color='#3498db')
            ax.set_title('月度消费趋势')
            ax.set_xlabel('月份')
            ax.set_ylabel('消费金额 (¥)')
            ax.grid(True, alpha=0.3)
            
            # 旋转x轴标签以避免重叠
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # 格式化y轴标签
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x:,.2f}'))
        
        self.monthly_canvas.draw()
    
    def update_platform_chart(self, platform_data):
        """更新平台消费占比图表"""
        self.platform_figure.clear()
        ax = self.platform_figure.add_subplot(111)
        
        # 过滤掉金额为0的平台
        filtered_data = {k: v for k, v in platform_data.items() if v > 0}
        
        if filtered_data:
            platforms = list(filtered_data.keys())
            amounts = list(filtered_data.values())
            
            # 创建饼图
            wedges, texts, autotexts = ax.pie(amounts, labels=platforms, autopct='%1.1f%%',
                                             startangle=90, colors=plt.cm.Set3.colors)
            ax.set_title('平台消费占比')
            
            # 设置标签样式
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        self.platform_canvas.draw()
    
    def update_statistics_tables(self, stats):
        """更新统计表格"""
        # 平台统计表格
        platform_data = sorted(stats['platform_data'].items(), key=lambda x: x[1], reverse=True)
        self.platform_table.setRowCount(len(platform_data))
        for row, (platform, amount) in enumerate(platform_data):
            self.platform_table.setItem(row, 0, QTableWidgetItem(platform))
            self.platform_table.setItem(row, 1, QTableWidgetItem(f'¥ {amount:,.2f}'))
        
        # 用途统计表格
        category_data = sorted(stats['category_data'].items(), key=lambda x: x[1], reverse=True)
        self.category_table.setRowCount(len(category_data))
        for row, (category, amount) in enumerate(category_data):
            self.category_table.setItem(row, 0, QTableWidgetItem(category))
            self.category_table.setItem(row, 1, QTableWidgetItem(f'¥ {amount:,.2f}'))