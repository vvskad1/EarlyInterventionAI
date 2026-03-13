"""
Safety classifier for detecting clinical red flags in observations.

These detectors identify patterns that require urgent medical evaluation
beyond standard early intervention services.
"""
import re
from typing import Dict, List, Tuple


def detect_regression(observation: str) -> Tuple[bool, List[str]]:
    """
    Detect developmental regression indicators in observation text.
    
    Regression (loss of previously acquired skills) is a RED FLAG that requires
    urgent pediatric evaluation to rule out:
    - Neurological conditions
    - Metabolic disorders
    - Hearing/vision loss
    - Autism spectrum disorders
    - Other underlying medical causes
    
    Args:
        observation: User's observation text about the child
        
    Returns:
        Tuple of (is_regression_detected, matched_patterns)
    """
    if not observation:
        return False, []
    
    regression_patterns = [
        # Direct loss indicators
        "lost ability",
        "lost skill",
        "can't anymore",
        "cannot anymore",
        "stopped doing",
        "no longer",
        "used to be able to",
        "used to do",
        "used to say",
        "used to stand",
        "used to walk",
        "was saying",
        "previously could",
        "previously did",
        
        # Regression terminology
        "regression",
        "regressed",
        "regressing",
        "going backward",
        "moving backward",
        
        # Skill loss specifics
        "stopped talking",
        "stopped saying",
        "stopped walking",
        "stopped standing",
        "stopped sitting",
        "stopped responding",
        "stopped making eye contact",
        "stopped playing",
        "lost words",
        "lost language",
        "lost motor skills",
        "not able now",
        "unable now",
        
        # Comparative weakness/decline
        "weaker than before",
        "weaker than used to",
        "less active than before",
        "less engaged than before",
        "more floppy than before"
    ]

    regression_regex_patterns = [
        r'used to\s+\w+.*\b(stopped|no longer|lost)\b',
        r'was\s+\w+ing.*\b(stopped|no longer|lost)\b',
        r'used to\s+\w+.*\b(not able|unable|cannot|can\'t|isn\'t able|is not able)\b.*\b(now|anymore)?\b',
        r'previously\s+\w+.*\b(not able|unable|cannot|can\'t|isn\'t able|is not able)\b.*\b(now|anymore)?\b',
        r'no longer\s+\w+',
        r'lost\s+(words?|language|speech|skills?)',
        r'stopped\s+(saying|talking|using words|responding|walking|standing|sitting)',
    ]
    
    obs_lower = observation.lower()
    matched = [pattern for pattern in regression_patterns if pattern in obs_lower]

    for regex in regression_regex_patterns:
        if re.search(regex, obs_lower):
            matched.append(f"regex:{regex}")

    # Composite heuristic: "used to / previously" + "stopped / no longer / lost"
    has_previous_ability = any(token in obs_lower for token in ["used to", "previously", "was saying", "before"])
    has_loss_signal = any(
        token in obs_lower
        for token in [
            "stopped",
            "no longer",
            "lost",
            "can't anymore",
            "cannot anymore",
            "not able",
            "unable",
            "isn't able",
            "is not able",
            "can't now",
            "cannot now",
        ]
    )
    if has_previous_ability and has_loss_signal:
        matched.append("composite:previous_ability_plus_loss")

    # De-duplicate while preserving order
    deduped = []
    for item in matched:
        if item not in deduped:
            deduped.append(item)

    return len(deduped) > 0, deduped


def detect_urgent_medical_flags(observation: str) -> Tuple[bool, List[str]]:
    """
    Detect urgent medical concerns that require immediate evaluation.
    
    These patterns indicate potential medical emergencies or urgent conditions
    beyond developmental concerns.
    
    Args:
        observation: User's observation text about the child
        
    Returns:
        Tuple of (urgent_flag_detected, matched_patterns)
    """
    if not observation:
        return False, []
    
    urgent_patterns = [
        # Seizure indicators
        "seizure",
        "convulsion",
        "staring spell",
        "shaking episode",
        
        # Loss of consciousness
        "passed out",
        "unresponsive",
        "won't wake up",
        
        # Severe tone issues
        "completely floppy",
        "very stiff",
        "arching back constantly",
        
        # Feeding emergencies
        "choking",
        "can't swallow",
        "turning blue",
        
        # Pain indicators
        "screaming in pain",
        "inconsolable crying",
        "won't stop crying",
        
        # Head concerns
        "head injury",
        "hit head",
        "fell on head"
    ]
    
    obs_lower = observation.lower()
    matched = [pattern for pattern in urgent_patterns if pattern in obs_lower]
    
    return len(matched) > 0, matched


