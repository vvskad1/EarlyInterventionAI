import json

with open('parsed_output/coaching_strategies_cleaned.json', encoding='utf-8') as f:
    strategies = json.load(f)

print(f"\n{'='*60}")
print(f"PHASE 1 COMPLETE - COACHING STRATEGIES EXTRACTED")
print(f"{'='*60}\n")

print(f"Total Strategies: {len(strategies)}")

# Count by layer
layer_counts = {}
for s in strategies:
    layer = s['layer']
    layer_counts[layer] = layer_counts.get(layer, 0) + 1

print(f"\nBreakdown by Layer:")
for layer in sorted(layer_counts.keys()):
    print(f"  {layer}: {layer_counts[layer]} strategies")

print(f"\n{'='*60}")
print("ALL STRATEGY TITLES:")
print(f"{'='*60}\n")

for i, s in enumerate(strategies, 1):
    print(f"{i:2d}. [{s['layer']}] {s['strategy_title']}")

print(f"\n{'='*60}")
