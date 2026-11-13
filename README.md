# Semantic Book Recommender

A semantic book discovery app that finds recommendations from natural-language descriptions, then lets readers narrow results by genre and emotional tone. It combines Python, Hugging Face language models, LangChain, and ChromaDB for semantic search, with a Gradio dashboard for exploring the recommendations.

## Tech stack

Python, Jupyter, Pandas, Hugging Face Transformers and Sentence Transformers, LangChain, ChromaDB, and Gradio.

## Notebooks and app

- `data-exploration.ipynb` downloads the 7k Books with Metadata dataset, explores and cleans it, and saves `data/books_cleaned.csv`.
- `vector-search.ipynb` prepares ISBN-tagged descriptions, creates/reuses the `books` Chroma collection in `chroma_db/`, and demonstrates semantic retrieval.
- `text-classification.ipynb` maps detailed genres to broader categories and uses zero-shot classification for unmapped books. Saves `data/books_with_categories.csv`.
- `sentiment-analysis.ipynb` scores description sentences for emotions and saves `data/books_with_emotions.csv`.
- `gradio-dashboard.py` retrieves books from the persisted Chroma collection and filters or ranks recommendations by category and emotional tone.

## Notebook run order

1. `data-exploration.ipynb`
2. `vector-search.ipynb` and `text-classification.ipynb` (either order; both use `books_cleaned.csv`)
3. `sentiment-analysis.ipynb` (uses `books_with_categories.csv`)
4. Run the dashboard with `gradio gradio-dashboard.py` after the vector collection and emotion CSV are available.

## Setup and model notes

Create and activate a Python environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Run Jupyter to execute the notebooks:

```bash
jupyter notebook
```

After the vector collection and emotion CSV are available, start the Gradio dashboard in reload mode:

```bash
gradio gradio-dashboard.py
```

The dashboard is available at `http://127.0.0.1:7860` by default. Gradio reload mode refreshes the app when you save changes.

Run the notebooks in order above. The first notebook downloads the dataset through KaggleHub. Hugging Face downloads these models on first use:

- `BAAI/bge-base-en-v1.5` for book and query embeddings
- `facebook/bart-large-mnli` for zero-shot Fiction/Nonfiction classification
- `j-hartmann/emotion-english-distilroberta-base` for emotion scores

The two classification notebooks specify `device=0`, which requires a compatible CUDA-enabled NVIDIA GPU and PyTorch CUDA installation. For CPU use, change `device=0` to `device=-1` in those notebooks; inference will be slower. The dashboard uses the same embedding model and existing Chroma vectors, so it does not need to ingest or embed all book descriptions again.

Generated CSV files and the Chroma database are local and are not tracked by Git.

## Tutorial

This project is a practice exercise based on freeCodeCamp's [Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/).
