# AegisPy

Advanced local security sandbox with TUI for safe code execution and analysis.

## Features

- **Secure Code Execution**: Run untrusted Python code in isolated environments
- **TUI Interface**: Beautiful terminal-based user interface powered by Rich
- **Security Analysis**: Static and dynamic analysis of suspicious code patterns
- **Resource Limits**: CPU, memory, and time constraints for sandboxed execution
- **Network Isolation**: Control network access for executed code
- **File System Isolation**: Chroot-like file system restrictions
- **Real-time Monitoring**: Live resource usage and execution metrics

## Installation

```bash
pip install aegispy
```

## Quick Start

```python
from aegispy.sandbox import SecureSandbox

sandbox = SecureSandbox()
result = sandbox.execute("print('Hello, World!')")
print(result.output)
```

## Usage

```bash
# Run code with sandbox
aegispy run "print('Hello')"

# Interactive TUI mode
aegispy tui

# Analyze suspicious code
aegispy analyze suspicious_script.py
```

## Security Features

- Process isolation using Linux namespaces and cgroups
- Resource limits (CPU, memory, time, file descriptors)
- Network namespace isolation
- File system sandboxing
- System call filtering (seccomp)
- Static code analysis for dangerous patterns
- Dynamic behavior monitoring

## License

MIT
