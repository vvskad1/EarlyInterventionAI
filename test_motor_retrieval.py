"""Quick test: Verify motor milestones are being retrieved."""

from app.rag import retrieve_for_plan_sections

print("\n" + "="*80)
print("MOTOR MILESTONE RETRIEVAL TEST")
print("="*80)

# Test case: 9-month-old with gross motor concerns
context = retrieve_for_plan_sections(
    age_months=9,
    domain="gross_motor",
    extra_info="Child not yet sitting independently",
    budget=3000
)

print("\n" + "="*80)
print("RETRIEVED SOURCES:")
print("="*80)

# Extract just the milestone content
lines = context.split('\n')
source_count = 0
current_source = []

for line in lines:
    if line.startswith('[Source'):
        if current_source:
            # Print previous source
            text = '\n'.join(current_source)
            if 'Gross Motor' in text or 'sitting' in text.lower() or 'motor' in text.lower():
                source_count += 1
                print(f"\n{'='*60}")
                print(text[:300])
        current_source = [line]
    else:
        current_source.append(line)

# Print last source
if current_source:
    text = '\n'.join(current_source)
    if 'Gross Motor' in text or 'sitting' in text.lower() or 'motor' in text.lower():
        source_count += 1
        print(f"\n{'='*60}")
        print(text[:300])

print("\n" + "="*80)
if source_count > 0:
    print(f"✅ SUCCESS: Found {source_count} motor-related sources!")
    print("Motor milestones are now being retrieved correctly.")
else:
    print("❌ ISSUE: No motor sources found in retrieval")
print("="*80)
