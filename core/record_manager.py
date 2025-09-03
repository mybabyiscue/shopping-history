
from core.utils import read_csv_file, write_csv_file, read_json_file, write_json_file
from datetime import datetime
import os
import csv
import json
from typing import List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecordManager:
    def _ensure_chinese_headers(self):
        """确保CSV文件使用中文字段名"""
        if not os.path.exists(self.records_file):
            return
            
        # 检查文件是否为空
        if os.path.getsize(self.records_file) == 0:
            # 如果是空文件，直接写入正确的表头
            with open(self.records_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self._fieldnames)
                writer.writeheader()
            return
            
        # 读取第一行检查表头
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                
            # 如果文件已经有正确的表头，直接返回
            if '记录ID' in first_line:
                return
                
            # 如果不是中文表头，需要转换
            if first_line:  # 确保第一行不为空
                # 读取数据
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    records = list(reader)
                    
                # 重写为中文表头
                with open(self.records_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self._fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
        except Exception as e:
            # 如果出现异常，记录错误但继续执行
            logger.error(f"Error ensuring Chinese headers: {e}")
                
    def __init__(self):
        self.records_file = 'data/records.csv'
        self.summaries_file = 'data/summaries.json'
        
        # 定义字段名（移除了'是否报销'）
        self._fieldnames = [
            '记录ID', '用途', '平台', '物品',
            '数量', '总价', '购买日期',
            '是否收到', '是否开票'
        ]
        self.fieldnames = self._fieldnames  # 保持兼容性
        
        # 然后执行其他初始化操作
        # 只调用一次确保中文表头，避免递归
        self._ensure_chinese_headers()
        # 确保字段顺序一致
        
        # 确保summaries.json文件存在
        if not os.path.exists(self.summaries_file):
            os.makedirs(os.path.dirname(self.summaries_file), exist_ok=True)
            write_json_file(self.summaries_file, [])
    
    def add_record(self, record_data):
        """添加购物记录"""
        records = read_csv_file(self.records_file)
        
        # 生成唯一记录ID
        if '记录ID' not in record_data:
            record_data['记录ID'] = str(hash(frozenset(record_data.items())) % (10 ** 8))
        
        # 确保只保存必要的字段
        filtered_data = {k: v for k, v in record_data.items() if k in self._fieldnames}
        records.append(filtered_data)
        write_csv_file(self.records_file, records, self._fieldnames)
        return True, "记录添加成功"
    
    def get_all_records(self):
        """获取所有购物记录"""
        return read_csv_file(self.records_file)
    
    def query_records(self, filters=None):
        """查询购物记录"""
        records = self.get_all_records()
        
        if not filters:
            return records
        
        filtered_records = []
        for record in records:
            match = True
            
            # 日期范围筛选
            if 'start_date' in filters and filters['start_date']:
                try:
                    purchase_date = record.get('购买日期', '')
                    if purchase_date:
                        try:
                            purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                            if 'start_date' in filters and filters['start_date']:
                                start_dt = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                                if purchase_dt < start_dt:
                                    match = False
                            if 'end_date' in filters and filters['end_date']:
                                end_dt = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                                if purchase_dt > end_dt:
                                    match = False
                        except ValueError:
                            match = False
                    if purchase_date:
                        purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                        start_dt = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                        if purchase_dt < start_dt:
                            match = False
                except:
                    match = False
            
            if 'end_date' in filters and filters['end_date']:
                try:
                    purchase_date = record.get('购买日期', '')
                    if purchase_date:
                        purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                        end_dt = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                        if purchase_dt > end_dt:
                            match = False
                except:
                    match = False
            
            # 用途筛选（多选）- 修复多选逻辑
            if 'purposes' in filters and filters['purposes'] and len(filters['purposes']) > 0:
                if record['用途'] not in filters['purposes']:
                    match = False
            
            # 平台筛选（多选）- 修复多选逻辑
            if 'platforms' in filters and filters['platforms'] and len(filters['platforms']) > 0:
                if record['平台'] not in filters['platforms']:
                    match = False
            
            # 是否收到筛选
            if 'is_received' in filters and filters['is_received']:
                if record['是否收到'].lower() not in ['是', 'yes', 'true', '1']:
                    match = False
            
            # 是否开票筛选
            if 'is_invoiced' in filters and filters['is_invoiced']:
                if record['是否开票'].lower() not in ['是', 'yes', 'true', '1']:
                    match = False
            
            if match:
                filtered_records.append(record)
        
        return filtered_records
    
    def update_record(self, record_id, new_data):
        """更新购物记录"""
        if not record_id:
            return False, "无法更新：记录缺少ID"
            
        records = self.get_all_records()
        updated = False
        
        for i, record in enumerate(records):
            if str(record.get('记录ID')) == str(record_id):
                # 更新记录，只更新必要的字段
                for key in self._fieldnames:
                    if key in new_data:
                        record[key] = new_data[key]
                updated = True
                break
        
        if updated:
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
                
                # 写入文件
                with open(self.records_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self._fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
                return True, "记录更新成功"
            except Exception as e:
                return False, f"更新记录时出错: {str(e)}"
        
        return False, "未找到要更新的记录"

    def delete_record(self, record_id):
        """安全删除购物记录"""
        if not record_id:
            return False, "无法删除：记录缺少ID"
            
        records = self.get_all_records()
        original_count = len(records)
        
        # 精确匹配记录ID删除
        records = [r for r in records if str(r.get('记录ID')) != str(record_id)]
        
        if len(records) == original_count:
            return False, f"未找到要删除的记录ID: {record_id}"
            
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
            
            # 写入更新后的记录
            with open(self.records_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self._fieldnames)
                writer.writeheader()
                writer.writerows(records)
            
            # 删除后同步所有相关汇总记录
            summaries = self.get_all_summaries()
            if summaries:
                updated_summaries = []
                for summary in summaries:
                    if '记录详情' in summary:
                        summary['记录详情'] = [
                            r for r in summary['记录详情'] 
                            if str(r.get('记录ID')) != str(record_id)
                        ]
                    updated_summaries.append(summary)
                
                with open(self.summaries_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_summaries, f, ensure_ascii=False, indent=2)
            
            return True, f"记录ID {record_id} 删除成功"
        except Exception as e:
            return False, f"删除记录时出错: {str(e)}"
    
    def migrate_data_format(self):
        """迁移数据格式（英文字段名->中文字段名）"""
        if not os.path.exists(self.records_file):
            return
            
        # 读取现有数据
        with open(self.records_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            
        # 检查是否需要迁移（首行包含英文字段名）
        if 'record_id' in first_line:
            try:
                # 直接读取文件内容，避免递归调用
                records = []
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(row)
                
                # 映射字段名
                field_mapping = {
                    'record_id': '记录ID',
                    'purpose': '用途',
                    'platform': '平台',
                    'item': '物品',
                    'quantity': '数量',
                    'total_price': '总价',
                    'purchase_date': '购买日期',
                    'is_received': '是否收到',
                    'has_invoice': '是否开票'
                }
                
                # 转换记录
                migrated_records = []
                for record in records:
                    migrated_record = {}
                    for eng_key, chn_key in field_mapping.items():
                        if eng_key in record:
                            migrated_record[chn_key] = record[eng_key]
                    migrated_records.append(migrated_record)
                
                # 写入新格式
                with open(self.records_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                    writer.writeheader()
                    writer.writerows(migrated_records)
                    
                logger.info("数据格式迁移完成：英文字段名->中文字段名")
                
            except Exception as e:
                logger.error(f"数据格式迁移失败: {str(e)}")
                # 回滚到原始数据
                with open(self.records_file, 'w', encoding='utf-8') as f:
                    f.write(first_line + '\n')

    def get_statistics(self):
        """获取统计信息"""
        records = self.get_all_records()
        
        total_amount = 0
        monthly_data = {}
        platform_data = {}
        category_data = {}
        
        for record in records:
            try:
                # 总金额
                total_amount += float(record['总价'])
                
                # 月度数据
                purchase_date = record['购买日期']
                if purchase_date:
                    month = purchase_date[:7]  # YYYY-MM
                    monthly_data[month] = monthly_data.get(month, 0) + float(record['总价'])
                
                # 平台数据
                platform = record['平台']
                platform_data[platform] = platform_data.get(platform, 0) + float(record['总价'])
                
                # 用途数据
                category = record['用途']
                category_data[category] = category_data.get(category, 0) + float(record['总价'])
                
            except (ValueError, KeyError):
                continue
        
        return {
            'total_amount': total_amount,
            'monthly_data': monthly_data,
            'platform_data': platform_data,
            'category_data': category_data
        }
    
    # 汇总记录相关方法
    def add_summary(self, summary_data):
        """添加汇总记录"""
        try:
            summaries = self.get_all_summaries()
            
            # 检查汇总名称是否已存在
            for summary in summaries:
                if summary.get('汇总名称') == summary_data.get('汇总名称'):
                    return False, "汇总名称已存在"
            
            summaries.append(summary_data)
            write_json_file(self.summaries_file, summaries)
            return True, "汇总记录添加成功"
        except Exception as e:
            return False, f"添加汇总记录失败: {str(e)}"
    
    def get_all_summaries(self):
        """获取所有汇总记录"""
        try:
            return read_json_file(self.summaries_file)
        except:
            # 如果文件不存在或读取失败，返回空列表
            return []
    
    def get_summary_by_name(self, name):
        """根据名称获取汇总记录"""
        summaries = self.get_all_summaries()
        for summary in summaries:
            if summary.get('汇总名称') == name:
                return summary
        return None
    
    def update_summary_status(self, name, status_key, status_value):
        """更新汇总记录状态"""
        summaries = self.get_all_summaries()
        
        for i, summary in enumerate(summaries):
            if summary.get('汇总名称') == name:
                summaries[i][status_key] = status_value
                write_json_file(self.summaries_file, summaries)
                return True, f"汇总记录状态已更新为: {status_key}={status_value}"
        
        return False, "未找到要更新的汇总记录"
    
    def delete_summary(self, name):
        """删除汇总记录"""
        summaries = self.get_all_summaries()
        
        for i, summary in enumerate(summaries):
            if summary.get('汇总名称') == name:
                del summaries[i]
                write_json_file(self.summaries_file, summaries)
                return True, "汇总记录删除成功"
        
        return False, "未找到要删除的汇总记录"
        
    def generate_summary_csv(self, summary_name, output_path):
        """生成汇总CSV文件"""
        summary = self.get_summary_by_name(summary_name)
        if not summary:
            return False, "未找到指定汇总记录"
            
        # 获取所有记录
        all_records = self.get_all_records()
        
        # 筛选属于该汇总的记录
        record_ids = [r.get('记录ID') for r in summary.get('记录详情', [])]
        summary_records = [r for r in all_records if r.get('记录ID') in record_ids]
        
        # 写入CSV文件
        try:
            write_csv_file(output_path, summary_records, self.fieldnames)
            return True, f"汇总CSV已生成: {output_path}"
        except Exception as e:
            return False, f"生成汇总CSV失败: {str(e)}"
    
    def add_records_to_summary(self, summary_name, records):
        """添加记录到汇总"""
        summaries = self.get_all_summaries()
        
        for summary in summaries:
            if summary.get('汇总名称') == summary_name:
                if '记录详情' not in summary:
                    summary['记录详情'] = []
                
                # 添加新记录
                for record in records:
                    if record not in summary['记录详情']:
                        summary['记录详情'].append(record)
                
                # 更新记录数量和总价
                summary['记录数量'] = len(summary['记录详情'])
                summary['总价'] = sum(float(r['总价']) for r in summary['记录详情'])
                
                write_json_file(self.summaries_file, summaries)
                return True, "记录添加成功"
        
        return False, "未找到要更新的汇总记录"