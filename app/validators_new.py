"""
Simplified output validation for structured JSON intervention plans.

This validator keeps the structural checks from the JSON migration while
preserving critical EI quality checks (age appropriateness, outcome quality,
and citation/source grounding).
"""
import re
from typing import Dict, List, Tuple, Optional


VOCAB_COUNT_PATTERNS = [
    r'\b(\d+)[\s-]+words?\b',
    r'\bvocabulary\s+(?:to|of)\s+\d+',
    r'\bincrease.*vocabulary.*\d+',
    r'\bsay\s+\d+\s+words?',
]

SENTENCE_LENGTH_PATTERNS = [
    r'\b(\d+)[\s-]+word\s+sentences?',
    r'\b(\d+)[\s-]+word\s+phrases?',
]

ROUTINE_CONTEXT_PATTERNS = [
    r'\bduring\b',
    r'\bin\s+(?:play|mealtime|meal|bath|bedtime|dressing|diaper|floor\s*play|snack)\b',
    r'\broutine(?:s)?\b',
]

GENERIC_GOAL_PATTERNS = [
    r'\bimprov(?:e|ed|ement)\b',
    r'\bdemonstrate\s+improv(?:ed|ement)\b',
    r'\bmake\s+progress\b',
    r'\benhance\b',
]

INFANT_UNSAFE_STRATEGY_PATTERNS = [
    r'\bbalance\s+beam\b',
    r'\bunsupported\s+walking\b',
    r'\badvanced\s+walking\b',
]

QUESTIONABLE_SUPPORT_PATTERNS = [
    r'\bsupport\s+under\s+(?:the\s+)?arms\b',
    r'\bhold\s+under\s+(?:the\s+)?arms\b',
]


def _extract_rag_source_map(rag_context: str) -> Dict[int, str]:
    """Extract {source_id: source_title} from RAG context lines like [Source N] - Title."""
    source_map: Dict[int, str] = {}
    if not rag_context:
        return source_map

    pattern = r'\[Source\s+(\d+)\]\s*-\s*(.+)'
    for source_num, title in re.findall(pattern, rag_context):
        cleaned = title.strip().split('\n')[0].strip()
        source_map[int(source_num)] = cleaned
    return source_map


def _goal_has_measurable_components(goal_text: str) -> bool:
    """Heuristic check for measurable criterion + timeframe in an outcome sentence."""
    text = goal_text.lower()
    has_measure = bool(re.search(r'\b\d+\s*/\s*\d+\b|\bout of\s+\d+\b|\bopportunit(?:y|ies)\b|\bseconds?\b|\bminutes?\b|\btimes?\b', text))
    has_timeframe = bool(re.search(r'\b(across|within|over|by|for)\b.*\b(day|days|week|weeks|month|months)\b', text))
    return has_measure and has_timeframe


def _goal_has_routine_context(goal_text: str) -> bool:
    text = goal_text.lower()
    return any(re.search(pattern, text) for pattern in ROUTINE_CONTEXT_PATTERNS)


