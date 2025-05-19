from langchain_pinecone import PineconeVectorStore
from src.helper import download_hugging_face_embeddings
import os
from typing import Dict, Any

class VectorStoreService:
    def __init__(self):
        self.embeddings = download_hugging_face_embeddings()
        self.index_name = "test"
        self.docsearch = PineconeVectorStore.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        self.retriever = self.docsearch.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 3}
        )

    def get_retriever(self):
        return self.retriever

    def search_similar(self, query: str) -> Dict[str, Any]:
        try:
            return self.retriever.get_relevant_documents(query)
        except Exception as e:
            print(f"Error searching similar documents: {e}")
            return {} 