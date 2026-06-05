"""
从微信公众号文章中提取杭州中考数据并存储到SQLite数据库
"""
import sqlite3
from datetime import datetime

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect('C:/Users/Administrator/.workbuddy/skills/hangzhou-zhongkao-advisor/data/zhongkao_data.db')

def save_article_data():
    """保存从文章中提取的数据到数据库"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("开始保存从文章中提取的数据...")
        
        # 1. 保存2023年各区裸考率数据（整体）
        print("\n1. 保存2023年各区裸考率数据（整体）...")
        district_data = [
            ('西湖区(整体)', '西湖区', 2023, 9.26),
            ('滨江区(整体)', '滨江区', 2023, 8.68),
            ('上城区(整体)', '上城区', 2023, 7.37),
            ('拱墅区(整体)', '拱墅区', 2023, 6.71),
            ('钱塘区(整体)', '钱塘区', 2023, 5.23),
        ]
        
        for school_name, district, year, luokao_rate in district_data:
            # 查找或创建初中记录
            cursor.execute("SELECT id FROM middle_schools WHERE school_name = ?", (school_name,))
            result = cursor.fetchone()
            if not result:
                cursor.execute("INSERT INTO middle_schools (school_name, district) VALUES (?, ?)",
                            (school_name, district))
                middle_school_id = cursor.lastrowid
            else:
                middle_school_id = result[0]
            
            # 插入统计数据（裸考率存入luokao_chonggao_rate字段）
            cursor.execute(
                """INSERT OR REPLACE INTO middle_school_stats 
                (middle_school_id, year, luokao_chonggao_rate, data_source, created_at, updated_at) 
                VALUES (?, ?, ?, '小雨爸爸公众号', ?, ?)""",
                (middle_school_id, year, luokao_rate, datetime.now(), datetime.now())
            )
        print("   ✓ 保存各区整体裸考率数据完成")
        
        # 2. 保存2023年部分初中学校重高率、优高率数据
        print("\n2. 保存2023年部分初中学校数据...")
        school_data = [
            ('启正中学', '未知', 2023, 39.17, 72.92),
            ('绿城育华', '未知', 2023, 31.60, 75.20),
            ('大关实验', '未知', 2023, 28.07, 65.12),
            ('养正学校', '未知', 2023, 37.30, 76.98),
            ('保俶塔申花', '未知', 2023, 35.62, 69.41),
            ('嘉绿苑中学', '未知', 2023, 23.08, 58.70),
        ]
        
        for school_name, district, year, chonggao_rate, yougao_rate in school_data:
            # 查找或创建初中记录
            cursor.execute("SELECT id FROM middle_schools WHERE school_name = ?", (school_name,))
            result = cursor.fetchone()
            if not result:
                cursor.execute("INSERT INTO middle_schools (school_name, district) VALUES (?, ?)",
                            (school_name, district))
                middle_school_id = cursor.lastrowid
            else:
                middle_school_id = result[0]
            
            # 插入统计数据
            cursor.execute(
                """INSERT OR REPLACE INTO middle_school_stats 
                (middle_school_id, year, chonggao_rate, yougao_rate, data_source, created_at, updated_at) 
                VALUES (?, ?, ?, ?, '小雨爸爸公众号', ?, ?)""",
                (middle_school_id, year, chonggao_rate, yougao_rate, datetime.now(), datetime.now())
            )
        print("   ✓ 保存部分初中学校数据完成")
        
        # 3. 保存2023年高中录取分数线（优高线以上民办高中）
        print("\n3. 保存2023年高中录取分数线...")
        high_school_data = [
            ('学军文渊', None, 2023, 552),
            ('萧山实验中学', None, 2023, 548),
            ('富阳江南中学', None, 2023, 534),
            ('蕙兰未科学校', None, 2023, 525),
            ('建德新世纪实验', None, 2023, 522),
        ]
        
        for school_name, campus, year, score in high_school_data:
            # 查找或创建高中记录
            if campus:
                cursor.execute("SELECT id FROM high_schools WHERE school_name = ? AND campus = ?", (school_name, campus))
            else:
                cursor.execute("SELECT id FROM high_schools WHERE school_name = ? AND campus IS NULL", (school_name,))
            
            result = cursor.fetchone()
            if not result:
                cursor.execute("INSERT INTO high_schools (school_name, campus) VALUES (?, ?)",
                            (school_name, campus))
                high_school_id = cursor.lastrowid
            else:
                high_school_id = result[0]
            
            # 插入分数线
            cursor.execute(
                """INSERT OR REPLACE INTO high_school_scores 
                (high_school_id, year, admission_score, data_source, created_at, updated_at) 
                VALUES (?, ?, ?, '小雨爸爸公众号', ?, ?)""",
                (high_school_id, year, score, datetime.now(), datetime.now())
            )
        print("   ✓ 保存高中录取分数线完成")
        
        # 4. 打印中考人数预测数据（暂时不存入数据库，可以创建新表）
        print("\n4. 中考人数预测数据:")
        exam_data = [
            (2015, 39000, 2024, 40500),
            (2016, 40000, 2025, 41500),
            (2017, 46000, 2026, 47500),
            (2018, 49000, 2027, 50500),
        ]
        
        for primary_year, primary_num, exam_year, exam_num in exam_data:
            print(f"   小学入学年份: {primary_year}年({primary_num}人) -> 中考年份: {exam_year}年({exam_num}人)")
        
        conn.commit()
        print("\n✓ 所有数据保存成功！")
        
        # 5. 查询并显示已保存的数据
        print("\n" + "="*60)
        print("已保存到数据库的数据：")
        print("="*60)
        
        print("\n【初中学校统计数据】")
        cursor.execute("""
            SELECT m.school_name, m.district, s.year, s.luokao_chonggao_rate, s.chonggao_rate, s.yougao_rate
            FROM middle_schools m
            LEFT JOIN middle_school_stats s ON m.id = s.middle_school_id
            WHERE s.year IS NOT NULL
            ORDER BY s.year DESC, m.school_name
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]} ({row[1]}) - {row[2]}年: 裸考率={row[3]}, 重高率={row[4]}, 优高率={row[5]}")
        
        print("\n【高中录取分数线】")
        cursor.execute("""
            SELECT h.school_name, h.campus, s.year, s.admission_score
            FROM high_schools h
            LEFT JOIN high_school_scores s ON h.id = s.high_school_id
            WHERE s.year IS NOT NULL
            ORDER BY s.year DESC, s.admission_score DESC
        """)
        for row in cursor.fetchall():
            campus_str = f"({row[1]})" if row[1] else ""
            print(f"   {row[0]} {campus_str} - {row[2]}年: {row[3]}分")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    save_article_data()
