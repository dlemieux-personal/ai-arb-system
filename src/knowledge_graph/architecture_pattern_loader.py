"""
Architecture Pattern Loader Module
Loads architecture patterns into the knowledge graph.
"""

from typing import Dict, Any, List, cast
from pathlib import Path
import yaml


class ArchitecturePatternLoader:
    """Loads architecture patterns into knowledge graph"""
    
    def __init__(self, knowledge_path: Path):
        """
        Initialize the loader
        
        Args:
            knowledge_path: Path to architecture patterns directory
        """
        self.knowledge_path = Path(knowledge_path) / "architecture_patterns"
    
    def load_all_patterns(self) -> List[Dict[str, Any]]:
        """
        Load all architecture patterns
        
        Returns:
            List of pattern definitions
        """
        patterns = []
        
        for yaml_file in self.knowledge_path.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                pattern = yaml.safe_load(f)
                patterns.append(pattern)
        
        return patterns
    
    def load_pattern(self, pattern_name: str) -> Dict[str, Any]:
        """
        Load a specific architecture pattern
        
        Args:
            pattern_name: Name of the pattern (without extension)
            
        Returns:
            Pattern definition
        """
        pattern_file = self.knowledge_path / f"{pattern_name}.yaml"
        
        if not pattern_file.exists():
            raise FileNotFoundError(f"Pattern not found: {pattern_name}")
        
        with open(pattern_file, 'r', encoding='utf-8') as f:
            return cast(Dict[str, Any], yaml.safe_load(f))
