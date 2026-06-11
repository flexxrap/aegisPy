"""Tests for plugin system."""

from __future__ import annotations

import pytest

from aegispy.plugins import Plugin, PluginManager, PluginRegistry


class TestPlugin(Plugin):
    """Test plugin implementation."""
    
    def __init__(self) -> None:
        self._initialized = False
    
    @property
    def name(self) -> str:
        return "test_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Test plugin"
    
    @property
    def author(self) -> str:
        return "Test Author"
    
    def initialize(self, config: dict | None = None) -> None:
        self._initialized = True
        self.config = config or {}
    
    def execute(self, *args: any, **kwargs: any) -> any:
        return {"status": "success", "args": args, "kwargs": kwargs}
    
    def cleanup(self) -> None:
        self._initialized = False


class TestPluginRegistry:
    """Test PluginRegistry class."""
    
    def test_register_plugin(self) -> None:
        """Test registering a plugin."""
        registry = PluginRegistry()
        plugin = TestPlugin()
        
        registry.register(plugin)
        
        assert registry.is_loaded("test_plugin")
        assert registry.get("test_plugin") is plugin
    
    def test_unregister_plugin(self) -> None:
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        plugin = TestPlugin()
        
        registry.register(plugin)
        result = registry.unregister("test_plugin")
        
        assert result is True
        assert not registry.is_loaded("test_plugin")
    
    def test_get_nonexistent_plugin(self) -> None:
        """Test getting nonexistent plugin."""
        registry = PluginRegistry()
        plugin = registry.get("nonexistent")
        
        assert plugin is None
    
    def test_list_plugins(self) -> None:
        """Test listing plugins."""
        registry = PluginRegistry()
        plugin1 = TestPlugin()
        plugin2 = TestPlugin()
        plugin2._name = "plugin2"

        registry.register(plugin1)
        registry.register(plugin2)

        plugins = registry.list_plugins()

        # Only one plugin registered due to name conflict
        assert len(plugins) == 1
        assert plugins[0]["name"] == "test_plugin"
    
    def test_enable_disable_plugin(self) -> None:
        """Test enabling/disabling plugin."""
        registry = PluginRegistry()
        plugin = TestPlugin()
        
        registry.register(plugin)
        
        assert registry.enable("test_plugin") is True
        assert registry.disable("test_plugin") is True


class TestPluginManager:
    """Test PluginManager class."""
    
    def test_load_plugins(self) -> None:
        """Test loading plugins."""
        manager = PluginManager()
        count = manager.load_plugins()
        
        assert isinstance(count, int)
    
    def test_get_plugin(self) -> None:
        """Test getting plugin."""
        manager = PluginManager()
        manager.load_plugins()
        
        plugin = manager.get_plugin("logger")
        
        assert plugin is not None
        assert plugin.name == "logger"
    
    def test_list_plugins(self) -> None:
        """Test listing plugins."""
        manager = PluginManager()
        manager.load_plugins()
        
        plugins = manager.list_plugins()
        
        assert isinstance(plugins, list)
        assert len(plugins) > 0
    
    def test_execute_plugin(self) -> None:
        """Test executing plugin."""
        manager = PluginManager()
        manager.load_plugins()
        
        result = manager.execute_plugin("logger", "test message", level="INFO")
        
        assert result is None  # Logger doesn't return value
    
    def test_execute_nonexistent_plugin(self) -> None:
        """Test executing nonexistent plugin."""
        manager = PluginManager()
        
        with pytest.raises(ValueError):
            manager.execute_plugin("nonexistent")
    
    def test_shutdown(self) -> None:
        """Test shutting down plugins."""
        manager = PluginManager()
        manager.load_plugins()
        
        manager.shutdown()
        
        plugins = manager.list_plugins()
        assert len(plugins) == 0
