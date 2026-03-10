"""
学生数据清理脚本
- 统一学号为整数格式
- 删除重复记录
- 更新关联的成绩记录
"""

import sqlite3

DB_PATH = r"C:\Users\58452\.openclaw\workspace\study\backend\scores.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("  Student Data Cleanup")
print("=" * 60)

# 1. 备份当前数据
print("\n[1] Creating backup...")
cursor.execute("CREATE TABLE IF NOT EXISTS students_backup AS SELECT * FROM students")
cursor.execute("CREATE TABLE IF NOT EXISTS scores_backup AS SELECT * FROM scores")
print("  OK: Backup created")

# 2. 找出所有重复的学生（按姓名分组）
print("\n[2] Finding duplicates...")
duplicates = cursor.execute("""
    SELECT student_name, MIN(CAST(student_id AS INTEGER)) as keep_id, 
           GROUP_CONCAT(student_id) as all_ids
    FROM students
    GROUP BY student_name
    HAVING COUNT(*) > 1
""").fetchall()

print(f"  Found {len(duplicates)} duplicate groups")

# 3. 对每个重复组，保留整数 ID，删除浮点 ID
print("\n[3] Merging duplicates...")
merged_count = 0
for dup in duplicates:
    name = dup[0]
    keep_id = int(dup[1])
    all_ids = [str(x) for x in dup[2].split(',')]
    
    # 找出要删除的 ID（浮点格式）
    delete_ids = [id for id in all_ids if '.' in id or float(id) != keep_id]
    
    # 更新成绩记录中的学号
    for del_id in delete_ids:
        cursor.execute("""
            UPDATE scores SET student_id = ? WHERE student_id = ?
        """, (str(keep_id), del_id))
        merged_count += 1
    
    # 删除重复的学生记录
    for del_id in delete_ids:
        cursor.execute("DELETE FROM students WHERE student_id = ?", (del_id,))

print(f"  OK: Merged {merged_count} score records")

# 4. 清理剩余学生的学号格式（确保都是整数）
print("\n[4] Normalizing student IDs...")
all_students = cursor.execute("SELECT student_id, student_name FROM students").fetchall()
normalized = 0
for student in all_students:
    old_id = student[0]
    new_id = str(int(float(old_id)))  # 确保转换为整数
    if old_id != new_id:
        cursor.execute("UPDATE students SET student_id = ? WHERE student_id = ?", (new_id, old_id))
        cursor.execute("UPDATE scores SET student_id = ? WHERE student_id = ?", (new_id, old_id))
        normalized += 1

print(f"  OK: Normalized {normalized} student IDs")

# 5. 删除孤立的分数记录（没有对应学生的记录）
print("\n[5] Cleaning orphaned scores...")
cursor.execute("""
    DELETE FROM scores 
    WHERE student_id NOT IN (SELECT student_id FROM students)
""")
orphaned = cursor.rowcount
print(f"  OK: Deleted {orphaned} orphaned score records")

# 6. 验证结果
print("\n[6] Verification...")
student_count = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
score_count = cursor.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
duplicate_count = cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT student_name FROM students GROUP BY student_name HAVING COUNT(*) > 1
    )
""").fetchone()[0]

print(f"  Total students: {student_count}")
print(f"  Total scores: {score_count}")
print(f"  Remaining duplicates: {duplicate_count}")

# 7. 提交更改
print("\n[7] Committing changes...")
conn.commit()

# 8. 显示清理后的前 20 个学生
print("\n[8] Sample students after cleanup:")
clean_students = cursor.execute("SELECT * FROM students ORDER BY CAST(student_id AS INTEGER) LIMIT 20").fetchall()
for s in clean_students:
    print(f"  ID:{s[0]} | Name:{s[2]} | Class:{s[3]}")

conn.close()

print("\n" + "=" * 60)
print("  Cleanup Complete!")
print("=" * 60)
print("\nNext steps:")
print("  1. Restart backend service")
print("  2. Refresh browser (Ctrl+F5)")
print("  3. Check student list")
