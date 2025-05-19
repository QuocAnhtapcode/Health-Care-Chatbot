from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.prompt import system_prompt
from services.vector_store_service.vector_service import VectorStoreService
import os
from typing import Dict, Any

class ChatService:
    def __init__(self):
        self.llm = OpenAI(temperature=0.4, max_tokens=500)
        self.vector_service = VectorStoreService()
        self._setup_chains()

    def _setup_chains(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        self.question_answer_chain = create_stuff_documents_chain(
            self.llm, 
            self.prompt
        )
        self.rag_chain = create_retrieval_chain(
            self.vector_service.get_retriever(), 
            self.question_answer_chain
        )

    def get_response(self, message: str) -> Dict[str, Any]:
        try:
            response = self.rag_chain.invoke({"input": message})
            return {"answer": response["answer"]}
        except Exception as e:
            print(f"Error getting chat response: {e}")
            return {"answer": "Sorry, I encountered an error. Please try again."} 