from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from core.auth import AuthManager

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('购物记录管理系统 - 登录')
        self.setFixedSize(450, 350)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title_label = QLabel('购物记录管理系统')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold; color: #2196F3; margin: 10px;')
        layout.addWidget(title_label)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        username_label.setFixedWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        password_label.setFixedWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 登录按钮
        login_button = QPushButton('登录')
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)
        
        # 设置布局
        self.setLayout(layout)
        
        # 设置默认焦点
        self.username_input.setFocus()
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '输入错误', '用户名和密码不能为空')
            return
        
        success, message, role = self.auth_manager.login(username, password)
        
        if success:
            QMessageBox.information(self, '登录成功', message)
            self.open_main_window()
        else:
            QMessageBox.critical(self, '登录失败', message)
    
    def open_main_window(self):
        """打开主窗口"""
        try:
            # 动态导入以避免循环导入
            from ui.main_window import MainWindow
            self.main_window = MainWindow(self.auth_manager)
            self.main_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法打开主窗口: {str(e)}')
            import traceback
            traceback.print_exc()