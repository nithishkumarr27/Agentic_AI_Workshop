import os
import json
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.vector_store = None
        self.company_data_path = "company_data/"
        self.index_path = "faiss_index"
        
        # Create directories if they don't exist
        os.makedirs(self.company_data_path, exist_ok=True)
        self._create_sample_data_if_empty()
        self.load_or_create_vector_store()

    def _create_sample_data_if_empty(self):
        """Create sample data if no company data exists"""
        if not os.listdir(self.company_data_path):
            sample_data = [{
                "company": "TechCorp",
                "role": "Senior Python Developer",
                "required_skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
                "nice_to_have": ["AWS", "Docker", "Machine Learning"],
                "description": "We're looking for a senior Python developer with 5+ years experience building web applications using Django and PostgreSQL."
            }, {
                "company": "DataSystems",
                "role": "Data Engineer",
                "required_skills": ["Python", "SQL", "ETL", "Big Data"],
                "nice_to_have": ["Spark", "Hadoop", "Airflow"],
                "description": "Seeking a data engineer to design and implement our data pipelines and ETL processes."
            }]
            
            for i, data in enumerate(sample_data):
                with open(f"{self.company_data_path}/sample_{i}.json", 'w') as f:
                    json.dump(data, f)

    def load_or_create_vector_store(self):
        """Load existing FAISS index or create new one"""
        try:
            if os.path.exists(self.index_path):
                # Check if index is valid
                if len(os.listdir(self.index_path)) > 0:
                    self.vector_store = FAISS.load_local(
                        self.index_path,
                        self.embedding_model,
                        allow_dangerous_deserialization=True
                    )
                    print("Successfully loaded FAISS index")
                    return
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
        
        # Create new index if loading failed or doesn't exist
        self._create_vector_store_from_company_data()

    def _create_vector_store_from_company_data(self):
        """Create FAISS index from company data with better debugging"""
        documents = []
        metadatas = []
        
        print(f"Checking company_data directory: {os.listdir(self.company_data_path)}")
        
        for filename in os.listdir(self.company_data_path):
            filepath = os.path.join(self.company_data_path, filename)
            print(f"Processing file: {filepath}")
            
            if filename.endswith('.json'):
                try:
                    with open(filepath, 'r') as f:
                        print(f"Reading file: {filename}")
                        data = json.load(f)
                        print(f"File content: {data}")
                        
                        if not isinstance(data, dict):
                            print(f"Skipping {filename}: Not a dictionary")
                            continue
                            
                        description = data.get('description', '')
                        if not description:
                            print(f"Skipping {filename}: Empty or missing description")
                            continue
                            
                        documents.append(description)
                        metadatas.append({
                            'company': data.get('company', 'Unknown'),
                            'role': data.get('role', 'Unknown'),
                            'required_skills': ', '.join(data.get('required_skills', [])),
                            'nice_to_have': ', '.join(data.get('nice_to_have', []))
                        })
                        print(f"Added document from {filename}")
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON in {filename}: {e}")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        print(f"Total valid documents found: {len(documents)}")
        
        if documents:
            try:
                print("Creating FAISS index...")
                self.vector_store = FAISS.from_texts(
                    documents,
                    self.embedding_model,
                    metadatas=metadatas
                )
                self.vector_store.save_local(self.index_path)
                print(f"Successfully created FAISS index with {len(documents)} documents")
            except Exception as e:
                print(f"Error creating FAISS index: {e}")
        else:
            print("No valid documents found to create index")

    def query_company_requirements(self, query: str, k: int = 3) -> List[Dict]:
        """Search for similar job descriptions"""
        if not self.vector_store:
            self.load_or_create_vector_store()
            if not self.vector_store:
                return []
        
        try:
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
            results = []
            for doc, score in docs_and_scores:
                results.append({
                    'company': doc.metadata.get('company', 'Unknown'),
                    'role': doc.metadata.get('role', 'Unknown'),
                    'required_skills': doc.metadata.get('required_skills', ''),
                    'nice_to_have': doc.metadata.get('nice_to_have', ''),
                    'similarity_score': float(1 - score)  # Convert distance to similarity
                })
            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return []