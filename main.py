from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/faculty")
def get_faculty_data():
    conn = sqlite3.connect("faculty.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM faculty")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to list of dicts
    faculty_list = [dict(zip(columns, row)) for row in rows]
    return {"faculty": faculty_list}
