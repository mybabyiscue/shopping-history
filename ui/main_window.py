import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('购物记录管理系统')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QTableView {
                gridline-color: #ddd;
                alternate-background-color: #f9f9f9;
            }
            QTableView::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)
        
        # 顶部信息栏
        info_layout = QHBoxLayout()
        user_info = self.auth_manager.get_current_user()
        if user_info:
            user_label = QLabel(f'当前用户: {user_info["username"]} ({user_info["role"]})')
        else:
            user_label = QLabel('当前用户: 未登录')
        user_label.setStyleSheet('font-size: 14px; color: #666; font-weight: bold;')
        
        logout_button = QPushButton('退出登录')
        logout_button.setStyleSheet('font-size: 12px; padding: 8px 16px;')
        logout_button.clicked.connect(self.handle_logout)
        
        info_layout.addWidget(user_label)
        info_layout.addStretch()
        info_layout.addWidget(logout_button)
        main_layout.addLayout(info_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 动态导入标签页以避免循环导入
        try:
            from ui.record_tab import RecordTab
            self.record_tab = RecordTab()
            self.tab_widget.addTab(self.record_tab, "购物记录录入")
        except Exception as e:
            print(f"无法加载购物记录标签页: {e}")
        
        try:
            from ui.browse_tab import BrowseTab
            from core.record_manager import RecordManager
            self.browse_tab = BrowseTab(RecordManager())
            self.tab_widget.addTab(self.browse_tab, "数据浏览与查询")
        except Exception as e:
            print(f"无法加载数据浏览标签页: {e}")
        
        try:
            from ui.reimbursement_tab import ReimbursementTab
            self.reimbursement_tab = ReimbursementTab()
            self.tab_widget.addTab(self.reimbursement_tab, "报销记录")
        except Exception as e:
            print(f"无法加载报销记录标签页: {e}")
        
        try:
            from ui.stats_tab_fixed import StatsTab
            self.stats_tab = StatsTab()
            self.tab_widget.addTab(self.stats_tab, "统计分析")
        except Exception as e:
            print(f"无法加载统计分析标签页: {e}")
        
        # 用户管理标签页（仅管理员可见）
        if self.auth_manager.has_admin_permission():
            try:
                from ui.user_tab import UserTab
                self.user_tab = UserTab()
                self.tab_widget.addTab(self.user_tab, "用户管理")
            except Exception as e:
                print(f"无法加载用户管理标签页: {e}")
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        main_layout.addWidget(self.tab_widget)
    
    def on_tab_changed(self, index):
        """处理标签页切换事件，自动刷新当前标签页"""
        current_tab = self.tab_widget.widget(index)
        
        # 如果是数据浏览与查询tab页，执行重置操作
        if hasattr(current_tab, 'reset_filters') and current_tab == self.browse_tab:
            current_tab.reset_filters()
        # 对于其他标签页，如果有load_data方法则调用
        elif hasattr(current_tab, 'load_data'):
            current_tab.load_data()
    
    def handle_logout(self):
        """处理退出登录"""
        self.auth_manager.logout()
        self.close()