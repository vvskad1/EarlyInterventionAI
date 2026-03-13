"""
Output validation for Early Intervention plan quality.

Implements pre-output checks to catch common reliability issues:
- Vocabulary count outcomes
- Unexplained frameworks/acronyms
- Unrealistic developmental targets
- Non-functional outcome phrasing
- Missing citations and sources
- Insufficient content in required sections
- Source hallucination and URL fabrication
"""
import re
from typing import Dict, List, Tuple, Optional, Set


class PlanValidator:
    """Validates intervention plan outputs for EI best practices."""
    
    # Patterns that indicate problematic outcome phrasing
    VOCAB_COUNT_PATTERNS = [
        r'\b(\d+)[\s-]+words?\b',           # "20 words", "5 words"
        r'\bvocabulary\s+(?:to|of)\s+\d+',  # "vocabulary to 50"
        r'\bincrease.*vocabulary.*\d+',     # "increase vocabulary to X"
        r'\bsay\s+\d+\s+words?',            # "say 10 words"
    ]
    
    # Sentence length targets (problematic for young children)
    SENTENCE_LENGTH_PATTERNS = [
        r'\b(\d+)[\s-]+word\s+sentences?',  # "5-word sentences"
        r'\b(\d+)[\s-]+word\s+phrases?',    # "3-word phrases"
    ]
    
    # Framework/acronym patterns (need explanation)
    FRAMEWORK_PATTERNS = [
        r'\bSS-OO-PP-RR\b',
        r'\b[A-Z]{2,}-[A-Z]{2,}\b',         # Any hyphenated acronyms
        r'\b(?:[A-Z]\.){2,}\b',             # A.B.C. style
    ]
    
    # Assessment-focused language (not functional)
    ASSESSMENT_LANGUAGE = [
        r'\btest\b',
        r'\bperformance\b',
        r'\bmilestone\b',
        r'\bdelay\b',
    ]
    
    @classmethod
    def extract_section(cls, content: str, section_name: str) -> Optional[str]:
        """
        Extract a specific section from markdown content.
        
        Args:
            content: Full markdown content
            section_name: Name of section to extract (e.g., "Outcomes", "Strategies")
            
        Returns:
            Extracted section text or None if not found
        """
        # Match section headers with various emoji patterns
        pattern = rf'###\s*[🎯🔧💡📚]?\s*{re.escape(section_name)}\s*\n(.*?)(?=###|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    @classmethod
    def count_bullet_points(cls, text: str) -> int:
        """Count bullet points in text."""
        if not text:
            return 0
        lines = text.split('\n')
        return len([line for line in lines if line.strip().startswith(('-', '•', '*'))])
    
    @classmethod
    def check_citations(cls, text: str) -> Tuple[bool, int]:
        """
        Check if text contains inline citations.
        
        Returns:
            Tuple of (has_citations, citation_count)
        """
        citation_pattern = r'\(Source\s+\d+(?:,\s*Source\s+\d+)*\)'
        citations = re.findall(citation_pattern, text, re.IGNORECASE)
        return len(citations) > 0, len(citations)
    
    @classmethod
    def validate_outcomes(cls, outcomes_text: str, age_months: int = None) -> Tuple[bool, List[str]]:
        """
        Validate outcome quality against EI best practices.
        
        Args:
            outcomes_text: The outcomes section text to validate
            age_months: Child's age in months (optional, for age-specific checks)
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        if not outcomes_text:
            warnings.append("❌ MISSING SECTION: Outcomes section is empty or missing")
            return False, warnings
        
        # Check for minimum number of outcomes (at least 2)
        num_outcomes = cls.count_bullet_points(outcomes_text)
        if num_outcomes < 2:
            warnings.append(
                f"❌ INSUFFICIENT OUTCOMES: Only {num_outcomes} outcome(s) provided. Minimum 2-3 required."
            )
        
        # Check for citations in outcomes
        has_citations, citation_count = cls.check_citations(outcomes_text)
        if not has_citations:
            warnings.append(
                "❌ MISSING CITATIONS: Outcomes must include inline citations to RAG sources (e.g., 'Source 1')"
            )
        
        # Check for vocabulary count outcomes
        for pattern in cls.VOCAB_COUNT_PATTERNS:
            if re.search(pattern, outcomes_text, re.IGNORECASE):
                warnings.append(
                    "❌ VOCABULARY COUNT OUTCOME: Outcomes should focus on functional use "
                    "(request, label, comment) rather than word counts"
                )
                break
        
        # Check for sentence length targets
        for pattern in cls.SENTENCE_LENGTH_PATTERNS:
            match = re.search(pattern, outcomes_text, re.IGNORECASE)
            if match:
                sentence_length = int(match.group(1))
                if age_months and age_months < 24 and sentence_length > 2:
                    warnings.append(
                        f"❌ UNREALISTIC TARGET: {sentence_length}-word sentences "
                        f"for {age_months}-month-old is developmentally inappropriate"
                    )
                elif sentence_length > 3:
                    warnings.append(
                        "⚠️ SENTENCE LENGTH: Consider if this target is appropriate "
                        "for child's current baseline"
                    )
                break
        
        # Check for routine embedding
        routine_keywords = ['during', 'snack', 'play', 'diaper', 'bath', 'meal', 'dressing', 'routine']
        has_routine_context = any(keyword in outcomes_text.lower() for keyword in routine_keywords)
        if not has_routine_context:
            warnings.append(
                "⚠️ ROUTINE CONTEXT: Outcomes should specify routines/contexts "
                "(e.g., 'during snack and play')"
            )
        
        # Check for measurable criteria
        measurable_patterns = [
            r'\d+\s+(?:out of|of|/)\s+\d+',  # "4 out of 5", "3/5"
            r'\d+\s+seconds?',                # "10 seconds"
            r'\d+\s+times?',                  # "3 times"
        ]
        has_criterion = any(re.search(p, outcomes_text, re.IGNORECASE) for p in measurable_patterns)
        if not has_criterion:
            warnings.append(
                "⚠️ MEASURABILITY: Outcomes should include specific criteria "
                "(e.g., '4 out of 5 opportunities')"
            )
        
        is_valid = len([w for w in warnings if w.startswith('❌')]) == 0
        return is_valid, warnings
    
    @classmethod
    def validate_strategies(cls, strategies_text: str) -> Tuple[bool, List[str]]:
        """
        Validate strategies section for unexplained frameworks and jargon.
        
        Args:
            strategies_text: The strategies section text to validate
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        if not strategies_text:
            warnings.append("❌ MISSING SECTION: Strategies section is empty or missing")
            return False, warnings
        
        # Check for minimum number of strategies (at least 3)
        # Count "Strategy N:" patterns (both bold and non-bold formats)
        strategy_pattern = r'(?:\*\*)?Strategy\s+\d+:(?:\*\*)?'
        strategy_matches = re.findall(strategy_pattern, strategies_text)
        num_strategies = len(strategy_matches)
        
        if num_strategies < 3:
            warnings.append(
                f"❌ INSUFFICIENT STRATEGIES: Only {num_strategies} strategy(ies) provided. Minimum 3-5 required."
            )
        
        # Check for improperly formatted strategy headers (with asterisk prefix)
        improper_headers = re.findall(r'\*\s+Strategy\s+\d+:', strategies_text)
        if improper_headers:
            warnings.append(
                f"❌ FORMATTING ERROR: Strategy headers should NOT have asterisks before them. Found: {len(improper_headers)} improperly formatted header(s). "
                "Headers should be plain text: 'Strategy 1: Name' (not '* Strategy 1: Name')"
            )
        
        # Check if strategies are numbered properly (1, 2, 3, etc.)
        if num_strategies > 0:
            strategy_numbers = re.findall(r'Strategy\s+(\d+):', strategies_text)
            strategy_numbers = [int(n) for n in strategy_numbers]
            expected_sequence = list(range(1, num_strategies + 1))
            if strategy_numbers != expected_sequence:
                warnings.append(
                    f"⚠️ NUMBERING ERROR: Strategy numbers are not sequential. Found: {strategy_numbers}, Expected: {expected_sequence}. "
                    "Each strategy MUST start with 'Strategy N:' header where N starts at 1 and increments."
                )
            
            # Specific check for missing Strategy 1
            if 1 not in strategy_numbers and len(strategy_numbers) > 0:
                warnings.append(
                    f"❌ MISSING STRATEGY 1 HEADER: First strategy must have 'Strategy 1: [Name]' header. "
                    "Do not omit the header - every strategy needs its numbered title."
                )
        
        # Check for Examples sections (both bold and non-bold formats)
        has_examples = bool(re.search(r'(?:\*\s*\*\*)?Examples:(?:\*\*)?', strategies_text))
        if not has_examples:
            warnings.append(
                "⚠️ MISSING EXAMPLES: Strategies should include concrete examples for each strategy."
            )
        
        # Check for Routine sections (both bold and non-bold formats)
        has_routine = bool(re.search(r'(?:\*\s*\*\*)?Routine:(?:\*\*)?', strategies_text))
        if not has_routine:
            warnings.append(
                "⚠️ MISSING ROUTINE: Strategies should include routine/frequency suggestions for implementation."
            )
        
        # Check for introduction statement
        intro_patterns = [
            r'Based on the child\'s age',
            r'here are some strategies',
            r'support their development'
        ]
        has_intro = any(re.search(pattern, strategies_text, re.IGNORECASE) for pattern in intro_patterns)
        if not has_intro:
            warnings.append(
                "⚠️ MISSING INTRO: Strategies section should start with an introduction statement about the child's age and domain."
            )
        
        # Check for citations in strategies (at least some should be cited)
        has_citations, citation_count = cls.check_citations(strategies_text)
        if not has_citations:
            warnings.append(
                "⚠️ FEW CITATIONS: Strategies should include inline citations where applicable"
            )
        
        # Check for unexplained frameworks/acronyms
        for pattern in cls.FRAMEWORK_PATTERNS:
            matches = re.findall(pattern, strategies_text)
            if matches:
                for match in matches:
                    # Check if there's explanation nearby (within 100 chars)
                    match_pos = strategies_text.find(match)
                    context = strategies_text[max(0, match_pos-50):match_pos+150]
                    
                    # Simple heuristic: if acronym appears but not explained
                    # (no parentheses or colon nearby), flag it
                    if '(' not in context and ':' not in context[context.find(match):]:
                        warnings.append(
                            f"❌ UNEXPLAINED ACRONYM: '{match}' used without explanation. "
                            "Describe strategies in plain language or explain acronyms."
                        )
                        break
        
        # Check for assessment-focused language
        for pattern in cls.ASSESSMENT_LANGUAGE:
            if re.search(pattern, strategies_text, re.IGNORECASE):
                warnings.append(
                    "⚠️ ASSESSMENT LANGUAGE: Focus on functional participation "
                    "rather than testing/milestones"
                )
                break
        
        is_valid = len([w for w in warnings if w.startswith('❌')]) == 0
        return is_valid, warnings
    
    @classmethod
    def validate_advice(cls, advice_text: str) -> Tuple[bool, List[str]]:
        """
        Validate advice section for parent-friendly content.
        
        Args:
            advice_text: The advice section text to validate
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        if not advice_text:
            warnings.append("❌ MISSING SECTION: Advice for Parents section is empty or missing")
            return False, warnings
        
        # Check for minimum number of advice items (at least 4)
        num_advice = cls.count_bullet_points(advice_text)
        if num_advice < 4:
            warnings.append(
                f"❌ INSUFFICIENT ADVICE: Only {num_advice} advice item(s) provided. Minimum 4-6 required."
            )
        
        is_valid = len([w for w in warnings if w.startswith('❌')]) == 0
        return is_valid, warnings
    
    @classmethod
    def validate_sources(cls, sources_text: str, plan_content: str) -> Tuple[bool, List[str]]:
        """
        Validate sources section.
        
        Args:
            sources_text: The sources section text
            plan_content: Full plan content to check for citations
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        if not sources_text:
            warnings.append("❌ MISSING SOURCES: Sources section is required")
            return False, warnings
        
        # Check if sources section contains actual source listings
        # Support both formats: "- Source 1:" and "- **Source 1**:"
        source_pattern = r'-\s*\*{0,2}Source\s+\d+\*{0,2}:'
        sources_listed = re.findall(source_pattern, sources_text, re.IGNORECASE)
        
        if not sources_listed:
            # Check for the "no sources" disclaimer
            if "no" in sources_text.lower() and ("retrieved" in sources_text.lower() or "available" in sources_text.lower()):
                warnings.append(
                    "⚠️ NO SOURCES RETRIEVED: Plan acknowledges no sources were available"
                )
            else:
                warnings.append(
                    "❌ INVALID SOURCES FORMAT: Sources must be listed as '- Source 1: [title]' or '- **Source 1**: [title]'"
                )
        else:
            # Check if number of cited sources matches sources listed
            all_citations = re.findall(r'\(Source\s+(\d+)(?:,\s*Source\s+(\d+))*\)', plan_content, re.IGNORECASE)
            cited_numbers = set()
            for match in all_citations:
                for num in match:
                    if num:
                        cited_numbers.add(int(num))
            
            listed_numbers = set()
            for source_line in sources_listed:
                num_match = re.search(r'Source\s+(\d+)', source_line, re.IGNORECASE)
                if num_match:
                    listed_numbers.add(int(num_match.group(1)))
            
            # Check for orphaned citations
            orphaned = cited_numbers - listed_numbers
            if orphaned:
                warnings.append(
                    f"⚠️ ORPHANED CITATIONS: Citations {orphaned} appear in text but not listed in Sources"
                )
            
            # Check for unused sources
            unused = listed_numbers - cited_numbers
            if unused:
                warnings.append(
                    f"⚠️ UNUSED SOURCES: Sources {unused} listed but not cited in text"
                )
        
        is_valid = len([w for w in warnings if w.startswith('❌')]) == 0
        return is_valid, warnings
    
    @staticmethod
    def extract_source_ids_from_context(rag_context: str) -> Set[int]:
        """
        Extract source IDs from RAG context.
        
        The RAG context contains sources in format: [Source N]
        This function extracts all N values to create whitelist.
        
        Args:
            rag_context: RAG context string with [Source N] labels
            
        Returns:
            Set of valid source ID numbers
        """
        pattern = r'\[Source\s+(\d+)\]'
        matches = re.findall(pattern, rag_context, re.IGNORECASE)
        return {int(num) for num in matches}
    
    @classmethod
    def validate_source_whitelist(
        cls,
        sources_text: str,
        plan_content: str,
        allowed_source_ids: Set[int]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all sources in the plan come ONLY from retrieved RAG sources.
        
        This is the CRITICAL anti-hallucination check:
        - Ensures LLM only cites retrieved sources
        - Detects URL fabrication
        - Prevents external reference invention
        
        Args:
            sources_text: The Sources section from the generated plan
            plan_content: Full plan content for citation checking
            allowed_source_ids: Set of source IDs that were in the RAG context
            
        Returns:
            Tuple of (is_valid, list_of_critical_errors)
        """
        errors = []
        
        if not sources_text:
            errors.append("❌ CRITICAL: Sources section missing entirely")
            return False, errors
        
        # === CHECK 1: URL Detection ===
        # Detect any URL patterns (http://, https://, www., markdown links)
        url_patterns = [
            r'https?://',           # http:// or https://
            r'www\.',               # www.
            r'\[.*?\]\(.*?\)',      # Markdown link syntax [text](url)
            r'doi\.org',            # DOI links
            r'researchgate\.net',   # ResearchGate
        ]
        
        for pattern in url_patterns:
            if re.search(pattern, sources_text, re.IGNORECASE):
                errors.append(
                    f"❌ CRITICAL: URL/LINK DETECTED in Sources section - Model is hallucinating external references"
                )
                break
        
        # === CHECK 2: Source ID Whitelist Validation ===
        # Extract all Source IDs listed in the Sources section
        source_pattern = r'-\s*Source\s+(\d+):'
        listed_sources = re.findall(source_pattern, sources_text, re.IGNORECASE)
        
        if not listed_sources:
            # Check if it's the acceptable "no sources" case
            if "no" in sources_text.lower() and "retrieved" in sources_text.lower():
                # This is OK if there were genuinely no sources
                if not allowed_source_ids:
                    return True, []
                else:
                    errors.append(
                        "❌ CRITICAL: Plan claims no sources retrieved, but sources WERE provided"
                    )
                    return False, errors
            else:
                errors.append(
                    "❌ CRITICAL: Sources section has no properly formatted source listings"
                )
                return False, errors
        
        # Check each listed source against whitelist
        hallucinated_sources = []
        for source_id_str in listed_sources:
            source_id = int(source_id_str)
            if source_id not in allowed_source_ids:
                hallucinated_sources.append(source_id)
        
        if hallucinated_sources:
            errors.append(
                f"❌ CRITICAL: HALLUCINATED SOURCES DETECTED - "
                f"Sources {hallucinated_sources} were NOT in the retrieved RAG context. "
                f"Only {sorted(allowed_source_ids)} were provided."
            )
        
        # === CHECK 3: Verify Citations Match Retrieved Sources ===
        # Extract all citations from plan content
        citation_pattern = r'\(Source\s+(\d+)(?:,\s*Source\s+(\d+))*\)'
        all_citations = re.findall(citation_pattern, plan_content, re.IGNORECASE)
        cited_ids = set()
        for match in all_citations:
            for num_str in match:
                if num_str:
                    cited_ids.add(int(num_str))
        
        # Check if any citations reference sources not in RAG context
        hallucinated_citations = cited_ids - allowed_source_ids
        if hallucinated_citations:
            errors.append(
                f"❌ CRITICAL: HALLUCINATED CITATIONS - "
                f"Plan cites {hallucinated_citations} which were NOT in retrieved context"
            )
        
        # === CHECK 4: Generic/Invented Source Names ===
        # Check for forbidden generic labels
        forbidden_patterns = [
            r'general\s+(?:ei|early intervention)\s+principles',
            r'aap\s+guidelines',
            r'cdc\s+milestones',
            r'best\s+practices',
            r'research-based',
            r'evidence-based\s+practice',
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, sources_text, re.IGNORECASE):
                errors.append(
                    f"❌ CRITICAL: Generic/invented source label detected - Must use only numbered sources from RAG"
                )
                break
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @classmethod
    def validate_plan(cls, plan_json: Dict, age_months: int = None) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate complete intervention plan with markdown structure.
        
        Args:
            plan_json: The plan response JSON with Intervention_Plan key
            age_months: Child's age in months (optional)
            
        Returns:
            Tuple of (is_valid, warnings_by_section)
        """
        all_warnings = {}
        
        # Check if plan has the expected structure
        if 'Intervention_Plan' not in plan_json:
            # Legacy format support
            if 'Outcomes' in plan_json:
                return cls._validate_legacy_format(plan_json, age_months)
            
            all_warnings['Structure'] = ["❌ MISSING KEY: Response must contain 'Intervention_Plan' key"]
            return False, all_warnings
        
        content = plan_json['Intervention_Plan']
        
        # Check for main heading
        if not re.search(r'##\s*Intervention Plan', content, re.IGNORECASE):
            all_warnings['Structure'] = ["⚠️ MISSING HEADING: Should start with '## Intervention Plan'"]
        
        # Extract and validate each section
        outcomes_text = cls.extract_section(content, 'Outcomes')
        strategies_text = cls.extract_section(content, 'Strategies')
        advice_text = cls.extract_section(content, 'Advice for Parents')
        sources_text = cls.extract_section(content, 'Sources')
        
        # Validate Outcomes
        if outcomes_text is not None:
            outcomes_valid, outcomes_warnings = cls.validate_outcomes(outcomes_text, age_months)
            if outcomes_warnings:
                all_warnings['Outcomes'] = outcomes_warnings
        else:
            all_warnings['Outcomes'] = ["❌ MISSING SECTION: Outcomes section not found"]
        
        # Validate Strategies
        if strategies_text is not None:
            strategies_valid, strategies_warnings = cls.validate_strategies(strategies_text)
            if strategies_warnings:
                all_warnings['Strategies'] = strategies_warnings
        else:
            all_warnings['Strategies'] = ["❌ MISSING SECTION: Strategies section not found"]
        
        # Validate Advice
        if advice_text is not None:
            advice_valid, advice_warnings = cls.validate_advice(advice_text)
            if advice_warnings:
                all_warnings['Advice for Parents'] = advice_warnings
        else:
            all_warnings['Advice for Parents'] = ["❌ MISSING SECTION: Advice for Parents section not found"]
        
        # Validate Sources
        if sources_text is not None:
            sources_valid, sources_warnings = cls.validate_sources(sources_text, content)
            if sources_warnings:
                all_warnings['Sources'] = sources_warnings
        else:
            all_warnings['Sources'] = ["❌ MISSING SECTION: Sources section not found"]
        
        # Check if any critical errors (❌) exist
        critical_errors = []
        for section, warnings in all_warnings.items():
            critical_errors.extend([w for w in warnings if w.startswith('❌')])
        
        is_valid = len(critical_errors) == 0
        
        return is_valid, all_warnings
    
    @classmethod
    def _validate_legacy_format(cls, plan_json: Dict, age_months: int = None) -> Tuple[bool, Dict[str, List[str]]]:
        """Support for legacy format validation."""
        all_warnings = {}
        
        # Validate Outcomes
        if 'Outcomes' in plan_json:
            outcomes_valid, outcomes_warnings = cls.validate_outcomes(
                plan_json['Outcomes'],
                age_months
            )
            if goals_warnings:
                all_warnings['Goals'] = goals_warnings
        
        # Validate Strategies
        if 'Strategies' in plan_json:
            strategies_valid, strategies_warnings = cls.validate_strategies(
                plan_json['Strategies']
            )
            if strategies_warnings:
                all_warnings['Strategies'] = strategies_warnings
        
        # Check if any critical errors (❌) exist
        critical_errors = []
        for section, warnings in all_warnings.items():
            critical_errors.extend([w for w in warnings if w.startswith('❌')])
        
        is_valid = len(critical_errors) == 0
        
        return is_valid, all_warnings
    
    @classmethod
    def get_validation_report(cls, plan_json: Dict, age_months: int = None) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            plan_json: The plan response JSON
            age_months: Child's age in months (optional)
            
        Returns:
            Formatted validation report string
        """
        is_valid, warnings = cls.validate_plan(plan_json, age_months)
        
        if is_valid and not warnings:
            return "✅ Plan passes validation checks"
        
        report = []
        if is_valid:
            report.append("⚠️ Plan passes critical checks but has quality warnings:\n")
        else:
            report.append("❌ Plan has critical reliability issues:\n")
        
        for section, section_warnings in warnings.items():
            report.append(f"\n[{section}]")
            for warning in section_warnings:
                report.append(f"  {warning}")
        
        return "\n".join(report)


# Quick validation function for easy import
def validate_intervention_plan(
    plan_json: Dict,
    age_months: int = None,
    rag_context: str = None
) -> Tuple[bool, str]:
    """
    Quick validation function for intervention plans.
    
    Args:
        plan_json: Plan response JSON
        age_months: Child's age in months
        rag_context: RAG context string (for source whitelist validation)
        
    Returns:
        Tuple of (is_valid, validation_report)
    """
    validator = PlanValidator()
    is_valid, warnings = validator.validate_plan(plan_json, age_months)
    report = validator.get_validation_report(plan_json, age_months)
    
    # Add source whitelist validation if RAG context provided
    if rag_context and 'Intervention_Plan' in plan_json:
        content = plan_json['Intervention_Plan']
        sources_text = validator.extract_section(content, 'Sources')
        
        if sources_text:
            allowed_ids = validator.extract_source_ids_from_context(rag_context)
            whitelist_valid, whitelist_errors = validator.validate_source_whitelist(
                sources_text,
                content,
                allowed_ids
            )
            
            if not whitelist_valid:
                report += "\n\n🚨 SOURCE HALLUCINATION DETECTED 🚨\n"
                report += "\n".join(whitelist_errors)
                is_valid = False
    
    return is_valid, report


def verify_critical_requirements(
    plan_json: Dict,
    rag_context: str = None
) -> Tuple[bool, List[str]]:
    """
    Verify critical requirements before returning final response.
    
    This is a strict check that MUST pass before any response is returned.
    Checks:
    1. At least 2 outcomes are present
    2. At least 4 strategies are present
    3. At least 4 advice bullet points are present
    4. Citations are present in outcomes
    5. A Sources section is included
    6. Sources match retrieved RAG context (no hallucination)
    
    Args:
        plan_json: Plan response JSON
        rag_context: RAG context string (for source validation)
        
    Returns:
        Tuple of (all_requirements_met, list_of_failed_requirements)
    """
    failed_requirements = []
    validator = PlanValidator()
    
    # Check if using new format
    if 'Intervention_Plan' not in plan_json:
        failed_requirements.append("Response missing 'Intervention_Plan' key")
        return False, failed_requirements
    
    content = plan_json['Intervention_Plan']
    
    # Requirement 1: At least 2 goals
    goals_text = validator.extract_section(content, 'Goals')
    if goals_text:
        num_goals = validator.count_bullet_points(goals_text)
        if num_goals < 2:
            failed_requirements.append(f"Only {num_goals} goal(s) present - minimum 2 required")
    else:
        failed_requirements.append("Goals section missing")
    
    # Requirement 2: At least 3 strategies
    strategies_text = validator.extract_section(content, 'Strategies')
    if strategies_text:
        # Count "Strategy N:" patterns (both bold and non-bold formats)
        strategy_pattern = r'(?:\*\*)?Strategy\s+\d+:(?:\*\*)?'
        strategy_matches = re.findall(strategy_pattern, strategies_text)
        num_strategies = len(strategy_matches)
        if num_strategies < 3:
            failed_requirements.append(f"Only {num_strategies} strategy(ies) present - minimum 3 required")
    else:
        failed_requirements.append("Strategies section missing")
    
    # Requirement 3: At least 4 advice items
    advice_text = validator.extract_section(content, 'Advice for Parents')
    if advice_text:
        num_advice = validator.count_bullet_points(advice_text)
        if num_advice < 4:
            failed_requirements.append(f"Only {num_advice} advice item(s) present - minimum 4 required")
    else:
        failed_requirements.append("Advice for Parents section missing")
    
    # Requirement 4: Citations present in outcomes
    if outcomes_text:
        has_citations, _ = validator.check_citations(outcomes_text)
        if not has_citations:
            failed_requirements.append("No citations found in Outcomes section")
    
    # Requirement 5: Sources section is included
    sources_text = validator.extract_section(content, 'Sources')
    if not sources_text:
        failed_requirements.append("Sources section missing")
    else:
        # Check if sources section has actual content
        # Support both formats: "- Source 1:" and "- **Source 1**:"
        source_pattern = r'-\s*\*{0,2}Source\s+\d+\*{0,2}:'
        sources_listed = re.findall(source_pattern, sources_text, re.IGNORECASE)
        if not sources_listed:
            # Check for the acceptable "no sources" disclaimer
            if not ("no" in sources_text.lower() and ("retrieved" in sources_text.lower() or "available" in sources_text.lower())):
                failed_requirements.append("Sources section empty or improperly formatted")
    
    # Requirement 6: SOURCE WHITELIST - No hallucinated sources
    if rag_context and sources_text:
        allowed_ids = validator.extract_source_ids_from_context(rag_context)
        whitelist_valid, whitelist_errors = validator.validate_source_whitelist(
            sources_text,
            content,
            allowed_ids
        )
        if not whitelist_valid:
            failed_requirements.extend(whitelist_errors)
    
    all_requirements_met = len(failed_requirements) == 0
    return all_requirements_met, failed_requirements
