# Semantic Book Recommender

A learning project that began as a semantic book recommender tutorial and is now expanding into a full stack book discovery app. The extended version aims to combine natural-language recommendations with a searchable catalogue, book details, and personal favorites.

The tutorial implementation is preserved on a separate branch. This branch contains the tutorial notebooks alongside the groundwork for the extended app.

## App direction

The planned experience includes:

- Find books from a natural-language description, with category and emotional-tone filters.
- Browse and filter the full catalogue by title, author, category, publication year, and rating.
- Open a detail view for a book and save books to favorites.
- Shuffle or vary recommendations so repeated searches can surface different books.

These are product goals; the full user-facing app is not implemented yet.

## Architecture

The project is being prepared to support two configurations:

| Configuration | Embeddings | Vector store | Purpose |
| --- | --- | --- | --- |
| Local | Hugging Face `BAAI/bge-base-en-v1.5` | Chroma | Continue running the tutorial dashboard locally |
| Supabase | Gemini `gemini-embedding-2` | PostgreSQL with pgvector | Support the extended app and future deployment |

The intended request flow is for a client to call the Flask API, which handles book queries and semantic search. The Flask API currently has a health endpoint only; recommendation endpoints and a frontend remain future work. The existing Gradio dashboard still uses the local Chroma collection.

## Current implementation

- Tutorial notebooks for data exploration, text classification, emotion analysis, and local vector search.
- A CSV ingestion notebook that loads `books_with_emotions.csv` into the Supabase `books` table, skips ISBN-13 values already present, and verifies the inserted records.
- A Gemini embedding workflow that skips books already embedded for the selected model, processes books in batches, and saves vectors with their source book IDs to `book_embeddings`.
- A query-embedding and pgvector similarity-search example in the Gemini notebook.
- Flask app setup, a health endpoint, SQLAlchemy models, and migrations for `books`, `book_embeddings`, and `search_events`.
- Environment configuration for the local Chroma/Hugging Face and Supabase/Gemini setups.

Gemini ingestion currently processes up to 800 books per notebook run. It can be run again to continue with books that remain unembedded.

## Repository structure

- `backend/` — Flask application, database models, and migrations.
- `notebooks/` — tutorial analysis and vector search, plus CSV and Gemini ingestion workflows.
- `gradio-dashboard.py` — tutorial-era local recommendation interface.
- `requirements.txt` and `.env.example` — Python dependencies and environment variable template.
- `semantic-book-recommender_demo.gif` and `cover-not-found.jpg` — dashboard demo and fallback cover image.

Generated datasets in `data/` and the local Chroma database in `chroma_db/` are git-ignored, so they are not included in a clone.

## Data and embedding workflow

The existing data preparation notebooks produce `data/books_with_emotions.csv`. The CSV ingestion notebook loads those records into Supabase. The Gemini notebook then reads book descriptions from the database, generates document embeddings, and stores them in `book_embeddings`. For semantic search, it embeds the user's query with Gemini and ranks matching books by pgvector distance.

Before using the Supabase ingestion workflow, run the tutorial data-preparation notebooks in order: `data-exploration.ipynb`, `text-classification.ipynb`, then `sentiment-analysis.ipynb`. They generate the cleaned CSV files, including `books_with_emotions.csv`, which the Supabase CSV ingestion notebook expects. `vector-search.ipynb` is only needed for the local Chroma/Gradio tutorial workflow.

For the tutorial workflow, `vector-search.ipynb` creates or reuses the local Chroma collection from `data/tagged_description.txt`; the Gradio dashboard uses that collection and does not re-ingest the books on each launch.

## Setup

Use Python 3.11 or newer and install the project dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the credentials for the configuration you want to use. The Supabase workflows require `SUPABASE_DATABASE_URL`; Gemini embeddings also require `GOOGLE_API_KEY` and `GEMINI_EMBEDDING_MODEL`. Do not commit `.env` or other credentials.

### Run the tutorial dashboard

Prepare the local data and Chroma collection by running the tutorial notebooks, then start Gradio:

```bash
gradio gradio-dashboard.py
```

The dashboard is available at `http://127.0.0.1:7860` by default. The Hugging Face models used by the notebooks download on first use. The zero-shot and emotion-classification notebooks are configured for CUDA (`device=0`); for CPU use, change this to `device=-1`, which will run more slowly.

### Run the Flask API

Start the backend from the repository root:

```bash
python -m backend.run
```

The API runs at `http://127.0.0.1:5000`. Its current health check is `GET /api/health`. Database migrations are managed with Flask-Migrate; see `backend/README.md` for migration commands.

## Learning source

The original tutorial is [Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/), published by freeCodeCamp.
