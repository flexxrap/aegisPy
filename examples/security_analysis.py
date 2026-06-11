"""Example: Security analysis."""

from aegispy.core.security import DangerousPatternDetector

detector = DangerousPatternDetector()

# Code to analyze
code = """
import os
import subprocess

def calculate(x, y):
    return x + y

result = calculate(1, 2)
print(result)
"""

# Analyze code
result = detector.analyze(code)

print(f"Risk Level: {result['risk_level'].upper()}")
print(f"Risk Score: {result['risk_score']}")
print(f"Safe: {result['is_safe']}")

if result['imports']:
    print(f"\nDangerous imports: {result['imports']}")

if result['functions']:
    print(f"Dangerous functions: {result['functions']}")

if result['patterns']:
    print(f"Patterns found: {result['patterns'][:5]}")
