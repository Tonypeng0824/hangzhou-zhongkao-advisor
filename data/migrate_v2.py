#!/usr/bin/env python3
"""
schools.db v2 迁移脚本
新增：allocation_quota_details（分配生名额明细表）、historical_score_lines（历年分数线表）
并填充已有数据
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "schools.db")

CREATE_ALLOCATION_QUOTAS = """
CREATE TABLE IF NOT EXISTS allocation_quota_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    high_school_name TEXT NOT NULL,
    campus TEXT,
    middle_school_name TEXT NOT NULL,
    district TEXT,
    quota_2026 INTEGER,
    total_students_2026 INTEGER,
    quota_2025 INTEGER,
    note TEXT,
    source TEXT DEFAULT '杭州市教育局/初中校内公示',
    year INTEGER DEFAULT 2026,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_HISTORICAL_SCORES = """
CREATE TABLE IF NOT EXISTS historical_score_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    high_school_name TEXT NOT NULL,
    campus TEXT,
    full_name TEXT NOT NULL UNIQUE,
    tier INTEGER,
    tier_name TEXT,
    year INTEGER NOT NULL,
    admission_score REAL,
    first_tier_line REAL,
    second_tier_line REAL,
    score_rate REAL,
    enrollment_plan INTEGER,
    note TEXT,
    education_group TEXT,
    boarding_available TEXT,
    district TEXT,
    source TEXT DEFAULT '杭州市教育局/微信公众号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 杭州高中梯队数据 (基于2025年录取数据)
HIGH_SCHOOLS_DATA = [
    # 格式: name, campus, full_name, tier, tier_name, year, admission_score, first_tier_line, second_tier_line, score_rate, enrollment_plan, note, education_group, boarding_available, district

    # 第一梯队 - 前三所
    ("杭二中", "滨江校区", "杭二滨江", 1, "第一梯队-前三所", 2025, None, 563, 280, 96.46, None, "清北/浙大录取数领跑",
     "杭二中教育集团", "是", "滨江区"),
    ("学军中学", "西溪校区", "学军西溪", 1, "第一梯队-前三所", 2025, None, 563, 280, 96.46, None, "与杭二并列顶尖",
     "学军教育集团", "部分床位", "西湖区"),
    ("杭高", "贡院校区", "杭高贡院", 1, "第一梯队-前三所", 2025, None, 563, 280, 95.5, None, "传统名校",
     "杭高教育集团", "是", "拱墅区"),

    # 第二梯队 - 前八所
    ("杭十四中", "凤起校区", "杭十四凤起", 2, "第二梯队-重高", 2025, None, 563, 280, None, None, "老牌重高",
     "杭十四教育集团", "部分床位", "拱墅区"),
    ("杭四中", "下沙校区", "杭四下沙", 2, "第二梯队-重高", 2025, None, 563, 280, None, None, "老牌重高",
     "杭四中教育集团", "是", "钱塘区"),
    ("浙大附中", "玉泉校区", "浙大附中玉泉", 2, "第二梯队-重高", 2025, None, 563, 280, None, None, "位置优越",
     "浙大附中教育集团", "否", "西湖区"),
    ("学军中学", "紫金港校区", "学军紫金港", 2, "第二梯队-重高", 2025, None, 563, 280, None, None, "2025年首次进入前八",
     "学军教育集团", "是", "西湖区"),
    ("长河高中", "主校区", "长河高中", 2, "第二梯队-重高", 2025, None, 563, 280, None, None, "",
     "无", "是", "滨江区"),

    # 第三梯队 - 优高及其他
    ("杭师大附中", "主校区", "杭师大附中", 3, "第三梯队-优高", 2025, 593, 563, 280, None, None, "2025年录取案例593分",
     "无", "是", "西湖区"),
    ("杭二中东河", "校区", "杭二东河", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "有首创班",
     "杭二中教育集团", "否", "上城区"),
    ("杭高钱江", "校区", "杭高钱江", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "",
     "杭高教育集团", "是", "钱塘区"),
    ("源清中学", "主校区", "源清中学", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "稳定优高",
     "无", "是", "拱墅区"),
    ("杭十四康桥", "校区", "杭十四康桥", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "",
     "杭十四教育集团", "是", "拱墅区"),
    ("杭四中", "吴山校区", "杭四吴山", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "",
     "杭四中教育集团", "否", "上城区"),
    ("浙大附中", "丁兰校区", "浙大附中丁兰", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "",
     "浙大附中教育集团", "是", "上城区"),
    ("杭七中", "转塘校区", "杭七中转塘", 3, "第三梯队-优高", 2025, None, 563, 280, None, None, "",
     "无", "是", "西湖区"),

    # 2026年新增
    ("杭二中", "高新校区", "杭二高新", 3, "第三梯队-优高", 2026, None, 563, 280, None, 18 * 45, "2026新增，杭二中教育集团新校区",
     "杭二中教育集团", "是", "滨江区"),
    ("浙大附中", "实验校区", "浙大附实验", 3, "第三梯队-优高", 2026, None, 563, 280, None, 14 * 45, "2026新增，浙大附中新校区",
     "浙大附中教育集团", "是", "上城区"),
    ("淳安中学", "主校区", "淳安中学", 3, "第三梯队-优高", 2026, None, 563, 280, None, None, "首次面向主城区招生",
     "无", "是", "淳安县(首次面向主城区)"),
    ("严州中学", "新安江校区", "严州中学新安江", 3, "第三梯队-优高", 2026, None, 563, 280, None, None, "首次面向主城区招生",
     "无", "是", "建德市(首次面向主城区)"),
    ("建德市新安江中学", "主校区", "建德新安江中学", 3, "第三梯队-优高", 2026, None, 563, 280, None, None, "首次面向主城区招生",
     "无", "是", "建德市(首次面向主城区)"),
]

# 分配生比例数据 (2026年)
ALLOCATION_QUOTA_DATA = [
    ("杭二中", "滨江校区", "", "", None, None, None, "前三所重高，分配生比例70%"),
    ("学军中学", "西溪校区", "", "", None, None, None, "前三所重高，分配生比例70%"),
    ("杭高", "贡院校区", "", "", None, None, None, "前三所重高，分配生比例70%"),
    ("杭二中", "高新校区", "", "", None, None, None, "2026新增，分配生比例40%，招18班"),
    ("浙大附中", "实验校区", "", "", None, None, None, "2026新增，分配生比例40%，招14班"),
]

# 2026年中考关键参数表
CREATE_KEY_PARAMS = """
CREATE TABLE IF NOT EXISTS key_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    param_name TEXT NOT NULL,
    param_value TEXT,
    param_type TEXT,
    year INTEGER NOT NULL,
    category TEXT,
    note TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

