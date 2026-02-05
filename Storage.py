import sqlite3

conn = sqlite3.connect('faculty.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS faculty (
        name TEXT PRIMARY KEY,
        areaSpecialization TEXT,
        facultyEducation TEXT,
        number TEXT,
        address TEXT,
        email TEXT,
        biography TEXT,
        publications TEXT
    )
''')

for category, records in all_faculty_records.items():
    for faculty_obj in records:
        cursor.execute('''
            INSERT OR REPLACE INTO faculty
            (name, areaSpecialization, facultyEducation, number, address, email, biography, publications)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            faculty_obj.name,
            faculty_obj.specialization,
            faculty_obj.education,
            faculty_obj.number,
            faculty_obj.address,
            faculty_obj.email,
            faculty_obj.biography,
            faculty_obj.publications
        ))

conn.commit()
conn.close()

print("Data insertion complete.")
