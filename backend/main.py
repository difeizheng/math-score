"""
数学成绩分析系统 - 后端 API
作者：非哥家庭助手
功能：成绩数据导入、分析、可视化
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
from datetime import datetime
import os
from typing import List, Dict, Any
import numpy as np

# 导入高级分析模块
from advanced_analysis import (
    get_semester_stats,
    predict_next_score,
    analyze_risk,
    calculate_percentile_rank,
    analyze_stability,
    generate_learning_advice
)

app = FastAPI(title="数学成绩分析系统", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "scores.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建学生表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            student_name TEXT,
            class_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建成绩表
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
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

@app.get("/")
def root():
    return {"message": "数学成绩分析系统 API", "version": "1.0.0"}

@app.post("/api/import/excel")
async def import_excel(file: UploadFile = File(...)):
    """
    导入 Excel 成绩数据
    支持的列：学号、姓名、班级、考试名称、考试日期、成绩、满分、排名、年级、学期
    """
    try:
        # 读取 Excel
        contents = await file.read()
        df = pd.read_excel(contents)
        
        # 标准化列名
        column_mapping = {
            '学号': 'student_id',
            '姓名': 'student_name',
            '班级': 'class_name',
            '考试名称': 'exam_name',
            '考试日期': 'exam_date',
            '成绩': 'score',
            '满分': 'full_score',
            '排名': 'rank',
            '年级': 'grade_level',
            '学期': 'semester',
            '班级平均分': 'class_avg'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 检查必要列
        required_cols = ['student_id', 'student_name', 'exam_name', 'score']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"缺少必要列：{missing_cols}")
        
        # 存入数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        imported_count = 0
        for _, row in df.iterrows():
            # 插入或更新学生信息
            cursor.execute('''
                INSERT OR REPLACE INTO students (student_id, student_name, class_name)
                VALUES (?, ?, ?)
            ''', (
                str(row['student_id']),
                row['student_name'],
                row.get('class_name', '')
            ))
            
            # 插入成绩记录
            exam_date = row.get('exam_date', datetime.now().strftime('%Y-%m-%d'))
            if hasattr(exam_date, 'strftime'):
                exam_date = exam_date.strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO scores (student_id, exam_name, exam_date, score, full_score, rank, class_avg, grade_level, semester)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(row['student_id']),
                row['exam_name'],
                exam_date,
                row['score'],
                row.get('full_score', 100),
                row.get('rank'),
                row.get('class_avg'),
                row.get('grade_level', ''),
                row.get('semester', '')
            ))
            
            imported_count += 1
        
        conn.commit()
        conn.close()
        
        return {
            "message": "数据导入成功",
            "imported_count": imported_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students")
def get_students():
    """获取所有学生列表"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM students ORDER BY class_name, student_name", conn)
    conn.close()
    return df.to_dict('records')

