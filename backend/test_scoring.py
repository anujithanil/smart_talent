#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from services.scorer import calculate_score, experience_weight

# Test experience weight function
print("=" * 50)
print("EXPERIENCE WEIGHT TESTING")
print("=" * 50)
print(f"3 years:  {experience_weight(3):.3f}")
print(f"5 years:  {experience_weight(5):.3f}")
print(f"11 years: {experience_weight(11):.3f}")

print("\n" + "=" * 50)
print("CANDIDATE SCORING - John vs Rahul")
print("=" * 50)

# John Doe: 76.64% semantic, 75% skills, 3 years
john_score = calculate_score(0.7664, 3, 0.75)

# Rahul Khanna: 59.38% semantic, 58.33% skills, 5 years  
rahul_score = calculate_score(0.5938, 5, 0.5833)

print(f"\nJohn Doe:")
print(f"  - Semantic: 76.64%, Skills: 75%, Experience: 3 years")
print(f"  - Score: {john_score:.4f} ({john_score*100:.2f}%)")

print(f"\nRahul Khanna:")
print(f"  - Semantic: 59.38%, Skills: 58.33%, Experience: 5 years")
print(f"  - Score: {rahul_score:.4f} ({rahul_score*100:.2f}%)")

print("\n" + "=" * 50)
print(f"RESULT: {'✓ John ranks HIGHER' if john_score > rahul_score else '✗ Rahul ranks HIGHER'}")
print(f"Difference: {abs(john_score - rahul_score)*100:.2f} percentage points")
print("=" * 50)
