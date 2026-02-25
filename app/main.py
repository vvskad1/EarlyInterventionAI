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

from app import rag, prompts, utils, memory, safety
from app.schemas import (
    PlanRequest, PlanResponse,
    ChatRequest, ChatResponse
)
# Use new simplified JSON validators
from app.validators_new import validate_intervention_plan_json, verify_critical_requirements

# LangChain imports
from langchain_groq import ChatGroq


# Load environment variables
load_dotenv()

# Maximum messages to keep per session (for memory manager)
MAX_CHAT_HISTORY = 12

# Initialize ChatGroq
def get_chat_model() -> ChatGroq:
    """Get or create ChatGroq instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    return ChatGroq(
        api_key=api_key,
        model=model_name,
        temperature=0.3,
        max_tokens=None,
        timeout=None
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    """
    # Startup
    print("=" * 60)
    print("Starting Early Intervention GenAI FastAPI Server")
    print("=" * 60)
    
    # Check vector store collection
    from app.vector_store import get_vector_store
    vector_store = get_vector_store()
    count = vector_store.get_collection_count()
    
    if count > 0:
        print(f"✓ Vector store loaded: {count} documents")
        print(f"✓ Collection: early_intervention_complete")
    else:
        print("⚠️ Vector store is empty!")
        print("   Run 'python load_structured_data.py' to populate the collection")
    
    # Create KB directory (for legacy compatibility if needed)
    rag.ensure_kb_directory()
    
    # Print configuration
    port = os.getenv("PORT", "8080")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
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
    
    Implements auto-retry with validation feedback if initial attempt fails quality checks.
    """
    
    # Validate age range
    if not (0 <= plan_req.age_months <= 36):
        raise HTTPException(
            status_code=400,
            detail="age_months must be between 0 and 36"
        )
    
    try:
        # === SAFETY ANALYSIS LAYER ===
        # Check for regression or urgent medical concerns before generating plan
        safety_analysis = safety.analyze_safety_concerns(
            observation=plan_req.notes or "",
            notes=plan_req.extra_info or ""
        )
        
        if safety_analysis["has_concerns"]:
            print(f"\n⚠️ SAFETY CONCERN DETECTED:")
            print(f"   Level: {safety_analysis['safety_level'].upper()}")
            print(f"   Patterns matched: {safety_analysis['matched_patterns']}")
            print(f"   Action: {safety_analysis['recommended_action']}")
        
        # Retrieve RAG context with section-specific sources
        rag_budget = int(os.getenv("RAG_CONTEXT_BUDGET", "12000"))  # Increased for diverse sources and better citation coverage
        
        # Build query from all domains
        domains_text = ", ".join(plan_req.domains)
        extra_context = plan_req.extra_info or ""
        if plan_req.notes:
            extra_context = f"{plan_req.notes}. {extra_context}" if extra_context else plan_req.notes
        
        # Use enhanced retrieval for plan generation
        # This gets: milestones (Goals) + FGRBI techniques (Strategies) + family advice (Advice)
        context = rag.retrieve_for_plan_sections(
            age_months=plan_req.age_months,
            domain=domains_text,
            extra_info=extra_context,
            budget=rag_budget
        )
        
        # Build user message
        areas_formatted = ", ".join([d.replace("_", " ").title() for d in plan_req.domains])
        user_message = f"Create an intervention plan for a {plan_req.age_months}-month-old child with concerns in: {areas_formatted}."
        if plan_req.notes:
            user_message += f"\n\nNotes: {plan_req.notes}"
        if plan_req.extra_info:
            user_message += f"\n\nAdditional context: {plan_req.extra_info}"
        
        # Create LLM with temperature for this request
        from langchain_core.messages import SystemMessage, HumanMessage
        
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=0.2,
            max_tokens=6000  # Increased to ensure full plan with Sources section
        )
        # Don't bind JSON format - let LLM generate freely and parse ourselves
        # llm = llm.bind(response_format={"type": "json_object"})
        
        # Auto-retry with validation feedback
        max_attempts = 3
        best_response = None
        best_validation_score = float('inf')  # Track how many critical errors (fewer is better)
        validation_feedback = []
        
        for attempt in range(max_attempts):
            # Build system prompt (add validation feedback if retrying)
            system_prompt = prompts.plan_system_prompt(context)
            
            # === INJECT SAFETY WARNINGS ===
            # If regression or urgent concerns detected, prepend safety instructions
            safety_injection = safety.generate_safety_prompt_injection(safety_analysis)
            if safety_injection:
                system_prompt = safety_injection + "\n\n" + system_prompt
            
            if attempt > 0 and validation_feedback:
                system_prompt += "\n\n" + "="*60 + "\n"
                system_prompt += "CRITICAL CORRECTION REQUIRED:\n"
                system_prompt += "Your previous attempt had the following issues:\n"
                for feedback in validation_feedback:
                    system_prompt += f"  • {feedback}\n"
                system_prompt += "\nGenerate a NEW plan that addresses these issues.\n"
                system_prompt += "="*60
                
                print(f"\n[Attempt {attempt + 1}/{max_attempts}] Retrying with validation feedback...")
            
            # Convert to LangChain format
            lc_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            response = llm.invoke(lc_messages)
            response_text = response.content
            
            # Parse and repair JSON if needed
            response_json = utils.extract_or_repair_json(response_text)

            if (
                isinstance(response_json, dict)
                and isinstance(response_json.get("goals"), list)
                and len(response_json.get("goals", [])) == 0
                and '"goals"' in response_text.lower()
            ):
                print("[DEBUG] ⚠ JSON parse fallback detected: raw response included goals but parsed payload is empty")

            # Deterministic safety triage payload (cannot be omitted by LLM)
            safety_alert_payload = safety.build_safety_alert_payload(safety_analysis)
            if safety_alert_payload:
                response_json["safety_alert"] = safety_alert_payload

            # Deterministic safety guidance inside advice list (cannot be omitted by LLM)
            response_json = safety.inject_safety_guidance_into_advice(response_json, safety_analysis)
            
            # DEBUG: Print raw response for troubleshooting
            print(f"\n[DEBUG] Raw LLM response (first 500 chars):")
            print(response_text[:500])
            print(f"\n[DEBUG] Parsed JSON keys: {list(response_json.keys())}")

            # Deterministically normalize sources to exact RAG labels
            if context:
                response_json = utils.normalize_sources_from_rag_context(response_json, context)

            # Deterministically rewrite disallowed vocabulary-count goals
            goals_before_sanitize = []
            if isinstance(response_json.get("goals"), list):
                goals_before_sanitize = [g.get("text", "") for g in response_json["goals"] if isinstance(g, dict)]

            response_json = utils.sanitize_vocabulary_count_goals(response_json)

            if isinstance(response_json.get("goals"), list):
                goals_after_sanitize = [g.get("text", "") for g in response_json["goals"] if isinstance(g, dict)]
                if goals_before_sanitize != goals_after_sanitize:
                    print("[DEBUG] ✓ Sanitized count-based language goals into functional communication goals")

            # Deterministically enrich emotional-regulation content for tantrum/transition cases
            response_json = utils.enrich_emotional_regulation_content(
                response_json,
                notes_text=f"{plan_req.notes or ''} {plan_req.extra_info or ''}",
                selected_domains=plan_req.domains,
            )
            
            # === INJECT SOURCE EXCERPTS ===
            # Post-process to add actual source excerpts for transparency
            if context:
                response_json = utils.inject_excerpts_into_json(response_json, context)
                print("[DEBUG] ✓ Injected source excerpts into JSON")
            
            # Validate plan quality (including source whitelist check)
            is_valid, validation_report = validate_intervention_plan_json(
                response_json, 
                plan_req.age_months,
                rag_context=context,  # Pass RAG context for source validation
                safety_analysis=safety_analysis
            )
            
            # Count critical errors (❌)
            critical_errors = validation_report.count("❌")
            
            # Track best attempt
            if best_response is None or critical_errors < best_validation_score:
                best_response = response_json
                best_validation_score = critical_errors
            
            # Log validation results
            print("\n" + "="*60)
            print(f"PLAN VALIDATION REPORT (Attempt {attempt + 1}/{max_attempts})")
            print("="*60)
            print(validation_report)
            print("="*60 + "\n")
            
            # CRITICAL: Verify minimum requirements before considering success
            requirements_met, failed_requirements = verify_critical_requirements(
                response_json,
                rag_context=context,  # Pass RAG context for source validation
                safety_analysis=safety_analysis
            )
            
            if requirements_met:
                print(f"✅ Plan passed critical requirements check on attempt {attempt + 1}")
                # Also check general validation
                if is_valid or critical_errors == 0:
                    print(f"✅ Plan passed all validation checks")
                    try:
                        plan_response = PlanResponse(**response_json)
                        return plan_response
                    except Exception as schema_error:
                        schema_msg = f"Schema validation failed: {schema_error}"
                        print(f"❌ {schema_msg}")
                        validation_feedback.append(schema_msg)
                else:
                    # Has critical requirements but quality issues - keep as best
                    if best_response is None or critical_errors < best_validation_score:
                        best_response = response_json
                        best_validation_score = critical_errors
            else:
                print(f"❌ Plan failed critical requirements:")
                for req in failed_requirements:
                    print(f"  - {req}")
                # Add failed requirements to feedback for next attempt
                validation_feedback.extend(failed_requirements)
            
            # If valid (no critical errors) AND requirements met, return immediately
            if is_valid and requirements_met:
                print(f"✅ Plan passed full validation on attempt {attempt + 1}")
                try:
                    plan_response = PlanResponse(**response_json)
                    return plan_response
                except Exception as schema_error:
                    schema_msg = f"Schema validation failed: {schema_error}"
                    print(f"❌ {schema_msg}")
                    validation_feedback.append(schema_msg)
            
            # Extract critical errors for feedback on next attempt if not already added
            if not validation_feedback or not any("goal" in f.lower() or "strateg" in f.lower() for f in validation_feedback):
                for line in validation_report.split('\n'):
                    if line.strip().startswith('❌'):
                        validation_feedback.append(line.strip())
        
        # FINAL VERIFICATION: Check if best attempt meets critical requirements
        if best_response:
            requirements_met, failed_requirements = verify_critical_requirements(
                best_response,
                rag_context=context,  # Pass RAG context for source validation
                safety_analysis=safety_analysis
            )
            final_is_valid, final_validation_report = validate_intervention_plan_json(
                best_response,
                plan_req.age_months,
                rag_context=context,
                safety_analysis=safety_analysis
            )

            if requirements_met and final_is_valid:
                print(f"⚠️ Returning best attempt (passed critical requirements but had quality warnings)")
                try:
                    plan_response = PlanResponse(**best_response)
                    return plan_response
                except Exception as schema_error:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unable to generate schema-valid plan after {max_attempts} attempts: {schema_error}"
                    )
            else:
                print(f"❌ CRITICAL: Best attempt not returnable")
                if failed_requirements:
                    print(f"   Requirements issues: {failed_requirements}")
                if not final_is_valid:
                    print(f"   Validation issues: {final_validation_report}")
                # Don't return a response that fails critical requirements
                raise HTTPException(
                    status_code=500,
                    detail=f"Unable to generate valid plan after {max_attempts} attempts. Failed requirements: {', '.join(failed_requirements) if failed_requirements else 'none'}. Validation: {final_validation_report}"
                )
        
        # Should never reach here, but fallback
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate valid plan after {max_attempts} attempts"
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating plan: {str(e)}")
        print(error_details)
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
        
        # Retrieve RAG context if age/domains provided
        context = ""
        if chat_req.age_months is not None and chat_req.domains and len(chat_req.domains) > 0:
            rag_budget = int(os.getenv("RAG_CONTEXT_BUDGET", "6000"))
            domains_text = ", ".join(chat_req.domains)
            extra_context = chat_req.message
            if chat_req.notes:
                extra_context = f"{chat_req.notes}. {extra_context}"
            
            context = rag.retrieve_context(
                age_months=chat_req.age_months,
                domain=domains_text,
                extra_info=extra_context,
                budget=rag_budget
            )
        
        # Build system prompt with age/domains context
        domains_for_prompt = ", ".join(chat_req.domains) if chat_req.domains else None
        system_prompt = prompts.chat_system_prompt(
            context=context,
            age_months=chat_req.age_months,
            domain=domains_for_prompt,
            notes=chat_req.notes
        )
        
        # Get messages with history from memory manager
        messages = memory.get_llm_context(session_id, system_prompt)
        
        # Add current user message
        messages.append({"role": "user", "content": chat_req.message})
        
        # Call ChatGroq
        llm = get_chat_model()
        
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        
        # Convert to LangChain format
        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        
        response = llm.invoke(lc_messages)
        response_text = response.content
        
        # Store in memory
        memory.add_to_memory(session_id, chat_req.message, response_text)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
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