@app.get("/api/exams")
def get_exams():
    """获取所有考试列表"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('''
        SELECT DISTINCT exam_name, exam_date, semester, grade_level 
        FROM scores 
        ORDER BY exam_date DESC
    ''', conn)
    conn.close()
    return df.to_dict('records')

@app.get("/api/student/{student_id}/scores")
def get_student_scores(student_id: str):
    """获取指定学生的所有成绩"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('''
        SELECT s.*, st.student_name, st.class_name
        FROM scores s
        JOIN students st ON s.student_id = st.student_id
        WHERE s.student_id = ?
        ORDER BY s.exam_date DESC
    ''', conn, params=(student_id,))
    conn.close()
    return df.to_dict('records')

@app.get("/api/analysis/overview")
def analysis_overview():
    """
    整体分析概览
    - 总学生数、总考试次数
    - 平均分趋势
    - 分数段分布
    """
    conn = sqlite3.connect(DB_PATH)
    
    # 基础统计
    student_count = int(pd.read_sql_query("SELECT COUNT(DISTINCT student_id) as count FROM students", conn).iloc[0]['count'])
    exam_count = int(pd.read_sql_query("SELECT COUNT(DISTINCT exam_name) as count FROM scores", conn).iloc[0]['count'])
    total_records = int(pd.read_sql_query("SELECT COUNT(*) as count FROM scores", conn).iloc[0]['count'])
    
    # 平均分趋势（按考试）
    avg_trend = pd.read_sql_query('''
        SELECT exam_name, exam_date, AVG(score) as avg_score, COUNT(*) as student_count
        FROM scores
        GROUP BY exam_name, exam_date
        ORDER BY exam_date
    ''', conn)
    
    # 分数段分布
    score_distribution = pd.read_sql_query('''
        SELECT 
            CASE 
                WHEN score >= 90 THEN '90-100 (优秀)'
                WHEN score >= 80 THEN '80-89 (良好)'
                WHEN score >= 70 THEN '70-79 (中等)'
                WHEN score >= 60 THEN '60-69 (及格)'
                ELSE '60 以下 (待提高)'
            END as level,
            COUNT(*) as count
        FROM scores
        GROUP BY level
    ''', conn)
    
    conn.close()
    
    # 转换 numpy 类型为 Python 原生类型
    avg_trend_list = []
    for _, row in avg_trend.iterrows():
        avg_trend_list.append({
            'exam_name': str(row['exam_name']),
            'exam_date': str(row['exam_date']),
            'avg_score': float(row['avg_score']) if pd.notna(row['avg_score']) else 0,
            'student_count': int(row['student_count'])
        })
    
    score_dist_list = []
    for _, row in score_distribution.iterrows():
        score_dist_list.append({
            'level': str(row['level']),
            'count': int(row['count'])
        })
    
    return {
        "basic_stats": {
            "total_students": student_count,
            "total_exams": exam_count,
            "total_records": total_records
        },
        "avg_trend": avg_trend_list,
        "score_distribution": score_dist_list
    }

@app.get("/api/analysis/class/{class_name}")
def analysis_class(class_name: str):
    """
    班级分析
    - 班级平均分
    - 各分数段人数
    - 进步/退步学生
    """
    conn = sqlite3.connect(DB_PATH)
    
    # 班级学生列表
    students = pd.read_sql_query('''
        SELECT DISTINCT student_id, student_name 
        FROM students 
        WHERE class_name = ?
    ''', conn, params=(class_name,))
    
    student_ids = students['student_id'].tolist()
    
    if not student_ids:
        conn.close()
        return {"error": "未找到该班级"}
    
    # 班级成绩统计
    class_scores = pd.read_sql_query('''
        SELECT s.*, st.student_name
        FROM scores s
        JOIN students st ON s.student_id = st.student_id
        WHERE st.class_name = ?
        ORDER BY s.exam_date DESC
    ''', conn, params=(class_name,))
    
    # 按考试统计
    exam_stats = pd.read_sql_query('''
        SELECT exam_name, exam_date, 
               AVG(score) as avg_score,
               MAX(score) as max_score,
               MIN(score) as min_score,
               COUNT(*) as student_count
        FROM scores s
        JOIN students st ON s.student_id = st.student_id
        WHERE st.class_name = ?
        GROUP BY exam_name, exam_date
        ORDER BY exam_date DESC
    ''', conn, params=(class_name,))
    
    conn.close()
    
    return {
        "class_name": class_name,
        "student_count": len(student_ids),
        "students": students.to_dict('records'),
        "exam_stats": exam_stats.to_dict('records'),
        "all_scores": class_scores.to_dict('records')
    }

@app.get("/api/analysis/student/{student_id}/trend")
def analysis_student_trend(student_id: str):
    """
    学生个人趋势分析
    - 成绩变化曲线
    - 排名变化
    - 与班级平均分对比
    """
    conn = sqlite3.connect(DB_PATH)
    
    # 学生成绩
    scores = pd.read_sql_query('''
        SELECT s.*, st.student_name, st.class_name
        FROM scores s
        JOIN students st ON s.student_id = st.student_id
        WHERE s.student_id = ?
        ORDER BY s.exam_date
    ''', conn, params=(student_id,))
    
    if scores.empty:
        conn.close()
        return {"error": "未找到该学生成绩"}
    
    # 计算趋势指标
    if len(scores) > 1:
        scores['score_change'] = scores['score'].diff()
        scores['trend'] = scores['score_change'].apply(lambda x: '上升' if pd.notna(x) and x > 0 else ('下降' if pd.notna(x) and x < 0 else '持平'))
    
    # 转换为列表，处理 NaN 值
    score_trend_list = []
    for _, row in scores.iterrows():
        record = {
            'id': int(row['id']) if pd.notna(row.get('id')) else None,
            'student_id': str(row['student_id']),
            'exam_name': str(row['exam_name']),
            'exam_date': str(row['exam_date']) if pd.notna(row.get('exam_date')) else '',
            'score': float(row['score']) if pd.notna(row.get('score')) else 0,
            'full_score': float(row['full_score']) if pd.notna(row.get('full_score')) else 100,
            'rank': int(row['rank']) if pd.notna(row.get('rank')) else None,
            'class_avg': float(row['class_avg']) if pd.notna(row.get('class_avg')) else None,
            'grade_level': str(row['grade_level']) if pd.notna(row.get('grade_level')) else '',
            'semester': str(row['semester']) if pd.notna(row.get('semester')) else '',
            'student_name': str(row['student_name']),
            'class_name': str(row['class_name']),
            'score_change': float(row['score_change']) if 'score_change' in row and pd.notna(row.get('score_change')) else None,
            'trend': str(row['trend']) if 'trend' in row and pd.notna(row.get('trend')) else None
        }
        score_trend_list.append(record)
    
    conn.close()
    
    # 处理 summary 的 NaN 值
    avg_score = float(scores['score'].mean()) if pd.notna(scores['score'].mean()) else 0
    max_score = float(scores['score'].max()) if pd.notna(scores['score'].max()) else 0
    min_score = float(scores['score'].min()) if pd.notna(scores['score'].min()) else 0
    
    return {
        "student_info": {
            "student_id": student_id,
            "student_name": str(scores.iloc[0]['student_name']),
            "class_name": str(scores.iloc[0]['class_name'])
        },
        "score_trend": score_trend_list,
        "summary": {
            "avg_score": avg_score,
            "max_score": max_score,
            "min_score": min_score,
            "latest_score": float(scores.iloc[-1]['score']) if len(scores) > 0 else 0,
            "total_exams": len(scores)
        }
    }

@app.get("/api/analysis/comparison")
def analysis_comparison():
    """
    对比分析
    - 学生之间对比
    - 班级之间对比（如果有多个班级）
    """
    conn = sqlite3.connect(DB_PATH)
    
    # 班级对比
    class_comparison = pd.read_sql_query('''
        SELECT st.class_name,
               AVG(s.score) as avg_score,
               COUNT(DISTINCT st.student_id) as student_count,
               MAX(s.score) as max_score,
               MIN(s.score) as min_score
        FROM scores s
        JOIN students st ON s.student_id = st.student_id
        GROUP BY st.class_name
    ''', conn)
    
    # 最近一次考试排名
    latest_exam = pd.read_sql_query('''
        SELECT exam_name, exam_date 
        FROM scores 
        ORDER BY exam_date DESC 
        LIMIT 1
    ''', conn)
    
    if not latest_exam.empty:
        exam_name = latest_exam.iloc[0]['exam_name']
        rank_list = pd.read_sql_query('''
            SELECT st.student_name, st.class_name, s.score, s.rank
            FROM scores s
            JOIN students st ON s.student_id = st.student_id
            WHERE s.exam_name = ?
            ORDER BY s.score DESC
        ''', conn, params=(exam_name,))
    else:
        rank_list = pd.DataFrame()
    
    conn.close()
    
    return {
        "class_comparison": class_comparison.to_dict('records'),
        "latest_exam": latest_exam.to_dict('records')[0] if not latest_exam.empty else None,
        "rank_list": rank_list.to_dict('records') if not rank_list.empty else []
    }

@app.get("/api/analysis/statistics")
def analysis_statistics():
    """
    统计分析
    - 标准差、方差
    - 正态分布分析
    - 异常值检测
    """
    conn = sqlite3.connect(DB_PATH)
    
    all_scores = pd.read_sql_query("SELECT score FROM scores", conn)
    conn.close()
    
    if all_scores.empty:
        return {"error": "无数据"}
    
    scores = all_scores['score']
    
    # 统计指标
    stats = {
        "mean": scores.mean(),
        "median": scores.median(),
        "std": scores.std(),
        "variance": scores.var(),
        "skewness": scores.skew(),
        "kurtosis": scores.kurtosis(),
        "percentile_25": scores.quantile(0.25),
        "percentile_75": scores.quantile(0.75),
        "percentile_90": scores.quantile(0.90),
        "percentile_95": scores.quantile(0.95)
    }
    
    # 异常值检测（超过 2 个标准差）
    lower_bound = stats['mean'] - 2 * stats['std']
    upper_bound = stats['mean'] + 2 * stats['std']
    outliers = scores[(scores < lower_bound) | (scores > upper_bound)]
    
    stats['outliers_count'] = len(outliers)
    stats['outliers_percentage'] = len(outliers) / len(scores) * 100
    
    return {
        "descriptive_stats": stats,
        "normal_distribution": {
            "is_normal": abs(stats['skewness']) < 0.5 and abs(stats['kurtosis']) < 0.5,
            "skewness_interpretation": "接近正态" if abs(stats['skewness']) < 0.5 else ("右偏" if stats['skewness'] > 0 else "左偏"),
        }
    }

@app.delete("/api/data/clear")
def clear_data():
    """清空所有数据（慎用）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scores")
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()
    return {"message": "数据已清空"}

# ==================== 高级宏观分析 API ====================

@app.get("/api/advanced/semester-stats")
def api_semester_stats(student_id: str = None):
    """
    学年对比分析
    """
    return get_semester_stats(student_id)

@app.get("/api/advanced/predict")
def api_predict(student_id: str):
    """
    成绩预测
    """
    return predict_next_score(student_id)

@app.get("/api/advanced/risk")
def api_risk(student_id: str):
    """
    风险预警
    """
    return analyze_risk(student_id)

@app.get("/api/advanced/percentile")
def api_percentile(student_id: str, exam_name: str = None):
    """
    百分位排名
    """
    return calculate_percentile_rank(student_id, exam_name)

@app.get("/api/advanced/stability")
def api_stability(student_id: str):
    """
    稳定性分析
    """
    return analyze_stability(student_id)

@app.get("/api/advanced/advice")
def api_advice(student_id: str):
    """
    学习建议
    """
    return {"advice": generate_learning_advice(student_id)}

@app.get("/api/advanced/dashboard/{student_id}")
def api_dashboard(student_id: str):
    """
    综合仪表盘 - 聚合所有分析
    """
    return {
        "student_id": student_id,
        "semester_stats": get_semester_stats(student_id),
        "prediction": predict_next_score(student_id),
        "risk": analyze_risk(student_id),
        "percentile": calculate_percentile_rank(student_id),
        "stability": analyze_stability(student_id),
        "advice": generate_learning_advice(student_id)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8808)
