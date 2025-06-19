from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List, Dict
import os

class JobDescriptionVectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = None
        self._initialize_db()
    
    def _initialize_db(self):
        if os.path.exists("data/job_descriptions.faiss"):
            self.db = FAISS.load_local("data/job_descriptions.faiss", self.embeddings)
        else:
            # Initialize with empty DB
            self.db = FAISS.from_texts(["placeholder"], self.embeddings)
    
    def retrieve_similar_jobs(self, query: str, k: int = 3) -> List[Dict]:
        docs = self.db.similarity_search(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]

# Singleton instance
vector_store = JobDescriptionVectorStore()

def retrieve_similar_jobs(role_title: str) -> List[Dict]:
    return vector_store.retrieve_similar_jobs(role_title)