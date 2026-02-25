"""
RAG (Retrieval-Augmented Generation) implementation using LangChain and ChromaDB.

Implements semantic search using:
- ChromaDB vector store
- HuggingFace embeddings
- Semantic similarity search
"""
import os
from pathlib import Path
from typing import Optional, List
from app.vector_store import get_vector_store


# Domain mapping: Frontend domain names -> Structured data domains
# Maps user-facing domain selections to actual milestone/strategy domains
DOMAIN_MAPPING = {
    # Frontend value: [list of matching structured data domains]
    'gross_motor': ['Gross Motor', 'Play', 'Language'],  # CDC Gross Motor + SCGC Play/Language
    'fine_motor': ['Gross Motor', 'Play', 'Language'],   # CDC includes fine motor in Movement/Physical
    'social': ['Social Interaction', 'Emotional Regulation'],  # Social-emotional
    'cognitive': ['Self-Directed Learning', 'Language', 'Play'],  # Cognitive skills
    'language': ['Language'],  # Direct match
    'communication': ['Language', 'Social Interaction'],  # Communication spans multiple
    'adaptive': ['Self-Directed Learning', 'Emotional Regulation'],  # Adaptive behavior
    
    # Also support direct domain names (case-insensitive)
    'play': ['Play'],
    'language': ['Language'],
    'social interaction': ['Social Interaction'],
    'emotional regulation': ['Emotional Regulation'],
    'self-directed learning': ['Self-Directed Learning'],
    'social communication': ['Social Interaction', 'Language'],  # For coaching strategies
    'gross motor': ['Gross Motor'],  # CDC motor domain
}


