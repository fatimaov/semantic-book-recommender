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
    persist_directory="./chroma_books",
    embedding_function=embeddings
)
