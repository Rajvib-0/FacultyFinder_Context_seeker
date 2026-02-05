# FacultyFinder_Context_seeker
FacultyFinder is a data engineering project designed to help students and researchers discover faculty members by research interests, even if those exact phrases don’t appear in their department titles. The system crawls faculty profiles, cleans and structures the data, and serves it via a FastAPI endpoint for downstream semantic search.

# Objectives
- **Final Goal**: Enable natural language queries like “Who is working on sustainable energy and carbon capture?” and return relevant faculty.
- **Current Goal**: build the ingestion, cleaning, storage, and serving pipeline.
  
##  Project Lifecycle

| Lifecycle Step   | Tool(s) Used              | 
|------------------|---------------------------|
| **Generation**   | HTML / Web Content        | 
| **Ingestion**    | `requests`, `BeautifulSoup` | 
| **Transformation** | `pandas`, `cleantext`   | 
| **Storage**      | `sqlite3`                 | 
| **Serving**      | `FastAPI`                 | 

##  Data Schema

The data is stored in **faculty.db** using SQLite.  
**Table:** `faculty`

| Column            | Type | Description                                | Example Value |
|-------------------|------|--------------------------------------------|---------------|
| `name`            | TEXT | Faculty member's full name (**PRIMARY KEY**) | "Abhishek Gupta" |
| `areaSpecialization` | TEXT | Research interests / bio summary            | "Machine Learning, Statistical Signal Processing..." |
| `facultyEducation`   | TEXT | Educational qualifications                  | "PhD (Electrical and Computer Engineering), Toronto Metropolitan University, Canada" |
| `contactDetails`     | TEXT | Combined phone, address, email              | "079-68261598 \| #3208, FB-3... \| abhishek_gupta[at]dau[dot]ac[dot]in" |
| `biography`        | TEXT |  Faculty biography                            | "Assistant Professor at DA-IICT..."


## Data Completeness Summary
| Category                | Total |  Name | Specialization | Education | Phone | Address | Email | Biography | Publications |
| ----------------------- | ----: | ----: | -------------: | --------: | ----: | ------: | ----: | --------: | -----------: |
| FACULTY                 |    69 | 69/69 |          68/69 |     69/69 | 68/69 |   68/69 | 68/69 |     60/69 |        64/69 |
| ADJUNCT                 |    26 | 26/26 |          25/26 |     26/26 |  9/26 |    5/26 | 26/26 |      7/26 |         6/26 |
| ADJUNCT_INTERNATIONAL   |    11 | 11/11 |           9/11 |     11/11 |  0/11 |    1/11 | 11/11 |      1/11 |         0/11 |
| DISTINGUISHED_PROFESSOR |     2 |   2/2 |            2/2 |       2/2 |   2/2 |     2/2 |   2/2 |       1/2 |          2/2 |
| PROFESSOR_OF_PRACTICE   |     4 |   4/4 |            4/4 |       4/4 |   1/4 |     1/4 |   4/4 |       1/4 |          1/4 |


##  Project Structure
├── main.py              # FastAPI app serving faculty data 

├──  Ingestion.py        # Notebook1 (The Scraper)

├──  Cleaner.py          # Notebook2 (Transformation)

├──  Storage.py          # Notebook3 (Schema)

├── faculty.db           # SQLite database

├── requirements.txt     #  dependencies

├── README.md            # Documentation

├── LLM_usage            # Name of llm & prompt

└── LICENSE              # MIT License

## Work Flow
  → Scraping (requests + BeautifulSoup)
  
  → Raw Faculty Data
  
  → Cleaning (Cleaner.py)
  
  → Clean Structured Records
  
  → Storage (SQLite: faculty.db)
  
  → API Layer (FastAPI)
  
  → Semantic Search & NLP Applications

## Live Demo
  https://facultyfinder-context-seeker.onrender.com/faculty

##  Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Rajvib-0/FacultyFinder_Context_seeker.git
   cd FacultyFinder_Context_seeker

2. Install dependencies:
    ```bash
   pip install -r requirements.txt
3. Run the FastAPI app:
    ```bash
   uvicorn main:app --reload
4.  Access endpoints:
- http://127.0.0.1:8000/faculty → returns all faculty data
- http://127.0.0.1:8000/docs → interactive API docs

## Outcomes
- Clean Dataset — SQLite database ready for NLP tasks.
- API Endpoint — /faculty serving JSON for downstream embedding.
- Documentation — Clear schema and setup instructions.

## Future Steps
- Implement vector search with embeddings for natural language queries
- Extend API to support semantic search endpoints

## License
This project is licensed under the MIT License.
