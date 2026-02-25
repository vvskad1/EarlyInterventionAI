"""
Test script for source whitelist validation.

Tests that the validator correctly:
1. Extracts source IDs from RAG context
2. Detects hallucinated sources
3. Detects URL fabrication
4. Allows valid sources
"""
from app.validators import PlanValidator


def test_extraction():
    """Test extracting source IDs from RAG context."""
    print("="*80)
    print("TEST 1: Extract Source IDs from RAG Context")
    print("="*80)
    
    rag_context = """
[Source 1]
CDC milestones for 9 month development...

[Source 2]
SCGC social communication milestone...

[Source 3]
FGRBI coaching strategy about...
"""
    
    validator = PlanValidator()
    ids = validator.extract_source_ids_from_context(rag_context)
    
    print(f"RAG Context has: {ids}")
    expected = {1, 2, 3}
    if ids == expected:
        print("✅ PASS - Correctly extracted {1, 2, 3}")
    else:
        print(f"❌ FAIL - Expected {expected}, got {ids}")
    print()


def test_valid_sources():
    """Test that valid sources pass validation."""
    print("="*80)
    print("TEST 2: Valid Sources (Should Pass)")
    print("="*80)
    
    sources_text = """
- Source 1: CDC developmental milestones
- Source 2: SCGC social communication
- Source 3: FGRBI coaching strategies
"""
    
    plan_content = """
### 🎯 Goals
- Child will request items in 4/5 opportunities (Source 1).
- Child will make eye contact during play (Source 2).

### 📚 Sources
- Source 1: CDC developmental milestones
- Source 2: SCGC social communication
- Source 3: FGRBI coaching strategies
"""
    
    allowed_ids = {1, 2, 3}
    
    validator = PlanValidator()
    is_valid, errors = validator.validate_source_whitelist(
        sources_text,
        plan_content,
        allowed_ids
    )
    
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    if is_valid:
        print("✅ PASS - Valid sources accepted")
    else:
        print(f"❌ FAIL - Should have passed but got errors: {errors}")
    print()


def test_hallucinated_sources():
    """Test that hallucinated sources are detected."""
    print("="*80)
    print("TEST 3: Hallucinated Sources (Should Reject)")
    print("="*80)
    
    sources_text = """
- Source 1: CDC developmental milestones
- Source 2: SCGC social communication
- Source 5: Invented source that wasn't retrieved
- Source 7: Another hallucinated source
"""
    
    plan_content = """
### 🎯 Goals
- Child will request items (Source 1).
- Child will make eye contact (Source 5).
"""
    
    allowed_ids = {1, 2, 3}  # Only 1-3 were retrieved
    
    validator = PlanValidator()
    is_valid, errors = validator.validate_source_whitelist(
        sources_text,
        plan_content,
        allowed_ids
    )
    
    print(f"Valid: {is_valid}")
    print(f"Errors detected: {len(errors)}")
    for error in errors:
        print(f"  - {error}")
    
    if not is_valid and "HALLUCINATED SOURCES" in errors[0]:
        print("✅ PASS - Hallucinated sources correctly detected")
    else:
        print("❌ FAIL - Should have detected hallucinated sources")
    print()


def test_url_detection():
    """Test that URLs in sources are detected."""
    print("="*80)
    print("TEST 4: URL Fabrication (Should Reject)")
    print("="*80)
    
    sources_text = """
- Source 1: [CDC Milestones](https://www.researchgate.net/publication/123456)
- Source 2: [FGRBI Manual](https://doi.org/10.1234/example)
- Source 3: Regular source without URL
"""
    
    plan_content = """
### 🎯 Goals
- Child will request items (Source 1).
"""
    
    allowed_ids = {1, 2, 3}
    
    validator = PlanValidator()
    is_valid, errors = validator.validate_source_whitelist(
        sources_text,
        plan_content,
        allowed_ids
    )
    
    print(f"Valid: {is_valid}")
    print(f"Errors detected: {len(errors)}")
    for error in errors:
        print(f"  - {error}")
    
    if not is_valid and any("URL" in e or "LINK" in e for e in errors):
        print("✅ PASS - URL fabrication correctly detected")
    else:
        print("❌ FAIL - Should have detected URLs")
    print()


def test_hallucinated_citations():
    """Test that hallucinated citations are detected."""
    print("="*80)
    print("TEST 5: Hallucinated Citations (Should Reject)")
    print("="*80)
    
    sources_text = """
- Source 1: CDC developmental milestones
- Source 2: SCGC social communication
"""
    
    plan_content = """
### 🎯 Goals
- Child will request items (Source 1).
- Child will make eye contact (Source 2).
- Child will play with toys (Source 8).

### 📚 Sources
- Source 1: CDC developmental milestones
- Source 2: SCGC social communication
"""
    
    allowed_ids = {1, 2, 3}  # Only 1-3 were retrieved, but plan cites Source 8
    
    validator = PlanValidator()
    is_valid, errors = validator.validate_source_whitelist(
        sources_text,
        plan_content,
        allowed_ids
    )
    
    print(f"Valid: {is_valid}")
    print(f"Errors detected: {len(errors)}")
    for error in errors:
        print(f"  - {error}")
    
    if not is_valid and any("HALLUCINATED CITATIONS" in e for e in errors):
        print("✅ PASS - Hallucinated citations correctly detected")
    else:
        print("❌ FAIL - Should have detected hallucinated citation to Source 8")
    print()


def run_all_tests():
    """Run all source validation tests."""
    print("\n" + "="*80)
    print("SOURCE WHITELIST VALIDATION TEST SUITE")
    print("="*80 + "\n")
    
    test_extraction()
    test_valid_sources()
    test_hallucinated_sources()
    test_url_detection()
    test_hallucinated_citations()
    
    print("="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
    print("\nAll tests should pass to ensure source integrity is enforced.")


if __name__ == "__main__":
    run_all_tests()
