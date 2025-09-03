from core.utils import read_csv_file, write_csv_file, hash_password

class UserManager:
    def __init__(self):
        self.users_file = 'data/users.csv'
        self.fieldnames = ['username', 'password_hash', 'role']
    
    def get_all_users(self):
        """获取所有用户"""
        return read_csv_file(self.users_file)
    
    def add_user(self, username, password, role='user'):
        """添加用户"""
        users = self.get_all_users()
        
        # 检查用户名是否已存在
        for user in users:
            if user['username'] == username:
                return False, "用户名已存在"
        
        # 加密密码
        password_hash = hash_password(password)
        
        new_user = {
            'username': username,
            'password_hash': password_hash,
            'role': role
        }
        
        users.append(new_user)
        write_csv_file(self.users_file, users, self.fieldnames)
        return True, "用户添加成功"
    
    def delete_user(self, username):
        """删除用户"""
        users = self.get_all_users()
        
        # 不能删除管理员账号
        for user in users:
            if user['username'] == username and user['role'] == 'admin':
                return False, "不能删除管理员账号"
        
        # 删除用户
        updated_users = [user for user in users if user['username'] != username]
        
        if len(updated_users) == len(users):
            return False, "用户不存在"
        
        write_csv_file(self.users_file, updated_users, self.fieldnames)
        return True, "用户删除成功"
    
    def update_user_password(self, username, new_password):
        """更新用户密码"""
        users = self.get_all_users()
        
        for user in users:
            if user['username'] == username:
                user['password_hash'] = hash_password(new_password)
                write_csv_file(self.users_file, users, self.fieldnames)
                return True, "密码更新成功"
        
        return False, "用户不存在"