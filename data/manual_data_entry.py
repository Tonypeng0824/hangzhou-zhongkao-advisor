#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动数据录入模板
用于录入从"小雨爸爸"公众号文章中获取的数据
"""

import sqlite3
from datetime import datetime

DB_PATH = 'zhongkao_data.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_high_school_score(school_name, year, admission_score):
    """录入高中录取分数线"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 查找或创建高中
    cursor.execute("SELECT id FROM high_schools WHERE school_name = ?", (school_name,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO high_schools (school_name) VALUES (?)", (school_name,))
        high_school_id = cursor.lastrowid
    else:
        high_school_id = result[0]
    
    # 插入或更新录取分数线
    cursor.execute("""
        INSERT OR REPLACE INTO high_school_scores 
        (high_school_id, year, admission_score, data_source, created_at, updated_at) 
        VALUES (?, ?, ?, '手动录入', ?, ?)
    """, (high_school_id, year, admission_score, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()
    print(f"✓ 已录入：{school_name} ({year}年) 录取分数线：{admission_score}分")

def insert_middle_school_stats(school_name, district, year, 
                               chonggao_rate=None, yougao_rate=None,
                               luokao_chonggao_rate=None, luokao_yougao_rate=None,
                               qiansan_rate=None, student_count=None, allocation_quota=None):
    """录入初中数据（重高率、优高率等）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 查找或创建初中
    cursor.execute("SELECT id FROM middle_schools WHERE school_name = ?", (school_name,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO middle_schools (school_name, district) VALUES (?, ?)", 
                      (school_name, district))
        middle_school_id = cursor.lastrowid
    else:
        middle_school_id = result[0]
    
    # 插入或更新初中数据
    cursor.execute("""
        INSERT OR REPLACE INTO middle_school_stats 
        (middle_school_id, year, student_count, 
         luokao_chonggao_rate, luokao_yougao_rate,
         chonggao_rate, yougao_rate, qiansan_rate,
         allocation_quota, data_source, created_at, updated_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '手动录入', ?, ?)
    """, (middle_school_id, year, student_count,
          luokao_chonggao_rate, luokao_yougao_rate,
          chonggao_rate, yougao_rate, qiansan_rate,
          allocation_quota, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()
    print(f"✓ 已录入：{school_name} ({year}年) 重高率：{chonggao_rate}%, 优高率：{yougao_rate}%")

def batch_insert_2025_data():
    """批量录入2025年数据（示例）"""
    print("=== 批量录入2025年数据 ===")
    print()
    
    # 示例：2025年高中录取分数线
    print("1. 录入2025年高中录取分数线...")
    high_school_data_2025 = [
        # (学校名称, 年份, 录取分数线)
        ('杭州第二中学(滨江校区)', 2025, 630),
        ('杭州学军中学(西溪校区)', 2025, 629),
        ('杭州高级中学(贡院校区)', 2025, 627),
        # 添加更多学校...
    ]
    
    for school_name, year, score in high_school_data_2025:
        insert_high_school_score(school_name, year, score)
    
    print()
    # 示例：2025年初中数据
    print("2. 录入2025年初中数据...")
    middle_school_data_2025 = [
        # (学校名称, 区域, 年份, 重高率, 优高率)
        ('某初中1', '西湖区', 2025, 25.5, 65.2),
        ('某初中2', '拱墅区', 2025, 22.3, 61.8),
        # 添加更多初中...
    ]
    
    for data in middle_school_data_2025:
        school_name, district, year, chonggao_rate, yougao_rate = data
        insert_middle_school_stats(school_name, district, year, chonggao_rate, yougao_rate)
    
    print()
    print("=== 录入完成 ===")

def batch_insert_2024_data():
    """批量录入2024年数据（示例）"""
    print("=== 批量录入2024年数据 ===")
    print()
    
    # TODO: 从"小雨爸爸"公众号文章中手动录入2024年数据
    print("请手动录入2024年数据...")
    print("提示：找到文章中的图片，使用OCR工具识别后，手动录入到这里")
    
    print()
    print("=== 录入完成 ===")

if __name__ == '__main__':
    print("手动数据录入模板")
    print("=" * 50)
    print()
    print("使用说明：")
    print("1. 在微信中打开'小雨爸爸'公众号")
    print("2. 找到包含数据表格的文章")
    print("3. 截图保存包含数据表格的图片")
    print("4. 使用OCR工具识别图片中的文字（推荐：腾讯云OCR、百度OCR、Google Keep）")
    print("5. 将识别出的数据填入下面的函数中")
    print("6. 运行脚本：python manual_data_entry.py")
    print()
    print("=" * 50)
    print()
    
    # 取消注释以录入数据
    # batch_insert_2025_data()
    # batch_insert_2024_data()
    
    print("提示：请编辑此脚本，取消注释要运行的函数，然后重新运行")
