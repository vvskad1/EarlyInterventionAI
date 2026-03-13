"""
Utility functions for JSON repair and other helpers.
"""
import json
import re
from typing import Dict, Any


def extract_or_repair_json(text: str) -> Dict[str, Any]:
    """
    Attempt to extract or repair JSON from potentially malformed text.
    
    Strategy:
    1. Try direct JSON parsing
    2. Extract last {...} block with regex
    3. Final fallback: return empty structure with expected keys
    
    Args:
        text: Raw text that should contain JSON
        
    Returns:
        Parsed dictionary with at least the expected structure
    """
    def is_plan_payload(candidate: Any) -> bool:
        return isinstance(candidate, dict) and ('outcomes' in candidate or 'Intervention_Plan' in candidate)

    def try_parse(candidate_text: str) -> Dict[str, Any] | None:
        try:
            parsed_candidate = json.loads(candidate_text)
            if is_plan_payload(parsed_candidate):
                return parsed_candidate
        except json.JSONDecodeError:
            return None
        return None

    # Strategy 1: Direct parse
    parsed = try_parse(text)
    if parsed is not None:
        return parsed

    # Strategy 2: Strip fenced code block wrappers and retry
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        parsed = try_parse(cleaned)
        if parsed is not None:
            return parsed

    # Strategy 3: Parse text between first '{' and last '}'
    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        sliced = cleaned[first_brace:last_brace + 1]
        parsed = try_parse(sliced)
        if parsed is not None:
            return parsed

    # Strategy 4: Balanced-brace scan for top-level JSON objects
    candidates = []
    start_idx = None
    depth = 0
    in_string = False
    escaped = False
    for idx, ch in enumerate(cleaned):
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\\\':
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == '{':
            if depth == 0:
                start_idx = idx
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    candidates.append(cleaned[start_idx:idx + 1])
                    start_idx = None

    # Prefer larger candidates first
    candidates.sort(key=len, reverse=True)
    for candidate in candidates:
        parsed = try_parse(candidate)
        if parsed is not None:
            return parsed

    # Strategy 5: Attempt auto-closing truncated JSON from first '{' onward
    # Handles outputs cut off before final closing braces/brackets.
    first_brace = cleaned.find('{')
    if first_brace != -1:
        partial = cleaned[first_brace:]

        # Build repaired text by balancing object/array delimiters outside strings.
        stack = []
        in_string = False
        escaped = False
        repaired_chars = []

        for ch in partial:
            repaired_chars.append(ch)

            if in_string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch in '{[':
                stack.append(ch)
            elif ch == '}' and stack and stack[-1] == '{':
                stack.pop()
            elif ch == ']' and stack and stack[-1] == '[':
                stack.pop()

        repaired = "".join(repaired_chars).rstrip()

        # Remove trailing comma if output was truncated at item boundary.
        repaired = re.sub(r',\s*$', '', repaired)

        # Close remaining open containers in reverse order.
        closers = []
        while stack:
            opener = stack.pop()
            closers.append('}' if opener == '{' else ']')
        repaired = repaired + "".join(closers)

        parsed = try_parse(repaired)
        if parsed is not None:
            return parsed

    # Strategy 6: Final fallback - return minimal valid structure for new structured format
    fallback = {
        "outcomes": [],
        "strategies": [],
        "advice": [],
        "sources": []
    }
    
    return fallback
    
    # Try to extract any meaningful content from the text if it exists
    if text.strip() and len(text.strip()) > 50:
        # If it looks like markdown content already, use it
        if '##' in text or '###' in text:
            fallback["Intervention_Plan"] = text
    
    return fallback


def ensure_json_keys(data: Dict[str, Any], required_keys: list) -> Dict[str, Any]:
    """
    Ensure a dictionary contains all required keys, adding defaults if missing.
    
    Supports both new format (Intervention_Plan) and legacy format (Outcomes, Strategies, etc.).
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
        
    Returns:
        Dictionary with all required keys present
    """
    # Check if using new format
    if 'Intervention_Plan' in required_keys:
        if 'Intervention_Plan' not in data:
            data['Intervention_Plan'] = """## Intervention Plan

### 🎯 Outcomes
(Default content - key was missing)

### 🔧 Strategies
(Default content - key was missing)

### 💡 Advice for Parents
(Default content - key was missing)

### 📚 Sources
No sources available."""
        return data
    
    # Legacy format support
    for key in required_keys:
        if key not in data:
            data[key] = ""
    return data


