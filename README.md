# Semantic Book Recommender

A learning project evolving from a semantic-search tutorial into a book discovery app. It currently provides natural-language recommendations through a Gradio frontend and Flask API. Catalogue browsing, book details, and favorites remain future product work.

## Product direction

| Discover | Explore |
| --- | --- |
| Find books from a description; narrow by category and tone | Search and filter the catalogue by title, author, category, year, and rating |
| Vary recommendations between searches | View book details and save favorites |

## Tech stack

- **Language and analysis:** Python, Pandas, Jupyter
- **NLP and embeddings:** Hugging Face Transformers, Sentence Transformers, Gemini embeddings
- **Vector search:** Chroma (local), PostgreSQL with pgvector (Supabase)
- **Application:** Flask REST API and Gradio frontend client
- **Database and migrations:** PostgreSQL, SQLAlchemy, Flask-Migrate

## Deployed apps

- **Gradio frontend:** [Open the book recommender](https://client-semantic-book-recommender.onrender.com/).
- **Flask API:** Open the [API documentation](https://semantic-book-recommender-4tbl.onrender.com/api/docs/) to explore its endpoints. The backend runs on Render's free tier, so its first request may take 30–60 seconds.

## Architecture and progress

```text
Gradio frontend ──> Flask REST API ──┬── APP_ENV=local ──> Hugging Face + Chroma
                                     └── APP_ENV=production ──> Gemini + Supabase pgvector

Tutorial notebooks ──> prepared book data and embeddings for the selected backend
```

- **Implemented:** Flask recommendation API with environment-selected retrieval, category and emotion filtering, and up to 240 results; Gradio frontend with 16 results per page; notebook workflows for data preparation and embedding ingestion.
- **Planned:** catalogue browsing, book details, and favorites.
- Gemini embedding ingestion currently processes up to 800 books per run and can resume in later runs.

## Notebook workflow

To prepare data for Supabase, run these tutorial notebooks in order:

1. `notebooks/data-exploration.ipynb`
2. `notebooks/text-classification.ipynb`
3. `notebooks/sentiment-analysis.ipynb`
4. `notebooks/csv-data-ingestion.ipynb` — imports the resulting `books_with_emotions.csv` into Supabase.
5. `notebooks/gemini_book_embeddings_ingestion.ipynb` — creates document embeddings and demonstrates query embedding and pgvector search.

For local semantic recommendations, `notebooks/vector-search.ipynb` can create or reuse the Chroma collection used by Flask when `APP_ENV=local`. Set `FLASK_API_URL=http://127.0.0.1:5000` in the root `.env`, start Flask as described in [`backend/README.md`](backend/README.md), then run `./.venv/Scripts/python.exe -m frontend.app` from the repository root. Generated `data/` files and the local `chroma_db/` collection are git-ignored.

## Repository map

- `backend/` — Flask recommendation API, retrieval services, and database migrations. See [`backend/README.md`](backend/README.md) for backend setup, configuration, endpoint, and migration instructions.
- `frontend/` — Gradio interface and Flask API client. See [`frontend/README.md`](frontend/README.md) for frontend setup.
- `notebooks/` — data preparation, local search, and Supabase ingestion workflows.
- `requirements.txt`, `.env.example` — dependencies and configuration template.
- `semantic-book-recommender_demo.gif`, `cover-not-found.jpg` — project demo and source fallback cover.

## Learning source

The tutorial foundation is [Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/). The original tutorial app is preserved on the [`version/tutorial` branch](https://github.com/fatimaov/semantic-book-recommender/tree/version/tutorial); its README includes instructions for running the app.
