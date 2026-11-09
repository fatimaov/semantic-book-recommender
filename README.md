# Semantic Book Recommender

A learning project to prepare book metadata and descriptions for a semantic recommendation system. The current implementation is an exploratory data analysis and cleaning workflow in Jupyter; semantic search and the recommendation interface are future steps.

## Current implementation

[`data-exploration.ipynb`](data-exploration.ipynb) downloads the 7k Books with Metadata dataset through KaggleHub and:

- Loads and inspects the book metadata with Pandas.
- Examines missing values and visualizes missingness and Spearman correlations.
- Adds a missing-description indicator and estimates book age using 2026 as the reference year.
- Removes records missing a description, page count, average rating, or publication year. In the current run, this leaves 6,507 records.
- Counts description words and keeps books with descriptions of at least 25 words, leaving 5,197 records.
- Combines titles with available subtitles and prefixes descriptions with each book's ISBN-13.
- Exports the prepared records to `data/books_cleaned.csv`.

## Run the notebook

1. Create and activate a Python environment.
2. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Open `data-exploration.ipynb` in Jupyter and run the cells from top to bottom. The first cell downloads the dataset with KaggleHub; the final cell writes `data/books_cleaned.csv`.

## Project status

The dataset exploration, filtering, and export steps are implemented. Text embeddings, semantic search, recommendation logic, and a user interface have not yet been implemented.

## Learning resource

This project follows the freeCodeCamp tutorial [Build a Semantic Book Recommender Using an LLM and Python](https://www.freecodecamp.org/news/build-a-semantic-book-recommender-using-an-llm-and-python/).