def extract_excerpts_from_rag_context(rag_context: str) -> Dict[int, str]:
    """
    Extract source excerpts from RAG context string.
    
    Args:
        rag_context: The RAG context string with [Source N] labels and EXCERPT lines
        
    Returns:
        Dictionary mapping source_id -> excerpt text
    """
    excerpts = {}
    
    # Pattern to match [Source N] followed by EXCERPT: "..."
    # Use DOTALL to handle multi-line
    pattern = r'\[Source\s+(\d+)\].*?EXCERPT:\s*"([^"]+)"'
    
    matches = re.findall(pattern, rag_context, re.DOTALL | re.IGNORECASE)
    
    for source_num, excerpt_text in matches:
        excerpts[int(source_num)] = excerpt_text.strip()
    
    return excerpts


def inject_excerpts_into_json(plan_data: Dict, rag_context: str) -> Dict:
    """
    Inject actual source excerpts into structured JSON plan.
    
    Args:
        plan_data: The generated intervention plan as JSON dict
        rag_context: The RAG context string with excerpts
        
    Returns:
        Modified plan with excerpts injected into sources array
    """
    # Extract excerpts from RAG context
    excerpts = extract_excerpts_from_rag_context(rag_context)
    
    if not excerpts or 'sources' not in plan_data:
        return plan_data  # No excerpts or no sources array
    
    # Inject excerpts into each source
    for source in plan_data['sources']:
        if 'id' in source and source['id'] in excerpts:
            source['excerpt'] = excerpts[source['id']]
    
    return plan_data


def normalize_sources_from_rag_context(plan_data: Dict, rag_context: str) -> Dict:
    """
    Normalize sources[] to exact [Source N] titles from RAG context.

    This prevents LLM truncation/abbreviation from failing strict title validation.
    Also ensures all cited source IDs exist in sources[].
    """
    if not isinstance(plan_data, dict) or not rag_context:
        return plan_data

    source_map = {}
    pattern = r'\[Source\s+(\d+)\]\s*-\s*(.+)'
    for source_num, title in re.findall(pattern, rag_context):
        cleaned_title = title.strip().split('\n')[0].strip()
        source_map[int(source_num)] = cleaned_title

    if not source_map:
        return plan_data

    # Ensure sources list exists
    if not isinstance(plan_data.get('sources'), list):
        plan_data['sources'] = []

    # Normalize existing source titles
    seen_ids = set()
    normalized_sources = []
    for source in plan_data.get('sources', []):
        if not isinstance(source, dict):
            continue
        source_id = source.get('id')
        if not isinstance(source_id, int):
            continue
        seen_ids.add(source_id)

        normalized_sources.append({
            'id': source_id,
            'title': source_map.get(source_id, source.get('title', '')).strip(),
            'excerpt': source.get('excerpt', ''),
        })

    # Add any cited IDs missing from sources list
    cited_ids = set()
    for outcome in plan_data.get('outcomes', []) if isinstance(plan_data.get('outcomes'), list) else []:
        if isinstance(outcome, dict) and isinstance(outcome.get('source'), int):
            cited_ids.add(outcome['source'])
    for strategy in plan_data.get('strategies', []) if isinstance(plan_data.get('strategies'), list) else []:
        if isinstance(strategy, dict) and isinstance(strategy.get('source'), int):
            cited_ids.add(strategy['source'])
    for advice in plan_data.get('advice', []) if isinstance(plan_data.get('advice'), list) else []:
        if isinstance(advice, dict) and isinstance(advice.get('source'), int):
            cited_ids.add(advice['source'])

    existing_ids = {src['id'] for src in normalized_sources if isinstance(src.get('id'), int)}
    for source_id in sorted(cited_ids):
        if source_id not in existing_ids:
            normalized_sources.append({
                'id': source_id,
                'title': source_map.get(source_id, f'Source {source_id}'),
                'excerpt': '',
            })

    plan_data['sources'] = normalized_sources
    return plan_data


