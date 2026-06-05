-- 初中基本信息表
CREATE TABLE IF NOT EXISTS middle_schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL UNIQUE,
    district TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初中年度统计数据表
CREATE TABLE IF NOT EXISTS middle_school_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    middle_school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    student_count INTEGER,
    luokao_chonggao_rate REAL,
    luokao_yougao_rate REAL,
    chonggao_rate REAL,
    yougao_rate REAL,
    qiansan_rate REAL,
    allocation_quota INTEGER,
    data_source TEXT DEFAULT '小雨爸爸公众号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(middle_school_id, year),
    FOREIGN KEY (middle_school_id) REFERENCES middle_schools(id)
);

-- 高中基本信息表
CREATE TABLE IF NOT EXISTS high_schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    campus TEXT,
    district TEXT,
    address TEXT,
    metro_station TEXT,
    boarding_available TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 高中录取分数线表
CREATE TABLE IF NOT EXISTS high_school_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    high_school_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    admission_score INTEGER,
    data_source TEXT DEFAULT '小雨爸爸公众号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(high_school_id, year),
    FOREIGN KEY (high_school_id) REFERENCES high_schools(id)
);

-- 分配生数据表
CREATE TABLE IF NOT EXISTS allocation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    middle_school_id INTEGER NOT NULL,
    high_school_id INTEGER NOT NULL,
    allocated_count INTEGER,
    data_source TEXT DEFAULT '小雨爸爸公众号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, middle_school_id, high_school_id),
    FOREIGN KEY (middle_school_id) REFERENCES middle_schools(id),
    FOREIGN KEY (high_school_id) REFERENCES high_schools(id)
);

-- 高中生源统计数据表
CREATE TABLE IF NOT EXISTS student_source_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    high_school_id INTEGER NOT NULL,
    middle_school_id INTEGER NOT NULL,
    student_count INTEGER,
    source_type TEXT,
    data_source TEXT DEFAULT '小雨爸爸公众号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, high_school_id, middle_school_id, source_type),
    FOREIGN KEY (middle_school_id) REFERENCES middle_schools(id),
    FOREIGN KEY (high_school_id) REFERENCES high_schools(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_middle_school_stats_year ON middle_school_stats(year);
CREATE INDEX IF NOT EXISTS idx_high_school_scores_year ON high_school_scores(year);
CREATE INDEX IF NOT EXISTS idx_allocation_data_year ON allocation_data(year);
CREATE INDEX IF NOT EXISTS idx_student_source_stats_year ON student_source_stats(year);
