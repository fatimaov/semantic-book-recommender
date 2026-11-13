import pandas as pd
import numpy as np

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import gradio as gr

# Load the book metadata and build a larger cover URL for display.
books = pd.read_csv("data/books_with_emotions.csv")
books["large_thumbnail"] = books["thumbnail"] + "&fife=w800"
# Use a local placeholder when a book has no thumbnail URL.
books["large_thumbnail"] = np.where(
    books["large_thumbnail"].isna(),
    "cover-not-found.jpg",
    books["large_thumbnail"],
)

# Load the text embedding model used to represent books as vectors.
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

# Connect to the persisted Chroma collection so the dashboard can query book vectors.
db_books = Chroma(
    collection_name="books",
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

def retrieve_semantic_recommendations(
        query: str,
        category: str = None,
        tone: str = None,
        initial_top_k: int = 50,
        final_top_k: int = 16,
) -> pd.DataFrame:
    # Find the nearest book vectors, then extract their ISBNs from stored document text.
    recs = db_books.similarity_search(query, k=initial_top_k)
    books_list = [int(rec.page_content.strip('"').split()[0]) for rec in recs]
    # Keep matching metadata rows in their original dataset order.
    book_recs = books[books["isbn13"].isin(books_list)].head(initial_top_k)

    # Optionally narrow results to one category and cap the number returned.
    if category != "All":
        book_recs = book_recs[book_recs["simple_categories"] == category].head(final_top_k)
    else:
        book_recs = book_recs.head(final_top_k)

    # Rank the selected books by the emotion score requested by the user.
    if tone == "Happy":
        book_recs.sort_values(by="joy", ascending=False, inplace=True)
    elif tone == "Surprising":
        book_recs.sort_values(by="surprise", ascending=False, inplace=True)
    elif tone == "Angry":
        book_recs.sort_values(by="anger", ascending=False, inplace=True)
    elif tone == "Suspenseful":
        book_recs.sort_values(by="fear", ascending=False, inplace=True)
    elif tone == "Sad":
        book_recs.sort_values(by="sadness", ascending=False, inplace=True)

    return book_recs


def recommend_books(
        query: str,
        category: str,
        tone: str
):
    # Convert each recommended book into a thumbnail and caption for the gallery.
    recommendations = retrieve_semantic_recommendations(query, category, tone)
    results = []

    for _, row in recommendations.iterrows():
        description = row["description"]
        # Keep captions compact by showing only the first 20 description words.
        truncated_desc_split = description.split()
        truncated_description = " ".join(truncated_desc_split[:20]) + "..."

        # Format author names naturally when the metadata lists multiple authors.
        authors_split = row["authors"].split(";")
        if len(authors_split) == 2:
            authors_str = f"{authors_split[0]} and {authors_split[1]}"
        elif len(authors_split) > 2:
            authors_str = f"{', '.join(authors_split[:-1])}, and {authors_split[-1]}"
        else:
            authors_str = row["authors"]

        caption = f"{row['title']} by {authors_str}: {truncated_description}"
        results.append((row["large_thumbnail"], caption))
    return results

categories = ["All"] + sorted(books["simple_categories"].unique())
tones = ["All"] + ["Happy", "Surprising", "Angry", "Suspenseful", "Sad"]

# Build a responsive search form and connect it to the recommendation function.
dashboard_css = """
.gradio-container {max-width: 1100px !important; margin: auto !important;}
#search-controls {padding: 1rem; border: 1px solid var(--border-color-primary); border-radius: 16px;}
"""

with gr.Blocks(
    theme=gr.Theme.from_hub("bencw/soft-no-dark-theme"),
    css=dashboard_css,
) as dashboard:
    gr.Markdown("# Find your next favorite book\nDescribe a story, topic, or mood and explore books that match.")

    with gr.Column(elem_id="search-controls"):
        user_query = gr.Textbox(
            label="What kind of book are you looking for?",
            placeholder="e.g., A story about forgiveness",
            lines=2,
        )
        with gr.Row():
            category_dropdown = gr.Dropdown(choices=categories, label="Category", value="All")
            tone_dropdown = gr.Dropdown(choices=tones, label="Mood", value="All")
        submit_button = gr.Button("Find recommendations", variant="primary")

    gr.Markdown("## Recommendations")
    output = gr.Gallery(label="Books selected for you", columns=(1, 2, 4), rows=2)

    submit_button.click(fn = recommend_books,
                        inputs = [user_query, category_dropdown, tone_dropdown],
                        outputs = output)

if __name__ == "__main__":
    dashboard.launch()