def sanitize_vocabulary_count_outcomes(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rewrite disallowed vocabulary-count outcomes into functional communication outcomes.

    This keeps the plan clinically aligned with validator policy while avoiding
    repeated retry failures when LLM insists on "X words" targets.
    """
    if not isinstance(plan_data, dict) or not isinstance(plan_data.get('outcomes'), list):
        return plan_data

    replacements = [
        (r'\buse\s+at\s+least\s+\d+(?:\s*[-–]\s*\d+)?\s+words?\b', 'use gestures, word approximations, or single words'),
        (r'\buse\s+\d+(?:\s*[-–]\s*\d+)?\s+words?\b', 'use gestures, word approximations, or single words'),
        (r'\buse\s+(?:an?\s+)?\d+(?:\s*[-–]\s*\d+)?\s+words?\b', 'use gestures, word approximations, or single words'),
        (r'\buse\s+at\s+least\s+\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+phrases?\b', 'use functional word combinations or gesture+word combinations'),
        (r'\buse\s+\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+phrases?\b', 'use functional word combinations or gesture+word combinations'),
        (r'\buse\s+(?:an?\s+)?\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+phrases?\b', 'use functional word combinations or gesture+word combinations'),
        (r'\buse\s+\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+sentences?\b', 'use functional communication attempts in routines'),
        (r'\buse\s+(?:an?\s+)?\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+sentences?\b', 'use functional communication attempts in routines'),
        (r'\bsay\s+at\s+least\s+\d+(?:\s*[-–]\s*\d+)?\s+words?\b', 'use a functional word, word approximation, or gesture'),
        (r'\bsay\s+\d+(?:\s*[-–]\s*\d+)?\s+words?\b', 'use a functional word, word approximation, or gesture'),
        (r'\bsay\s+\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+phrases?\b', 'use a functional communication attempt (gesture, single word, or word combination)'),
        (r'\bsay\s+(?:an?\s+)?\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+phrases?\b', 'use a functional communication attempt (gesture, single word, or word combination)'),
        (r'\b\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+phrases?\b', 'functional communication attempts'),
        (r'\b\d+(?:\s*[-–]\s*\d+)?\s*[-\s]*word\s+sentences?\b', 'functional communication attempts'),
        (r'\bincrease\s+vocabulary\s+to\s+\d+\b', 'increase functional communication attempts in routines'),
        (r'\bvocabulary\s+of\s+\d+\b', 'functional communication in routines'),
    ]

    for outcome in plan_data['outcomes']:
        if not isinstance(outcome, dict) or not isinstance(outcome.get('text'), str):
            continue

        updated_text = outcome['text']
        for pattern, replacement in replacements:
            updated_text = re.sub(pattern, replacement, updated_text, flags=re.IGNORECASE)

        # Cleanup duplicate spacing introduced by replacements
        updated_text = re.sub(r'\s{2,}', ' ', updated_text).strip()
        outcome['text'] = updated_text

    return plan_data


def enrich_emotional_regulation_content(
    plan_data: Dict[str, Any],
    notes_text: str = "",
    selected_domains: Any = None,
) -> Dict[str, Any]:
    """
    Deterministically enrich plans for tantrum/transition emotional-regulation cases.

    Adds one measurable emotional regulation outcome and one co-regulation strategy if
    the case context suggests transition distress/tantrums and content is missing.
    """
    if not isinstance(plan_data, dict):
        return plan_data

    notes_lower = (notes_text or "").lower()
    domain_tokens = []
    if isinstance(selected_domains, list):
        domain_tokens = [str(d).lower() for d in selected_domains]
    elif isinstance(selected_domains, str):
        domain_tokens = [token.strip().lower() for token in selected_domains.split(',')]

    has_reg_domain = any(token in {"social", "emotional regulation", "adaptive", "social interaction"} for token in domain_tokens)
    has_transition_distress = any(token in notes_lower for token in ["tantrum", "transition", "meltdown", "frustrat", "upset"])

    if not (has_reg_domain or has_transition_distress):
        return plan_data

    if not isinstance(plan_data.get('outcomes'), list):
        plan_data['outcomes'] = []
    if not isinstance(plan_data.get('strategies'), list):
        plan_data['strategies'] = []
    if not isinstance(plan_data.get('advice'), list):
        plan_data['advice'] = []

    # Pick a usable source id
    source_id = 1
    if isinstance(plan_data.get('sources'), list):
        for src in plan_data['sources']:
            if isinstance(src, dict) and isinstance(src.get('id'), int):
                source_id = src['id']
                break

    # Ensure at least one explicit emotional regulation outcome
    outcome_text_all = " ".join(
        g.get('text', '') for g in plan_data['outcomes'] if isinstance(g, dict)
    ).lower()
    has_reg_outcome = any(token in outcome_text_all for token in ["tantrum", "transition", "calm", "co-reg", "emotion"])

    if not has_reg_outcome:
        plan_data['outcomes'].append({
            "text": "During transitions, child will use a supported calming strategy (e.g., visual cue, comfort object, or co-regulated breathing) and return to a calm state within 3 minutes in 4 out of 5 opportunities across 2 weeks.",
            "source": source_id,
        })

    # Ensure at least one explicit co-regulation strategy
    strategy_text_all = " ".join(
        " ".join([
            str(s.get('name', '')),
            " ".join(s.get('description', []) if isinstance(s.get('description'), list) else []),
            " ".join(s.get('examples', []) if isinstance(s.get('examples'), list) else []),
            str(s.get('routine', '')),
        ])
        for s in plan_data['strategies'] if isinstance(s, dict)
    ).lower()
    has_reg_strategy = any(token in strategy_text_all for token in ["transition warning", "co-reg", "calm", "emotion label", "visual schedule"])

    if not has_reg_strategy:
        plan_data['strategies'].append({
            "name": "Support Co-Regulation During Transitions",
            "description": [
                "Provide predictable transition warnings and visual cues before changes in activity.",
                "Use co-regulation by naming emotions, staying close, and guiding a brief calming routine."
            ],
            "examples": [
                "Give a 2-minute and 30-second countdown before cleanup or moving activities.",
                "Use emotion words: 'You're upset; I'll help you calm your body.'",
                "Offer a comfort object and model one slow breath together before transitioning."
            ],
            "routine": "Use at every major transition (play to meal, outing to home, bedtime), daily",
            "source": source_id,
        })

    # Ensure advice includes emotion labeling / validation
    advice_text_all = " ".join(a.get('text', '') for a in plan_data['advice'] if isinstance(a, dict)).lower()
    has_validation_advice = any(token in advice_text_all for token in ["validate", "emotion", "name feelings", "co-reg"]) 
    if not has_validation_advice:
        plan_data['advice'].append({
            "text": "Validate your child's feelings during transitions and model simple emotion words ('mad', 'sad', 'help') while guiding calm-down routines.",
            "source": source_id,
        })

    return plan_data


def inject_excerpts_into_sources_section(plan_text: str, rag_context: str) -> str:
    """
    Post-process the generated plan to inject actual source excerpts into the Sources section.
    
    This makes sources transparent and verifiable by showing actual text from each source.
    
    Args:
        plan_text: The generated intervention plan markdown
        rag_context: The RAG context string with excerpts
        
    Returns:
        Modified plan with excerpts injected into Sources section
    """
    # Extract excerpts from RAG context
    excerpts = extract_excerpts_from_rag_context(rag_context)
    
    if not excerpts:
        return plan_text  # No excerpts found, return original
    
    # Find the Sources section
    sources_pattern = r'(###\s*📚\s*Sources.*?)(?=###|\Z)'
    sources_match = re.search(sources_pattern, plan_text, re.DOTALL | re.IGNORECASE)
    
    if not sources_match:
        return plan_text  # No Sources section found
    
    sources_section = sources_match.group(1)
    
    # Find each source listing and inject excerpt
    # Pattern: - Source N: Title...
    modified_sources = sources_section
    injections_count = 0
    
    for source_id, excerpt in sorted(excerpts.items()):
        # Match "- Source N:" or "- **Source N**:"
        source_pattern = rf'(-\s*\*{{0,2}}Source\s+{source_id}\*{{0,2}}:\s*[^\n]+)'
        
        def add_excerpt(match):
            nonlocal injections_count
            source_line = match.group(1)
            # Check if excerpt already exists (avoid duplicates)
            if '  >' in source_line or '  > "' in match.group(0):
                return match.group(0)
            # Add excerpt blockquote on next line
            injections_count += 1
            return f'{source_line}\n  > "{excerpt}"'
        
        modified_sources = re.sub(
            source_pattern,
            add_excerpt,
            modified_sources,
            count=1
        )
    
    # Replace the original sources section with modified one
    modified_plan = plan_text[:sources_match.start()] + modified_sources + plan_text[sources_match.end():]
    
    return modified_plan

def remove_hallucinated_source_citations(plan_text: str, rag_context: str) -> str:
    """
    Remove citations to sources that don't exist in the RAG context.
    
    Args:
        plan_text: The intervention plan text
        rag_context: The RAG context with valid source labels
        
    Returns:
        Plan with hallucinated citations removed
    """
    import re
    
    # Extract valid source IDs from RAG context
    valid_sources = set()
    source_pattern = r'\[Source\s+(\d+)\]'
    matches = re.findall(source_pattern, rag_context)
    for match in matches:
        valid_sources.add(int(match))
    
    if not valid_sources:
        return plan_text
    
    # Remove inline citations to invalid sources: (Source N) or (Source N, Source M)
    def filter_inline_citations(match):
        full_match = match.group(0)
        # Extract all source numbers from the citation
        cited_sources = re.findall(r'Source\s+(\d+)', full_match)
        valid_cited = [f"Source {s}" for s in cited_sources if int(s) in valid_sources]
        
        if not valid_cited:
            return ""  # Remove entire citation if all sources invalid
        elif len(valid_cited) == len(cited_sources):
            return full_match  # Keep as-is if all valid
        else:
            # Reconstruct with only valid sources
            return f"({', '.join(valid_cited)})"
    
    # Pattern matches: (Source 1), (Source 2, Source 3), etc.
    plan_text = re.sub(r'\(Source\s+\d+(?:,\s*Source\s+\d+)*\)', filter_inline_citations, plan_text)
    
    # Remove source listings from Sources section for invalid sources
    max_source = max(valid_sources)
    for i in range(1, max_source + 20):  # Check up to max + 20
        if i not in valid_sources:
            # Remove lines like "- Source N: ..." including any following excerpt
            pattern = rf'^-\s*Source\s+{i}:.*?(?=^-\s*Source|\Z)'
            plan_text = re.sub(pattern, '', plan_text, flags=re.MULTILINE | re.DOTALL)
    
    return plan_text