"""
Vector Store module using ChromaDB for semantic search and RAG.

Provides functionality for:
- Document ingestion and chunking
- Vector embeddings with sentence-transformers
- Semantic similarity search
- Context retrieval for RAG
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader
from langchain_core.documents import Document


class VectorStoreManager:
    """
    Manages ChromaDB vector store for RAG-based context retrieval.
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize vector store manager.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            embedding_model: HuggingFace model for embeddings
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize or load vector store
        self.vector_store: Optional[Chroma] = None
        self._load_or_create_store()
    
    def _load_or_create_store(self):
        """Load existing vector store or create new one."""
        try:
            if Path(self.persist_directory).exists():
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"✓ Loaded existing vector store from {self.persist_directory}")
            else:
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"✓ Created new vector store at {self.persist_directory}")
        except Exception as e:
            print(f"⚠ Error loading/creating vector store: {e}")
            self.vector_store = None
    
    def ingest_text_file(self, file_path: str, metadata: Optional[Dict] = None) -> int:
        """
        Ingest text file into vector store.
        
        Args:
            file_path: Path to text file
            metadata: Optional metadata to attach to documents
            
        Returns:
            Number of chunks created
        """
        try:
            # Load document
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            # Add metadata if provided
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            if self.vector_store is not None:
                self.vector_store.add_documents(chunks)
                print(f"✓ Ingested {len(chunks)} chunks from {file_path}")
                return len(chunks)
            else:
                print("⚠ Vector store not initialized")
                return 0
                
        except Exception as e:
            print(f"⚠ Error ingesting text file: {e}")
            return 0
    
    def ingest_pdf_file(self, file_path: str, metadata: Optional[Dict] = None) -> int:
        """
        Ingest PDF file into vector store.
        
        Args:
            file_path: Path to PDF file
            metadata: Optional metadata to attach to documents
            
        Returns:
            Number of chunks created
        """
        try:
            # Load PDF
            loader = PDFPlumberLoader(file_path)
            documents = loader.load()
            
            # Add metadata if provided
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            if self.vector_store is not None:
                self.vector_store.add_documents(chunks)
                print(f"✓ Ingested {len(chunks)} chunks from {file_path}")
                return len(chunks)
            else:
                print("⚠ Vector store not initialized")
                return 0
                
        except Exception as e:
            print(f"⚠ Error ingesting PDF file: {e}")
            return 0
    
    def ingest_text_content(self, text: str, metadata: Optional[Dict] = None) -> int:
        """
        Ingest raw text content into vector store.
        
        Args:
            text: Text content to ingest
            metadata: Optional metadata to attach to documents
            
        Returns:
            Number of chunks created
        """
        try:
            # Create document
            doc = Document(page_content=text, metadata=metadata or {})
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add to vector store
            if self.vector_store is not None:
                self.vector_store.add_documents(chunks)
                print(f"✓ Ingested {len(chunks)} chunks from raw text")
                return len(chunks)
            else:
                print("⚠ Vector store not initialized")
                return 0
                
        except Exception as e:
            print(f"⚠ Error ingesting text content: {e}")
            return 0
    
    def semantic_search(
        self,
        query: str,
        k: int = 4,
        filter_metadata: Optional[Dict] = None
    ) -> List[Document]:
        """
        Perform semantic similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        try:
            if self.vector_store is None:
                print("⚠ Vector store not initialized")
                return []
            
            if filter_metadata:
                results = self.vector_store.similarity_search(
                    query,
                    k=k,
                    filter=filter_metadata
                )
            else:
                results = self.vector_store.similarity_search(query, k=k)
            
            return results
            
        except Exception as e:
            print(f"⚠ Error performing semantic search: {e}")
            return []
    
    def retrieve_context(
        self,
        query: str,
        k: int = 4,
        filter_metadata: Optional[Dict] = None
    ) -> str:
        """
        Retrieve context for RAG from vector store.
        
        Args:
            query: Search query
            k: Number of chunks to retrieve
            filter_metadata: Optional metadata filter
            
        Returns:
            Combined context string
        """
        documents = self.semantic_search(query, k=k, filter_metadata=filter_metadata)
        
        if not documents:
            return ""
        
        # Combine document contents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Context {i}]\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    def clear_store(self):
        """Clear all data from vector store."""
        try:
            if self.vector_store is not None:
                self.vector_store.delete_collection()
                self._load_or_create_store()
                print("✓ Vector store cleared")
        except Exception as e:
            print(f"⚠ Error clearing vector store: {e}")
    
    def get_collection_count(self) -> int:
        """Get number of documents in vector store."""
        try:
            if self.vector_store is not None:
                return self.vector_store._collection.count()
            return 0
        except Exception as e:
            print(f"⚠ Error getting collection count: {e}")
            return 0


# Global vector store instance
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store() -> VectorStoreManager:
    """
    Get or create global vector store manager instance.
    
    Returns:
        VectorStoreManager instance
    """
    global _vector_store_manager
    
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    
    return _vector_store_manager


def initialize_vector_store_from_kb(kb_file_path: str) -> int:
    """
    Initialize vector store from knowledge base file.
    
    Args:
        kb_file_path: Path to knowledge base file (.txt or .pdf)
        
    Returns:
        Number of chunks ingested
    """
    vector_store = get_vector_store()
    
    # Clear existing data
    vector_store.clear_store()
    
    # Ingest file
    file_ext = Path(kb_file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return vector_store.ingest_pdf_file(kb_file_path)
    elif file_ext in ['.txt', '.md']:
        return vector_store.ingest_text_file(kb_file_path)
    else:
        print(f"⚠ Unsupported file type: {file_ext}")
        return 0
