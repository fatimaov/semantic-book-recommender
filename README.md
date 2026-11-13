# Semantic Book Recommender

A learning project that prepares book descriptions and searches them by meaning using text embeddings and ChromaDB.

## Notebooks

- `data-exploration.ipynb` downloads the 7k Books with Metadata dataset from Kaggle, cleans it, and writes `data/books_cleaned.csv`.
- `vector-search.ipynb` turns each book description into an embedding, stores the vectors in `chroma_db/`, and searches them with natural-language queries.
- `text-classification.ipynb` maps common categories to broader labels and uses a zero-shot classifier to label books with unmapped categories as Fiction or Nonfiction. It evaluates the model on a sample and writes `data/books_with_categories.csv`.
- `sentiment-analysis.ipynb` runs the `j-hartmann/emotion-english-distilroberta-base` classifier on each sentence in every book description, takes the maximum sentence score for each emotion, joins the scores to the books by ISBN, and writes `data/books_with_emotions.csv`. The export drops the intermediate `C15`–`C31` columns.

## Recommended notebook run order

1. Run `data-exploration.ipynb` to create `data/books_cleaned.csv`.
2. Run `vector-search.ipynb` and/or `text-classification.ipynb`. Both use the cleaned CSV, so either can run next. The text classification notebook creates `data/books_with_categories.csv`.
3. To generate emotion scores, run `sentiment-analysis.ipynb` after text classification. It reads `data/books_with_categories.csv` and writes `data/books_with_emotions.csv`.

The generated CSV files and Chroma database are local and are not tracked by Git.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start Jupyter and follow the recommended notebook run order above.

The notebooks download their Hugging Face models on first use: `BAAI/bge-base-en-v1.5` for vector search, `facebook/bart-large-mnli` for category classification, and `j-hartmann/emotion-english-distilroberta-base` for emotion scoring. Text classification and sentiment analysis use CUDA device 0, so both require a CUDA-enabled NVIDIA GPU. Dataset download requires KaggleHub access.

## Current scope

Semantic retrieval is implemented as a notebook prototype. The recommendation helper fetches up to 50 similar books; it does not yet use its `top_k` argument or return results in similarity order. There is no application interface or LLM-based recommendation step yet.

## Learning resource

[Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/)
