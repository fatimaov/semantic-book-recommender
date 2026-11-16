# Semantic Book Recommender

A learning project evolving from a semantic-search tutorial into a full stack book discovery app. The extended app aims to combine natural-language recommendations with catalogue browsing, book details, and favorites. The app experience is still in development.

## Product direction

| Discover | Explore |
| --- | --- |
| Find books from a description; narrow by category and tone | Search and filter the catalogue by title, author, category, year, and rating |
| Vary recommendations between searches | View book details and save favorites |

## Tech stack

- **Language and analysis:** Python, Pandas, Jupyter
- **NLP and embeddings:** Hugging Face Transformers, Sentence Transformers, Gemini embeddings
- **Vector search:** Chroma (local), PostgreSQL with pgvector (Supabase)
- **Application:** Flask API, Gradio tutorial dashboard
- **Database and migrations:** PostgreSQL, SQLAlchemy, Flask-Migrate

## Architecture and progress

```text
Tutorial notebooks ──> cleaned CSV ──> Supabase books
       │                                  │
       └──> Chroma ──> Gradio             └──> Gemini embeddings ──> pgvector search

Planned app: frontend ──> Flask API ──> catalogue and semantic search
```

- **Implemented:** tutorial analysis and local Chroma/Gradio workflow; CSV import and resumable Gemini embedding notebooks; database groundwork for the extended app.
- **Planned:** recommendation API, frontend, and user-facing discovery features.
- Gemini embedding ingestion currently processes up to 800 books per run and can resume in later runs.

## Notebook workflow

To prepare data for Supabase, run these tutorial notebooks in order:

1. `notebooks/data-exploration.ipynb`
2. `notebooks/text-classification.ipynb`
3. `notebooks/sentiment-analysis.ipynb`
4. `notebooks/csv-data-ingestion.ipynb` — imports the resulting `books_with_emotions.csv` into Supabase.
5. `notebooks/gemini_book_embeddings_ingestion.ipynb` — creates document embeddings and demonstrates query embedding and pgvector search.

The separate local tutorial path uses `notebooks/vector-search.ipynb` to create or reuse the Chroma collection, then `gradio-dashboard.py` to run the dashboard. Generated `data/` files and the local `chroma_db/` collection are git-ignored.

## Repository map

- `backend/` — Flask application and database groundwork. See [`backend/README.md`](backend/README.md) for backend setup, configuration, endpoint, and migration instructions.
- `notebooks/` — data preparation, local search, and Supabase ingestion workflows.
- `gradio-dashboard.py` — tutorial dashboard.
- `requirements.txt`, `.env.example` — dependencies and configuration template.
- `semantic-book-recommender_demo.gif`, `cover-not-found.jpg` — dashboard demo and fallback cover.

## Learning source

The tutorial foundation is [Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/). The original tutorial app is preserved on the [`version/tutorial` branch](https://github.com/fatimaov/semantic-book-recommender/tree/version/tutorial); its README includes instructions for running the app.
