import sqlite3

DB_PATH = r"C:\Users\58452\.openclaw\workspace\study\backend\scores.db"

conn = sqlite3.connect(DB_PATH)

print("=" * 60)
print("  Current Students Status")
print("=" * 60)

# 查看所有学生
students = conn.execute("SELECT * FROM students ORDER BY student_name").fetchall()
print(f"\nTotal students: {len(students)}")

# 查找重复的学生（按姓名）
print("\n=== Duplicate Students (by name) ===")
duplicates = conn.execute("""
    SELECT student_name, COUNT(*) as count, GROUP_CONCAT(student_id) as ids
    FROM students
    GROUP BY student_name
    HAVING count > 1
""").fetchall()

for dup in duplicates:
    print(f"  {dup[0]}: {dup[1]} records, IDs: {dup[2]}")

# 显示前 20 个学生
print("\n=== First 20 Students ===")
for s in students[:20]:
    print(f"  ID:{s[0]} | StudentID:{s[1]} | Name:{s[2]} | Class:{s[3]}")

conn.close()