KEY_PARAMS_DATA = [
    # 2025年关键参数
    ("分配生总数", "8004", "integer", 2025, "分配生", "22所学校/28个招生单位", "杭州市教育局"),
    ("分配生占毕业生比例", "19.4", "percent", 2025, "分配生", "", "杭州市教育局"),
    ("分配生控制线", "563", "integer", 2025, "分数线", "一段线=分配生控制线", "杭州市教育局"),
    ("一段线", "563", "integer", 2025, "分数线", "集中统一第一段", "杭州市教育局"),
    ("二段线", "280", "integer", 2025, "分数线", "集中统一第二段", "杭州市教育局"),
    ("中考总分", "650", "integer", 2025, "考试", "文化课620+体育30", "杭州市教育局"),
    ("前三所分配生比例", "70", "percent", 2025, "分配生", "8个重高主校区", "杭州市教育局"),
    # 2026年关键参数
    ("分配生总数", "9021", "integer", 2026, "分配生", "24所学校/30个招生单位，增1017名", "杭州市教育局"),
    ("分配生占毕业生比例", "20.5", "percent", 2026, "分配生", "较2025年+1.1pp", "杭州市教育局"),
    ("市区初三毕业生总数", "44000", "integer", 2026, "考试", "约4.4万人", "多家公众号"),
    ("中考人数增长", "3100", "integer", 2026, "考试", "较2025年增3100人", "微信公众号"),
    ("分配生控制线参考(2025)", "563", "integer", 2026, "分数线", "参考2025年", "杭州市教育局"),
    ("新增分配生招生学校", "杭二高新、浙大附实验", "string", 2026, "分配生", "2026年新参与分配生招生", "杭州市教育局"),
    ("志愿填报时间", "5月29日-30日", "string", 2026, "时间节点", "16:00关闭", "杭州市教育局"),
    ("中考考试时间", "6月20日-21日", "string", 2026, "时间节点", "", "杭州市教育局"),
    ("志愿填报系统", "www.hzjyks.net", "string", 2026, "系统", "", "杭州市教育局"),
]


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建新表
    cursor.execute(CREATE_ALLOCATION_QUOTAS)
    print("[OK] allocation_quota_details table created")

    cursor.execute(CREATE_HISTORICAL_SCORES)
    print("[OK] historical_score_lines table created")

    cursor.execute(CREATE_KEY_PARAMS)
    print("[OK] key_params table created")

    # 填充高中分数线数据
    existing = set()
    cursor.execute("SELECT full_name FROM historical_score_lines")
    for r in cursor.fetchall():
        existing.add(r[0])

    inserted = 0
    for hs in HIGH_SCHOOLS_DATA:
        full_name = hs[2]
        if full_name in existing:
            continue
        cursor.execute("""
            INSERT INTO historical_score_lines 
            (high_school_name, campus, full_name, tier, tier_name, year, 
             admission_score, first_tier_line, second_tier_line, score_rate,
             enrollment_plan, note, education_group, boarding_available, district)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, hs)
        inserted += 1

    print(f"[OK] historical_score_lines: {inserted} rows inserted")

    # 填充2026年分配生名额
    existing_q = set()
    cursor.execute("SELECT high_school_name, campus FROM allocation_quota_details WHERE year=2026")
    for r in cursor.fetchall():
        existing_q.add((r[0], r[1] or ""))

    inserted_q = 0
    for aq in ALLOCATION_QUOTA_DATA:
        key = (aq[0], aq[1] or "")
        if key in existing_q:
            continue
        cursor.execute("""
            INSERT INTO allocation_quota_details
            (high_school_name, campus, middle_school_name, district,
             quota_2026, total_students_2026, quota_2025, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, aq)
        inserted_q += 1

    print(f"[OK] allocation_quota_details: {inserted_q} rows inserted")

    # 填充关键参数
    existing_p = set()
    cursor.execute("SELECT param_name, year FROM key_params")
    for r in cursor.fetchall():
        existing_p.add((r[0], r[1]))

    inserted_p = 0
    for kp in KEY_PARAMS_DATA:
        key = (kp[0], kp[3])
        if key in existing_p:
            continue
        cursor.execute("""
            INSERT INTO key_params
            (param_name, param_value, param_type, year, category, note, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, kp)
        inserted_p += 1

    print(f"[OK] key_params: {inserted_p} rows inserted")

    conn.commit()
    conn.close()

    print("\nMigration complete!")


if __name__ == "__main__":
    migrate()
