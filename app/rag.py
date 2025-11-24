"""
RAG (Retrieval-Augmented Generation) implementation for knowledge base retrieval.

Implements naive retrieval using:
- Fixed-size text chunking
- Token overlap scoring
- Top-k context concatenation
"""
import os
from pathlib import Path
from typing import List, Optional


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


def load_kb_text() -> str:
    """
    Load the knowledge base text from file.
    
    Returns:
        Knowledge base text content, or empty string if file doesn't exist
    """
    kb_path = get_kb_file_path()
    
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"Warning: Error reading KB file: {e}")
        return ""


def chunk_text(text: str, size: int = 1000) -> List[str]:
    """
    Split text into chunks of approximately equal size.
    
    Simple chunking strategy: split on newlines first, then combine
    into chunks that don't exceed size. This preserves paragraph boundaries
    when possible.
    
    Args:
        text: Text to chunk
        size: Target size for each chunk (approximate)
        
    Returns:
        List of text chunks
    """
    if not text.strip():
        return []
    
    # Split into paragraphs (double newline) or lines
    paragraphs = text.split("\n\n")
    if len(paragraphs) == 1:
        # No paragraph breaks, try single newlines
        paragraphs = text.split("\n")
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If adding this paragraph would exceed size, save current chunk
        if current_chunk and len(current_chunk) + len(para) + 2 > size:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            # Add to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def tokenize_simple(text: str) -> set:
    """
    Simple tokenization: lowercase, split on whitespace and punctuation.
    
    Args:
        text: Text to tokenize
        
    Returns:
        Set of tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace punctuation with spaces
    for char in ".,!?;:()[]{}\"'":
        text = text.replace(char, " ")
    
    # Split and return unique tokens
    tokens = set(text.split())
    return tokens


def score_chunk(query_tokens: set, chunk_text: str) -> int:
    """
    Score a chunk based on token overlap with query.
    
    Args:
        query_tokens: Set of query tokens
        chunk_text: Text chunk to score
        
    Returns:
        Overlap score (number of matching tokens)
    """
    chunk_tokens = tokenize_simple(chunk_text)
    overlap = query_tokens & chunk_tokens  # Set intersection
    return len(overlap)


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
        
        parts.append(f"{age_months} months")
    
    if domain:
        parts.append(domain)
        # Add common variations/synonyms
        domain_lower = domain.lower().replace("_", " ")
        parts.append(domain_lower)
    
    if extra_info:
        parts.append(extra_info)
    
    return " ".join(parts)


def retrieve_context(
    age_months: Optional[int] = None,
    domain: Optional[str] = None,
    extra_info: Optional[str] = None,
    budget: int = 6000
) -> str:
    """
    Retrieve relevant context from knowledge base using naive RAG.
    
    Args:
        age_months: Child's age in months
        domain: Development domain
        extra_info: Additional context
        budget: Maximum characters to return
        
    Returns:
        Concatenated context from top-scoring chunks
    """
    # Load KB
    kb_text = load_kb_text()
    if not kb_text.strip():
        return ""
    
    # Build query and tokenize
    query = build_query(age_months, domain, extra_info)
    query_tokens = tokenize_simple(query)
    
    # Chunk KB
    chunks = chunk_text(kb_text)
    if not chunks:
        return ""
    
    # Score all chunks
    scored_chunks = []
    for chunk in chunks:
        score = score_chunk(query_tokens, chunk)
        scored_chunks.append((score, chunk))
    
    # Sort by score (descending)
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Concatenate top chunks until budget is reached
    context_parts = []
    total_chars = 0
    
    for score, chunk in scored_chunks:
        # Skip chunks with zero overlap if we already have some context
        if score == 0 and context_parts:
            continue
            
        chunk_len = len(chunk)
        
        # Check if adding this chunk would exceed budget
        if total_chars + chunk_len > budget:
            # Try to add partial chunk if we don't have any context yet
            if not context_parts:
                remaining = budget - total_chars
                context_parts.append(chunk[:remaining] + "...")
                break
            else:
                break
        
        context_parts.append(chunk)
        total_chars += chunk_len + 2  # +2 for separator
        
        # Stop if we've used up the budget
        if total_chars >= budget:
            break
    
    return "\n\n".join(context_parts)
