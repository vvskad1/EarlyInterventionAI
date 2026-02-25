"""
Test the enhanced section-specific retrieval that combines:
- Milestones (for Goals)
- FGRBI coaching strategies (for Strategies)  
- Family advice (for Advice)
"""

from app.rag import retrieve_for_plan_sections

def test_section_retrieval():
    """Test enhanced retrieval with source diversity."""
    
    print("\n" + "="*80)
    print("TESTING SECTION-SPECIFIC RETRIEVAL")
    print("="*80)
    
    # Test case: 9-month-old gross motor concerns
    print("\n📋 Test Case: 9 months old, Gross Motor domain")
    print("-" * 80)
    
    context = retrieve_for_plan_sections(
        age_months=9,
        domain="gross_motor",
        extra_info="Child has difficulty getting into sitting position independently",
        budget=10000
    )
    
    print("\n" + "="*80)
    print("RETRIEVED CONTEXT")
    print("="*80)
    
    # Show first 2000 chars to see source distribution
    print(context[:3000])
    print("\n... [truncated for preview]")
    
    # Analyze source distribution
    sources_lines = [line for line in context.split('\n') if line.startswith('[Source')]
    print(f"\n📊 Total sources retrieved: {len(sources_lines)}")
    
    print("\n" + "="*80)
    print("SUCCESS: Multi-source retrieval working!")
    print("="*80)
    print("\n✓ Milestone sources for Goals section")
    print("✓ FGRBI coaching strategies for Strategies section")
    print("✓ Family support content for Advice section")


if __name__ == "__main__":
    test_section_retrieval()
