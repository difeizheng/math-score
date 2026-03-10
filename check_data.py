import sqlite3

conn = sqlite3.connect(r'C:\Users\58452\.openclaw\workspace\study\backend\scores.db')

print('=== Database Status ===')
students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
print(f'Students: {students}')

scores = conn.execute('SELECT COUNT(*) FROM scores').fetchone()[0]
print(f'Score records: {scores}')

print('\n=== Sample Students ===')
for row in conn.execute('SELECT student_id, student_name FROM students LIMIT 10'):
    print(f'  ID:{row[0]} Name:{row[1]}')

print('\n=== Mingxin Scores ===')
for row in conn.execute("""
    SELECT s.exam_name, s.score, s.semester 
    FROM scores s 
    JOIN students st ON s.student_id = st.student_id 
    WHERE st.student_name LIKE '%茗心%' 
    LIMIT 10
"""):
    print(f'  Exam:{row[0]} Score:{row[1]} Semester:{row[2]}')

print('\n=== All Exams ===')
for row in conn.execute('SELECT DISTINCT exam_name FROM scores LIMIT 20'):
    print(f'  {row[0]}')

conn.close()
