"""
高级宏观分析模块
包含：学年对比、能力雷达图、成绩预测、风险预警、群体分析等
作者：非哥家庭助手
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

DB_PATH = r"C:\Users\58452\.openclaw\workspace\study\backend\scores.db"

def get_semester_stats(student_id: str = None) -> Dict:
    """
    学年对比分析
    按学期统计各项指标
    """
    conn = sqlite3.connect(DB_PATH)
    
    if student_id:
        query = '''
            SELECT 
                s.semester,
                AVG(s.score) as avg_score,
                MAX(s.score) as max_score,
                MIN(s.score) as min_score,
                COUNT(*) as exam_count
            FROM scores s
            WHERE s.student_id = ?
            GROUP BY s.semester
            ORDER BY s.semester
        '''
        df = pd.read_sql_query(query, conn, params=(student_id,))
    else:
        query = '''
            SELECT 
                s.semester,
                AVG(s.score) as avg_score,
                MAX(s.score) as max_score,
                MIN(s.score) as min_score,
                COUNT(*) as exam_count
            FROM scores s
            GROUP BY s.semester
            ORDER BY s.semester
        '''
        df = pd.read_sql_query(query, conn)
    
    # 转换为列表，处理 NaN
    result = []
    for _, row in df.iterrows():
        semester = str(row['semester'])
        
        # 单独查询该学期的分数来计算标准差
        if student_id:
            scores_query = 'SELECT score FROM scores WHERE student_id = ? AND semester = ?'
            scores_df = pd.read_sql_query(scores_query, conn, params=(student_id, semester))
        else:
            scores_query = 'SELECT score FROM scores WHERE semester = ?'
            scores_df = pd.read_sql_query(scores_query, conn, params=(semester,))
        
        std_dev = scores_df['score'].std() if len(scores_df) > 1 else 0
        
        result.append({
            'semester': semester,
            'avg_score': float(row['avg_score']) if pd.notna(row['avg_score']) else 0,
            'max_score': float(row['max_score']) if pd.notna(row['max_score']) else 0,
            'min_score': float(row['min_score']) if pd.notna(row['min_score']) else 0,
            'std_dev': float(std_dev) if pd.notna(std_dev) else 0,
            'exam_count': int(row['exam_count'])
        })
    
    conn.close()
    
    return {
        'semester_stats': result,
        'trend': calculate_trend(result)
    }

def calculate_trend(semester_stats: List[Dict]) -> Dict:
    """
    计算学期间趋势
    """
    if len(semester_stats) < 2:
        return {'direction': 'stable', 'slope': 0, 'comment': '数据不足'}
    
    scores = [s['avg_score'] for s in semester_stats]
    slope = (scores[-1] - scores[0]) / len(scores)
    
    if slope > 2:
        direction = 'rising'
        comment = '持续进步中 📈'
    elif slope < -2:
        direction = 'falling'
        comment = '需要关注 📉'
    else:
        direction = 'stable'
        comment = '保持稳定 ➡️'
    
    return {
        'direction': direction,
        'slope': round(slope, 2),
        'comment': comment,
        'total_improvement': round(scores[-1] - scores[0], 2)
    }

def predict_next_score(student_id: str) -> Dict:
    """
    成绩预测模型
    使用线性回归预测下次考试成绩
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT score, exam_date
        FROM scores
        WHERE student_id = ?
        ORDER BY exam_date
    '''
    df = pd.read_sql_query(query, conn, params=(student_id,))
    conn.close()
    
    if len(df) < 3:
        return {'error': '数据不足，需要至少 3 次考试成绩'}
    
    scores = df['score'].values
    
    # 简单线性回归
    x = np.arange(len(scores))
    y = scores
    
    # 计算斜率和截距
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x ** 2)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    
    # 预测下次考试
    next_x = len(scores)
    predicted = slope * next_x + intercept
    
    # 计算置信区间（简化版）
    std_err = np.std(scores) / np.sqrt(len(scores))
    confidence_interval = 1.96 * std_err
    
    # 限制预测范围在 0-100
    predicted = max(0, min(100, predicted))
    lower_bound = max(0, min(100, predicted - confidence_interval))
    upper_bound = max(0, min(100, predicted + confidence_interval))
    
    # 计算最近 3 次的平均分作为参考
    recent_avg = scores[-3:].mean() if len(scores) >= 3 else scores.mean()
    
    return {
        'predicted_score': round(predicted, 1),
        'confidence_interval': {
            'lower': round(lower_bound, 1),
            'upper': round(upper_bound, 1)
        },
        'recent_avg': round(recent_avg, 1),
        'trend': '上升' if slope > 0.5 else ('下降' if slope < -0.5 else '平稳'),
        'confidence': '高' if std_err < 3 else ('中' if std_err < 5 else '低')
    }

def analyze_risk(student_id: str) -> Dict:
    """
    风险预警系统
    检测成绩下滑风险
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT score, exam_name, exam_date
        FROM scores
        WHERE student_id = ?
        ORDER BY exam_date DESC
        LIMIT 10
    '''
    df = pd.read_sql_query(query, conn, params=(student_id,))
    conn.close()
    
    if len(df) < 3:
        return {'risk_level': 'unknown', 'message': '数据不足'}
    
    scores = df['score'].values[::-1]  # 按时间正序
    
    # 检测连续下降
    consecutive_decline = 0
    for i in range(1, len(scores)):
        if scores[i] < scores[i-1]:
            consecutive_decline += 1
        else:
            consecutive_decline = 0
    
    # 计算波动率
    volatility = np.std(scores)
    
    # 计算最近趋势
    recent_trend = scores[-1] - scores[-3] if len(scores) >= 3 else 0
    
    # 风险等级判定
    risk_factors = []
    risk_score = 0
    
    if consecutive_decline >= 3:
        risk_score += 3
        risk_factors.append('连续 3 次下降')
    elif consecutive_decline >= 2:
        risk_score += 2
        risk_factors.append('连续 2 次下降')
    elif consecutive_decline >= 1:
        risk_score += 1
        risk_factors.append('单次下降')
    
    if volatility > 10:
        risk_score += 2
        risk_factors.append('成绩波动大')
    elif volatility > 5:
        risk_score += 1
        risk_factors.append('成绩有一定波动')
    
    if recent_trend < -5:
        risk_score += 2
        risk_factors.append('近期明显下滑')
    elif recent_trend < 0:
        risk_score += 1
        risk_factors.append('近期略有下滑')
    
    # 确定风险等级
    if risk_score >= 5:
        risk_level = 'high'
        color = '🔴'
        message = '高风险：需要立即关注！'
    elif risk_score >= 3:
        risk_level = 'medium'
        color = '🟠'
        message = '中风险：建议加强辅导'
    elif risk_score >= 1:
        risk_level = 'low'
        color = '🟡'
        message = '低风险：保持关注'
    else:
        risk_level = 'safe'
        color = '🟢'
        message = '安全：状态良好'
    
    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'color': color,
        'message': message,
        'risk_factors': risk_factors,
        'volatility': round(volatility, 2),
        'recent_trend': round(recent_trend, 2),
        'consecutive_decline': consecutive_decline
    }

