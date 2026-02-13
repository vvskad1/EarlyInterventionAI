"""
Validation Test Examples
Demonstrates the validator catching common reliability issues.
"""
from app.validators import PlanValidator, validate_intervention_plan


def test_vocabulary_count_detection():
    """Test detection of vocabulary count goals (assessment metrics)"""
    print("\n" + "="*80)
    print("TEST 1: Vocabulary Count Detection")
    print("="*80)
    
    bad_goals = """
    Within the next 6 months, the child will increase their vocabulary to 20 words,
    use 5-word sentences, and initiate communication in 50% of interactions.
    """
    
    is_valid, warnings = PlanValidator.validate_goals(bad_goals, age_months=18)
    
    print(f"Goals Text: {bad_goals.strip()}")
    print(f"\nValid: {is_valid}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")
    
    print("\n✅ Expected: Should catch vocabulary count and sentence length")


def test_framework_without_explanation():
    """Test detection of unexplained frameworks/acronyms"""
    print("\n" + "="*80)
    print("TEST 2: Unexplained Framework Detection")
    print("="*80)
    
    bad_strategies = """
    Embed responsive communication strategies in daily routines, such as using interesting
    sounds and actions. Use the SS-OO-PP-RR framework to structure interactions.
    """
    
    is_valid, warnings = PlanValidator.validate_strategies(bad_strategies)
    
    print(f"Strategies Text: {bad_strategies.strip()}")
    print(f"\nValid: {is_valid}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")
    
    print("\n✅ Expected: Should catch unexplained SS-OO-PP-RR acronym")


def test_good_goals():
    """Test that well-formed goals pass validation"""
    print("\n" + "="*80)
    print("TEST 3: Well-Formed Goals")
    print("="*80)
    
    good_goals = """
    During snack and play routines, child will use gestures, signs, or words to request 
    preferred items in 4 out of 5 opportunities across 2 consecutive weeks. During floor 
    play and caregiving routines, child will maintain sitting balance for 10 seconds in 
    3 out of 5 trials for 1 week.
    """
    
    is_valid, warnings = PlanValidator.validate_goals(good_goals, age_months=12)
    
    print(f"Goals Text: {good_goals.strip()}")
    print(f"\nValid: {is_valid}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")
    
    print("\n✅ Expected: Should pass with no critical errors")


def test_full_plan_validation():
    """Test complete plan validation"""
    print("\n" + "="*80)
    print("TEST 4: Full Plan Validation")
    print("="*80)
    
    # This is the problematic output from the user's test
    problematic_plan = {
        "Goals": "During daily routines and play, the child will use 5-10 words in 4 out of 5 opportunities across 2 consecutive weeks, and will initiate communication by pointing to or naming 2 objects in 3 out of 5 trials for 1 week.",
        "Strategies": "Embed responsive communication strategies in daily routines, such as using interesting sounds and actions, taking turns, and offering choices. Use the SS-OO-PP-RR framework to structure interactions, focusing on serving and returning, observing and responding, prompting and reinforcing, and repeating and expanding.",
        "Advice for Parents": "Try using simple and clear language when giving directions, and encourage the child to point to or name objects."
    }
    
    is_valid, report = validate_intervention_plan(problematic_plan, age_months=18)
    
    print(f"Plan JSON:")
    for key, value in problematic_plan.items():
        print(f"  {key}: {value[:80]}...")
    
    print(f"\n{report}")
    
    print("\n✅ Expected: Should catch vocabulary count and SS-OO-PP-RR issues")


def test_corrected_plan():
    """Test that corrected plan passes"""
    print("\n" + "="*80)
    print("TEST 5: Corrected Plan (Gold Standard)")
    print("="*80)
    
    corrected_plan = {
        "Goals": "During daily routines (e.g., snack, play, dressing), the child will initiate communication using a gesture, sign, or word (e.g., pointing, reaching, vocalizing, or naming) in 4 out of 5 opportunities across 2 consecutive weeks. During play and caregiving routines, the child will use a spoken word or word approximation to request or label an object or action in 3 out of 5 opportunities across 1 week.",
        "Strategies": "Embed responsive communication strategies within daily routines by positioning face-to-face and following the child's lead, modeling simple functional words during meaningful activities, pausing expectantly to create opportunities for the child to communicate, responding immediately and expanding on the child's attempts (e.g., 'ball' → 'big ball'), and providing multiple opportunities for practice across familiar routines.",
        "Advice for Parents": "During everyday routines and play, model simple words and gestures related to what your child is doing, and then pause to give them a chance to respond. If your child points, reaches, or makes a sound, respond as if they are communicating and build on their attempt."
    }
    
    is_valid, report = validate_intervention_plan(corrected_plan, age_months=18)
    
    print(f"Plan JSON:")
    for key, value in corrected_plan.items():
        print(f"  {key}: {value[:80]}...")
    
    print(f"\n{report}")
    
    print("\n✅ Expected: Should pass with minimal or no warnings")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("INTERVENTION PLAN VALIDATOR - TEST SUITE")
    print("="*80)
    
    test_vocabulary_count_detection()
    test_framework_without_explanation()
    test_good_goals()
    test_full_plan_validation()
    test_corrected_plan()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
