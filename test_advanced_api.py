import requests

API = 'http://localhost:8808/api'
STUDENT_ID = '3'

print("=" * 60)
print("  Testing Advanced Analysis API")
print("=" * 60)

# Test 1: 学年对比
print("\n[1] Semester Stats")
r = requests.get(f'{API}/advanced/semester-stats', params={'student_id': STUDENT_ID})
if r.status_code == 200:
    data = r.json()
    print(f"  Semesters: {len(data['semester_stats'])}")
    print(f"  Trend: {data['trend']['comment']}")
    for sem in data['semester_stats'][:3]:
        print(f"    {sem['semester']}: {sem['avg_score']:.1f}")
else:
    print(f"  Error: {r.status_code} - {r.text[:200]}")

# Test 2: 成绩预测
print("\n[2] Score Prediction")
r = requests.get(f'{API}/advanced/predict', params={'student_id': STUDENT_ID})
if r.status_code == 200:
    data = r.json()
    if 'error' not in data:
        print(f"  Predicted: {data['predicted_score']}")
        print(f"  Range: {data['confidence_interval']['lower']}-{data['confidence_interval']['upper']}")
        print(f"  Trend: {data['trend']}")
    else:
        print(f"  {data['error']}")
else:
    print(f"  Error: {r.status_code}")

# Test 3: 风险预警
print("\n[3] Risk Analysis")
r = requests.get(f'{API}/advanced/risk', params={'student_id': STUDENT_ID})
if r.status_code == 200:
    data = r.json()
    print(f"  Level: {data['risk_level']}")
    print(f"  Message: {data['message']}")
    print(f"  Score: {data['risk_score']}")
    if data['risk_factors']:
        print(f"  Factors: {data['risk_factors']}")
else:
    print(f"  Error: {r.status_code}")

# Test 4: 百分位排名
print("\n[4] Percentile Rank")
r = requests.get(f'{API}/advanced/percentile', params={'student_id': STUDENT_ID})
if r.status_code == 200:
    data = r.json()
    if 'error' not in data:
        print(f"  Layer: {data['layer']}")
        print(f"  Percentile: {data['percentile']}%")
        print(f"  Rank: {data['rank_description']}")
    else:
        print(f"  {data['error']}")
else:
    print(f"  Error: {r.status_code}")

# Test 5: 稳定性分析
print("\n[5] Stability Analysis")
r = requests.get(f'{API}/advanced/stability', params={'student_id': STUDENT_ID})
if r.status_code == 200:
    data = r.json()
    if 'error' not in data:
        print(f"  Stability: {data['stability']}")
        print(f"  Mean: {data['mean_score']}")
        print(f"  Std Dev: {data['std_dev']}")
        print(f"  CV: {data['cv']}%")
    else:
        print(f"  {data['error']}")
else:
    print(f"  Error: {r.status_code}")

# Test 6: 学习建议
print("\n[6] Learning Advice")
r = requests.get(f'{API}/advanced/advice', params={'student_id': STUDENT_ID})
if r.status_code == 200:
    data = r.json()
    print(f"  Advice Count: {len(data['advice'])}")
    for advice in data['advice'][:2]:
        print(f"    {advice['title']}: {advice['content'][:60]}")
else:
    print(f"  Error: {r.status_code}")

# Test 7: 综合仪表盘
print("\n[7] Dashboard")
r = requests.get(f'{API}/advanced/dashboard/{STUDENT_ID}')
if r.status_code == 200:
    data = r.json()
    print(f"  OK - Dashboard complete")
    print(f"  Semesters: {len(data['semester_stats']['semester_stats'])}")
    print(f"  Prediction: {data['prediction'].get('predicted_score', 'N/A')}")
    print(f"  Risk: {data['risk']['message']}")
else:
    print(f"  Error: {r.status_code}")

print("\n" + "=" * 60)
print("  Tests Complete!")
print("=" * 60)
