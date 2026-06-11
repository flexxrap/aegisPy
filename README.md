# AegisPy

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/flexxrap/aegisPy/releases)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/flexxrap/aegisPy/ci.yml?branch=main&label=CI)](https://github.com/flexxrap/aegisPy/actions)
[![Tests](https://img.shields.io/badge/tests-27%20passed%20%E2%80%A2%201%20skipped-success)](https://github.com/flexxrap/aegisPy/actions)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-FFD21F.svg)](https://github.com/astral-sh/ruff)
[![Downloads](https://img.shields.io/badge/downloads-static-purple)](https://github.com/flexxrap/aegisPy)

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
