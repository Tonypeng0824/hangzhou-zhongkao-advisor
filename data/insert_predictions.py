#!/usr/bin/env python3
"""Insert mock exam cutoffs, 2025 actual scores, and 2026 predictions into schools.db"""
import sqlite3

db = 'C:/Users/Administrator/.workbuddy/skills/hangzhou-zhongkao-advisor/data/schools.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# === Table: mock_exam_cutoffs ===
c.execute('''CREATE TABLE IF NOT EXISTS mock_exam_cutoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL, district TEXT NOT NULL,
    top3_line REAL, top8_line REAL, heavy_high_line REAL, excellent_high_line REAL,
    a_line REAL, b_line REAL, c_line REAL, d_line REAL,
    includes_pe BOOLEAN DEFAULT 0, note TEXT, source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# === Table: score_line_predictions ===
c.execute('''CREATE TABLE IF NOT EXISTS score_line_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_for_year INTEGER NOT NULL, line_name TEXT NOT NULL,
    predicted_score REAL, score_low REAL, score_high REAL,
    confidence TEXT, method TEXT, factors TEXT, source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# === 2025 Mock Exam Cutoffs ===
c.execute("DELETE FROM mock_exam_cutoffs WHERE year=2025")
mock_2025 = [
    (2025, '西湖区', 582, None, 565, 515, None, None, None, None, 0, '前三582/重高565/优高515', '网易/杭州芽儿升学'),
    (2025, '拱墅区', 576, 556, None, 496, None, None, None, None, 0, '前三576/前八556/优高496', '网易/杭州芽儿升学'),
    (2025, '上城区', None, None, None, None, 554.5, 506.5, None, None, 0, 'A线(前30%)/B线(前50%)', '19楼/sjds对比'),
    (2025, '滨江区', None, None, 562, 490.5, None, None, None, None, 0, '重高562/优高490.5', '头条/sjds对比'),
    (2025, '钱塘区', None, None, None, None, None, None, None, None, 0, '2025数据暂缺', 'N/A'),
]
c.executemany('INSERT INTO mock_exam_cutoffs (year,district,top3_line,top8_line,heavy_high_line,excellent_high_line,a_line,b_line,c_line,d_line,includes_pe,note,source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', mock_2025)

# === 2026 Mock Exam Cutoffs ===
c.execute("DELETE FROM mock_exam_cutoffs WHERE year=2026")
mock_2026 = [
    (2026, '西湖区', 584.5, None, 570, 519, None, None, None, None, 0, '前三584.5/重高570/优高519; +5/+4 vs2025', 'sjds.net'),
    (2026, '拱墅区', None, None, None, None, 588.5, 574, 521.5, 462.5, 0, 'A/B/C/D四线制', 'sjds.net'),
    (2026, '上城区', None, None, None, None, 559, 515, None, None, 0, 'A线559(前25%)/B515(前50%); +4.5/+8.5', 'sjds.net/19楼'),
    (2026, '滨江区', None, None, 555, 497.5, None, None, 442.5, None, 0, '重高555/优高497.5/C442.5; 重高-7/优高+7', 'sjds.net'),
    (2026, '钱塘区', None, None, 595.5, 557.5, None, None, 547.5, 535, 1, '含体育! -30后重高565.5/优高527.5', 'sjds.net'),
]
c.executemany('INSERT INTO mock_exam_cutoffs (year,district,top3_line,top8_line,heavy_high_line,excellent_high_line,a_line,b_line,c_line,d_line,includes_pe,note,source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', mock_2026)

# === Update historical_score_lines with actual 2025 scores ===
actual_scores = {
    '杭二滨江': (630, 1, '杭二中教育集团'),
    '学军西溪': (629, 1, '学军教育集团'),
    '杭高贡院': (627, 1, '杭高教育集团'),
    '杭十四凤起': (624, 2, '杭十四教育集团'),
    '学军紫金港': (623, 2, '学军教育集团'),
    '杭四下沙': (622, 2, '杭四中教育集团'),
    '浙大附中玉泉': (620, 2, '浙大附中教育集团'),
    '长河高中': (619, 2, ''),
    '杭师大附中': (617, 3, ''),
    '杭高钱江': (617, 3, '杭高教育集团'),
    '杭十四康桥': (612, 3, '杭十四教育集团'),
    '浙大附中丁兰': (610, 3, '浙大附中教育集团'),
    '源清中学': (607, 3, ''),
    '杭二东河': (602, 3, '杭二中教育集团'),
}

for full_name, (score, tier, group) in actual_scores.items():
    c.execute('SELECT id FROM historical_score_lines WHERE full_name=? AND year=2025', (full_name,))
    existing = c.fetchone()
    if existing:
        c.execute('UPDATE historical_score_lines SET admission_score=?, first_tier_line=563, second_tier_line=280, tier=?, education_group=? WHERE full_name=? AND year=2025',
                  (score, tier, group, full_name))
    else:
        c.execute('INSERT INTO historical_score_lines (high_school_name, campus, full_name, tier, tier_name, year, admission_score, first_tier_line, second_tier_line, education_group) VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (full_name, '', full_name, tier, '', 2025, score, 563, 280, group))

# === 2026 predictions ===
c.execute("DELETE FROM score_line_predictions")
predictions = [
    (2026, '一段线', 567, 563, 572, '中高', '一模修正+竞争',
     '2025=563; 2026一模普涨3-5分; 考生+3100推高2-4; 新增学位缓冲1-2; 预测567±5', '综合分析'),
    (2026, '二段线', 285, 280, 290, '高', '基本稳定',
     '历年二段线变化小; 考生增加不影响底部', '综合分析'),
    (2026, '前三所重高(杭二/学军/杭高)', 632, 628, 636, '中', '一模前三线趋势',
     '2025前三627-630; 西湖一模前三584.5(+2.5); 修正+47.5=632; 综合632±4', '一模修正'),
    (2026, '重高末位(长河/杭师附)', 622, 618, 626, '中', '一模重高线趋势',
     '2025重高末位617-619; 西湖重高570(+5)+52修正=622; 上城A线559(+4.5)+63=622', '一模修正(西湖基准)'),
    (2026, '优高线(源清/康桥级)', 610, 606, 614, '中', '一模优高线趋势',
     '2025优高607/612/610; 西湖优高519(+4)+91修正=610; 上城B515(+8.5)+95=610', '一模修正'),
    (2026, '杭二高新(新校)', 600, 593, 607, '低', '新校首年推测',
     '新校<主校15-25分; 杭二品牌+5-10; 参考东河602; 预计593-600', '新校推测'),
    (2026, '浙大附实验(新校)', 595, 588, 602, '低', '新校首年推测',
     '浙大丁兰610; 新校-10~15; 预计588-602', '新校推测'),
    (2026, '淳安中学(首招主城)', 570, 565, 578, '低', '县中首年推测',
     '首招主城区; 略高于一段线; 预计565-578', '新校推测'),
]
c.executemany('INSERT INTO score_line_predictions (prediction_for_year,line_name,predicted_score,score_low,score_high,confidence,method,factors,source) VALUES (?,?,?,?,?,?,?,?,?)', predictions)

# Add key_params for 2025
for p in [('一段线', '563', 'integer', 2025, '分数线', '集中统一第一段', '杭州市教育局'),
          ('二段线', '280', 'integer', 2025, '分数线', '集中统一第二段', '杭州市教育局'),
          ('前三最低录取分', '627', 'integer', 2025, '分数线', '杭高贡院最低', '杭州市教育局'),
          ('重高末位录取分', '619', 'integer', 2025, '分数线', '长河高中最低', '杭州市教育局'),
          ('优高末位录取分', '602', 'integer', 2025, '分数线', '杭二东河', '杭州市教育局')]:
    c.execute('SELECT COUNT(*) FROM key_params WHERE param_name=? AND year=?', (p[0], p[3]))
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO key_params (param_name,param_value,param_type,year,category,note,source) VALUES (?,?,?,?,?,?,?)', p)

conn.commit()

# === Print summary ===
print('=== mock_exam_cutoffs ===')
for r in c.execute('SELECT year,district,heavy_high_line,excellent_high_line,a_line,b_line FROM mock_exam_cutoffs ORDER BY year,district'):
    print(f'  {r[0]} {r[1]:6s} 重高:{r[2]} 优高:{r[3]} A:{r[4]} B:{r[5]}')

print('\n=== 2025 actual scores ===')
for r in c.execute('SELECT full_name,admission_score FROM historical_score_lines WHERE admission_score IS NOT NULL AND year=2025 ORDER BY admission_score DESC'):
    print(f'  {r[0]:14s} {r[1]:.0f}')

print('\n=== 2026 predictions ===')
for r in c.execute('SELECT line_name,predicted_score,score_low,score_high,confidence FROM score_line_predictions'):
    print(f'  {r[0]:30s} {r[1]:.0f} ({r[2]:.0f}-{r[3]:.0f}) conf:{r[4]}')

print('\n=== key_params 2025 ===')
for r in c.execute("SELECT param_name,param_value FROM key_params WHERE year=2025 AND category='分数线'"):
    print(f'  {r[0]}: {r[1]}')

conn.close()
print('\nDone!')
