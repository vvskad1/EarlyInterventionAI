"""
Output validation for Early Intervention plan quality.

Implements pre-output checks to catch common reliability issues:
- Vocabulary count goals
- Unexplained frameworks/acronyms
- Unrealistic developmental targets
- Non-functional goal phrasing
"""
import re
from typing import Dict, List, Tuple


class PlanValidator:
    """Validates intervention plan outputs for EI best practices."""
    
    # Patterns that indicate problematic goal phrasing
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
    def validate_goals(cls, goals_text: str, age_months: int = None) -> Tuple[bool, List[str]]:
        """
        Validate goal quality against EI best practices.
        
        Args:
            goals_text: The goals section text to validate
            age_months: Child's age in months (optional, for age-specific checks)
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check for vocabulary count goals
        for pattern in cls.VOCAB_COUNT_PATTERNS:
            if re.search(pattern, goals_text, re.IGNORECASE):
                warnings.append(
                    "❌ VOCABULARY COUNT GOAL: Goals should focus on functional use "
                    "(request, label, comment) rather than word counts"
                )
                break
        
        # Check for sentence length targets
        for pattern in cls.SENTENCE_LENGTH_PATTERNS:
            match = re.search(pattern, goals_text, re.IGNORECASE)
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
        has_routine_context = any(keyword in goals_text.lower() for keyword in routine_keywords)
        if not has_routine_context:
            warnings.append(
                "⚠️ ROUTINE CONTEXT: Goals should specify routines/contexts "
                "(e.g., 'during snack and play')"
            )
        
        # Check for measurable criteria
        measurable_patterns = [
            r'\d+\s+(?:out of|of|/)\s+\d+',  # "4 out of 5", "3/5"
            r'\d+\s+seconds?',                # "10 seconds"
            r'\d+\s+times?',                  # "3 times"
        ]
        has_criterion = any(re.search(p, goals_text, re.IGNORECASE) for p in measurable_patterns)
        if not has_criterion:
            warnings.append(
                "⚠️ MEASURABILITY: Goals should include specific criteria "
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
    def validate_plan(cls, plan_json: Dict, age_months: int = None) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate complete intervention plan.
        
        Args:
            plan_json: The plan response JSON with Goals, Strategies, Advice for Parents
            age_months: Child's age in months (optional)
            
        Returns:
            Tuple of (is_valid, warnings_by_section)
        """
        all_warnings = {}
        
        # Validate Goals
        if 'Goals' in plan_json:
            goals_valid, goals_warnings = cls.validate_goals(
                plan_json['Goals'], 
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
def validate_intervention_plan(plan_json: Dict, age_months: int = None) -> Tuple[bool, str]:
    """
    Quick validation function for intervention plans.
    
    Args:
        plan_json: Plan response JSON
        age_months: Child's age in months
        
    Returns:
        Tuple of (is_valid, validation_report)
    """
    validator = PlanValidator()
    is_valid, warnings = validator.validate_plan(plan_json, age_months)
    report = validator.get_validation_report(plan_json, age_months)
    
    return is_valid, report
