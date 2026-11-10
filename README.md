# Semantic Book Recommender

A learning project that prepares book descriptions and searches them by meaning using text embeddings and ChromaDB.

## Notebooks

- `data-exploration.ipynb` downloads the 7k Books with Metadata dataset from Kaggle, cleans it, and writes `data/books_cleaned.csv`.
- `vector-search.ipynb` turns each book description into an embedding, stores the vectors in `chroma_db/`, and searches them with natural-language queries.

Run the notebooks in that order. The cleaned CSV and Chroma database are local generated files and are not tracked by Git.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start Jupyter and run `data-exploration.ipynb` from top to bottom, then `vector-search.ipynb`.

The vector search downloads the `BAAI/bge-base-en-v1.5` embedding model on first use. Dataset download requires KaggleHub access.

## Current scope

Semantic retrieval is implemented as a notebook prototype. The recommendation helper fetches up to 50 similar books; it does not yet use its `top_k` argument or return results in similarity order. There is no application interface or LLM-based recommendation step yet.

## Learning resource

[Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/)
