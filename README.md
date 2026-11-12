# Semantic Book Recommender

A learning project that prepares book descriptions and searches them by meaning using text embeddings and ChromaDB.

## Notebooks

- `data-exploration.ipynb` downloads the 7k Books with Metadata dataset from Kaggle, cleans it, and writes `data/books_cleaned.csv`.
- `vector-search.ipynb` turns each book description into an embedding, stores the vectors in `chroma_db/`, and searches them with natural-language queries.
- `text-classification.ipynb` maps common categories to broader labels and uses a zero-shot classifier to label books with unmapped categories as Fiction or Nonfiction. It evaluates the model on a sample and writes `data/books_with_categories.csv`.

Run `data-exploration.ipynb` first. Then run `vector-search.ipynb` and/or `text-classification.ipynb`; both use `data/books_cleaned.csv`. The generated CSV files and Chroma database are local and are not tracked by Git.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start Jupyter and run the notebooks from top to bottom, beginning with `data-exploration.ipynb`.

Vector search downloads the `BAAI/bge-base-en-v1.5` embedding model on first use. Text classification uses Hugging Face Transformers and `facebook/bart-large-mnli`; its notebook is configured to use a CUDA-enabled NVIDIA GPU. Dataset download requires KaggleHub access.

## Current scope

Semantic retrieval is implemented as a notebook prototype. The recommendation helper fetches up to 50 similar books; it does not yet use its `top_k` argument or return results in similarity order. There is no application interface or LLM-based recommendation step yet.

## Learning resource

[Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/)
