# AegisPy

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/pypi/v/aegispy.svg)](https://pypi.org/project/aegispy/)
[![Python Version](https://img.shields.io/pypi/pyversions/aegispy.svg)](https://pypi.org/project/aegispy/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/flexxrap/aegisPy/ci.yml?branch=main)](https://github.com/flexxrap/aegisPy/actions)
[![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/flexxrap/raw/aegispy-tests.json)](https://github.com/flexxrap/aegisPy/actions)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/aegispy)](https://pepy.tech/project/aegispy)

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

GPL v3
