"""Plugin system for AegisPy."""

from __future__ import annotations

import importlib.util
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Base class for all plugins.

    All plugins must inherit from this class and implement required methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return plugin version."""
        pass

    @property
    def description(self) -> str:
        """Return plugin description."""
        return "No description provided"

    @property
    def author(self) -> str:
        """Return plugin author."""
        return "Unknown"

    @abstractmethod
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the plugin.

        Args:
            config: Optional configuration dictionary
        """
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute plugin functionality.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""

    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return True


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self) -> None:
        """Initialize plugin registry."""
        self._plugins: dict[str, Plugin] = {}
        self._load_paths: list[Path] = []

    def register(self, plugin: Plugin) -> None:
        """Register a plugin.

        Args:
            plugin: Plugin instance to register
        """
        if plugin.name in self._plugins:
            logger.warning("Plugin %s already registered, overwriting", plugin.name)

        self._plugins[plugin.name] = plugin
        logger.info("Registered plugin: %s v%s", plugin.name, plugin.version)

    def unregister(self, name: str) -> bool:
        """Unregister a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was unregistered, False if not found
        """
        if name in self._plugins:
            plugin = self._plugins[name]
            plugin.cleanup()
            del self._plugins[name]
            logger.info("Unregistered plugin: %s", name)
            return True

        logger.warning("Plugin %s not found", name)
        return False

    def get(self, name: str) -> Plugin | None:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)

    def list_plugins(self) -> list[dict[str, str]]:
        """List all registered plugins.

        Returns:
            List of plugin information dictionaries
        """
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author,
                "enabled": str(plugin.is_enabled()),
            }
            for plugin in self._plugins.values()
        ]

    def enable(self, name: str) -> bool:
        """Enable a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was enabled, False if not found or already enabled
        """
        plugin = self._plugins.get(name)
        if plugin:
            plugin.initialize()
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was disabled, False if not found
        """
        plugin = self._plugins.get(name)
        if plugin:
            plugin.cleanup()
            return True
        return False

    def is_loaded(self, name: str) -> bool:
        """Check if a plugin is loaded.

        Args:
            name: Plugin name

        Returns:
            True if plugin is loaded
        """
        return name in self._plugins

    def add_load_path(self, path: Path) -> None:
        """Add a path to search for plugins.

        Args:
            path: Path to search for plugins
        """
        if path not in self._load_paths:
            self._load_paths.append(path)
            logger.info("Added plugin load path: %s", path)

    def load_from_directory(self, directory: Path) -> int:
        """Load all plugins from a directory.

        Args:
            directory: Directory to search for plugins

        Returns:
            Number of plugins loaded
        """
        if not directory.exists():
            logger.warning("Plugin directory not found: %s", directory)
            return 0

        count = 0
        for plugin_file in directory.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem,
                    plugin_file,
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, Plugin)
                            and attr is not Plugin
                        ):
                            plugin = attr()
                            plugin.initialize()
                            self.register(plugin)
                            count += 1
                            logger.info("Loaded plugin from %s: %s", plugin_file, plugin.name)
            except Exception as e:
                logger.error("Failed to load plugin from %s: %s", plugin_file, e)

        return count

    def load_all(self) -> int:
        """Load plugins from all registered paths.

        Returns:
            Number of plugins loaded
        """
        count = 0
        for path in self._load_paths:
            count += self.load_from_directory(path)
        return count


class PluginManager:
    """Manager for plugin lifecycle."""

    def __init__(self) -> None:
        """Initialize plugin manager."""
        self.registry = PluginRegistry()
        self._default_paths = [
            Path(__file__).parent.parent / "plugins",
            Path.cwd() / "plugins",
        ]

        for path in self._default_paths:
            self.registry.add_load_path(path)

    def load_plugins(self) -> int:
        """Load all plugins.

        Returns:
            Number of plugins loaded
        """
        return self.registry.load_all()

    def get_plugin(self, name: str) -> Plugin | None:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.registry.get(name)

    def list_plugins(self) -> list[dict[str, str]]:
        """List all loaded plugins.

        Returns:
            List of plugin information
        """
        return self.registry.list_plugins()

    def execute_plugin(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a plugin.

        Args:
            name: Plugin name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Execution result

        Raises:
            ValueError: If plugin not found
        """
        plugin = self.registry.get(name)
        if not plugin:
            raise ValueError(f"Plugin not found: {name}")

        if not plugin.is_enabled():
            logger.warning("Plugin %s is disabled", name)
            return None

        return plugin.execute(*args, **kwargs)

    def shutdown(self) -> None:
        """Shutdown all plugins."""
        for name in list(self.registry._plugins.keys()):
            self.registry.unregister(name)
        logger.info("All plugins shut down")
