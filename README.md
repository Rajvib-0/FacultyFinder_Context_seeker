# FacultyFinder_Context_seeker
FacultyFinder is a data engineering project designed to help students and researchers discover faculty members by research interests, even if those exact phrases don’t appear in their department titles. The system crawls faculty profiles, cleans and structures the data, and serves it via a FastAPI endpoint for downstream semantic search.

## Objectives
- **Final Goal**: Build a system where a student or researcher can type "Who is working on sustainable energy and carbon capture?" and find relevant faculty members, even if
those specific phrases aren't in their official department title.
- **Part 1**: Build the ingestion, cleaning, storage, and serving pipeline.
- **Part 2**: Implement advanced semantic search engine and deploy production-ready web interface.
  
  
##  Project Lifecycle & Tools Overview 

| Lifecycle Step   | Tool(s) Used              | 
|------------------|---------------------------|
| **Generation**   | `HTML` / `Web Content`    | 
| **Ingestion**    | `requests`,`BeautifulSoup`| 
| **Transformation** | `pandas`, `cleantext`   | 
| **Storage**      | `sqlite3`,  `CSV`         | 
| **Serving**      | `FastAPI`, `Flask`        | 
|**Search Engine** | `sentence-transformers`,`FAISS`| 
| **Models**      | `torch`, `scikit-learn`    | 
| **Web Interface** | `HTML5`, `CSS3`, `JavaScript`| 

##  Data Schema

The data is stored in -[faculty.db](faculty.db) using SQLite.  
**Table:** `faculty`

| Column            | Type | Description                                | Example Value |
|-------------------|------|--------------------------------------------|---------------|
| `name`            | TEXT | Faculty member's full name (**PRIMARY KEY**) | "Abhishek Gupta" |
| `areaSpecialization` | TEXT | Research interests / bio summary            | "Machine Learning, Statistical Signal Processing..." |
| `facultyEducation`   | TEXT | Educational qualifications                  | "PhD (Electrical and Computer Engineering), Toronto Metropolitan University, Canada" |
| `contactDetails`     | TEXT | Combined phone, address, email              | "079-68261598 \| #3208, FB-3... \| abhishek_gupta[at]dau[dot]ac[dot]in" |
| `biography`        | TEXT |  Faculty biography                            | "Assistant Professor at DA-IICT..."
| `publications`     | TEXT | Research output | "Journal Articles:D. Maradia, A. Jindal, and C. Jos, "Integrating..."


## Data Completeness Summary 
| Category                | Total |  Name | Specialization | Education | Phone | Address | Email | Biography | Publications |
| ----------------------- | ----: | ----: | -------------: | --------: | ----: | ------: | ----: | --------: | -----------: |
| FACULTY                 |    69 | 69/69 |          68/69 |     69/69 | 68/69 |   68/69 | 68/69 |     60/69 |        64/69 |
| ADJUNCT                 |    26 | 26/26 |          25/26 |     26/26 |  9/26 |    5/26 | 26/26 |      7/26 |         6/26 |
| ADJUNCT_INTERNATIONAL   |    11 | 11/11 |           9/11 |     11/11 |  0/11 |    1/11 | 11/11 |      1/11 |         0/11 |
| DISTINGUISHED_PROFESSOR |     2 |   2/2 |            2/2 |       2/2 |   2/2 |     2/2 |   2/2 |       1/2 |          2/2 |
| PROFESSOR_OF_PRACTICE   |     4 |   4/4 |            4/4 |       4/4 |   1/4 |     1/4 |   4/4 |       1/4 |          1/4 |


##  Project Structure
FacultyFinder_Context_seeker/
 │
---
├── Part 1: Data Pipeline
 
   ├── [main.py](main.py)                            # FastAPI app

   ├──-[Ingestion.py](Ingestion.py)                   # Web scraper

   ├──-[Cleaner.py ](Cleaner.py )                     # Data transformation

   ├──-[Storage.py]( Storage.py)                      # Database schema

   └──-[faculty.db](faculty.db )                      # SQLite database

---
├── Part 2: Search Engine & Web App

   ├── [app.py](app.py)                         # Flask web application

   ├── [search_engine_improved.py](search_engine_improved.py)        # Enhanced semantic search

   ├── [faculty_data.csv](faculty_data.csv )                # Exported faculty data

   ├── templates/                       # HTML templates

   ├── [index.html](index.html )                   # Home page

   ├── [search.html](search.html)                 # Search interface

   ├── [404.html](404.html)                     # Error pages

   └── [500.html](500.html)

   ├── static/                          # Static assets

   \ ├── css/
   
   \└── [style.css](style.css)                # Main stylesheet

   \└── js/

  ├── [main.js](main.js)                 # Main JavaScript

  └── [search.js](search.js)                # Search page logic

   └── enhanced_search_cache_multi.pkl  # Embeddings cache
   
---
├── Documentation

   ├── README.md                        # This file

├── Deployment

   ├── [requirements.txt ](requirements.txt)                # Python dependencies

   ├── [render.yaml](render.yaml)                      # Render configuration

   └── .gitignore

└── LICENSE                              # MIT License

---
## Live Demo
  https://facultyfinder-context-seeker.onrender.com/faculty
  

##  Running Locally

**Part 1: Data Pipeline**
1. Clone the repository:
   ```bash
   git clone https://github.com/Rajvib-0/FacultyFinder_Context_seeker.git
   cd FacultyFinder_Context_seeker

2. Install dependencies:
    ```bash
   pip install fastapi uvicorn requests beautifulsoup4 lxml pandas
3. Run the FastAPI app:
    ```bash
   uvicorn main:app --reload
4.  Access endpoints:
- http://127.0.0.1:8000/faculty → returns all faculty data
- http://127.0.0.1:8000/docs → interactive API docs

**Part 2 Semantic Search Engine**
1. Install additional dependencies:
   ```bash
   pip install flask flask-cors sentence-transformers faiss-cpu torch transformers scikit-learn scipy
2. Ensure you have faculty data:
   ```bash
   Export from SQLite or use provided CSV
  [faculty_data.csv](faculty_data.csv)
  
3. Run the Flask app:
   ```bash
   python app.py
   

## Outcomes
- Clean Dataset — SQLite database ready for NLP tasks.
- API Endpoint — /faculty serving JSON for downstream embedding.
- Documentation — Clear schema and setup instructions.

## Future Steps
- Implement vector search with embeddings for natural language queries
- Extend API to support semantic search endpoints

## License
This project is licensed under the MIT License.
