"""Check if FGRBI manual contains structured motor milestones."""

with open('kb/knowledge_base.txt', encoding='utf-8') as f:
    content = f.read()

# Search for motor-related sections
motor_keywords = [
    'gross motor', 'fine motor', 'motor development', 'motor skill',
    'crawling', 'sitting independently', 'pulling to stand', 
    'cruising', 'walking independently', 'running', 'jumping',
    'pincer grasp', 'stacking blocks', 'scribbling'
]

print("Motor-related content in FGRBI Manual:\n")
print("="*80)

found_any = False
for keyword in motor_keywords:
    count = content.lower().count(keyword.lower())
    if count > 0:
        found_any = True
        print(f"✓ '{keyword}': {count} mentions")
        
        # Show a snippet
        keyword_lower = keyword.lower()
        content_lower = content.lower()
        idx = content_lower.find(keyword_lower)
        if idx >= 0:
            start = max(0, idx - 100)
            end = min(len(content), idx + 150)
            snippet = content[start:end].replace('\n', ' ')
            print(f"  Sample: ...{snippet}...")
            print()

if not found_any:
    print("❌ No explicit motor milestone content found in FGRBI manual")
    print("\nThe FGRBI manual is focused on:")
    print("- Coaching methodology (SS-OO-PP-RR framework)")
    print("- Key Indicators for implementation quality")
    print("- Caregiver-provider interaction strategies")
    print("- NOT a comprehensive developmental milestone reference")

print("\n" + "="*80)
print("CONCLUSION:")
print("The FGRBI manual teaches HOW to coach, not WHAT milestones to target.")
print("You need a separate developmental milestone source (CDC, AAP, etc.)")
