"""Example: Basic code execution."""

from aegispy.sandbox import SecureSandbox

# Create sandbox instance
sandbox = SecureSandbox()

# Execute safe code
result = sandbox.execute("print('Hello, World!')")
print(f"Output: {result.stdout}")
print(f"Exit code: {result.exit_code}")