def calculate_percentile_rank(student_id: str, exam_name: str = None) -> Dict:
    """
    计算学生在群体中的百分位排名
    """
    conn = sqlite3.connect(DB_PATH)
    
    # 获取该学生的最新成绩
    if exam_name:
        query_student = '''
            SELECT score FROM scores
            WHERE student_id = ? AND exam_name = ?
        '''
        student_score = pd.read_sql_query(query_student, conn, params=(student_id, exam_name))
    else:
        query_student = '''
            SELECT score FROM scores
            WHERE student_id = ?
            ORDER BY exam_date DESC
            LIMIT 1
        '''
        student_score = pd.read_sql_query(query_student, conn, params=(student_id,))
    
    if student_score.empty:
        conn.close()
        return {'error': '未找到学生成绩'}
    
    student_score = student_score.iloc[0]['score']
    
    # 获取同次考试所有学生成绩
    if exam_name:
        query_all = '''
            SELECT s.score FROM scores s
            WHERE s.exam_name = ?
        '''
        all_scores = pd.read_sql_query(query_all, conn, params=(exam_name,))
    else:
        query_all = '''
            SELECT score FROM scores
        '''
        all_scores = pd.read_sql_query(query_all, conn)
    
    conn.close()
    
    if all_scores.empty:
        return {'error': '无群体数据'}
    
    # 计算百分位
    percentile = (all_scores['score'] < student_score).sum() / len(all_scores) * 100
    
    # 确定层级
    if percentile >= 95:
        layer = '顶尖层'
        emoji = '🏆'
    elif percentile >= 80:
        layer = '优秀层'
        emoji = '🌟'
    elif percentile >= 50:
        layer = '中上层'
        emoji = '📚'
    elif percentile >= 20:
        layer = '中等层'
        emoji = '💪'
    else:
        layer = '基础层'
        emoji = '🎯'
    
    return {
        'student_score': student_score,
        'percentile': round(percentile, 1),
        'rank_description': f'前{100-percentile:.1f}%',
        'layer': layer,
        'emoji': emoji,
        'total_students': len(all_scores)
    }

