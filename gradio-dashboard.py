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
    descriptions = []

    for _, row in recommendations.iterrows():
        description = row["description"]
        description = "" if pd.isna(description) else str(description)
        descriptions.append(description)

        # Format author names naturally when the metadata lists multiple authors.
        authors_split = row["authors"].split(";")
        if len(authors_split) == 2:
            authors_str = f"{authors_split[0]} and {authors_split[1]}"
        elif len(authors_split) > 2:
            authors_str = f"{', '.join(authors_split[:-1])}, and {authors_split[-1]}"
        else:
            authors_str = row["authors"]

        caption = f"{row['title']} by {authors_str}"
        results.append((row["large_thumbnail"], caption))
    # Clear the description whenever a fresh set of recommendations is loaded.
    return results, descriptions, "Select a recommended book to read its full description."


def show_selected_description(descriptions, evt: gr.SelectData):
    # Read the description at the position selected in the recommendations gallery.
    index = evt.index
    index = index[0] if isinstance(index, (tuple, list)) else index
    if not descriptions:
        return "No description is available for this book."
    if index < 0 or index >= len(descriptions):
        return "No description is available for this book."
    return descriptions[index] or "No description is available for this book."

categories = ["All"] + sorted(books["simple_categories"].unique())
tones = ["All"] + ["Happy", "Surprising", "Angry", "Suspenseful", "Sad"]

# Build the search form and connect its button to the recommendation function.
with gr.Blocks(theme=gr.Theme.from_hub("bencw/soft-no-dark-theme")) as dashboard:
    gr.Markdown("# Semantic Book Recommender")

    with gr.Row():
        user_query = gr.Textbox(label = "Please enter a description of a book:",
                                placeholder = "e.g., A story about forgiveness")
        category_dropdown = gr.Dropdown(choices = categories, label = "Select a category:", value = "All")
        tone_dropdown = gr.Dropdown(choices = tones, label = "Select an emotional tone:", value = "All")
        submit_button = gr.Button("Find recommendations")

    gr.Markdown("## Recommendations")
    output = gr.Gallery(label = "Recommended books", columns = 8, rows = 2)
    recommendations_state = gr.State([])
    full_description = gr.Textbox(label="Full description", lines=8, interactive=False)

    submit_button.click(fn = recommend_books,
                        inputs = [user_query, category_dropdown, tone_dropdown],
                        outputs = [output, recommendations_state, full_description])
    output.select(fn=show_selected_description,
                  inputs=[recommendations_state],
                  outputs=full_description)

if __name__ == "__main__":
    dashboard.launch()
