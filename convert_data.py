"""
数学成绩数据转换脚本
将横向 Excel 数据转换为系统可用的纵向格式
作者：非哥家庭助手
"""

import pandas as pd
import os
import sqlite3
from datetime import datetime

# 数据目录
DATA_DIR = r"D:\openclaw\workspace\projects\study\data"
DB_PATH = r"C:\Users\58452\.openclaw\workspace\study\backend\scores.db"

# 考试名称映射（根据文件名推测）
EXAM_MAPPING = {
    '10032': '三年级上学期',
    '10033': '三年级下学期', 
    '10034': '四年级上学期',
    '10035': '四年级下学期',
    '10036': '五年级上学期',
    '10037': '五年级下学期'
}

# 列名映射（中文列名转标准列名）
COLUMN_MAPPING = {
    '姓名': 'student_name',
    '练习 1': '练习 1',
    '练习 2': '练习 2',
    '练习 3': '练习 3',
    '练习 4': '练习 4',
    '练习 5': '练习 5',
    '练习 6': '练习 6',
    '练习 7': '练习 7',
    '练习 8': '练习 8',
    '练习 9': '练习 9',
    '练习 10': '练习 10',
    '练习 11': '练习 11',
    '练习 12': '练习 12',
    '练习 13': '练习 13',
    '练习 14': '练习 14',
    '练习 15': '练习 15',
    '练习 16': '练习 16',
    '期末模 1': '期末模拟 1',
    '期末模 2': '期末模拟 2',
    '期末模 3': '期末模拟 3',
    '期末模 4': '期末模拟 4',
    '期末': '期末考试'
}

def convert_exam_name(filename, exam_col):
    """根据文件名和列名生成完整考试名称"""
    # 从文件名提取学期
    semester = None
    for code, name in EXAM_MAPPING.items():
        if code in filename:
            semester = name
            break
    
    if semester and exam_col:
        return f"{semester}-{exam_col}"
    return exam_col

def process_excel_file(filepath, filename):
    """处理单个 Excel 文件"""
    print(f"\n处理文件：{filename}")
    
    # 读取 Excel
    df = pd.read_excel(filepath)
    print(f"  原始数据：{len(df)} 行 × {len(df.columns)} 列")
    
    # 重命名列
    df = df.rename(columns=COLUMN_MAPPING)
    
    # 提取考试列（排除学号、姓名）
    exam_cols = [col for col in df.columns if col not in ['学号', 'student_name', '姓名']]
    
    # 转换数据格式（横向→纵向）
    records = []
    for _, row in df.iterrows():
        student_id = str(row.get('学号', row.iloc[0]))
        student_name = row.get('student_name', row.iloc[1] if len(row) > 1 else '未知')
        
        # 跳过空行
        if pd.isna(student_name) or student_name == '':
            continue
        
        # 处理每次考试成绩
        for exam_col in exam_cols:
            if exam_col in row:
                val = row[exam_col]
                # 跳过空值
                if pd.isna(val) or (isinstance(val, str) and val.strip() == ''):
                    continue
                try:
                    score = float(val)
                    exam_name = convert_exam_name(filename, exam_col)
                    
                    records.append({
                        'student_id': student_id,
                        'student_name': student_name,
                        'exam_name': exam_name,
                        'score': score,
                        'full_score': 100,
                        'semester': EXAM_MAPPING.get(filename[:5], '')
                    })
                except (ValueError, TypeError):
                    continue
    
    print(f"  转换后：{len(records)} 条成绩记录")
    return records

def save_to_database(records):
    """保存数据到 SQLite 数据库"""
    print(f"\n保存到数据库...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            student_name TEXT,
            class_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            exam_name TEXT,
            exam_date DATE,
            score REAL,
            full_score REAL DEFAULT 100,
            rank INTEGER,
            class_avg REAL,
            grade_level TEXT,
            semester TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')
    
    # 插入学生
    students = {}
    for record in records:
        sid = record['student_id']
        if sid not in students:
            students[sid] = record['student_name']
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO students (student_id, student_name, class_name)
                    VALUES (?, ?, ?)
                ''', (sid, record['student_name'], '班级'))
            except Exception as e:
                print(f"  插入学生 {sid} 失败：{e}")
    
    print(f"  插入学生：{len(students)} 人")
    
    # 插入成绩
    inserted = 0
    for record in records:
        try:
            cursor.execute('''
                INSERT INTO scores (student_id, exam_name, exam_date, score, full_score, semester)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record['student_id'],
                record['exam_name'],
                datetime.now().strftime('%Y-%m-%d'),
                record['score'],
                record['full_score'],
                record['semester']
            ))
            inserted += 1
        except Exception as e:
            print(f"  插入成绩失败：{e}")
    
    print(f"  插入成绩：{inserted} 条")
    
    conn.commit()
    conn.close()
    return inserted

def main():
    """主函数"""
    print("=" * 60)
    print("  Math Score Data Converter")
    print("  Non哥 Family Assistant 2026")
    print("=" * 60)
    
    # 获取所有 Excel 文件
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]
    print(f"\n找到 {len(excel_files)} 个 Excel 文件:")
    for i, f in enumerate(excel_files, 1):
        print(f"  {i}. {f}")
    
    # 处理所有文件
    all_records = []
    for filename in excel_files:
        filepath = os.path.join(DATA_DIR, filename)
        records = process_excel_file(filepath, filename)
        all_records.extend(records)
    
    print(f"\n总计：{len(all_records)} 条成绩记录")
    
    # 保存到数据库
    if all_records:
        inserted = save_to_database(all_records)
        print(f"\n[OK] 完成！共导入 {inserted} 条成绩记录")
        print(f"\nNext steps:")
        print(f"  1. Double click: study\\qidong-houduan.bat")
        print(f"  2. Double click: study\\qidong-qianduan.bat")
        print(f"  3. Open browser: http://localhost:3000")
    else:
        print("\n[ERROR] No data to import")

if __name__ == "__main__":
    main()
