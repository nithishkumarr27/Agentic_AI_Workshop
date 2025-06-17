import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Any
import numpy as np

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain.vectorstores import FAISS
from langchain.schema import Document

# Utilities
from utils import create_company_data_folder, load_job_description, get_available_job_files

class RAGPipeline:
    """RAG Pipeline for job description processing and retrieval"""
    
    def __init__(self, 
                 company_data_folder: str = "company_data",
                 vector_store_path: str = "vector_store",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        
        self.company_data_folder = Path(company_data_folder)
        self.vector_store_path = Path(vector_store_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize components
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Ensure folders exist
        self.company_data_folder.mkdir(exist_ok=True)
        self.vector_store_path.mkdir(exist_ok=True)
        
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize Google Generative AI embeddings"""
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            )
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            raise Exception("Failed to initialize embeddings. Please check your API key.")
    
    def initialize_vector_store(self, force_rebuild: bool = False):
        """Initialize or load the vector store"""
        
        # Check if vector store already exists and is up to date
        if not force_rebuild and self._is_vector_store_current():
            print("Loading existing vector store...")
            self._load_vector_store()
            return
        
        print("Building new vector store...")
        
        # Create sample data if company_data folder is empty
        if not any(self.company_data_folder.iterdir()):
            create_company_data_folder()
        
        # Load and process documents
        documents = self._load_company_documents()
        
        if not documents:
            raise Exception("No documents found to process. Please add job descriptions to company_data/ folder.")
        
        # Create vector store
        self._create_vector_store(documents)
        
        # Save vector store and metadata
        self._save_vector_store()
        self._save_metadata(documents)
    
    def _is_vector_store_current(self) -> bool:
        """Check if existing vector store is current with source files"""
        
        # Check if vector store files exist
        faiss_index_path = self.vector_store_path / "index.faiss"
        faiss_pkl_path = self.vector_store_path / "index.pkl"
        metadata_path = self.vector_store_path / "metadata.json"
        
        if not all([faiss_index_path.exists(), faiss_pkl_path.exists(), metadata_path.exists()]):
            return False
        
        try:
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Check if source files have changed
            current_files = {}
            for file_path in self.company_data_folder.glob("*.txt"):
                current_files[str(file_path)] = file_path.stat().st_mtime
            for file_path in self.company_data_folder.glob("*.json"):
                current_files[str(file_path)] = file_path.stat().st_mtime
            
            stored_files = metadata.get('source_files', {})
            
            # Compare file modification times
            if set(current_files.keys()) != set(stored_files.keys()):
                return False
            
            for file_path, mtime in current_files.items():
                if stored_files.get(file_path) != mtime:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking vector store currency: {e}")
            return False
    
    def _load_company_documents(self) -> List[Document]:
        """Load all company job description documents"""
        
        documents = []
        
        # Process text files
        for file_path in self.company_data_folder.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': str(file_path),
                        'filename': file_path.name,
                        'type': 'job_description',
                        'company_role': file_path.stem.replace('_', ' ').title()
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Process JSON files
        for file_path in self.company_data_folder.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract content from JSON
                content = ""
                if isinstance(data, dict):
                    content = data.get('description', data.get('content', str(data)))
                else:
                    content = str(data)
                
                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': str(file_path),
                        'filename': file_path.name,
                        'type': 'job_description',
                        'company_role': file_path.stem.replace('_', ' ').title()
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(documents)} documents")
        return documents
    
    def _create_vector_store(self, documents: List[Document]):
        """Create FAISS vector store from documents"""
        
        # Split documents into chunks
        split_docs = []
        for doc in documents:
            chunks = self.text_splitter.split_documents([doc])
            split_docs.extend(chunks)
        
        print(f"Split into {len(split_docs)} chunks")
        
        if not split_docs:
            raise Exception("No document chunks created")
        
        # Create vector store
        try:
            self.vector_store = FAISS.from_documents(
                documents=split_docs,
                embedding=self.embeddings
            )
            print("Vector store created successfully")
            
        except Exception as e:
            print(f"Error creating vector store: {e}")
            raise Exception(f"Failed to create vector store: {str(e)}")
    
    def _save_vector_store(self):
        """Save FAISS vector store to disk"""
        if self.vector_store is None:
            raise Exception("No vector store to save")
        
        try:
            self.vector_store.save_local(str(self.vector_store_path))
            print(f"Vector store saved to {self.vector_store_path}")
        except Exception as e:
            print(f"Error saving vector store: {e}")
            raise Exception(f"Failed to save vector store: {str(e)}")
    
    def _load_vector_store(self):
        """Load FAISS vector store from disk"""
        try:
            self.vector_store = FAISS.load_local(
                str(self.vector_store_path), 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("Vector store loaded successfully")
        except Exception as e:
            print(f"Error loading vector store: {e}")
            raise Exception(f"Failed to load vector store: {str(e)}")
    
    def _save_metadata(self, documents: List[Document]):
        """Save metadata about processed documents"""
        
        # Collect file modification times
        source_files = {}
        for file_path in self.company_data_folder.glob("*.txt"):
            source_files[str(file_path)] = file_path.stat().st_mtime
        for file_path in self.company_data_folder.glob("*.json"):
            source_files[str(file_path)] = file_path.stat().st_mtime
        
        metadata = {
            'num_documents': len(documents),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'source_files': source_files,
            'document_list': [doc.metadata.get('company_role', 'Unknown') for doc in documents]
        }
        
        metadata_path = self.vector_store_path / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def query_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Query the vector store for relevant documents"""
        
        if self.vector_store is None:
            raise Exception("Vector store not initialized. Please call initialize_vector_store() first.")
        
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score),
                    'company_role': doc.metadata.get('company_role', 'Unknown')
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        
        metadata_path = self.vector_store_path / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata.get('num_documents', 0)
            except Exception:
                pass
        
        return 0
    
    def get_available_documents(self) -> List[str]:
        """Get list of available document names/roles"""
        
        metadata_path = self.vector_store_path / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata.get('document_list', [])
            except Exception:
                pass
        
        # Fallback to reading from file system
        return get_available_job_files(self.company_data_folder)
    
    def add_document(self, content: str, metadata: Dict[str, Any]):
        """Add a new document to the vector store"""
        
        if self.vector_store is None:
            raise Exception("Vector store not initialized")
        
        try:
            # Create document
            doc = Document(page_content=content, metadata=metadata)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add to existing vector store
            self.vector_store.add_documents(chunks)
            
            print(f"Added document: {metadata.get('company_role', 'Unknown')}")
            
        except Exception as e:
            print(f"Error adding document: {e}")
            raise Exception(f"Failed to add document: {str(e)}")
    
    def search_similar_roles(self, query: str, threshold: float = 0.7) -> List[str]:
        """Search for roles similar to the query"""
        
        if self.vector_store is None:
            return []
        
        try:
            results = self.query_documents(query, top_k=10)
            
            # Filter by similarity threshold and extract unique roles
            similar_roles = set()
            for result in results:
                if result['similarity_score'] >= threshold:
                    similar_roles.add(result['company_role'])
            
            return list(similar_roles)
            
        except Exception as e:
            print(f"Error searching similar roles: {e}")
            return []
    
    def get_role_context(self, role_name: str) -> str:
        """Get full context for a specific role"""
        
        try:
            results = self.query_documents(role_name, top_k=5)
            
            # Filter results for the specific role
            role_chunks = []
            for result in results:
                if role_name.lower() in result['company_role'].lower():
                    role_chunks.append(result['content'])
            
            # Combine chunks
            return "\n\n".join(role_chunks)
            
        except Exception as e:
            print(f"Error getting role context: {e}")
            return ""

# Utility functions for RAG pipeline management

def initialize_rag_pipeline(force_rebuild: bool = False) -> RAGPipeline:
    """Initialize RAG pipeline with error handling"""
    
    try:
        pipeline = RAGPipeline()
        pipeline.initialize_vector_store(force_rebuild=force_rebuild)
        return pipeline
    except Exception as e:
        print(f"Failed to initialize RAG pipeline: {e}")
        raise

def rebuild_vector_store() -> RAGPipeline:
    """Rebuild vector store from scratch"""
    
    try:
        pipeline = RAGPipeline()
        pipeline.initialize_vector_store(force_rebuild=True)
        print("Vector store rebuilt successfully")
        return pipeline
    except Exception as e:
        print(f"Failed to rebuild vector store: {e}")
        raise

def query_job_descriptions(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Quick utility to query job descriptions"""
    
    try:
        pipeline = initialize_rag_pipeline()
        return pipeline.query_documents(query, top_k=top_k)
    except Exception as e:
        print(f"Error querying job descriptions: {e}")
        return []

def find_matching_roles(skills: List[str], experience_level: str = "") -> Dict[str, Any]:
    """Find roles matching given skills and experience level"""
    
    try:
        pipeline = initialize_rag_pipeline()
        
        # Construct query from skills and experience
        query_parts = skills.copy()
        if experience_level:
            query_parts.append(experience_level)
        
        query = " ".join(query_parts)
        
        # Search for matching roles
        results = pipeline.query_documents(query, top_k=10)
        
        # Group results by role
        role_matches = {}
        for result in results:
            role = result['company_role']
            if role not in role_matches:
                role_matches[role] = {
                    'role': role,
                    'matches': [],
                    'avg_score': 0.0,
                    'total_chunks': 0
                }
            
            role_matches[role]['matches'].append(result)
            role_matches[role]['total_chunks'] += 1
        
        # Calculate average scores
        for role_data in role_matches.values():
            scores = [match['similarity_score'] for match in role_data['matches']]
            role_data['avg_score'] = sum(scores) / len(scores) if scores else 0.0
        
        # Sort by average score
        sorted_roles = sorted(role_matches.values(), 
                            key=lambda x: x['avg_score'], 
                            reverse=True)
        
        return {
            'query': query,
            'matching_roles': sorted_roles[:5],  # Top 5 matches
            'total_roles_found': len(role_matches)
        }
        
    except Exception as e:
        print(f"Error finding matching roles: {e}")
        return {'query': query, 'matching_roles': [], 'total_roles_found': 0}

def get_role_requirements(role_name: str) -> Dict[str, Any]:
    """Extract specific requirements for a role"""
    
    try:
        pipeline = initialize_rag_pipeline()
        
        # Get full context for the role
        context = pipeline.get_role_context(role_name)
        
        if not context:
            return {'role': role_name, 'requirements': [], 'context': ''}
        
        # Search for requirement-related chunks
        requirement_queries = [
            f"{role_name} requirements",
            f"{role_name} qualifications",
            f"{role_name} skills needed",
            f"{role_name} experience"
        ]
        
        all_requirements = []
        for query in requirement_queries:
            results = pipeline.query_documents(query, top_k=3)
            for result in results:
                if role_name.lower() in result['company_role'].lower():
                    all_requirements.append({
                        'content': result['content'],
                        'score': result['similarity_score']
                    })
        
        # Remove duplicates and sort by score
        unique_requirements = []
        seen_content = set()
        for req in all_requirements:
            if req['content'] not in seen_content:
                unique_requirements.append(req)
                seen_content.add(req['content'])
        
        unique_requirements.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'role': role_name,
            'requirements': unique_requirements[:5],  # Top 5 requirement chunks
            'full_context': context
        }
        
    except Exception as e:
        print(f"Error getting role requirements: {e}")
        return {'role': role_name, 'requirements': [], 'full_context': ''}

def analyze_skill_gaps(target_role: str, current_skills: List[str]) -> Dict[str, Any]:
    """Analyze skill gaps for a target role"""
    
    try:
        # Get role requirements
        role_info = get_role_requirements(target_role)
        
        if not role_info['requirements']:
            return {
                'target_role': target_role,
                'skill_gaps': [],
                'recommendations': [],
                'match_score': 0.0
            }
        
        # Extract required skills from role context
        # This is a simplified extraction - in practice, you might use NLP techniques
        role_context = role_info['full_context'].lower()
        current_skills_lower = [skill.lower() for skill in current_skills]
        
        # Simple skill matching
        matched_skills = []
        for skill in current_skills_lower:
            if skill in role_context:
                matched_skills.append(skill)
        
        # Calculate match score
        total_skills = len(current_skills)
        match_score = len(matched_skills) / total_skills if total_skills > 0 else 0.0
        
        return {
            'target_role': target_role,
            'current_skills': current_skills,
            'matched_skills': matched_skills,
            'match_score': match_score,
            'role_context_preview': role_context[:500] + "..." if len(role_context) > 500 else role_context,
            'recommendations': [
                f"Review the full job description for {target_role}",
                "Consider highlighting transferable skills",
                "Look for skill development opportunities" if match_score < 0.7 else "Strong skill match - focus on experience"
            ]
        }
        
    except Exception as e:
        print(f"Error analyzing skill gaps: {e}")
        return {
            'target_role': target_role,
            'skill_gaps': [],
            'recommendations': [],
            'match_score': 0.0
        }

def export_pipeline_stats() -> Dict[str, Any]:
    """Export pipeline statistics and metadata"""
    
    try:
        pipeline = initialize_rag_pipeline()
        
        stats = {
            'total_documents': pipeline.get_document_count(),
            'available_roles': pipeline.get_available_documents(),
            'chunk_size': pipeline.chunk_size,
            'chunk_overlap': pipeline.chunk_overlap,
            'vector_store_path': str(pipeline.vector_store_path),
            'company_data_path': str(pipeline.company_data_folder)
        }
        
        # Get metadata if available
        metadata_path = pipeline.vector_store_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                stats.update(metadata)
        
        return stats
        
    except Exception as e:
        print(f"Error exporting pipeline stats: {e}")
        return {}

# Main execution example
# if __name__ == "__main__":
#     """Example usage of the RAG pipeline"""
    
#     try:
#         print("Initializing RAG Pipeline...")
#         pipeline = initialize_rag_pipeline()
        
#         print(f"\nPipeline Stats:")
#         stats = export_pipeline_stats()
#         print(f"Total Documents: {stats.get('total_documents', 0)}")
#         print(f"Available Roles: {stats.get('available_roles', [])}")
        
#         # Example query
#         print(f"\nExample Query: 'python developer'")
#         results = pipeline.query_documents("python developer", top_k=3)
        
#         for i, result in enumerate(results, 1):
#             print(f"\nResult {i}:")
#             print(f"Role: {result['company_role']}")
#             print(f"Score: {result['similarity_score']:.3f}")
#             print(f"Content Preview: {result['content'][:200]}...")
        
#         # Example skill matching
#         print(f"\nExample Skill Matching:")
#         skills = ["python", "machine learning", "sql"]
#         matches = find_matching_roles(skills, "junior")
        
#         print(f"Query: {matches['query']}")
#         print(f"Total Roles Found: {matches['total_roles_found']}")
        
#         for role in matches['matching_roles'][:3]:
#             print(f"- {role['role']}: {role['avg_score']:.3f}")
        
#     except Exception as e:
#         print(f"Error in main execution: {e}")