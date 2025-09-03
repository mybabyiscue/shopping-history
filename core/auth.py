from core.utils import read_csv_file, hash_password

class AuthManager:
    def __init__(self):
        self.users_file = 'data/users.csv'
        self.current_user = None
    
    def login(self, username, password):
        """用户登录验证"""
        users = read_csv_file(self.users_file)
        password_hash = hash_password(password)
        
        for user in users:
            if user['username'] == username and user['password_hash'] == password_hash:
                self.current_user = user
                return True, "登录成功", user['role']
        
        return False, "用户名或密码错误", None
    
    def get_current_user(self):
        """获取当前登录用户"""
        return self.current_user
    
    def has_admin_permission(self):
        """检查当前用户是否有管理员权限"""
        return self.current_user and self.current_user['role'] == 'admin'
    
    def logout(self):
        """用户登出"""
        self.current_user = None