"""
系统调试检查脚本
检查数据库、API、前端连接
"""

import sqlite3
import requests

DB_PATH = r"C:\Users\58452\.openclaw\workspace\study\backend\scores.db"
API = 'http://localhost:8808/api'

print("=" * 60)
print("  System Debug Check")
print("=" * 60)

# ========== 1. 检查数据库 ==========
print("\n[1] Database Check")
print("-" * 40)

conn = sqlite3.connect(DB_PATH)

# 学生数
cursor = conn.execute("SELECT COUNT(*) FROM students")
student_count = cursor.fetchone()[0]
print(f"  Students: {student_count}")

# 成绩数
cursor = conn.execute("SELECT COUNT(*) FROM scores")
score_count = cursor.fetchone()[0]
print(f"  Scores: {score_count}")

# 查找茗心
cursor = conn.execute("""
    SELECT student_id, student_name 
    FROM students 
    WHERE student_name LIKE '%茗心%' OR student_name LIKE '%郑%'
""")
mingxin = cursor.fetchall()
print(f"  茗心查找：{mingxin}")

# 茗心的成绩
if mingxin:
    student_id = mingxin[0][0]
    cursor = conn.execute("""
        SELECT exam_name, score, semester 
        FROM scores 
        WHERE student_id = ?
        LIMIT 5
    """, (student_id,))
    scores = cursor.fetchall()
    print(f"  茗心的成绩 (前 5 条):")
    for s in scores:
        print(f"    {s[0]}: {s[1]} ({s[2]})")

# 考试列表
cursor = conn.execute("SELECT DISTINCT semester FROM scores ORDER BY semester")
semesters = cursor.fetchall()
print(f"  学期列表：{[s[0] for s in semesters]}")

conn.close()

# ========== 2. 检查 API ==========
print("\n[2] API Check")
print("-" * 40)

try:
    # 测试根路径
    r = requests.get('http://localhost:8808/', timeout=5)
    print(f"  Root: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"  Root: ERROR - {e}")

try:
    # 测试学生 API
    r = requests.get(f'{API}/students', timeout=5)
    if r.status_code == 200:
        students = r.json()
        print(f"  /api/students: {r.status_code} - {len(students)} students")
        # 查找茗心
        mingxin_api = [s for s in students if '茗心' in str(s)]
        if mingxin_api:
            print(f"    茗心：{mingxin_api[0]}")
    else:
        print(f"  /api/students: {r.status_code}")
except Exception as e:
    print(f"  /api/students: ERROR - {e}")

try:
    # 测试概览 API
    r = requests.get(f'{API}/analysis/overview', timeout=5)
    if r.status_code == 200:
        data = r.json()
        stats = data.get('basic_stats', {})
        print(f"  /api/analysis/overview: {r.status_code}")
        print(f"    Students: {stats.get('total_students')}")
        print(f"    Exams: {stats.get('total_exams')}")
        print(f"    Records: {stats.get('total_records')}")
    else:
        print(f"  /api/analysis/overview: {r.status_code} - {r.text[:200]}")
except Exception as e:
    print(f"  /api/analysis/overview: ERROR - {e}")

try:
    # 如果找到茗心，测试她的成绩
    if mingxin:
        student_id = mingxin[0][0]
        r = requests.get(f'{API}/analysis/student/{student_id}/trend', timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"  /api/analysis/student/{student_id}/trend: {r.status_code}")
            if 'score_trend' in data:
                print(f"    成绩记录：{len(data['score_trend'])} 条")
                if data['score_trend']:
                    print(f"    第一条：{data['score_trend'][0]}")
        else:
            print(f"  /api/analysis/student/{student_id}/trend: {r.status_code} - {r.text[:200]}")
except Exception as e:
    print(f"  Student trend: ERROR - {e}")

# ========== 3. 检查前端文件 ==========
print("\n[3] Frontend File Check")
print("-" * 40)

import os
frontend_path = r"C:\Users\58452\.openclaw\workspace\study\frontend\index.html"
if os.path.exists(frontend_path):
    with open(frontend_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"  index.html: {len(content)} bytes")
        
        # 检查 API 地址
        if 'http://localhost:8808/api' in content:
            print(f"  API 地址：✅ 8808 端口正确")
        elif 'http://localhost:8000/api' in content:
            print(f"  API 地址：❌ 8000 端口（需要修改）")
        else:
            print(f"  API 地址：❓ 未找到")
        
        # 检查关键组件
        checks = {
            'Vue': 'createApp',
            'ECharts': 'echarts',
            '学生选择器': 'student-select',
            '成绩趋势图': 'studentTrendChart',
            '成就系统': 'achievement'
        }
        
        for name, keyword in checks.items():
            if keyword in content:
                print(f"  {name}: ✅")
            else:
                print(f"  {name}: ❌")
else:
    print(f"  index.html: ❌ 文件不存在")

print("\n" + "=" * 60)
print("  Debug Check Complete")
print("=" * 60)
