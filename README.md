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
| **Serving**      | `FastAPI`, `unicorn`        | 
|**Search Engine** | `sentence-transformers`,`FAISS`| 
| **Models**      | `torch`, `scikit-learn`    | 
| **Deployment** | `Render`, `HuggingFace spaces`| 

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
 
   ├── [main.py](Back/main.py)                            # FastAPI app

   ├──-[Ingestion.py](Back/Ingestion.py)                   # Web scraper

   ├──-[Cleaner.py ](Back/Cleaner.py )                     # Data transformation

   ├──-[Storage.py](Back/Storage.py)                      # Database schema

   └──-[faculty.db](Back/faculty.db )                      # SQLite database

---
├── Part 2: Search Engine & Web Ap

   ├── [app.py](front/app.py)                         # streamlit web application

   ├── [search_engine_improved.py](front/search_engine_improved.py)        # Enhanced semantic search

   ├── [faculty_data.csv](front/faculty_data.csv )                # Exported faculty data

          
  
   
---
├── Documentation

   ├── [README.md](README.md)                       # This file

├── Deployment

   ├── [requirements.txt part2](front/requirements.txt),[requirements.txt part1](Back/requirements.txt)                # Python dependencies

   └── [.gitignore](front/.gitignore)

├── [llm_logs.md](llm_logs.md)

└── LICENSE                              # MIT License

## Complete Workflow
**Part1 :**  

**Web Pages (HTML) -> Scraping (Ingestion.py) -> Cleaning & Transformation (Cleaner.py) -> SQLite Storage (Storage.py)->FastAPI Endpoint (/faculty)**

**Part2 :**
CSV Data (faculty_data.csv) --> Enhanced Search Engine (search_engine_improved.py)

    ├── Load & Process Data
    ├── Generate Multi-Field Embeddings (384-dim)
    ├── Build FAISS Index
    └── Cache for Fast Startup
    ↓
streamlit Web Application (app.py)

    ├── Home Page (Hero + Features)
    ├── Search Interface (Advanced Options)
    └── REST API Endpoints
    ↓
User Queries → Semantic Search → Ranked Results

---
## Live Demo
 Part1: https://facultyfinder-context-seeker.onrender.com/faculty
 
Part2: https://huggingface.co/spaces/MoriartyR/Faculty-Finder

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
   pip install streamlit numpy pandas sentence-transformers faiss-cpu torch transformers scikit-learn scipy
2. Ensure you have faculty data:
   ```bash
   Export from SQLite or use provided CSV
  [faculty_data.csv](faculty_data.csv)
  
3. Run the app:
   ```bash
   python app.py
4. Access the web interface:

Home: http://localhost:8081

Search: http://localhost:8081/search 

---
## Search Engine Features
1. Semantic Understanding
   
- Understands meaning, not just keywords

- 384-dimensional vector embeddings

- Cosine similarity matching

2. Hybrid Scoring
   
- pythonFinal Score = 0.75 × Semantic Score + 0.25 × Keyword Score
- Semantic (75%): Contextual meaning
- Keyword (25%): Exact term matching

3. Multi-Field Weighting
   
- Specialization: 3.0x (highest priority)

- Publications: 2.0x (research output)

- Biography: 2.0x (background context)

- Education: 1.5x (credentials)

- Name: 0.5x (name matching)

4. Query Expansion
 Automatically expands queries with related terms:
- "ml" → "machine learning"
- "renewable energy" → "renewable energy sustainable energy clean energy"

5. Performance Optimization

- FAISS indexing for fast vector search

- Caching system (30s → 2s startup)

- Search latency: 50-200ms

### Search Quality Improvements

| Metric           | Original              | Enhanced     (My model)           | Improvement                  |
|------------------|-----------------------|-----------------------------------|------------------------------|
| Score Range      | 0.3 - 0.7             | 0.2 - 0.95                        | Better separation            |
| Field Handling   | Equal weights         | Intelligent (3x - 0.5x)           | More relevant                |
| Missing Data     | Pollutes results      | Filtered out                      | Cleaner results              |
| Query Types      | Exact match           | Semantic + Keyword                | Broader coverage             |
| Relevance        | Moderate              | High                              | 40-60% better                |


## Model used for training is **all-MiniLM-L6-v2** - Sentence transformer model (384 dimensions)

## License
This project is licensed under the MIT License.
