## 1. Claude.ai
- prompt1 : i want you to cover all this urls for crawling faculty, adjucnt,disctigues, proff of practice for 
1. Ingestion (The Scraper)
The Task: Navigate the college directory. Fetch the HTML of individual faculty profiles.
2. Transformation (The Cleaner)
The Task: Extract specific entities from the messy HTML (e.g., separate the "Bio" section from the "Education" section)...initally i made a class for all and stored in list ...remember you might get (name, areaSpecialization, facultyEducation, contactDetails) but bio, publication etc you have to go to every faculty url for that ...if any person don't have that section or val in that section we have to print for that not provided 
3. Storage (The Structured Home)
The Task: Design a schema.
```notebook-python
import sqlite3
conn = sqlite3.connect('faculty.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS faculty (
        name TEXT NOT NULL PRIMARY KEY,
        areaSpecialization TEXT,
        facultyEducation TEXT,
 Biography TEXT,
        Publication TEXT,
        contactDetails TEXT

    )
''')
```
for contact details   f"{contact_obj.number} | {contact_obj.address} | {contact_obj.email}", and fastapi...I have done project for 1 url take it as reference and genralize... make it more structured...work thinking about 2 kind of people...one who is going to be part of devlopmet ...so process how it will do installation process etc and other any agent who should be able to work on it or any data sci...take time to think, don't ans quickly and share updated version of my ipynb in diif pys as per task.
<img width="918" height="479" alt="image" src="https://github.com/user-attachments/assets/5bb1241a-2749-408b-97af-611c936ad03f" />

---
- prompt2 : Desired end goal:
Work on the data produced before as a data scientist and create a recommender/search system.
 Faculty finder:
Given a text description, find best faculty suitable to talk to, join or refer.
i want a good search engin w.r.t context + search_engine file i was thinking to use baai algo ...any other context based (semantic algo) you think would be best...may be baai would be too much for this any simple for data appropriate model that you would like to suggest ?? tell me step by step what to do and where.

  ---
- prompt3 : can you help me in improving this...i think score are not  good ...may be issue w.r.t weightage ...consider every details don't think like if a col has many not provided so delete it..no don't do that... i want a good search engin w.r.t context
  <img width="914" height="487" alt="image" src="https://github.com/user-attachments/assets/e767e2e7-cd6f-4eab-83c0-bf2fe8e76bed" />

  ---
- prompt4 : let's go for hugging face then... what changes i am supposed to make in this for that https://github.com/Rajvib-0/FacultyFinder_Context_seeker/tree/main as for render i ran out of memory
  <img width="913" height="472" alt="image" src="https://github.com/user-attachments/assets/bb09632b-8b86-447b-a809-631ae6369e4f" />
