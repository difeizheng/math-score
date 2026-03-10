"""
数学成绩数据转换脚本 v2
正确解析 Excel 格式：
- 文件名表示学期（如 10032-1(2) 班上学期=一年级上学期）
- 第 1 列：序号（作为学号）
- 第 2 列：学生姓名
- 第 3 列开始：按时间顺序的每次考试成绩
"""

import pandas as pd
import os
import sqlite3
from datetime import datetime

# 数据目录
DATA_DIR = r"D:\openclaw\workspace\projects\study\data"
DB_PATH = r"C:\Users\58452\.openclaw\workspace\study\backend\scores.db"

# 文件名解析 - 学期映射
def parse_semester(filename):
    """从文件名解析学期信息"""
    # 10032-1(2) 班上学期数学考试分数-math_scores.xlsx
    # 提取数字部分
    if '10032' in filename:
        return '一年级上学期'
    elif '10033' in filename:
        return '一年级下学期'
    elif '10034' in filename:
        return '二年级上学期'
    elif '10035' in filename:
        return '二年级下学期'
    elif '10036' in filename:
        return '三年级上学期'
    elif '10037' in filename:
        return '三年级下学期'
    else:
        return '未知学期'

def parse_exam_columns(df):
    """解析考试列名，生成考试名称列表"""
    # 从第 3 列开始（索引 2）是考试成绩
    exam_cols = df.columns[2:].tolist()
    return exam_cols

def process_excel_file(filepath, filename):
    """处理单个 Excel 文件"""
    print(f"\nProcessing: {filename}")
    
    # 读取 Excel
    df = pd.read_excel(filepath)
    print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
    
    # 解析学期
    semester = parse_semester(filename)
    print(f"  Semester: {semester}")
    
    # 获取考试列名
    exam_cols = parse_exam_columns(df)
    print(f"  Exams: {len(exam_cols)} times")
    
    # 转换数据格式（横向→纵向）
    records = []
    students = {}
    
    for idx, row in df.iterrows():
        # 第 1 列=学号，第 2 列=姓名
        student_id = str(row.iloc[0]).strip()
        student_name = str(row.iloc[1]).strip()
        
        # 跳过空行
        if not student_id or not student_name or student_name == 'nan':
            continue
        
        # 记录学生信息
        if student_id not in students:
            students[student_id] = student_name
        
        # 处理每次考试成绩（从第 3 列开始）
        for exam_idx, exam_name in enumerate(exam_cols, start=1):
            score_val = row.iloc[exam_idx + 1]  # 从第 3 列开始（索引 2）
            
            # 跳过空值
            if pd.isna(score_val):
                continue
            
            try:
                score = float(score_val)
                # 生成完整考试名称
                full_exam_name = f"{semester}-第{exam_idx}次"
                
                records.append({
                    'student_id': student_id,
                    'student_name': student_name,
                    'exam_name': full_exam_name,
                    'exam_order': exam_idx,
                    'score': score,
                    'full_score': 100,
                    'semester': semester
                })
            except (ValueError, TypeError):
                continue
    
    print(f"  Students: {len(students)}")
    print(f"  Records: {len(records)}")
    
    return records, students

def save_to_database(all_records, all_students):
    """保存数据到 SQLite 数据库"""
    print(f"\nSaving to database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空旧数据
    print("  Clearing old data...")
    cursor.execute("DELETE FROM scores")
    cursor.execute("DELETE FROM students")
    
    # 插入学生
    print(f"  Inserting {len(all_students)} students...")
    for student_id, student_name in all_students.items():
        try:
            cursor.execute('''
                INSERT INTO students (student_id, student_name, class_name)
                VALUES (?, ?, ?)
            ''', (student_id, student_name, '班级'))
        except Exception as e:
            print(f"    Error inserting student {student_id}: {e}")
    
    # 插入成绩
    print(f"  Inserting {len(all_records)} scores...")
    inserted = 0
    for record in all_records:
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
            print(f"    Error inserting score: {e}")
    
    conn.commit()
    conn.close()
    
    return inserted

def main():
    """主函数"""
    print("=" * 60)
    print("  Math Score Data Converter v2")
    print("  Format: 序号 | 姓名 | 考试 1 | 考试 2 | ...")
    print("=" * 60)
    
    # 获取所有 Excel 文件
    excel_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')])
    print(f"\nFound {len(excel_files)} Excel files:")
    for i, f in enumerate(excel_files, 1):
        sem = parse_semester(f)
        print(f"  {i}. {f[:50]}... -> {sem}")
    
    # 处理所有文件
    all_records = []
    all_students = {}
    
    for filename in excel_files:
        filepath = os.path.join(DATA_DIR, filename)
        records, students = process_excel_file(filepath, filename)
        all_records.extend(records)
        all_students.update(students)
    
    print(f"\n{'='*60}")
    print(f"Total:")
    print(f"  Students: {len(all_students)}")
    print(f"  Records: {len(all_records)}")
    print(f"{'='*60}")
    
    # 保存到数据库
    if all_records:
        inserted = save_to_database(all_records, all_students)
        print(f"\n[OK] Done! Imported {inserted} score records")
        print(f"\nNext steps:")
        print(f"  1. Restart backend: python main.py")
        print(f"  2. Open browser: http://localhost:8808")
    else:
        print("\n[ERROR] No data to import")

if __name__ == "__main__":
    main()
