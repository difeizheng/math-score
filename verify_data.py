import requests

API = 'http://localhost:8808/api'

print('=== Verifying Data ===\n')

# Test 1: Students
print('1. Students...')
r = requests.get(f'{API}/students')
if r.status_code == 200:
    students = r.json()
    print(f'   OK: {len(students)} students')
    # Find 茗心
    mingxin = [s for s in students if '茗心' in s.get('student_name', '')]
    if mingxin:
        print(f'   茗心 found: {mingxin[0]}')
else:
    print(f'   Error: {r.status_code}')

# Test 2: Overview
print('\n2. Overview...')
r = requests.get(f'{API}/analysis/overview')
if r.status_code == 200:
    data = r.json()
    stats = data.get('basic_stats', {})
    print(f'   Students: {stats.get("total_students", 0)}')
    print(f'   Exams: {stats.get("total_exams", 0)}')
    print(f'   Records: {stats.get("total_records", 0)}')
else:
    print(f'   Error: {r.status_code}')

# Test 3: Exams
print('\n3. Exams...')
r = requests.get(f'{API}/exams')
if r.status_code == 200:
    exams = r.json()
    print(f'   OK: {len(exams)} exams')
    # Show semester distribution
    semesters = {}
    for exam in exams:
        sem = exam.get('semester', 'Unknown')
        semesters[sem] = semesters.get(sem, 0) + 1
    print('   By semester:')
    for sem, count in sorted(semesters.items()):
        print(f'     {sem}: {count} exams')
else:
    print(f'   Error: {r.status_code}')

print('\n=== Done ===')
