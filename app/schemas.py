"""
Pydantic models for request/response validation.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """Request model for generating intervention plans."""
    age_months: int = Field(..., ge=0, le=36, description="Child's age in months (0-36)")
    domains: List[str] = Field(..., min_length=1, description="List of development domains (e.g., fine_motor, gross_motor, social, communication, cognitive, adaptive)")
    notes: Optional[str] = Field(None, description="Additional notes or observations about the child")
    extra_info: Optional[str] = Field(None, description="Additional context or information")

    class Config:
        json_schema_extra = {
            "example": {
                "age_months": 24,
                "domains": ["communication", "social"],
                "notes": "Child is shy in group settings; prefers parallel play",
                "extra_info": "struggles to follow one-step directions; bilingual home"
            }
        }


class PlanResponse(BaseModel):
    """Response model for intervention plans with strict JSON structure."""
    Goals: str = Field(..., description="Specific, measurable goals for the child")
    Strategies: str = Field(..., description="Evidence-based intervention strategies")
    Advice_for_Parents: str = Field(..., alias="Advice for Parents", description="Practical advice for parents/caregivers")

    class Config:
        populate_by_name = True  # Allow both "Advice_for_Parents" and "Advice for Parents"
        json_schema_extra = {
            "example": {
                "Goals": "Follow 1-step play-based directions (e.g., 'push car') in 4/5 tries; sustain joint attention 8–10s; use 2-word combos during routines.",
                "Strategies": "Short cues + gestures; model–pause–wait; embed practice in play; offer choices; repeat & expand child's words.",
                "Advice for Parents": "Play daily in short bursts. Say one short direction, then wait. Celebrate attempts. Reuse the same words in snack/bath/cleanup."
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity (auto-generated if missing)")
    age_months: Optional[int] = Field(None, ge=0, le=36, description="Child's age in months for context (optional)")
    domains: Optional[List[str]] = Field(None, description="List of development domains for context (optional)")
    notes: Optional[str] = Field(None, description="Notes about the child for context (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "How do I reduce frustration during cleanup?",
                "age_months": 24,
                "domains": ["communication", "social"]
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response: str = Field(..., description="AI assistant's response")
    session_id: str = Field(..., description="Session ID for this conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "To reduce frustration during cleanup, try using visual timers, breaking tasks into smaller steps, and offering choices...",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
