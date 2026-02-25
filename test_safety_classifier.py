"""
Test script for safety classifier - regression detection.

Tests the safety layer with various observation patterns to ensure:
1. Regression is correctly detected
2. Urgent medical flags are identified
3. Routine cases don't trigger false positives
"""
from app.safety import (
    detect_regression,
    detect_urgent_medical_flags,
    analyze_safety_concerns,
    generate_safety_prompt_injection
)


def test_case(description: str, observation: str, expected_safety_level: str):
    """
    Test a single observation and print analysis.
    
    Args:
        description: Human-readable test case name
        observation: The observation text to analyze
        expected_safety_level: Expected result ("routine", "regression", "urgent")
    """
    print("\n" + "="*80)
    print(f"TEST CASE: {description}")
    print("="*80)
    print(f"Observation: \"{observation}\"")
    print()
    
    # Run analysis
    analysis = analyze_safety_concerns(observation)
    
    # Print results
    print(f"Safety Level: {analysis['safety_level'].upper()}")
    print(f"Has Concerns: {analysis['has_concerns']}")
    print(f"Regression Detected: {analysis['regression_detected']}")
    print(f"Urgent Medical Flag: {analysis['urgent_medical_flag']}")
    
    if analysis['matched_patterns']:
        print(f"Matched Patterns: {', '.join(analysis['matched_patterns'])}")
    
    print(f"Recommended Action: {analysis['recommended_action']}")
    
    # Check if matches expectation
    if analysis['safety_level'] == expected_safety_level:
        print(f"\n✅ PASS - Correctly identified as '{expected_safety_level}'")
    else:
        print(f"\n❌ FAIL - Expected '{expected_safety_level}', got '{analysis['safety_level']}'")
    
    # Show prompt injection if applicable
    if analysis['has_concerns']:
        print("\n--- SAFETY PROMPT INJECTION ---")
        injection = generate_safety_prompt_injection(analysis)
        print(injection[:500] + "..." if len(injection) > 500 else injection)


def run_all_tests():
    """Run comprehensive test suite."""
    print("="*80)
    print("SAFETY CLASSIFIER TEST SUITE")
    print("="*80)
    
    # ===== REGRESSION CASES (Should detect) =====
    
    test_case(
        "Motor Regression - Lost Standing",
        "Child lost ability to stand and seems weaker than before.",
        expected_safety_level="regression"
    )
    
    test_case(
        "Language Regression - Stopped Talking",
        "My 20-month-old stopped saying words she used to say regularly.",
        expected_safety_level="regression"
    )
    
    test_case(
        "Social Regression - Lost Eye Contact",
        "He used to make eye contact but stopped responding to his name.",
        expected_safety_level="regression"
    )
    
    test_case(
        "Motor Regression - Walking Loss",
        "She was walking independently but now can't anymore.",
        expected_safety_level="regression"
    )
    
    test_case(
        "Skill Regression - Multiple Domains",
        "Lost words and stopped playing with toys like before. Going backward.",
        expected_safety_level="regression"
    )
    
    # ===== URGENT MEDICAL CASES (Should detect) =====
    
    test_case(
        "Seizure Concern",
        "Baby had a shaking episode and staring spells this morning.",
        expected_safety_level="urgent"
    )
    
    test_case(
        "Severe Tone Issue",
        "Child is completely floppy and won't hold head up.",
        expected_safety_level="urgent"
    )
    
    # ===== ROUTINE CASES (Should NOT trigger) =====
    
    test_case(
        "Typical Delay - Not Walking Yet",
        "15-month-old not walking yet, but cruising furniture.",
        expected_safety_level="routine"
    )
    
    test_case(
        "Typical Delay - Limited Words",
        "18 months old with only 5 words. Seems to understand but not talking much.",
        expected_safety_level="routine"
    )
    
    test_case(
        "Typical Concern - Social Shyness",
        "Child is shy around strangers and prefers familiar adults.",
        expected_safety_level="routine"
    )
    
    test_case(
        "Normal Variation - Quiet Baby",
        "8-month-old doesn't babble as much as sibling did at this age.",
        expected_safety_level="routine"
    )
    
    # ===== EDGE CASES =====
    
    test_case(
        "Weak Language (Not Regression)",
        "Child seems weak in language skills for age.",
        expected_safety_level="routine"
    )
    
    test_case(
        "Standing Struggles (Not Loss)",
        "Having trouble standing without support at 10 months.",
        expected_safety_level="routine"
    )
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
    print("\nReview results above to verify:")
    print("✓ Regression cases properly detected")
    print("✓ Urgent medical flags identified")
    print("✓ Routine delays don't trigger false positives")
    print("✓ Edge cases handled appropriately")


if __name__ == "__main__":
    run_all_tests()