def map_domain_to_filters(domain_input: Optional[str]) -> List[str]:
    """
    Map user-facing domain name to actual structured data domains.
    
    Args:
        domain_input: Domain name from frontend or user input
        
    Returns:
        List of actual domain names to filter on
    """
    if not domain_input:
        return []
    
    # Support comma-separated multi-domain input (e.g., "communication, social")
    raw_parts = [part.strip() for part in str(domain_input).split(',') if part.strip()]
    if not raw_parts:
        return []

    resolved_domains: List[str] = []
    for part in raw_parts:
        domain_key = part.lower().strip()

        if domain_key in DOMAIN_MAPPING:
            resolved_domains.extend(DOMAIN_MAPPING[domain_key])
        else:
            # Fallback to raw part for potential direct metadata match
            resolved_domains.append(part)

    # Deduplicate while preserving order
    deduped: List[str] = []
    for domain_name in resolved_domains:
        if domain_name not in deduped:
            deduped.append(domain_name)

    return deduped


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
    [DEPRECATED] Initialize vector store from knowledge base file.
    
    No longer used - vector store is now pre-populated via load_structured_data.py
    which merges all data sources (knowledge base + structured milestones + strategies).
    
    Returns:
        0 (deprecated)
    """
    print("⚠️ This function is deprecated. Use load_structured_data.py to populate the vector store.")
    return 0


def retrieve_context(
    age_months: Optional[int] = None,
    domain: Optional[str] = None,
    extra_info: Optional[str] = None,
    budget: int = 6000,
    k: int = 4,
    return_metadata: bool = False
) -> str | tuple[str, list[dict]]:
    """
    Retrieve relevant context from vector store using semantic search WITH HARD FILTERS.
    
    **STRICT FILTERING LOGIC:**
    1. Filter by age range (age_min <= age <= age_max) if age provided
    2. Filter by domain if domain provided
    3. THEN apply semantic similarity on filtered subset
    
    Uses the unified 'early_intervention_complete' collection containing:
    - Original knowledge base
    - Structured milestones
    - Coaching strategies
    - Supplementary content
    
    Formats retrieved chunks with explicit source numbering for citation purposes.
    
    Args:
        age_months: Child's age in months (strict filter)
        domain: Development domain (strict filter)
        extra_info: Additional context (query only)
        budget: Maximum characters to return (approximate)
        k: Number of top chunks to retrieve
        return_metadata: If True, return (context, metadata_list) for testing
        
    Returns:
        If return_metadata=False: Concatenated context string
        If return_metadata=True: Tuple of (context string, list of metadata dicts)
    """
    # Get vector store (uses 'early_intervention_complete' collection)
    vector_store = get_vector_store()
    
    # Check if vector store has any data
    count = vector_store.get_collection_count()
    if count == 0:
        print("⚠️ Vector store is empty. Run load_structured_data.py to populate.")
        return ""
    
    # Build metadata filter (HARD FILTER before similarity)
    where_filter = None
    target_domains = []
    
    # Map frontend domain to actual structured data domains
    if domain:
        target_domains = map_domain_to_filters(domain)
        print(f"🗺️  Mapped '{domain}' → {target_domains}")
    
    # Build ChromaDB where clause for domain filtering
    if target_domains:
        if len(target_domains) == 1:
            # Single domain: simple filter
            where_filter = {"domain": target_domains[0]}
        else:
            # Multiple domains: OR filter
            where_filter = {"$or": [{"domain": d} for d in target_domains]}
    
    # Build query string (for semantic similarity)
    query = build_query(age_months, domain, extra_info)
    
    # Perform filtered semantic search
    try:
        # Get filtered documents
        if where_filter:
            print(f"🔍 Applying filter: {where_filter}")
            documents = vector_store.semantic_search(query, k=k*3, filter_metadata=where_filter)
        else:
            documents = vector_store.semantic_search(query, k=k*2)
        
        # Manual age filtering (since ChromaDB where clause doesn't support range queries on integers easily)
        if age_months is not None:
            filtered_docs = []
            for doc in documents:
                age_min = doc.metadata.get('age_min')
                age_max = doc.metadata.get('age_max')
                
                # Include if:
                # 1. No age metadata (knowledge_base chunks)
                # 2. Age falls within milestone range
                if age_min is None or age_max is None:
                    filtered_docs.append(doc)
                elif age_min <= age_months <= age_max:
                    filtered_docs.append(doc)
            
            documents = filtered_docs
            print(f"✓ Age filtered: {len(documents)} documents match {age_months} months")
        
        if not documents:
            print("⚠️ No documents match the filters")
            return ("", []) if return_metadata else ""
        
        # Concatenate chunks until budget is reached, with explicit source numbering
        context_parts = []
        total_chars = 0
        
        for idx, doc in enumerate(documents[:k], 1):  # Limit to k documents
            chunk_text = doc.page_content
            
            # Format with source marker for citation
            source_label = f"[Source {idx}]"
            formatted_chunk = f"{source_label}\n{chunk_text}\n"
            chunk_len = len(formatted_chunk)
            
            # Check if adding this chunk would exceed budget
            if total_chars + chunk_len > budget:
                # If we don't have any context yet, add partial chunk
                if not context_parts:
                    remaining = budget - total_chars - len(source_label) - 2
                    if remaining > 100:  # Only add if we have meaningful space
                        context_parts.append(f"{source_label}\n{chunk_text[:remaining]}...\n")
                break
            
            context_parts.append(formatted_chunk)
            total_chars += chunk_len
        
        context_str = "\n".join(context_parts)
        print(f"✓ Retrieved {len(context_parts)} sources ({total_chars} chars)")
        
        # Return metadata if requested (for testing)
        if return_metadata:
            metadata_list = [doc.metadata for doc in documents[:k]]
            return context_str, metadata_list
        
        return context_str
        
    except Exception as e:
        print(f"⚠ Error retrieving context: {e}")
        import traceback
        traceback.print_exc()
        return ("", []) if return_metadata else ""


def retrieve_for_plan_sections(
    age_months: Optional[int] = None,
    domain: Optional[str] = None,
    extra_info: Optional[str] = None,
    budget: int = 8000
) -> str:
    """
    Enhanced retrieval that gets diverse sources for different plan sections.
    
    **Strategy:**
    - Goals: Age + domain filtered milestones (what to target)
    - Strategies: FGRBI coaching techniques + parsed strategies (how to coach)
    - Advice: FGRBI family engagement content (supporting parents)
    
    Args:
        age_months: Child's age in months
        domain: Development domain
        extra_info: Additional context
        budget: Total character budget across all sources
        
    Returns:
        Combined context string with sources numbered sequentially
    """
    try:
        vector_store = get_vector_store()
        
        if vector_store.get_collection_count() == 0:
            print("⚠️ Vector store is empty")
            return ""
        
        # Build query text
        query_parts = []
        if domain:
            mapped_domains = map_domain_to_filters(domain)
            if mapped_domains:
                query_parts.append(f"{' '.join(mapped_domains)} development")
            else:
                query_parts.append(f"{domain} development")
        if age_months:
            query_parts.append(f"for {age_months} month old")
        if extra_info:
            query_parts.append(extra_info)
        query_text = " ".join(query_parts) if query_parts else "developmental milestones and coaching strategies"
        
        # === MILESTONE RETRIEVAL (for Goals section) ===
        # Domain + age filtered milestones
        milestone_docs = []
        if domain:
            target_domains = map_domain_to_filters(domain)
            print(f"🎯 Retrieving milestones: {target_domains}")
            
            # Build filter
            if len(target_domains) > 1:
                where_filter = {"$or": [{"domain": d} for d in target_domains]}
            else:
                where_filter = {"domain": target_domains[0]}
            
            # Add type filter to get only milestones
            where_filter = {"$and": [
                where_filter,
                {"type": "milestone"}
            ]}
            
            docs = vector_store.semantic_search(
                query=query_text,
                k=15,  # Get more, then filter by age
                filter_metadata=where_filter
            )
            
            # Age filter
            if age_months:
                for doc in docs:
                    age_min = doc.metadata.get('age_min')
                    age_max = doc.metadata.get('age_max')
                    if age_min is None or age_max is None:
                        continue
                    if age_min <= age_months <= age_max:
                        milestone_docs.append(doc)
            else:
                milestone_docs = docs[:6]
            
            milestone_docs = milestone_docs[:4]  # Limit to top 4
            print(f"  ✓ {len(milestone_docs)} milestone sources")
        
        # === COACHING STRATEGY RETRIEVAL (for Strategies section) ===
        # Get FGRBI coaching techniques
        strategy_query = f"coaching strategies embedding intervention daily routines {domain or 'development'}"
        print(f"🔧 Retrieving coaching strategies")
        
        strategy_docs = vector_store.semantic_search(
            query=strategy_query,
            k=20,
            filter_metadata={"type": "knowledge_base"}  # FGRBI manual chunks
        )[:3]  # Top 3 FGRBI techniques
        
        # Also get parsed coaching strategies if available
        parsed_strat_docs = vector_store.semantic_search(
            query=strategy_query,
            k=5,
            filter_metadata={"type": "coaching_strategy"}
        )[:1]  # 1 high-level principle
        
        strategy_docs = strategy_docs + parsed_strat_docs
        print(f"  ✓ {len(strategy_docs)} strategy sources")
        
        # === ADVICE RETRIEVAL (for Advice section) ===
        # Get FGRBI family engagement content + CDC parenting tips
        advice_query = "supporting families caregiver coaching partnership parent tips activities what you can do"
        print(f"💡 Retrieving family advice")
        
        # Get FGRBI coaching advice
        fgrbi_advice = vector_store.semantic_search(
            query=advice_query,
            k=8,
            filter_metadata={"type": "knowledge_base"}
        )[:2]  # Top 2 FGRBI family support chunks
        
        # Get CDC parenting tips (if available)
        cdc_advice = vector_store.semantic_search(
            query=advice_query,
            k=8,
            filter_metadata={"type": "cdc_guidance"}
        )[:2]  # Top 2 CDC parenting tips
        
        advice_docs = fgrbi_advice + cdc_advice
        print(f"  ✓ {len(advice_docs)} advice sources ({len(fgrbi_advice)} FGRBI + {len(cdc_advice)} CDC)")
        
        # === COMBINE ALL SOURCES ===
        all_docs = milestone_docs + strategy_docs + advice_docs
        
        if not all_docs:
            print("⚠️ No documents retrieved")
            return ""
        
        # Format with sequential source numbering and metadata for citation
        context_parts = []
        total_chars = 0
        
        for idx, doc in enumerate(all_docs, 1):
            chunk_text = doc.page_content
            metadata = doc.metadata
            
            # Build source metadata line
            source_info = f"[Source {idx}]"
            
            # Add metadata for citation formatting
            source_label = metadata.get('source', 'Unknown Source')
            doc_type = metadata.get('type', '')

            # Normalize generic placeholder source names for better downstream source titles
            if str(source_label).strip().lower() in {'knowledge_base.txt', 'unknown source', ''}:
                if doc_type == 'knowledge_base':
                    source_label = 'FGRBI Key Indicators Manual'
                elif doc_type == 'cdc_guidance':
                    source_label = 'CDC Developmental Guidance'
                elif doc_type == 'milestone':
                    source_label = 'Developmental Milestones Reference'
            
            # Add age/domain info if available (for milestones)
            if doc_type == 'milestone':
                age_range = metadata.get('age_range', '')
                domain = metadata.get('domain', '')
                if age_range and domain:
                    source_info += f" - {source_label} ({domain}, Ages {age_range})"
                else:
                    source_info += f" - {source_label}"
            else:
                source_info += f" - {source_label}"
            
            # Extract excerpt (first 50-60 chars for source citation)
            excerpt = chunk_text.strip()
            if len(excerpt) > 60:
                # Find natural break point
                excerpt = excerpt[:60]
                last_period = excerpt.rfind('.')
                last_space = excerpt.rfind(' ')
                if last_period > 40:
                    excerpt = excerpt[:last_period + 1]
                elif last_space > 40:
                    excerpt = excerpt[:last_space] + "..."
                else:
                    excerpt = excerpt + "..."
            
            source_info += f'\nEXCERPT: "{excerpt}"'
            
            formatted_chunk = f"{source_info}\n\nFULL CONTENT:\n{chunk_text}\n"
            chunk_len = len(formatted_chunk)
            
            if total_chars + chunk_len > budget:
                if not context_parts:
                    remaining = budget - total_chars - len(source_info) - 20
                    if remaining > 100:
                        context_parts.append(f"{source_info}\n\nFULL CONTENT:\n{chunk_text[:remaining]}...\n")
                break
            
            context_parts.append(formatted_chunk)
            total_chars += chunk_len
        
        context_str = "\n".join(context_parts)
        print(f"✓ Total: {len(context_parts)} sources ({total_chars} chars)")
        print(f"  - Milestones: {len(milestone_docs)}")
        print(f"  - Strategies: {len(strategy_docs)}")
        print(f"  - Advice: {len(advice_docs)}")
        
        return context_str
        
    except Exception as e:
        print(f"⚠ Error in section-specific retrieval: {e}")
        import traceback
        traceback.print_exc()
        return ""
