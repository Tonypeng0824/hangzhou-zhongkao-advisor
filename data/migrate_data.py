#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移旧数据库数据到新数据库，并插入2025年高中录取分数线
"""

import sqlite3
import os

# 数据库路径
OLD_DB = r'C:\Users\Administrator\.workbuddy\skills\hangzhou-zhongkao-advisor\data\schools.db'
NEW_DB = r'C:\Users\Administrator\.workbuddy\skills\hangzhou-zhongkao-advisor\data\zhongkao_data.db'

def migrate_data():
    # 连接到旧数据库
    old_conn = sqlite3.connect(OLD_DB)
    old_cursor = old_conn.cursor()

    # 连接到新数据库
    new_conn = sqlite3.connect(NEW_DB)
    new_cursor = new_conn.cursor()

    print("开始迁移数据...")

    # 1. 迁移初中基本信息
    print("\n1. 迁移初中基本信息...")
    old_cursor.execute("SELECT * FROM middle_schools")
    middle_schools = old_cursor.fetchall()

    for school in middle_schools:
        try:
            # 插入到新的middle_schools表
            new_cursor.execute(
                "INSERT OR IGNORE INTO middle_schools (school_name, district) VALUES (?, ?)",
                (school[1], school[2])  # school_name, district
            )
            print(f"  插入初中: {school[1]}")
        except Exception as e:
            print(f"  错误: {e}")

    new_conn.commit()

    # 2. 迁移初中统计数据
    print("\n2. 迁移初中统计数据...")
    for school in middle_schools:
        school_id = school[0]
        school_name = school[1]

        # 获取新数据库中对应的school_id
        new_cursor.execute("SELECT id FROM middle_schools WHERE school_name = ?", (school_name,))
        result = new_cursor.fetchone()
        if result:
            new_school_id = result[0]

            # 插入2024年数据
            if school[4] is not None:  # top3_rate_2024
                new_cursor.execute(
                    """INSERT OR IGNORE INTO middle_school_stats
                    (middle_school_id, year, qiansan_rate, yougao_rate, data_source)
                    VALUES (?, ?, ?, ?, ?)""",
                    (new_school_id, 2024, school[4], school[6], '旧数据库迁移')
                )
                print(f"  插入2024年数据: {school_name}")

            # 插入2025年数据
            if school[5] is not None:  # top3_rate_2025
                new_cursor.execute(
                    """INSERT OR IGNORE INTO middle_school_stats
                    (middle_school_id, year, student_count, qiansan_rate, yougao_rate, allocation_quota, data_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (new_school_id, 2025, school[3], school[5], school[7], school[8], '旧数据库迁移')
                )
                print(f"  插入2025年数据: {school_name}")

    new_conn.commit()

    # 3. 迁移高中基本信息
    print("\n3. 迁移高中基本信息...")
    old_cursor.execute("SELECT * FROM high_schools")
    high_schools = old_cursor.fetchall()

    for school in high_schools:
        try:
            new_cursor.execute(
                """INSERT OR IGNORE INTO high_schools
                (school_name, campus, district, address, metro_station, boarding_available)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (school[1], school[2], school[3], school[4], school[5], school[6])
            )
            print(f"  插入高中: {school[1]} ({school[2]})")
        except Exception as e:
            print(f"  错误: {e}")

    new_conn.commit()

    # 4. 迁移高中录取分数线
    print("\n4. 迁移高中录取分数线...")
    for school in high_schools:
        school_id = school[0]
        school_name = school[1]
        campus = school[2]
        score_2025 = school[7]  # admission_score_2025

        # 获取新数据库中对应的school_id
        if campus:
            new_cursor.execute("SELECT id FROM high_schools WHERE school_name = ? AND campus = ?", (school_name, campus))
        else:
            new_cursor.execute("SELECT id FROM high_schools WHERE school_name = ? AND campus IS NULL", (school_name,))

        result = new_cursor.fetchone()
        if result and score_2025 is not None:
            new_school_id = result[0]
            try:
                new_cursor.execute(
                    """INSERT OR IGNORE INTO high_school_scores
                    (high_school_id, year, admission_score, data_source)
                    VALUES (?, ?, ?, ?)""",
                    (new_school_id, 2025, score_2025, '旧数据库迁移')
                )
                print(f"  插入2025年分数线: {school_name} ({campus}) - {score_2025}分")
            except Exception as e:
                print(f"  错误: {e}")

    new_conn.commit()

    print("\n数据迁移完成！")

    # 关闭连接
    old_conn.close()
    new_conn.close()

if __name__ == '__main__':
    migrate_data()
