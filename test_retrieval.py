"""
Test script to verify domain filtering and age filtering in RAG retrieval.
This tests the retrieve_context() function with realistic queries.
"""
import sys
from app.rag import retrieve_context

def test_gross_motor_9_months():
    """Test retrieval for 9-month-old, Gross Motor domain."""
    print("\n" + "="*80)
    print("TEST 1: Age 9 months, Domain: Gross Motor")
    print("="*80)
    print("Expected: Should retrieve Play/Language milestones aged 7-10 months")
    print("Should NOT retrieve: 3-4 months or 11-12 months milestones")
    print()
    
    # Test query
    query = "What are appropriate gross motor skills and activities for a 9-month-old child?"
    age_months = 9
    domain = "gross_motor"
    
    # Retrieve context
    context, metadata = retrieve_context(
        age_months=age_months,
        domain=domain,
        extra_info=query,
        k=10,
        budget=8000,
        return_metadata=True
    )
    
    # Parse results
    print(f"Query: {query}")
    print(f"Age: {age_months} months")
    print(f"Domain: {domain}")
    print()
    print(f"Retrieved {len(metadata)} documents")
    print()
    
    # Show retrieved documents
    for i, meta in enumerate(metadata, 1):
        doc_domain = meta.get('domain', 'Unknown')
        age_min = meta.get('age_min', 'N/A')
        age_max = meta.get('age_max', 'N/A')
        title = meta.get('title', meta.get('source', 'Unknown'))
        
        print(f"Source {i}:")
        print(f"  Domain: {doc_domain}")
        print(f"  Age Range: {age_min}-{age_max} months")
        print(f"  Title: {title[:80]}...")
        print()
    
    # Verify expectations
    print("\n" + "-"*80)
    print("VERIFICATION:")
    print("-"*80)
    
    # Check domains
    domains_found = set(meta.get('domain', 'Unknown') for meta in metadata)
    print(f"Domains found: {domains_found}")
    
    expected_domains = {'Play', 'Language'}
    if domains_found.issubset(expected_domains) or domains_found.intersection(expected_domains):
        print("✅ Domain filtering: PASS (found expected domains)")
    else:
        print(f"❌ Domain filtering: FAIL (expected {expected_domains}, got {domains_found})")
    
    # Check age ranges
    ages_found = []
    for meta in metadata:
        age_min = meta.get('age_min')
        age_max = meta.get('age_max')
        if age_min is not None and age_max is not None:
            ages_found.append((age_min, age_max))
    
    print(f"\nAge ranges found: {ages_found}")
    
    # Check if any documents outside 6-11 month range (allowing some buffer)
    out_of_range = [
        (min_age, max_age) for min_age, max_age in ages_found 
        if max_age < 6 or min_age > 11
    ]
    
    if not out_of_range:
        print("✅ Age filtering: PASS (all documents within reasonable range)")
    else:
        print(f"❌ Age filtering: FAIL (found out-of-range documents: {out_of_range})")
    
    return context, metadata


def test_social_18_months():
    """Test retrieval for 18-month-old, Social domain."""
    print("\n" + "="*80)
    print("TEST 2: Age 18 months, Domain: Social")
    print("="*80)
    print("Expected: Should retrieve Social Interaction/Emotional Regulation milestones")
    print("Should be aged approximately 16-20 months")
    print()
    
    # Test query
    query = "What social-emotional skills should an 18-month-old demonstrate?"
    age_months = 18
    domain = "social"
    
    # Retrieve context
    context, metadata = retrieve_context(
        age_months=age_months,
        domain=domain,
        extra_info=query,
        k=10,
        budget=8000,
        return_metadata=True
    )
    
    # Parse results
    print(f"Query: {query}")
    print(f"Age: {age_months} months")
    print(f"Domain: {domain}")
    print()
    print(f"Retrieved {len(metadata)} documents")
    print()
    
    # Show retrieved documents
    for i, meta in enumerate(metadata, 1):
        doc_domain = meta.get('domain', 'Unknown')
        age_min = meta.get('age_min', 'N/A')
        age_max = meta.get('age_max', 'N/A')
        title = meta.get('title', meta.get('source', 'Unknown'))
        
        print(f"Source {i}:")
        print(f"  Domain: {doc_domain}")
        print(f"  Age Range: {age_min}-{age_max} months")
        print(f"  Title: {title[:80]}...")
        print()
    
    # Verify expectations
    print("\n" + "-"*80)
    print("VERIFICATION:")
    print("-"*80)
    
    # Check domains
    domains_found = set(meta.get('domain', 'Unknown') for meta in metadata)
    print(f"Domains found: {domains_found}")
    
    expected_domains = {'Social Interaction', 'Emotional Regulation'}
    if domains_found.intersection(expected_domains):
        print("✅ Domain filtering: PASS (found expected domains)")
    else:
        print(f"❌ Domain filtering: FAIL (expected {expected_domains}, got {domains_found})")
    
    # Check age ranges
    ages_found = []
    for meta in metadata:
        age_min = meta.get('age_min')
        age_max = meta.get('age_max')
        if age_min is not None and age_max is not None:
            ages_found.append((age_min, age_max))
    
    print(f"\nAge ranges found: {ages_found}")
    
    # Check if any documents outside 15-21 month range (allowing some buffer)
    out_of_range = [
        (min_age, max_age) for min_age, max_age in ages_found 
        if max_age < 15 or min_age > 21
    ]
    
    if not out_of_range:
        print("✅ Age filtering: PASS (all documents within reasonable range)")
    else:
        print(f"❌ Age filtering: FAIL (found out-of-range documents: {out_of_range})")
    
    return context, metadata


if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "RAG RETRIEVAL TEST SUITE" + " "*34 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        # Test 1: Gross Motor at 9 months (the user's problematic case)
        context1, metadata1 = test_gross_motor_9_months()
        
        # Test 2: Social at 18 months
        context2, metadata2 = test_social_18_months()
        
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*25 + "TESTS COMPLETE" + " "*38 + "║")
        print("╚" + "="*78 + "╝\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
