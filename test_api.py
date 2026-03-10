import requests

API = 'http://localhost:8808/api'

print('=== Testing API ===\n')

# Test 1: Students
print('1. Get students...')
r = requests.get(f'{API}/students')
if r.status_code == 200:
    students = r.json()
    print(f'   OK: {len(students)} students')
    if students:
        print(f'   Sample: {students[0]}')
else:
    print(f'   Error: {r.status_code}')

# Test 2: Overview
print('\n2. Get overview...')
r = requests.get(f'{API}/analysis/overview')
if r.status_code == 200:
    data = r.json()
    print(f'   OK: {data}')
else:
    print(f'   Error: {r.status_code} - {r.text[:200]}')

# Test 3: Exams
print('\n3. Get exams...')
r = requests.get(f'{API}/exams')
if r.status_code == 200:
    exams = r.json()
    print(f'   OK: {len(exams)} exams')
    if exams:
        print(f'   Sample: {exams[0]}')
else:
    print(f'   Error: {r.status_code}')

print('\n=== Done ===')
