import os
from pathlib import Path
from typing import Any

import pandas as pd
from langchain_chroma import Chroma

from . import serialize_book, validate_search_arguments


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class ChromaRepository:
    """Retrieve local Chroma candidates and enrich them from the books CSV."""

    def __init__(self) -> None:
        persist_directory = Path(
            os.getenv("CHROMA_PERSIST_DIRECTORY", str(PROJECT_ROOT / "chroma_db"))
        )
        if not persist_directory.is_absolute():
            persist_directory = PROJECT_ROOT / persist_directory

        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "books")
        self.vector_store = Chroma(
            collection_name=collection_name,
            persist_directory=str(persist_directory),
            embedding_function=None,
        )

        books_csv = PROJECT_ROOT / "data" / "books_with_emotions.csv"
        books = pd.read_csv(books_csv, dtype={"isbn13": "string"})
        books = books.dropna(subset=["isbn13"]).drop_duplicates(
            subset=["isbn13"], keep="first"
        )
        self.books_by_isbn = {
            str(row["isbn13"]).strip(): row
            for row in books.to_dict(orient="records")
        }

    def search_similar(
        self, query_vector: list[float], top_k: int = 250
    ) -> list[dict[str, Any]]:
        vector = validate_search_arguments(query_vector, top_k)
        results = self.vector_store.similarity_search_by_vector_with_relevance_scores(
            embedding=vector,
            k=top_k,
        )
        candidates = []
        for document, similarity_score in results:
            isbn13 = self._extract_isbn13(document.page_content)
            book = self.books_by_isbn.get(isbn13)
            if book is None:
                continue

            candidates.append(serialize_book(book, similarity_score))

        return candidates

    @staticmethod
    def _extract_isbn13(document: str) -> str | None:
        if not document:
            return None
        parts = document.strip().strip('"').split(maxsplit=1)
        if not parts:
            return None
        isbn13 = parts[0].strip('"\'')
        return isbn13 if isbn13.isdigit() else None
