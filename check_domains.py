"""Quick script to check what domains exist in milestones."""
import json

with open('parsed_output/milestones_structured.json', encoding='utf-8') as f:
    data = json.load(f)

domains = set(m['domain'] for m in data)
print('Domains found:', domains)
print(f'\nTotal milestones: {len(data)}')

# Check for motor-related keywords
motor_keywords = ['sit', 'crawl', 'walk', 'stand', 'roll', 'grasp', 'reach', 'balance', 'climb']
motor_related = []

for m in data:
    text = m['milestone_text'].lower()
    if any(keyword in text for keyword in motor_keywords):
        motor_related.append(m)

print(f'\nMilestones with motor keywords: {len(motor_related)}')
print('\nSample motor-related milestones:')
for m in motor_related[:10]:
    print(f"  - Domain: {m['domain']}")
    print(f"    Age: {m['age_min']}-{m['age_max']} months")
    print(f"    Text: {m['milestone_text'][:100]}")
    print()

# Check domain distribution
from collections import Counter
domain_counts = Counter(m['domain'] for m in data)
print('\nDomain distribution:')
for domain, count in sorted(domain_counts.items()):
    print(f"  {domain}: {count} milestones")