def analyze_stability(student_id: str) -> Dict:
    """
    成绩稳定性分析
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT score FROM scores
        WHERE student_id = ?
        ORDER BY exam_date
    '''
    df = pd.read_sql_query(query, conn, params=(student_id,))
    conn.close()
    
    if len(df) < 3:
        return {'error': '数据不足'}
    
    scores = df['score'].values
    
    # 计算各项稳定性指标
    mean_score = scores.mean()
    std_dev = scores.std()
    cv = (std_dev / mean_score * 100) if mean_score > 0 else 0  # 变异系数
    
    # 计算最大波动
    max_change = max(abs(scores[i] - scores[i-1]) for i in range(1, len(scores)))
    
    # 计算上升/下降次数
    up_count = sum(1 for i in range(1, len(scores)) if scores[i] > scores[i-1])
    down_count = sum(1 for i in range(1, len(scores)) if scores[i] < scores[i-1])
    stable_count = len(scores) - 1 - up_count - down_count
    
    # 稳定性评级
    if cv < 5:
        stability = '非常稳定'
        emoji = '✅'
    elif cv < 10:
        stability = '比较稳定'
        emoji = '👍'
    elif cv < 15:
        stability = '一般'
        emoji = '📊'
    else:
        stability = '波动较大'
        emoji = '⚠️'
    
    return {
        'mean_score': round(mean_score, 2),
        'std_dev': round(std_dev, 2),
        'cv': round(cv, 2),
        'max_change': round(max_change, 2),
        'stability': stability,
        'emoji': emoji,
        'up_count': up_count,
        'down_count': down_count,
        'stable_count': stable_count,
        'total_changes': len(scores) - 1
    }

def generate_learning_advice(student_id: str) -> List[Dict]:
    """
    生成个性化学习建议
    """
    risk = analyze_risk(student_id)
    stability = analyze_stability(student_id)
    prediction = predict_next_score(student_id)
    
    advice = []
    
    # 基于风险的建议
    if risk['risk_level'] == 'high':
        advice.append({
            'type': 'warning',
            'priority': 'high',
            'title': '⚠️ 成绩预警',
            'content': f"检测到{', '.join(risk['risk_factors'])}，建议立即加强学习。"
        })
    elif risk['risk_level'] == 'medium':
        advice.append({
            'type': 'notice',
            'priority': 'medium',
            'title': '📋 学习提醒',
            'content': f"近期表现有波动，建议关注{', '.join(risk['risk_factors'])}。"
        })
    
    # 基于稳定性的建议
    if '波动' in stability['stability']:
        advice.append({
            'type': 'tip',
            'priority': 'medium',
            'title': '🎯 稳定性建议',
            'content': '成绩波动较大，建议加强基础训练，保持学习节奏。'
        })
    
    # 基于预测的建议
    if prediction.get('trend') == '下降':
        advice.append({
            'type': 'prediction',
            'priority': 'medium',
            'title': '📉 趋势预测',
            'content': f"预测下次考试{prediction['predicted_score']}分，建议提前复习。"
        })
    elif prediction.get('trend') == '上升':
        advice.append({
            'type': 'encouragement',
            'priority': 'low',
            'title': '🌟 表现优秀',
            'content': f"状态良好，预测下次考试{prediction['predicted_score']}分，继续保持！"
        })
    
    # 通用建议
    if not advice:
        advice.append({
            'type': 'general',
            'priority': 'low',
            'title': '💡 学习建议',
            'content': '整体表现良好，建议保持当前学习节奏，适当挑战更高目标。'
        })
    
    return advice
