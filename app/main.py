"""
FastAPI application for Early Intervention GenAI prototype.

Provides endpoints for:
- RAG knowledge base upload
- Intervention plan generation
- Conversational chat with session memory
"""
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app import rag, groq, prompts, utils
from app.schemas import (
    PlanRequest, PlanResponse,
    ChatRequest, ChatResponse
)
from app.groq import GroqAPIError


# Load environment variables
load_dotenv()

# Global in-memory chat store: session_id -> list of message dicts
chat_store: Dict[str, List[Dict[str, str]]] = {}

# Maximum messages to keep per session
MAX_CHAT_HISTORY = 12


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    """
    # Startup: Ensure KB directory and file exist
    print("=" * 60)
    print("Starting Early Intervention GenAI FastAPI Server")
    print("=" * 60)
    
    # Create KB directory
    rag.ensure_kb_directory()
    kb_path = rag.get_kb_file_path()
    
    # Create empty KB file if it doesn't exist
    if not Path(kb_path).exists():
        Path(kb_path).write_text(
            "Early Intervention Knowledge Base\n\n"
            "This file will be used for RAG-based context retrieval.\n"
            "Upload your content via /api/rag/upload endpoint.\n",
            encoding="utf-8"
        )
        print(f"✓ Created knowledge base file: {kb_path}")
    else:
        # Check if file has content
        kb_content = rag.load_kb_text()
        if kb_content.strip():
            print(f"✓ Loaded knowledge base: {kb_path} ({len(kb_content)} chars)")
        else:
            print(f"⚠ Knowledge base exists but is empty: {kb_path}")
    
    # Print configuration
    port = os.getenv("PORT", "8080")
    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    rag_budget = os.getenv("RAG_CONTEXT_BUDGET", "6000")
    
    print(f"✓ Server port: {port}")
    print(f"✓ Groq model: {model}")
    print(f"✓ RAG context budget: {rag_budget} chars")
    print(f"✓ API key configured: {'Yes' if os.getenv('GROQ_API_KEY') else 'No (required!)'}")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("\nShutting down...")


# Create FastAPI app
app = FastAPI(
    title="Early Intervention GenAI API",
    description="Backend API for Early Intervention GenAI prototype with RAG-powered intervention planning and conversational chat",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS (open for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Early Intervention GenAI API",
        "version": "1.0.0",
        "endpoints": {
            "upload_kb": "POST /api/rag/upload",
            "generate_plan": "POST /api/plan",
            "chat": "POST /api/chat"
        },
        "docs": "/docs"
    }


@app.post("/api/rag/upload")
async def upload_knowledge_base(file: UploadFile = File(...)):
    """
    Upload a knowledge base file (.txt or .md) to use for RAG retrieval.
    
    Replaces the existing knowledge base file.
    """
    # Validate file extension
    allowed_extensions = [".txt", ".md"]
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only {', '.join(allowed_extensions)} files are allowed."
        )
    
    # Get KB file path
    kb_path = rag.get_kb_file_path()
    
    try:
        # Read and save file content
        content = await file.read()
        
        # Write to KB file
        Path(kb_path).write_bytes(content)
        
        # Verify content was saved
        saved_size = Path(kb_path).stat().st_size
        
        return {
            "ok": True,
            "kb_file": kb_path,
            "size_bytes": saved_size,
            "message": f"Successfully uploaded {file.filename} ({saved_size} bytes)"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save knowledge base file: {str(e)}"
        )


@app.post("/api/plan", response_model=PlanResponse)
async def generate_plan(plan_req: PlanRequest):
    """
    Generate an age-appropriate, domain-specific intervention plan.
    
    Uses RAG to ground recommendations in knowledge base content.
    Returns structured JSON with Goals, Strategies, and Advice for Parents.
    """
    
    # Validate age range
    if not (0 <= plan_req.age_months <= 36):
        raise HTTPException(
            status_code=400,
            detail="age_months must be between 0 and 36"
        )
    
    try:
        # Retrieve RAG context
        rag_budget = int(os.getenv("RAG_CONTEXT_BUDGET", "6000"))
        context = rag.retrieve_context(
            age_months=plan_req.age_months,
            domain=plan_req.domain,
            extra_info=plan_req.extra_info,
            budget=rag_budget
        )
        
        # Build system prompt with context
        system_prompt = prompts.plan_system_prompt(context)
        
        # Build user message
        user_message = f"Create an intervention plan for a {plan_req.age_months}-month-old child in the {plan_req.domain} domain."
        if plan_req.extra_info:
            user_message += f"\n\nAdditional context: {plan_req.extra_info}"
        
        # Call Groq with JSON mode
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response_text = await groq.chat(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Parse and repair JSON if needed
        response_json = utils.extract_or_repair_json(response_text)
        
        # Ensure required keys exist
        required_keys = ["Goals", "Strategies", "Advice for Parents"]
        response_json = utils.ensure_json_keys(response_json, required_keys)
        
        # Validate and return as PlanResponse
        plan_response = PlanResponse(**response_json)
        return plan_response
    
    except GroqAPIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Groq API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating plan: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_req: ChatRequest):
    """
    Conversational chat endpoint with session memory.
    
    Maintains conversation history per session_id (in-memory).
    Optionally uses RAG context when age_months and domain are provided.
    """
    
    # Validate age if provided
    if chat_req.age_months is not None and not (0 <= chat_req.age_months <= 36):
        raise HTTPException(
            status_code=400,
            detail="age_months must be between 0 and 36"
        )
    
    try:
        # Generate session ID if not provided
        if chat_req.session_id is None or not chat_req.session_id.strip():
            chat_req.session_id = str(uuid.uuid4())
        
        session_id = chat_req.session_id
        
        # Initialize session if new
        if session_id not in chat_store:
            chat_store[session_id] = []
        
        # Retrieve RAG context if age/domain provided
        context = ""
        if chat_req.age_months is not None and chat_req.domain is not None:
            rag_budget = int(os.getenv("RAG_CONTEXT_BUDGET", "6000"))
            context = rag.retrieve_context(
                age_months=chat_req.age_months,
                domain=chat_req.domain,
                extra_info=chat_req.message,
                budget=rag_budget
            )
        
        # Build system prompt
        system_prompt = prompts.chat_system_prompt(context)
        
        # Build messages list with history
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history (last N messages)
        history = chat_store[session_id][-MAX_CHAT_HISTORY:]
        messages.extend(history)
        
        # Add current user message
        messages.append({"role": "user", "content": chat_req.message})
        
        # Call Groq
        response_text = await groq.chat(
            messages=messages,
            temperature=0.3
        )
        
        # Store messages in history
        chat_store[session_id].append({"role": "user", "content": chat_req.message})
        chat_store[session_id].append({"role": "assistant", "content": response_text})
        
        # Trim history if too long
        if len(chat_store[session_id]) > MAX_CHAT_HISTORY:
            chat_store[session_id] = chat_store[session_id][-MAX_CHAT_HISTORY:]
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
    
    except GroqAPIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Groq API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
