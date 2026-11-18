from langchain_huggingface import HuggingFaceEmbeddings


class HuggingFaceEmbeddingProvider:
    """Generate query embeddings with the model used by the local Chroma store."""

    MODEL_NAME = "BAAI/bge-base-en-v1.5"
    DIMENSIONS = 768

    def __init__(self) -> None:
        self.embeddings = HuggingFaceEmbeddings(model_name=self.MODEL_NAME)

    def embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)
