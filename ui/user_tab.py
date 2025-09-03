from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QFormLayout)
from core.user_manager import UserManager

class UserTab(QWidget):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 添加用户表单
        add_user_group = QGroupBox("添加新用户")
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        form_layout.addRow('用户名:', self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('密码:', self.password_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(['user', 'admin'])
        form_layout.addRow('角色:', self.role_combo)
        
        add_button = QPushButton('添加用户')
        add_button.clicked.connect(self.add_user)
        form_layout.addRow('', add_button)
        
        add_user_group.setLayout(form_layout)
        layout.addWidget(add_user_group)
        
        # 用户列表
        users_group = QGroupBox("用户列表")
        users_layout = QVBoxLayout()
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(['用户名', '角色', '操作'])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        users_layout.addWidget(self.users_table)
        
        users_group.setLayout(users_layout)
        layout.addWidget(users_group)
        
        self.setLayout(layout)
    
    def load_users(self):
        """加载用户列表"""
        users = self.user_manager.get_all_users()
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # 用户名
            self.users_table.setItem(row, 0, QTableWidgetItem(user['username']))
            
            # 角色
            self.users_table.setItem(row, 1, QTableWidgetItem(user['role']))
            
            # 操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            button_widget.setLayout(button_layout)
            
            # 删除按钮（不能删除自己）
            delete_button = QPushButton('删除')
            delete_button.clicked.connect(lambda checked, u=user: self.delete_user(u))
            button_layout.addWidget(delete_button)
            
            # 重置密码按钮
            reset_button = QPushButton('重置密码')
            reset_button.clicked.connect(lambda checked, u=user: self.reset_password(u))
            button_layout.addWidget(reset_button)
            
            self.users_table.setCellWidget(row, 2, button_widget)
    
    def add_user(self):
        """添加新用户"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, '输入错误', '用户名和密码不能为空')
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, '密码太短', '密码长度至少需要6个字符')
            return
        
        success, message = self.user_manager.add_user(username, password, role)
        if success:
            QMessageBox.information(self, '成功', message)
            self.clear_form()
            self.load_users()
        else:
            QMessageBox.critical(self, '错误', message)
    
    def delete_user(self, user):
        """删除用户"""
        if user['role'] == 'admin':
            QMessageBox.warning(self, '删除失败', '不能删除管理员账号')
            return
        
        reply = QMessageBox.question(self, '确认删除', 
                                   f'确定要删除用户 "{user["username"]}" 吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.user_manager.delete_user(user['username'])
            if success:
                QMessageBox.information(self, '删除成功', message)
                self.load_users()
            else:
                QMessageBox.critical(self, '删除失败', message)
    
    def reset_password(self, user):
        """重置用户密码"""
        from PyQt5.QtWidgets import QInputDialog
        
        new_password, ok = QInputDialog.getText(
            self, '重置密码', 
            f'请输入用户 "{user["username"]}" 的新密码:',
            QLineEdit.Password
        )
        
        if ok and new_password:
            if len(new_password) < 6:
                QMessageBox.warning(self, '密码太短', '密码长度至少需要6个字符')
                return
            
            success, message = self.user_manager.update_user_password(user['username'], new_password)
            if success:
                QMessageBox.information(self, '成功', '密码重置成功')
            else:
                QMessageBox.critical(self, '错误', message)
    
    def clear_form(self):
        """清空表单"""
        self.username_input.clear()
        self.password_input.clear()
        self.role_combo.setCurrentIndex(0)