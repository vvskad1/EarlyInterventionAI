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


class Goal(BaseModel):
    """Individual goal with text and source citation."""
    text: str = Field(..., description="Goal text with routine, behavior, measurement, and timeframe")
    source: int = Field(..., description="Source ID number")


class Strategy(BaseModel):
    """Individual strategy with structured components."""
    name: str = Field(..., description="Strategy name/title")
    description: List[str] = Field(..., description="Main description points")
    examples: List[str] = Field(..., description="Concrete implementation examples")
    routine: str = Field(..., description="Frequency and timing suggestions")
    source: int = Field(..., description="Source ID number")


class Advice(BaseModel):
    """Individual advice item with text and source citation."""
    text: str = Field(..., description="Advice text for parents")
    source: int = Field(..., description="Source ID number")


class Source(BaseModel):
    """Source citation with metadata."""
    id: int = Field(..., description="Source number")
    title: str = Field(..., description="Source title")
    excerpt: str = Field("", description="Text excerpt from source")


class SafetyAlert(BaseModel):
    """Deterministic safety triage alert for regression/urgent concerns."""
    level: str = Field(..., description="Safety level: routine | regression | urgent")
    title: str = Field(..., description="Short safety alert title")
    message: str = Field(..., description="Safety interpretation message")
    recommended_action: str = Field(..., description="Recommended action for caregiver")
    matched_patterns: List[str] = Field(default_factory=list, description="Matched safety trigger phrases")


class PlanResponse(BaseModel):
    """Response model for intervention plans with structured data."""
    goals: List[Goal] = Field(..., description="List of intervention goals")
    strategies: List[Strategy] = Field(..., description="List of intervention strategies")
    advice: List[Advice] = Field(..., description="List of advice for parents")
    sources: List[Source] = Field(..., description="List of cited sources")
    safety_alert: Optional[SafetyAlert] = Field(None, description="Safety triage alert when regression/urgent concerns are detected")
    
    # Keep backward compatibility field for now
    Intervention_Plan: Optional[str] = Field(None, description="[DEPRECATED] Markdown-formatted plan - use structured fields instead")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Intervention_Plan": """## Intervention Plan

### 🎯 Goals
- During snack and play routines, child will use gestures/signs/words to request preferred items in 4 out of 5 opportunities across 2 consecutive weeks (Source 1).
- During floor play, child will maintain sitting balance for 10 seconds in 3 out of 5 trials for 1 week (Source 2).

### 🔧 Strategies
- Use model-pause-wait technique during play routines to encourage communication attempts (Source 1).
- Embed learning opportunities in daily routines like mealtime and bath time (Source 1).
- Provide physical support and gradually fade assistance during sitting activities (Source 2).
- Celebrate all attempts and provide positive reinforcement (Source 1).

### 💡 Advice for Parents
- Keep interactions playful and follow your child's lead during activities (Source 1).
- Use short, simple phrases and give your child time to respond (Source 1).
- Practice skills during everyday routines rather than separate "therapy time" (Source 1).
- Celebrate small wins and focus on progress, not perfection (Source 1).

### 📚 Sources
- Source 1: Early Intervention Communication Strategies
- Source 2: Gross Motor Development Guidelines"""
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
