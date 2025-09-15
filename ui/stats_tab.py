from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QTableWidget, QTableWidgetItem, QPushButton,
                             QDateEdit, QComboBox, QCheckBox, QHeaderView, QMessageBox)
from PyQt5.QtCore import QDate
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
        
        # 筛选区域
        filter_group = QGroupBox("筛选条件")
        filter_layout = QHBoxLayout()
        
        # 日期范围
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("日期范围:"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit(QDate.currentDate())
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        filter_layout.addLayout(date_layout)
        
        # 用途筛选
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部用途")
        self.category_combo.setEditable(True)
        filter_layout.addWidget(QLabel("用途:"))
        filter_layout.addWidget(self.category_combo)
        
        # 平台筛选
        self.platform_combo = QComboBox()
        self.platform_combo.addItem("全部平台")
        self.platform_combo.setEditable(True)
        filter_layout.addWidget(QLabel("平台:"))
        filter_layout.addWidget(self.platform_combo)
        
        # 是否收到/开票
        received_layout = QVBoxLayout()
        self.received_check = QComboBox()
        self.received_check.addItems(["全部", "已收到", "未收到"])
        received_layout.addWidget(QLabel("是否收到:"))
        received_layout.addWidget(self.received_check)
        filter_layout.addLayout(received_layout)
        
        invoiced_layout = QVBoxLayout()
        self.invoiced_check = QComboBox()
        self.invoiced_check.addItems(["全部", "已开票", "未开票"])
        invoiced_layout.addWidget(QLabel("是否开票:"))
        invoiced_layout.addWidget(self.invoiced_check)
        filter_layout.addLayout(invoiced_layout)
        
        # 筛选按钮
        filter_btn = QPushButton("应用筛选")
        filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(filter_btn)
        
        reset_btn = QPushButton("重置筛选")
        reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_btn)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
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
        
        # 明细表格
        detail_group = QGroupBox("消费明细")
        detail_layout = QVBoxLayout()
        
        # 当前筛选提示
        self.filter_label = QLabel("当前筛选: 全部记录")
        detail_layout.addWidget(self.filter_label)
        
        # 明细表格
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(7)
        self.detail_table.setHorizontalHeaderLabels(["日期", "用途", "平台", "物品", "数量", "总价", "状态"])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        detail_layout.addWidget(self.detail_table)
        
        # 分页控件
        page_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.prev_page)
        page_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("第1页")
        page_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.next_page)
        page_layout.addWidget(self.next_btn)
        
        detail_layout.addLayout(page_layout)
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        # 分类统计表格
        table_group = QGroupBox("分类统计")
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
        
        # 添加点击事件
        self.monthly_canvas.mpl_connect('button_press_event', self.on_monthly_click)
        
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
        
        # 添加点击事件
        self.platform_canvas.mpl_connect('button_press_event', self.on_platform_click)
        
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
    
    def on_monthly_click(self, event):
        """处理月度图表点击事件"""
        if event.inaxes != self.monthly_figure.axes[0]:
            return
            
        # 获取点击的月份
        xdata = event.xdata
        months = sorted(self.record_manager.get_monthly_stats().keys())
        if 0 <= xdata < len(months):
            month = months[int(xdata)]
            self.start_date.setDate(QDate.fromString(month[:7], "yyyy-MM"))
            self.end_date.setDate(QDate.fromString(month[:7], "yyyy-MM"))
            self.apply_filters()
        
    def on_platform_click(self, event):
        """处理平台图表点击事件"""
        if event.inaxes != self.platform_figure.axes[0]:
            return
            
        # 获取点击的平台
        for i, (wedge, platform) in enumerate(zip(
            self.platform_figure.axes[0].patches,
            self.record_manager.get_platform_stats().keys()
        )):
            if wedge.contains_point((event.x, event.y)):
                self.platform_combo.setCurrentText(platform)
                self.apply_filters()
                break
                
    def apply_filters(self):
        """应用筛选条件"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        category = self.category_combo.currentText() if self.category_combo.currentText() != "全部用途" else None
        platform = self.platform_combo.currentText() if self.platform_combo.currentText() != "全部平台" else None
        received = self.received_check.currentText()
        invoiced = self.invoiced_check.currentText()
        
        # 更新筛选提示
        filter_text = []
        if category:
            filter_text.append(f"用途={category}")
        if platform:
            filter_text.append(f"平台={platform}")
        if received != "全部":
            filter_text.append(f"收到={received}")
        if invoiced != "全部":
            filter_text.append(f"开票={invoiced}")
            
        self.filter_label.setText("当前筛选: " + ("; ".join(filter_text) if filter_text else "全部记录"))
        
        # 获取筛选后的数据
        filtered_data = self.record_manager.get_filtered_records(
            start_date, end_date, category, platform, 
            received if received != "全部" else None,
            invoiced if invoiced != "全部" else None
        )
        
        # 更新明细表格
        self.update_detail_table(filtered_data)
        
        # 重新加载统计
        self.load_statistics()
        
    def reset_filters(self):
        """重置筛选条件"""
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        self.category_combo.setCurrentIndex(0)
        self.platform_combo.setCurrentIndex(0)
        self.received_check.setCurrentIndex(0)
        self.invoiced_check.setCurrentIndex(0)
        self.apply_filters()
        
    def update_detail_table(self, records):
        """更新明细表格"""
        self.detail_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.detail_table.setItem(row, 0, QTableWidgetItem(record["date"]))
            self.detail_table.setItem(row, 1, QTableWidgetItem(record["category"]))
            self.detail_table.setItem(row, 2, QTableWidgetItem(record["platform"]))
            self.detail_table.setItem(row, 3, QTableWidgetItem(record["item"]))
            self.detail_table.setItem(row, 4, QTableWidgetItem(str(record["quantity"])))
            self.detail_table.setItem(row, 5, QTableWidgetItem(f"¥{record['amount']:,.2f}"))
            status = []
            if record["received"]:
                status.append("已收到")
            if record["invoiced"]:
                status.append("已开票")
            self.detail_table.setItem(row, 6, QTableWidgetItem(" ".join(status)))
            
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination()
            
    def update_pagination(self):
        """更新分页显示"""
        self.page_label.setText(f"第{self.current_page}页/共{self.total_pages}页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        # 重新加载当前页数据
        self.apply_filters()
        
    def update_statistics_tables(self, stats):
        """更新统计表格"""
        # 平台统计表格
        platform_data = sorted(stats['platform_data'].items(), key=lambda x: x[1], reverse=True)
        self.platform_table.setRowCount(len(platform_data))
        for row, (platform, amount) in enumerate(platform_data):
            self.platform_table.setItem(row, 0, QTableWidgetItem(platform))
            self.platform_table.setItem(row, 1, QTableWidgetItem(f'¥ {amount:,.2f}'))
        

    def on_monthly_click(self, event):
        """处理月度图表点击事件"""
        if event.inaxes != self.monthly_figure.axes[0]:
            return
            
        # 获取点击的月份
        xdata = event.xdata
        months = sorted(self.record_manager.get_monthly_stats().keys())
        if 0 <= xdata < len(months):
            month = months[int(xdata)]
            self.start_date.setDate(QDate.fromString(month[:7], "yyyy-MM"))
            self.end_date.setDate(QDate.fromString(month[:7], "yyyy-MM"))
            self.apply_filters()
        
    def on_platform_click(self, event):
        """处理平台图表点击事件"""
        if event.inaxes != self.platform_figure.axes[0]:
            return
            
        # 获取点击的平台
        for i, (wedge, platform) in enumerate(zip(
            self.platform_figure.axes[0].patches,
            self.record_manager.get_platform_stats().keys()
        )):
            if wedge.contains_point((event.x, event.y)):
                self.platform_combo.setCurrentText(platform)
                self.apply_filters()
                break
                
    def apply_filters(self):
        """应用筛选条件"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        category = self.category_combo.currentText() if self.category_combo.currentText() != "全部用途" else None
        platform = self.platform_combo.currentText() if self.platform_combo.currentText() != "全部平台" else None
        received = self.received_check.currentText()
        invoiced = self.invoiced_check.currentText()
        
        # 更新筛选提示
        filter_text = []
        if category:
            filter_text.append(f"用途={category}")
        if platform:
            filter_text.append(f"平台={platform}")
        if received != "全部":
            filter_text.append(f"收到={received}")
        if invoiced != "全部":
            filter_text.append(f"开票={invoiced}")
            
        self.filter_label.setText("当前筛选: " + ("; ".join(filter_text) if filter_text else "全部记录"))
        
        # 获取筛选后的数据
        filtered_data = self.record_manager.get_filtered_records(
            start_date, end_date, category, platform, 
            received if received != "全部" else None,
            invoiced if invoiced != "全部" else None
        )
        
        # 更新明细表格
        self.update_detail_table(filtered_data)
        
        # 重新加载统计
        self.load_statistics()
        
    def reset_filters(self):
        """重置筛选条件"""
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        self.category_combo.setCurrentIndex(0)
        self.platform_combo.setCurrentIndex(0)
        self.received_check.setCurrentIndex(0)
        self.invoiced_check.setCurrentIndex(0)
        self.apply_filters()
        
    def update_detail_table(self, records):
        """更新明细表格"""
        self.detail_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.detail_table.setItem(row, 0, QTableWidgetItem(record["date"]))
            self.detail_table.setItem(row, 1, QTableWidgetItem(record["category"]))
            self.detail_table.setItem(row, 2, QTableWidgetItem(record["platform"]))
            self.detail_table.setItem(row, 3, QTableWidgetItem(record["item"]))
            self.detail_table.setItem(row, 4, QTableWidgetItem(str(record["quantity"])))
            self.detail_table.setItem(row, 5, QTableWidgetItem(f"¥{record['amount']:,.2f}"))
            status = []
            if record["received"]:
                status.append("已收到")
            if record["invoiced"]:
                status.append("已开票")
            self.detail_table.setItem(row, 6, QTableWidgetItem(" ".join(status)))
            
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination()
            
    def update_pagination(self):
        """更新分页显示"""
        self.page_label.setText(f"第{self.current_page}页/共{self.total_pages}页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        # 重新加载当前页数据
        self.apply_filters()
        
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