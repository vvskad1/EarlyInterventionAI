"""
Phase 2: RAG Integration - Load Structured Data into Vector Store

Takes parsed JSON from Phase 1 and:
1. Loads structured milestones and coaching strategies
2. Generates embeddings using HuggingFace sentence-transformers
3. Stores in ChromaDB with rich metadata
4. Tests retrieval quality
"""

import json
from pathlib import Path
from typing import List, Dict
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

# Try new import first, fallback to old
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings


class StructuredDataLoader:
    """Load structured JSON data into ChromaDB vector store."""
    
    def __init__(
        self,
        parsed_dir: str = "parsed_output",
        kb_dir: str = "kb",
        persist_directory: str = "./chroma_db",
        collection_name: str = "early_intervention_complete"
    ):
        """
        Initialize loader.
        
        Args:
            parsed_dir: Directory containing parsed JSON files
            kb_dir: Directory containing knowledge base text files
            persist_directory: ChromaDB persistence directory
            collection_name: Name for the collection
        """
        self.parsed_dir = Path(parsed_dir)
        self.kb_dir = Path(kb_dir)
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings (same model as existing system)
        print("Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vector_store = None
    
    def load_milestones(self) -> List[Document]:
        """
        Load milestone data from multiple sources and convert to Document objects.
        
        Loads:
        - SCGC Social Communication milestones (109)
        - CDC developmental milestones (127)
        
        Returns:
            List of Document objects with milestone content and metadata
        """
        all_documents = []
        
        # Load SCGC milestones (social-communication focused)
        scgc_file = self.parsed_dir / "milestones_structured.json"
        if scgc_file.exists():
            with open(scgc_file, 'r', encoding='utf-8') as f:
                scgc_milestones = json.load(f)
            
            for milestone in scgc_milestones:
                content = self._format_milestone_content(milestone, source_type="SCGC")
                doc = Document(
                    page_content=content,
                    metadata={
                        "type": "milestone",
                        "source": "SCGC Social Communication Growth Charts",
                        "source_type": "SCGC",
                        "age_range": milestone.get("age_range", ""),
                        "age_min": milestone.get("age_min", 0),
                        "age_max": milestone.get("age_max", 0),
                        "domain": milestone.get("domain", ""),
                        "thread": milestone.get("thread", ""),
                        "page": milestone.get("page", 0)
                    }
                )
                all_documents.append(doc)
            print(f"✓ Loaded {len(scgc_milestones)} SCGC milestones")
        else:
            print(f"⚠ SCGC milestone file not found: {scgc_file}")
        
        # Load CDC milestones (comprehensive domains including motor)
        cdc_file = self.parsed_dir / "cdc_milestones_structured.json"
        if cdc_file.exists():
            with open(cdc_file, 'r', encoding='utf-8') as f:
                cdc_milestones = json.load(f)
            
            for milestone in cdc_milestones:
                content = self._format_milestone_content(milestone, source_type="CDC")
                doc = Document(
                    page_content=content,
                    metadata={
                        "type": "milestone",
                        "source": "CDC Learn the Signs. Act Early",
                        "source_type": "CDC",
                        "age_checkpoint": milestone.get("age_checkpoint", 0),
                        "age_min": milestone.get("age_min", 0),
                        "age_max": milestone.get("age_max", 0),
                        "domain": milestone.get("domain", ""),
                        "original_domain": milestone.get("original_domain", "")
                    }
                )
                all_documents.append(doc)
            print(f"✓ Loaded {len(cdc_milestones)} CDC milestones")
        else:
            print(f"⚠ CDC milestone file not found: {cdc_file}")
        
        print(f"✓ Total milestone documents: {len(all_documents)}")
        return all_documents
    
    def _format_milestone_content(self, milestone: Dict, source_type: str = "SCGC") -> str:
        """
        Format milestone as rich text for better semantic search.
        
        Args:
            milestone: Milestone dictionary
            source_type: "SCGC" or "CDC" to handle different data structures
            
        Returns:
            Formatted content string
        """
        if source_type == "SCGC":
            age_range = milestone.get("age_range", "")
            domain = milestone.get("domain", "")
            thread = milestone.get("thread", "")
            text = milestone.get("milestone_text", "")
            
            content = f"""Developmental Milestone for {age_range}
Domain: {domain}
Category: {thread}

{text}

This milestone is appropriate for children aged {age_range} in the {domain} domain.
Source: SCGC Social Communication Growth Charts"""
        
        elif source_type == "CDC":
            checkpoint = milestone.get("age_checkpoint", 0)
            domain = milestone.get("domain", "")
            original_domain = milestone.get("original_domain", "")
            text = milestone.get("milestone_text", "")
            age_min = milestone.get("age_min", 0)
            age_max = milestone.get("age_max", 0)
            
            content = f"""Developmental Milestone for {checkpoint} months
Domain: {domain}
CDC Category: {original_domain}

{text}

This milestone typically appears between {age_min}-{age_max} months in the {domain} domain.
Source: CDC Learn the Signs. Act Early"""
        
        else:
            content = milestone.get("milestone_text", "")
        
        return content.strip()
    
    def load_strategies(self) -> List[Document]:
        """
        Load coaching strategy data and convert to Document objects.
        
        Returns:
            List of Document objects with strategy content and metadata
        """
        strategy_file = self.parsed_dir / "coaching_strategies_cleaned.json"
        
        if not strategy_file.exists():
            print(f"⚠ Strategy file not found: {strategy_file}")
            return []
        
        with open(strategy_file, 'r', encoding='utf-8') as f:
            strategies = json.load(f)
        
        documents = []
        for strategy in strategies:
            # Create rich text content
            content = self._format_strategy_content(strategy)
            
            # Create document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "type": "strategy",
                    "source": strategy.get("source", ""),
                    "layer": strategy.get("layer", ""),
                    "strategy_title": strategy.get("strategy_title", ""),
                    "domain_tag": strategy.get("domain_tag", ""),
                    "page": strategy.get("page", 0)
                }
            )
            documents.append(doc)
        
        print(f"✓ Loaded {len(documents)} strategy documents")
        return documents
    
    def load_text_content(self) -> List[Document]:
        """
        Load supplementary text content and convert to Document objects.
        
        Returns:
            List of Document objects with text content
        """
        text_file = self.parsed_dir / "text_content.json"
        
        if not text_file.exists():
            print(f"⚠ Text content file not found: {text_file}")
            return []
        
        with open(text_file, 'r', encoding='utf-8') as f:
            text_data = json.load(f)
        
        documents = []
        for item in text_data:
            content = item.get("content", "")
            source = item.get("source", "text.txt")
            
            # Split long text into chunks for better retrieval
            # Split by double newlines (paragraphs)
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 100:  # Only include substantial paragraphs
                    doc = Document(
                        page_content=paragraph,
                        metadata={
                            "type": "text",
                            "source": source,
                            "chunk_index": i,
                            "category": "general_knowledge"
                        }
                    )
                    documents.append(doc)
        
        print(f"✓ Loaded {len(documents)} text content chunks")
        return documents
    
    def load_knowledge_base(self) -> List[Document]:
        """
        Load existing knowledge base text file and convert to Document objects.
        
        Returns:
            List of Document objects with knowledge base content
        """
        kb_file = self.kb_dir / "knowledge_base.txt"
        
        if not kb_file.exists():
            print(f"⚠ Knowledge base file not found: {kb_file}")
            return []
        
        with open(kb_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks (similar to original RAG system)
        # Use paragraph or section-based splitting
        chunks = []
        current_chunk = []
        current_length = 0
        max_chunk_length = 1000  # Characters per chunk
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            line_length = len(line)
            
            if current_length + line_length > max_chunk_length and current_chunk:
                # Save current chunk
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        # Add last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "type": "knowledge_base",
                    "source": "knowledge_base.txt",
                    "chunk_index": i
                }
            )
            documents.append(doc)
        
        print(f"✓ Loaded {len(documents)} knowledge base chunks")
        return documents
    
    def load_cdc_guidance(self) -> List[Document]:
        """
        Load CDC milestone guidance document with tips and activities.
        
        Returns:
            List of Document objects with CDC guidance content
        """
        cdc_file = Path("docs") / "CDC.txt"
        
        if not cdc_file.exists():
            print(f"⚠ CDC guidance file not found: {cdc_file}")
            return []
        
        with open(cdc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by age sections (each "Milestones by X Months" is a section)
        sections = []
        current_section = []
        current_age = None
        
        for line in content.split('\n'):
            # Detect new age section
            if 'Milestones by' in line and 'Month' in line:
                # Save previous section
                if current_section:
                    sections.append({
                        'age': current_age,
                        'content': '\n'.join(current_section)
                    })
                    current_section = []
                
                # Extract age
                import re
                age_match = re.search(r'(\d+)\s*Month', line)
                if age_match:
                    current_age = int(age_match.group(1))
            
            current_section.append(line)
        
        # Add last section
        if current_section:
            sections.append({
                'age': current_age,
                'content': '\n'.join(current_section)
            })
        
        # Further chunk large sections (keep under ~1500 chars per chunk)
        documents = []
        for section in sections:
            age = section['age']
            content_text = section['content']
            
            # Split into smaller chunks if needed
            chunks = []
            current_chunk = []
            current_length = 0
            max_chunk_length = 1500
            
            for line in content_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                line_length = len(line)
                
                if current_length + line_length > max_chunk_length and current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                    current_length = line_length
                else:
                    current_chunk.append(line)
                    current_length += line_length
            
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            
            # Create documents with age metadata
            for i, chunk_text in enumerate(chunks):
                doc = Document(
                    page_content=chunk_text,
                    metadata={
                        "type": "cdc_guidance",
                        "source": "CDC Learn the Signs Act Early",
                        "age_checkpoint": age if age else 0,
                        "chunk_index": i,
                        "content_type": "parenting_tips"  # For advice sections
                    }
                )
                documents.append(doc)
        
        print(f"✓ Loaded {len(documents)} CDC guidance chunks")
        return documents
    
    def _format_strategy_content(self, strategy: Dict) -> str:
        """Format strategy as rich text for better semantic search."""
        layer = strategy.get("layer", "")
        title = strategy.get("strategy_title", "")
        text = strategy.get("strategy_text", "")
        domain = strategy.get("domain_tag", "")
        
        # Create rich context
        content = f"""Coaching Strategy: {title}
Layer: {layer}
Domain: {domain}

{text}

This is a {layer} coaching strategy for supporting {domain}."""
        
        return content.strip()
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Create or update vector store with documents.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            ChromaDB vector store instance
        """
        print(f"\nCreating vector store with {len(documents)} documents...")
        print(f"Collection: {self.collection_name}")
        print(f"Persist directory: {self.persist_directory}")
        
        # Create vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
        
        print(f"✓ Vector store created with {len(documents)} documents")
        return vector_store
    
    def test_retrieval(self, vector_store: Chroma, test_queries: List[str], k: int = 3):
        """
        Test retrieval quality with sample queries.
        
        Args:
            vector_store: ChromaDB instance
            test_queries: List of test queries
            k: Number of results to retrieve
        """
        print("\n" + "="*80)
        print("TESTING RETRIEVAL QUALITY")
        print("="*80)
        
        for query in test_queries:
            print(f"\n📍 Query: {query}")
            print("-" * 80)
            
            results = vector_store.similarity_search(query, k=k)
            
            for i, doc in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"  Type: {doc.metadata.get('type', 'unknown')}")
                
                if doc.metadata.get('type') == 'milestone':
                    print(f"  Age: {doc.metadata.get('age_range', '')}")
                    print(f"  Domain: {doc.metadata.get('domain', '')}")
                    print(f"  Thread: {doc.metadata.get('thread', '')}")
                elif doc.metadata.get('type') == 'strategy':
                    print(f"  Layer: {doc.metadata.get('layer', '')}")
                    print(f"  Title: {doc.metadata.get('strategy_title', '')}")
                
                # Show first 150 chars of content
                content = doc.page_content[:150].replace('\n', ' ')
                print(f"  Content: {content}...")
    
    def run(self):
        """Main execution: Load all data and create vector store."""
        print("="*80)
        print("Phase 2: Loading Structured Data into Vector Store")
        print("="*80)
        
        # Load all documents
        print("\n📥 Loading documents...")
        kb_docs = self.load_knowledge_base()
        cdc_guidance_docs = self.load_cdc_guidance()
        milestone_docs = self.load_milestones()
        strategy_docs = self.load_strategies()
        text_docs = self.load_text_content()
        
        all_documents = kb_docs + cdc_guidance_docs + milestone_docs + strategy_docs + text_docs
        
        if not all_documents:
            print("\n❌ No documents to load!")
            return None
        
        print(f"\n📊 Total documents: {len(all_documents)}")
        print(f"   - FGRBI Manual: {len(kb_docs)}")
        print(f"   - CDC Guidance: {len(cdc_guidance_docs)}")
        print(f"   - Milestones: {len(milestone_docs)}")
        print(f"   - Strategies: {len(strategy_docs)}")
        print(f"   - Text content: {len(text_docs)}")
        
        # Create vector store
        vector_store = self.create_vector_store(all_documents)
        
        # Test retrieval
        test_queries = [
            "What milestones should a 9 month old baby reach?",
            "How can I support my baby's language development?",
            "What are strategies for creating learning moments?",
            "Social interaction milestones for 12 months",
            "Layer 2 coaching strategies"
        ]
        
        self.test_retrieval(vector_store, test_queries, k=3)
        
        print("\n" + "="*80)
        print("✅ Phase 2 Complete!")
        print("="*80)
        print(f"\nVector store created: {self.persist_directory}/{self.collection_name}")
        print(f"Total documents: {len(all_documents)}")
        print("\nNext steps:")
        print("1. Update app/rag.py to use this collection")
        print("2. Modify retrieve_context() to query structured data")
        print("3. Test with chatbot interface")
        
        return vector_store


def main():
    """Run Phase 2 data loading."""
    loader = StructuredDataLoader()
    vector_store = loader.run()
    
    if vector_store:
        print("\n🎉 Structured data successfully loaded into vector store!")


if __name__ == "__main__":
    main()
