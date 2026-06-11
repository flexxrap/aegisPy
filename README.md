# AegisPy

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/flexxrap/aegisPy/releases)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/flexxrap/aegisPy/ci.yml?branch=main&label=CI)](https://github.com/flexxrap/aegisPy/actions)
[![Tests](https://img.shields.io/badge/tests-54%20passed%20%E2%80%A2%208%20skipped-success)](https://github.com/flexxrap/aegisPy/actions)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-FFD21F.svg)](https://github.com/astral-sh/ruff)
[![Downloads](https://img.shields.io/badge/downloads-static-purple)](https://github.com/flexxrap/aegisPy)

Advanced local security sandbox with TUI for safe code execution and analysis.

## 🚀 Features

- **Secure Code Execution**: Run untrusted Python code in isolated environments
- **TUI Interface**: Beautiful terminal-based user interface powered by Rich
- **Security Analysis**: Static and dynamic analysis of suspicious code patterns
- **Resource Limits**: CPU, memory, and time constraints for sandboxed execution
- **Network Isolation**: Control network access for executed code
- **File System Isolation**: Chroot-like file system restrictions
- **Real-time Monitoring**: Live resource usage and execution metrics
- **Plugin System**: Extensible architecture for custom plugins
- **File Watcher**: Real-time file system monitoring
- **Report Generation**: Multi-format reports (JSON, CSV, TEXT, HTML)

## 📦 Installation

```bash
pip install aegispy
```

### Development Installation

```bash
git clone https://github.com/flexxrap/aegisPy.git
cd aegisPy
pip install -e .[dev]
```

## 🎯 Quick Start

### Basic Execution

```python
from aegispy.sandbox import SecureSandbox

sandbox = SecureSandbox()
result = sandbox.execute("print('Hello, World!')")
print(result.stdout)
```

### CLI Usage

```bash
# Run code with sandbox
aegispy run "print('Hello')"

# Interactive TUI mode
aegispy tui

# Analyze suspicious code
aegispy analyze suspicious_script.py

# Watch files for changes
aegispy watch ./src --interval 1.0

# Generate reports
aegispy report --format html --output report.html

# List plugins
aegispy plugins
```

## 🔒 Security Features

- Process isolation using Linux namespaces and cgroups
- Resource limits (CPU, memory, time, file descriptors)
- Network namespace isolation
- File system sandboxing
- System call filtering (seccomp)
- Static code analysis for dangerous patterns
- Dynamic behavior monitoring

## 📁 Project Structure

```
aegispy/
├── aegispy/
│   ├── cli.py              # CLI interface
│   ├── core/
│   │   ├── security.py     # Security analysis
│   │   └── logging_config.py
│   ├── sandbox/
│   │   ├── sandbox.py      # Secure sandbox
│   │   └── runner.py       # Script runner
│   ├── config/             # Configuration system
│   ├── plugins/            # Plugin architecture
│   ├── watcher/            # File watcher
│   ├── reports/            # Report generator
│   ├── ui/                 # TUI interface
│   └── tests/              # Test suite
├── docker/                 # Docker support
├── examples/               # Usage examples
├── .github/workflows/      # CI/CD pipelines
└── pyproject.toml
```

## 🐳 Docker

```bash
# Build and run
docker-compose up -d

# Or with Docker
docker build -t aegispy -f docker/Dockerfile .
docker run -it aegispy
```

## 📝 Configuration

Create `config.yaml`:

```yaml
sandbox:
  timeout: 30.0
  max_memory_mb: 512
  network_enabled: false

logging:
  level: INFO

ui:
  theme: default
```

Use with CLI:
```bash
aegispy -c config.yaml run "print('test')"
```

## 📊 Tests

```bash
# Run all tests
pytest aegispy/tests/ -v

# With coverage
pytest aegispy/tests/ --cov=aegispy --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest aegispy/tests/`
5. Submit a pull request

## 📄 License

This project is licensed under the GPL v3 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Rich for beautiful TUI
- Click for CLI
- pytest for testing
- ruff for linting

## 📞 Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/flexxrap/aegisPy/issues).

---

**Made with ❤️ by flexxrap**
