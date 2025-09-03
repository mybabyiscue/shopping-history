#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def setup_environment():
    """设置应用程序环境"""
    # 设置DPI感知和高分辨率支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Windows系统下设置DPI感知
    if sys.platform == 'win32':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 系统DPI感知
        except:
            pass
    
    # 创建数据目录和文件（如果不存在）
    os.makedirs('data', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    # 初始化默认用户文件
    users_file = 'data/users.csv'
    if not os.path.exists(users_file):
        with open(users_file, 'w', encoding='utf-8') as f:
            f.write('username,password_hash,role\n')
            f.write('admin,8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918,admin\n')
    
    # 初始化购物记录文件
    records_file = 'data/records.csv'
    if not os.path.exists(records_file):
        with open(records_file, 'w', encoding='utf-8') as f:
            f.write('记录ID,用途,平台,物品,数量,总价,购买日期,是否收到,是否开票\n')

def main():
    """主函数"""
    setup_environment()
    
    app = QApplication(sys.argv)
    
    # 设置应用程序字体
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    # 延迟导入以避免循环导入
    from ui.login_window import LoginWindow
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()