def validate_intervention_plan_json(
    plan_data: Dict,
    age_months: int = None,
    rag_context: str = "",
    safety_analysis: Optional[Dict] = None,
) -> Tuple[bool, str]:
    """
    Validate structured JSON intervention plan.
    
    Args:
        plan_data: Parsed JSON with outcomes, strategies, advice, sources arrays
        age_months: Child's age in months (optional)
        rag_context: RAG context for source validation (optional)
        
    Returns:
        Tuple of (is_valid, validation_report_string)
    """
    errors = []
    warnings = []
    
    # Extract available source IDs and exact source titles from RAG context
    rag_source_map = _extract_rag_source_map(rag_context)
    available_sources = set(rag_source_map.keys())
    
    # === CHECK OUTCOMES ===
    if 'outcomes' not in plan_data or not isinstance(plan_data['outcomes'], list):
        errors.append("❌ MISSING: 'outcomes' array is required")
    else:
        outcomes = plan_data['outcomes']
        if len(outcomes) < 2:
            errors.append(f"❌ INSUFFICIENT OUTCOMES: {len(outcomes)} provided, minimum 2 required")
        
        for i, outcome in enumerate(outcomes, 1):
            if not isinstance(outcome, dict):
                errors.append(f"❌ OUTCOME {i}: Must be an object with 'text' and 'source' fields")
                continue
            
            if 'text' not in outcome or not outcome['text'].strip():
                errors.append(f"❌ OUTCOME {i}: Missing 'text' field")
            
            if 'source' not in outcome:
                errors.append(f"❌ OUTCOME {i}: Missing 'source' citation")
            elif available_sources and outcome['source'] not in available_sources:
                errors.append(f"❌ OUTCOME {i}: Cites Source {outcome['source']} but only {available_sources} available in RAG context")

            outcome_text = (outcome.get('text') or '').strip()
            if outcome_text:
                # Disallow vocabulary-count and sentence-length targets
                for pattern in VOCAB_COUNT_PATTERNS:
                    if re.search(pattern, outcome_text, re.IGNORECASE):
                        errors.append(f"❌ OUTCOME {i}: Uses vocabulary-count target ('{outcome_text[:80]}...') which is not allowed")
                        break

                if age_months is not None and age_months < 24:
                    for pattern in SENTENCE_LENGTH_PATTERNS:
                        if re.search(pattern, outcome_text, re.IGNORECASE):
                            errors.append(f"❌ OUTCOME {i}: Sentence-length targets are not age-appropriate for children under 24 months")
                            break

                if any(re.search(pattern, outcome_text, re.IGNORECASE) for pattern in GENERIC_GOAL_PATTERNS):
                    errors.append(f"❌ OUTCOME {i}: Outcome is too generic; use observable and measurable IFSP-style phrasing")

                if not _goal_has_measurable_components(outcome_text):
                    errors.append(f"❌ OUTCOME {i}: Missing measurable criterion or clear timeframe (use X/Y or duration + time window)")

                if not _goal_has_routine_context(outcome_text):
                    errors.append(f"❌ OUTCOME {i}: Missing routine/context phrase (e.g., 'During play routines...')")
    
    # === CHECK STRATEGIES ===
    if 'strategies' not in plan_data or not isinstance(plan_data['strategies'], list):
        errors.append("❌ MISSING: 'strategies' array is required")
    else:
        strategies = plan_data['strategies']
        if len(strategies) < 3:
            errors.append(f"❌ INSUFFICIENT STRATEGIES: {len(strategies)} provided, minimum 3 required")
        
        for i, strategy in enumerate(strategies, 1):
            if not isinstance(strategy, dict):
                errors.append(f"❌ STRATEGY {i}: Must be an object")
                continue
            
            required_fields = ['name', 'description', 'examples', 'routine', 'source']
            for field in required_fields:
                if field not in strategy:
                    errors.append(f"❌ STRATEGY {i}: Missing '{field}' field")
                elif field in ['description', 'examples']:
                    if not isinstance(strategy[field], list) or len(strategy[field]) == 0:
                        errors.append(f"❌ STRATEGY {i}: '{field}' must be non-empty array")
            
            if 'source' in strategy and available_sources and strategy['source'] not in available_sources:
                errors.append(f"❌ STRATEGY {i}: Cites Source {strategy['source']} but only {available_sources} available")

            # Age safety checks for strategy content
            strategy_text = " ".join([
                str(strategy.get('name', '')),
                " ".join(strategy.get('description', []) if isinstance(strategy.get('description', []), list) else []),
                " ".join(strategy.get('examples', []) if isinstance(strategy.get('examples', []), list) else []),
                str(strategy.get('routine', '')),
            ]).lower()

            if age_months is not None and age_months < 12:
                for pattern in INFANT_UNSAFE_STRATEGY_PATTERNS:
                    if re.search(pattern, strategy_text, re.IGNORECASE):
                        errors.append(f"❌ STRATEGY {i}: Contains age-inappropriate activity for <12 months (e.g., balance beam/advanced walking)")
                        break

            for pattern in QUESTIONABLE_SUPPORT_PATTERNS:
                if re.search(pattern, strategy_text, re.IGNORECASE):
                    warnings.append(f"⚠️ STRATEGY {i}: Uses questionable phrasing about under-arm support; prefer trunk/hip support and floor-based positioning")
                    break
    
    # === CHECK ADVICE ===
    if 'advice' not in plan_data or not isinstance(plan_data['advice'], list):
        errors.append("❌ MISSING: 'advice' array is required")
    else:
        advice = plan_data['advice']
        if len(advice) < 4:
            warnings.append(f"⚠️ FEW ADVICE ITEMS: {len(advice)} provided, 4-6 recommended")
        
        for i, item in enumerate(advice, 1):
            if not isinstance(item, dict):
                errors.append(f"❌ ADVICE {i}: Must be an object with 'text' and 'source' fields")
                continue
            
            if 'text' not in item or not item['text'].strip():
                errors.append(f"❌ ADVICE {i}: Missing 'text' field")
            
            if 'source' not in item:
                errors.append(f"❌ ADVICE {i}: Missing 'source' citation")
            elif available_sources and item['source'] not in available_sources:
                errors.append(f"❌ ADVICE {i}: Cites Source {item['source']} but only {available_sources} available")
    
    # === CHECK SOURCES ===
    if 'sources' not in plan_data or not isinstance(plan_data['sources'], list):
        errors.append("❌ MISSING: 'sources' array is required")
    else:
        sources = plan_data['sources']
        if len(sources) == 0:
            errors.append("❌ NO SOURCES: At least one source must be cited")
        
        listed_source_ids = set()
        for i, source in enumerate(sources, 1):
            if not isinstance(source, dict):
                errors.append(f"❌ SOURCE {i}: Must be an object")
                continue
            
            if 'id' not in source:
                errors.append(f"❌ SOURCE {i}: Missing 'id' field")
            else:
                listed_source_ids.add(source['id'])
                if available_sources and source['id'] not in available_sources:
                    errors.append(f"❌ SOURCE {source['id']}: Not present in RAG context (available: {available_sources})")
            
            if 'title' not in source or not source['title'].strip():
                errors.append(f"❌ SOURCE {i}: Missing 'title' field")
            elif 'knowledge_base.txt' in source['title'].lower() or 'knowledge base reference' in source['title'].lower():
                errors.append(f"❌ SOURCE {i}: Using generic title '{source['title']}' - must use exact title from RAG context")
            elif available_sources and source.get('id') in rag_source_map:
                expected_title = rag_source_map[source['id']]
                if source['title'].strip() != expected_title:
                    errors.append(
                        f"❌ SOURCE {source['id']}: Title mismatch. Expected exact RAG title '{expected_title}', got '{source['title']}'"
                    )

    # Cross-check: all cited source IDs should be listed in sources[]
    cited_ids = set()
    for outcome in plan_data.get('outcomes', []) if isinstance(plan_data.get('outcomes', []), list) else []:
        if isinstance(outcome, dict) and isinstance(outcome.get('source'), int):
            cited_ids.add(outcome['source'])
    for strategy in plan_data.get('strategies', []) if isinstance(plan_data.get('strategies', []), list) else []:
        if isinstance(strategy, dict) and isinstance(strategy.get('source'), int):
            cited_ids.add(strategy['source'])
    for advice_item in plan_data.get('advice', []) if isinstance(plan_data.get('advice', []), list) else []:
        if isinstance(advice_item, dict) and isinstance(advice_item.get('source'), int):
            cited_ids.add(advice_item['source'])

    listed_ids = set()
    if isinstance(plan_data.get('sources'), list):
        for source in plan_data.get('sources', []):
            if isinstance(source, dict) and isinstance(source.get('id'), int):
                listed_ids.add(source['id'])

    missing_from_sources = cited_ids - listed_ids
    if missing_from_sources:
        errors.append(f"❌ SOURCES LIST INCOMPLETE: Cited source IDs not listed in sources[]: {sorted(missing_from_sources)}")

    # Safety triage requirement: if safety concerns detected, response must include safety_alert
    if safety_analysis and safety_analysis.get("has_concerns"):
        safety_alert = plan_data.get("safety_alert")
        if not isinstance(safety_alert, dict):
            errors.append("❌ SAFETY ALERT MISSING: safety_alert object is required when regression/urgent concerns are detected")
        else:
            for field in ["level", "title", "message", "recommended_action", "matched_patterns"]:
                if field not in safety_alert:
                    errors.append(f"❌ SAFETY ALERT: Missing '{field}' field")
    
    # === BUILD REPORT ===
    report_lines = []
    
    if errors:
        report_lines.append("❌ Plan has critical errors:\n")
        report_lines.extend(f"  {err}" for err in errors)
    
    if warnings:
        report_lines.append("\n⚠️ Quality warnings:\n")
        report_lines.extend(f"  {warn}" for warn in warnings)
    
    if not errors and not warnings:
        report_lines.append("✅ All validation checks passed")
    
    is_valid = len(errors) == 0
    report = "\n".join(report_lines)
    
    return is_valid, report


