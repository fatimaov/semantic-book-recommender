import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings


class GeminiEmbeddingProvider:
    """Generate Gemini query embeddings compatible with stored pgvector rows."""

    DIMENSIONS = 768

    def __init__(self) -> None:
        model_name = os.getenv("GEMINI_EMBEDDING_MODEL")
        if not model_name:
            raise ValueError("GEMINI_EMBEDDING_MODEL must be configured.")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=self.DIMENSIONS,
        )

    def embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)
