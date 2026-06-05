#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中考数据录入脚本
用于手动录入2022-2026年杭州中考数据到数据库
"""

import sqlite3
import os

DB_PATH = r'C:\Users\Administrator\.workbuddy\skills\hangzhou-zhongkao-advisor\data\zhongkao_data.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_middle_school(name, district):
    """插入初中基本信息"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO middle_schools (school_name, district) VALUES (?, ?)",
            (name, district)
        )
        conn.commit()
        print(f"✓ 插入初中: {name}")
        return cursor.lastrowid
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None
    finally:
        conn.close()

def insert_middle_school_stats(school_name, year, district=None, **kwargs):
    """插入初中统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 获取school_id
        if district:
            cursor.execute("SELECT id FROM middle_schools WHERE school_name = ? AND district = ?", (school_name, district))
        else:
            cursor.execute("SELECT id FROM middle_schools WHERE school_name = ?", (school_name,))
        
        result = cursor.fetchone()
        if not result:
            print(f"✗ 初中不存在: {school_name}")
            return False
        
        school_id = result[0]
        
        # 构建插入SQL
        fields = ['middle_school_id', 'year']
        values = [school_id, year]
        
        for key, value in kwargs.items():
            if value is not None:
                fields.append(key)
                values.append(value)
        
        placeholders = ', '.join(['?'] * len(values))
        sql = f"INSERT OR REPLACE INTO middle_school_stats ({', '.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(sql, values)
        conn.commit()
        print(f"✓ 插入{year}年初中统计: {school_name}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    finally:
        conn.close()

def insert_high_school(name, campus=None, district=None, address=None, metro_station=None, boarding_available=None):
    """插入高中基本信息"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT OR IGNORE INTO high_schools 
            (school_name, campus, district, address, metro_station, boarding_available) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (name, campus, district, address, metro_station, boarding_available)
        )
        conn.commit()
        print(f"✓ 插入高中: {name} ({campus})" if campus else f"✓ 插入高中: {name}")
        return cursor.lastrowid
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None
    finally:
        conn.close()

def insert_high_school_score(school_name, campus, year, score):
    """插入高中录取分数线"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 获取school_id
        if campus:
            cursor.execute("SELECT id FROM high_schools WHERE school_name = ? AND campus = ?", (school_name, campus))
        else:
            cursor.execute("SELECT id FROM high_schools WHERE school_name = ? AND campus IS NULL", (school_name,))
        
        result = cursor.fetchone()
        if not result:
            print(f"✗ 高中不存在: {school_name} ({campus})")
            return False
        
        school_id = result[0]
        
        cursor.execute(
            """INSERT OR REPLACE INTO high_school_scores 
            (high_school_id, year, admission_score, data_source) 
            VALUES (?, ?, ?, '手动录入')""",
            (school_id, year, score)
        )
        conn.commit()
        print(f"✓ 插入{year}年分数线: {school_name} ({campus}) - {score}分")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    finally:
        conn.close()

def query_data():
    """查询数据库中的数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n===== 数据库统计 =====")
    
    # 统计各表数据量
    tables = ['middle_schools', 'middle_school_stats', 'high_schools', 'high_school_scores', 'allocation_data', 'student_source_stats']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count}条")
    
    print("\n===== 2025年高中录取分数线 =====")
    cursor.execute("""
        SELECT h.school_name, h.campus, s.admission_score 
        FROM high_schools h 
        JOIN high_school_scores s ON h.id = s.high_school_id 
        WHERE s.year = 2025 
        ORDER BY s.admission_score DESC
    """)
    scores = cursor.fetchall()
    for row in scores:
        campus_str = f" ({row[1]})" if row[1] else ""
        print(f"  {row[0]}{campus_str}: {row[2]}分")
    
    conn.close()

if __name__ == '__main__':
    print("中考数据录入脚本")
    print("=" * 50)
    
    # 示例：查询当前数据
    query_data()
    
    print("\n" + "=" * 50)
    print("使用示例:")
    print("  insert_high_school_score('杭州第二中学', '滨江校区', 2025, 630)")
    print("  insert_middle_school_stats('嘉绿苑中学', 2025, '西湖区', yougao_rate=0.65)")
    print("=" * 50)