def analyze_safety_concerns(
    observation: str,
    notes: str = None
) -> Dict[str, any]:
    """
    Comprehensive safety analysis of child observations.
    
    Returns structured report of any concerning patterns that require
    medical evaluation or elevated clinical response.
    
    Args:
        observation: Primary observation text
        notes: Additional notes (optional)
        
    Returns:
        Dictionary with:
        - has_concerns: bool
        - regression_detected: bool
        - urgent_medical_flag: bool
        - matched_patterns: List[str]
        - safety_level: str ("routine", "regression", "urgent")
        - recommended_action: str
    """
    combined_text = observation or ""
    if notes:
        combined_text += " " + notes
    
    # Check for regression
    has_regression, regression_patterns = detect_regression(combined_text)
    
    # Check for urgent medical flags
    has_urgent, urgent_patterns = detect_urgent_medical_flags(combined_text)
    
    # Determine safety level
    if has_urgent:
        safety_level = "urgent"
        recommended_action = "IMMEDIATE medical evaluation required. Contact pediatrician or emergency services."
    elif has_regression:
        safety_level = "regression"
        recommended_action = "Prompt pediatric evaluation recommended to rule out underlying medical causes."
    else:
        safety_level = "routine"
        recommended_action = "Standard early intervention assessment and services."
    
    return {
        "has_concerns": has_regression or has_urgent,
        "regression_detected": has_regression,
        "urgent_medical_flag": has_urgent,
        "matched_patterns": regression_patterns + urgent_patterns,
        "safety_level": safety_level,
        "recommended_action": recommended_action
    }


def generate_safety_prompt_injection(safety_analysis: Dict[str, any]) -> str:
    """
    Generate prompt text to inject into system prompt when safety concerns detected.
    
    Args:
        safety_analysis: Output from analyze_safety_concerns()
        
    Returns:
        Formatted text to prepend to system prompt, or empty string if no concerns
    """
    if not safety_analysis["has_concerns"]:
        return ""
    
    if safety_analysis["urgent_medical_flag"]:
        return """
⚠️⚠️⚠️ URGENT MEDICAL CONCERN DETECTED ⚠️⚠️⚠️

The observation contains indicators of urgent medical concerns.

YOU MUST include this at the TOP of the intervention plan:

🚨 URGENT: The described symptoms require immediate medical evaluation.
Please contact your pediatrician or seek emergency care as appropriate.
The strategies below are supportive but do not replace medical assessment.

Then proceed with generating supportive strategies, but maintain urgent tone.
"""
    
    elif safety_analysis["regression_detected"]:
        return """
⚠️ REGRESSION INDICATOR DETECTED ⚠️

The observation suggests loss of previously acquired skills (developmental regression).

This is a RED FLAG that requires prompt medical evaluation.

YOU MUST include this safety section in your plan BEFORE the outcomes:

### 🚨 Important: Regression Concern

The reported loss of previously acquired skills warrants prompt evaluation by a pediatrician or developmental specialist. Regression can indicate:
- Underlying medical conditions
- Neurological concerns  
- Sensory changes (vision/hearing)
- Autism spectrum considerations
- Other treatable conditions

**Recommended Action**: Schedule a comprehensive evaluation with your child's pediatrician. Share this observation in detail.

The strategies below provide supportive approaches while awaiting evaluation, but medical assessment should be prioritized.

---

Then proceed with generating Outcomes, Strategies, and Advice sections as usual.

IMPORTANT: Maintain supportive, non-alarmist tone while clearly communicating the need for medical evaluation.
"""
    
    return ""


def build_safety_alert_payload(safety_analysis: Dict[str, any]) -> Dict[str, any]:
    """
    Build a deterministic safety alert payload for API responses.

    This ensures regression/urgent triage is always present in output even if
    the LLM does not follow prompt safety instructions perfectly.

    Returns:
        dict with safety alert fields, or empty dict when no concerns.
    """
    if not safety_analysis or not safety_analysis.get("has_concerns"):
        return {}

    level = safety_analysis.get("safety_level", "routine")
    matched_patterns = safety_analysis.get("matched_patterns", [])
    recommended_action = safety_analysis.get("recommended_action", "")

    if level == "urgent":
        title = "Urgent medical concern"
        message = (
            "The observation includes urgent red flags. Seek immediate medical evaluation. "
            "Supportive intervention strategies do not replace urgent care."
        )
    elif level == "regression":
        title = "Regression concern"
        message = (
            "Loss of previously acquired skills is a clinical red flag and warrants prompt "
            "evaluation by a pediatrician or developmental specialist."
        )
    else:
        title = "Safety note"
        message = "No urgent safety red flags were detected from the provided observation."

    return {
        "level": level,
        "title": title,
        "message": message,
        "recommended_action": recommended_action,
        "matched_patterns": matched_patterns,
    }


def inject_safety_guidance_into_advice(plan_data: Dict[str, any], safety_analysis: Dict[str, any]) -> Dict[str, any]:
    """
    Deterministically prepend a safety guidance advice item when concerns exist.

    This guarantees plan content itself (not only top-level safety_alert) contains
    triage language for regression/urgent cases.
    """
    if not safety_analysis or not safety_analysis.get("has_concerns"):
        return plan_data

    advice = plan_data.get("advice")
    if not isinstance(advice, list):
        return plan_data

    level = safety_analysis.get("safety_level")
    if level == "urgent":
        guidance_text = (
            "Seek immediate medical evaluation now. The supportive strategies below do not replace urgent care."
        )
    else:
        guidance_text = (
            "Because there is reported loss of previously acquired skills, schedule prompt pediatric evaluation while continuing supportive communication routines."
        )

    # Avoid duplicates across retries
    for item in advice:
        if isinstance(item, dict) and guidance_text.lower()[:40] in str(item.get("text", "")).lower():
            return plan_data

    # Choose a valid source id from listed sources if available
    source_id = None
    sources = plan_data.get("sources")
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict) and isinstance(source.get("id"), int):
                source_id = source["id"]
                break

    if source_id is None:
        source_id = 1

    advice.insert(0, {
        "text": guidance_text,
        "source": source_id,
    })

    return plan_data
