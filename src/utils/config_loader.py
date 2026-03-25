"""
Config Loader Module
Loads and manages configuration.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml


class ConfigLoader:
    """Loads and manages YAML configuration files"""
    
    def __init__(self, config_dir: Path):
        """
        Initialize config loader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.cache = {}
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load a configuration file
        
        Args:
            filename: Name of config file (with or without extension)
            
        Returns:
            Configuration dictionary
        """
        # Check cache
        if filename in self.cache:
            return self.cache[filename]
        
        # Add .yaml extension if not present
        if not filename.endswith(('.yaml', '.yml')):
            filename += '.yaml'
        
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.cache[filename] = config
        return config
    
    def get_config(self, filename: str, key: Optional[str] = None) -> Any:
        """
        Get configuration value
        
        Args:
            filename: Config filename
            key: Optional nested key path (dot-separated)
            
        Returns:
            Configuration value
        """
        config = self.load_config(filename)
        
        if key is None:
            return config
        
        # Navigate nested keys
        value = config
        for part in key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        
        return value
