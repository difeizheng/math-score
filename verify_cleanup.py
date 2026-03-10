import requests

API = 'http://localhost:8808/api'

print("=" * 60)
print("  Verify Student Cleanup")
print("=" * 60)

# Test 1: Get students
print("\n[1] Student List")
r = requests.get(f'{API}/students')
if r.status_code == 200:
    students = r.json()
    print(f"  Total: {len(students)} students")
    
    # Check for duplicates
    names = [s['student_name'] for s in students]
    duplicates = [name for name in names if names.count(name) > 1]
    
    if duplicates:
        print(f"  WARNING: Found duplicates: {set(duplicates)}")
    else:
        print("  OK: No duplicates found")
    
    # Show first 10
    print("\n  First 10 students:")
    for s in students[:10]:
        print(f"    ID:{s['student_id']} | Name:{s['student_name']}")
else:
    print(f"  Error: {r.status_code}")

# Test 2: Check 茗心
print("\n[2] Check 茗心")
mingxin = [s for s in students if '茗心' in s.get('student_name', '')]
if mingxin:
    print(f"  Found: {len(mingxin)} record(s)")
    for m in mingxin:
        print(f"    ID:{m['student_id']} | Name:{m['student_name']}")
else:
    print("  Not found")

# Test 3: Student trend
print("\n[3] Student Trend API")
if mingxin:
    student_id = mingxin[0]['student_id']
    r = requests.get(f'{API}/analysis/student/{student_id}/trend')
    if r.status_code == 200:
        data = r.json()
        print(f"  OK: {data['summary']['total_exams']} exams")
        print(f"  Avg: {data['summary']['avg_score']:.1f}")
    else:
        print(f"  Error: {r.status_code}")

print("\n" + "=" * 60)
print("  Verification Complete")
print("=" * 60)
