#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 设置Qt插件路径
os.environ['QT_PLUGIN_PATH'] = 'E:\\anaconda3\\Lib\\site-packages\\PyQt5\\Qt5\\plugins'

def test_complete_flow():
    """测试完整的登录到主窗口流程"""
    try:
        from PyQt5.QtWidgets import QApplication
        from core.auth import AuthManager
        from ui.login_window import LoginWindow
        
        app = QApplication(sys.argv)
        
        # 测试认证
        auth = AuthManager()
        success, message, role = auth.login('admin', 'admin')
        if not success:
            print(f"认证失败: {message}")
            return False
        
        print("✓ 管理员认证成功")
        
        # 测试登录窗口
        login_window = LoginWindow()
        print("✓ 登录窗口创建成功")
        
        # 测试主窗口创建（通过登录窗口的方法）
        try:
            login_window.open_main_window()
            print("✓ 主窗口创建成功")
            return True
        except Exception as e:
            print(f"主窗口创建失败: {e}")
            return False
            
    except Exception as e:
        print(f"完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("测试完整登录流程...")
    
    if test_complete_flow():
        print("\n🎉 所有测试通过！程序可以正常运行")
        print("使用命令启动: python main.py")
        print("默认管理员账号: admin/admin")
    else:
        print("\n❌ 测试失败，请检查错误信息")