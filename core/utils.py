import hashlib
import csv
import os
import json
from datetime import datetime

def hash_password(password):
    """使用SHA256加密密码"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def read_csv_file(file_path):
    """读取CSV文件，返回字典列表"""
    try:
        # 直接尝试读取文件，避免复杂的文件检查
        with open(file_path, 'r', encoding='utf-8') as file:
            # 读取第一行检查是否有内容
            first_line = file.readline()
            if not first_line:  # 空文件
                return []
            
            # 检查是否有数据行
            second_line = file.readline()
            if not second_line:  # 只有表头
                return []
            
            # 重置文件指针并读取所有数据
            file.seek(0)
            reader = csv.DictReader(file)
            data = []
            for row in reader:
                data.append(row)
            
            return data
            
    except FileNotFoundError:
        # 文件不存在，返回空列表
        return []
    except Exception as e:
        # 如果出现异常，返回空列表而不是让程序崩溃
        print(f"Warning: Error reading CSV file {file_path}: {e}")
        return []

def write_csv_file(file_path, data, fieldnames):
    """写入CSV文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 过滤数据，只保留指定字段
    filtered_data = []
    for row in data:
        filtered_row = {k: v for k, v in row.items() if k in fieldnames}
        # 确保所有字段都存在
        for field in fieldnames:
            if field not in filtered_row:
                filtered_row[field] = ''
        filtered_data.append(filtered_row)
    
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_data)

def read_json_file(file_path):
    """读取JSON文件，返回Python对象"""
    if not os.path.exists(file_path):
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 创建空JSON文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([], file)
        return []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(file_path, data):
    """写入数据到JSON文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def validate_fields(fields, required_fields):
    """验证字段完整性"""
    for field in required_fields:
        if not fields.get(field):
            return False, f"字段 '{field}' 不能为空"
    return True, ""