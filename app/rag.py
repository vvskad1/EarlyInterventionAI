"""
RAG (Retrieval-Augmented Generation) implementation using LangChain and ChromaDB.

Implements semantic search using:
- ChromaDB vector store
- HuggingFace embeddings
- Semantic similarity search
"""
import os
from pathlib import Path
from typing import Optional
from app.vector_store import get_vector_store, initialize_vector_store_from_kb


def ensure_kb_directory():
    """Ensure the kb directory exists."""
    kb_dir = Path("./kb")
    kb_dir.mkdir(parents=True, exist_ok=True)


def get_kb_file_path() -> str:
    """
    Get the knowledge base file path from environment or use default.
    
    Returns:
        Absolute path to the knowledge base file
    """
    kb_file = os.getenv("KB_FILE", "./kb/knowledge_base.txt")
    return str(Path(kb_file).resolve())


def build_query(
    age_months: Optional[int] = None,
    domain: Optional[str] = None,
    extra_info: Optional[str] = None
) -> str:
    """
    Build a retrieval query from structured inputs.
    
    Args:
        age_months: Child's age in months
        domain: Development domain
        extra_info: Additional context
        
    Returns:
        Query string combining all inputs
    """
    parts = []
    
    if age_months is not None:
        # Convert age to years/months for better matching
        years = age_months // 12
        months = age_months % 12
        
        if years > 0:
            parts.append(f"{years} year")
            if years > 1:
                parts[-1] += "s"
        if months > 0:
            parts.append(f"{months} month")
            if months > 1:
                parts[-1] += "s"
        
        parts.append(f"child age {age_months} months")
    
    if domain:
        parts.append(domain)
        # Add common variations/synonyms
        domain_lower = domain.lower().replace("_", " ")
        parts.append(f"development domain {domain_lower}")
    
    if extra_info:
        parts.append(extra_info)
    
    return " ".join(parts)


def initialize_kb() -> int:
    """
    Initialize vector store from knowledge base file.
    
    Returns:
        Number of chunks ingested, or 0 if failed
    """
    kb_path = get_kb_file_path()
    
    if not Path(kb_path).exists():
        print(f"⚠ Knowledge base file not found: {kb_path}")
        return 0
    
    try:
        num_chunks = initialize_vector_store_from_kb(kb_path)
        print(f"✓ Initialized vector store with {num_chunks} chunks from {kb_path}")
        return num_chunks
    except Exception as e:
        print(f"⚠ Error initializing vector store: {e}")
        return 0


def retrieve_context(
    age_months: Optional[int] = None,
    domain: Optional[str] = None,
    extra_info: Optional[str] = None,
    budget: int = 6000,
    k: int = 4
) -> str:
    """
    Retrieve relevant context from vector store using semantic search.
    
    Args:
        age_months: Child's age in months
        domain: Development domain
        extra_info: Additional context
        budget: Maximum characters to return (approximate)
        k: Number of top chunks to retrieve
        
    Returns:
        Concatenated context from top-k semantically similar chunks
    """
    # Get vector store
    vector_store = get_vector_store()
    
    # Check if vector store has any data
    count = vector_store.get_collection_count()
    if count == 0:
        # Try to initialize from KB file
        print("Vector store is empty, initializing from KB file...")
        num_chunks = initialize_kb()
        if num_chunks == 0:
            return ""
    
    # Build query
    query = build_query(age_months, domain, extra_info)
    
    # Perform semantic search
    try:
        # Get more chunks initially, then filter by budget
        documents = vector_store.semantic_search(query, k=k*2)
        
        if not documents:
            return ""
        
        # Concatenate chunks until budget is reached
        context_parts = []
        total_chars = 0
        
        for doc in documents:
            chunk_text = doc.page_content
            chunk_len = len(chunk_text)
            
            # Check if adding this chunk would exceed budget
            if total_chars + chunk_len > budget:
                # If we don't have any context yet, add partial chunk
                if not context_parts:
                    remaining = budget - total_chars
                    context_parts.append(chunk_text[:remaining] + "...")
                break
            
            context_parts.append(chunk_text)
            total_chars += chunk_len + 2  # +2 for separator
            
            # Stop if we've used up the budget or have enough chunks
            if total_chars >= budget or len(context_parts) >= k:
                break
        
        return "\n\n".join(context_parts)
        
    except Exception as e:
        print(f"⚠ Error retrieving context: {e}")
        return ""