def verify_critical_requirements(
    plan_data: Dict,
    rag_context: str = "",
    safety_analysis: Optional[Dict] = None,
) -> Tuple[bool, List[str]]:
    """
    Check minimum critical requirements (faster check for early rejection).
    
    Args:
        plan_data: Parsed JSON plan data
        rag_context: RAGcontext for source validation
        
    Returns:
        Tuple of (requirements_met, list_of_failed_requirements)
    """
    failed = []
    
    # Check key arrays exist
    if 'outcomes' not in plan_data or not isinstance(plan_data['outcomes'], list):
        failed.append("Missing 'outcomes' array")
    elif len(plan_data['outcomes']) < 2:
        failed.append(f"Only {len(plan_data['outcomes'])} outcome(s) - minimum 2 required")
    else:
        for idx, outcome in enumerate(plan_data['outcomes'], 1):
            if not isinstance(outcome, dict):
                failed.append(f"Outcome {idx} must be an object")
                continue
            if not outcome.get('text'):
                failed.append(f"Outcome {idx} missing 'text'")
            if 'source' not in outcome:
                failed.append(f"Outcome {idx} missing 'source'")
    
    if 'strategies' not in plan_data or not isinstance(plan_data['strategies'], list):
        failed.append("Missing 'strategies' array")
    elif len(plan_data['strategies']) < 3:
        failed.append(f"Only {len(plan_data['strategies'])} strategy(ies) - minimum 3 required")
    else:
        for idx, strategy in enumerate(plan_data['strategies'], 1):
            if not isinstance(strategy, dict):
                failed.append(f"Strategy {idx} must be an object")
                continue
            for field in ['name', 'description', 'examples', 'routine', 'source']:
                if field not in strategy:
                    failed.append(f"Strategy {idx} missing '{field}'")
            if 'description' in strategy and (not isinstance(strategy['description'], list) or not strategy['description']):
                failed.append(f"Strategy {idx} 'description' must be non-empty array")
            if 'examples' in strategy and (not isinstance(strategy['examples'], list) or not strategy['examples']):
                failed.append(f"Strategy {idx} 'examples' must be non-empty array")
    
    if 'advice' not in plan_data or not isinstance(plan_data['advice'], list):
        failed.append("Missing 'advice' array")
    elif len(plan_data['advice']) < 3:
        failed.append(f"Only {len(plan_data['advice'])} advice item(s) - minimum 3 required")
    else:
        for idx, item in enumerate(plan_data['advice'], 1):
            if not isinstance(item, dict):
                failed.append(f"Advice {idx} must be an object")
                continue
            if not item.get('text'):
                failed.append(f"Advice {idx} missing 'text'")
            if 'source' not in item:
                failed.append(f"Advice {idx} missing 'source'")
    
    if 'sources' not in plan_data or not isinstance(plan_data['sources'], list):
        failed.append("Missing 'sources' array")
    elif len(plan_data['sources']) == 0:
        failed.append("No sources listed")
    else:
        source_ids = set()
        for idx, source in enumerate(plan_data['sources'], 1):
            if not isinstance(source, dict):
                failed.append(f"Source {idx} must be an object")
                continue
            if 'id' not in source:
                failed.append(f"Source {idx} missing 'id'")
            else:
                source_ids.add(source['id'])
            if not source.get('title'):
                failed.append(f"Source {idx} missing 'title'")

        cited_ids = set()
        for outcome in plan_data.get('outcomes', []):
            if isinstance(outcome, dict) and isinstance(outcome.get('source'), int):
                cited_ids.add(outcome['source'])
        for strategy in plan_data.get('strategies', []):
            if isinstance(strategy, dict) and isinstance(strategy.get('source'), int):
                cited_ids.add(strategy['source'])
        for item in plan_data.get('advice', []):
            if isinstance(item, dict) and isinstance(item.get('source'), int):
                cited_ids.add(item['source'])

        missing = cited_ids - source_ids
        if missing:
            failed.append(f"Missing cited sources in sources[]: {sorted(missing)}")
    
    if safety_analysis and safety_analysis.get("has_concerns"):
        safety_alert = plan_data.get("safety_alert")
        if not isinstance(safety_alert, dict):
            failed.append("Missing safety_alert for detected regression/urgent concern")
        else:
            for field in ["level", "title", "message", "recommended_action", "matched_patterns"]:
                if field not in safety_alert:
                    failed.append(f"safety_alert missing '{field}'")

    requirements_met = len(failed) == 0
    return requirements_met, failed
