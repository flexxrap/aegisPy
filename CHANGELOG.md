# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-12

### Added
- **Core Features**
  - Secure code execution sandbox with resource limits
  - TUI (Terminal User Interface) powered by Rich
  - Security analysis with pattern detection
  - CLI with multiple commands (run, analyze, tui, watch, report, plugins)
  
- **Sandbox**
  - `SecureSandbox` for executing Python code in isolated environments
  - `ScriptRunner` for running arbitrary scripts with timeout and memory limits
  - Resource constraints (CPU, memory, time, file descriptors)
  - Network isolation and file system restrictions
  
- **Security**
  - `DangerousPatternDetector` for static code analysis
  - Detection of dangerous imports, functions, and patterns
  - Risk scoring and classification (low/medium/high)
  
- **Configuration**
  - YAML/JSON configuration support
  - `Config` and `ConfigLoader` classes
  - Command-line config file option (`--config`)
  
- **Plugin System**
  - Extensible plugin architecture
  - `Plugin`, `PluginManager`, `PluginRegistry` classes
  - Example plugins: ReportGenerator, Logger, Validator
  - CLI command `aegispy plugins`
  
- **File Watcher**
  - Real-time file system monitoring
  - `FileWatcher` with polling-based detection
  - Event callbacks and ignore patterns
  - CLI command `aegispy watch`
  
- **Report Generation**
  - Multi-format reports (JSON, CSV, TEXT, HTML)
  - `ReportGenerator` with template support
  - CLI command `aegispy report`
  
- **Development Tools**
  - CI/CD pipelines with GitHub Actions
  - Multi-OS testing (Ubuntu, macOS, Windows)
  - Code quality checks (ruff, mypy, black)
  - Comprehensive test suite (54+ tests)
  
- **Documentation**
  - README with badges
  - Docker support (Dockerfile, docker-compose)
  - PyPI publish workflow

### Changed
- Refactored project structure into `aegispy/` package
- Updated all imports to use relative paths
- Improved error handling throughout the codebase

### Fixed
- CI pipeline issues with flaky tests
- Import errors in TUI module
- Line length violations in code

## [0.1.0] - 2026-06-11

### Added
- Initial release
- Basic sandbox execution
- Security pattern detection
- CLI interface
- TUI prototype
