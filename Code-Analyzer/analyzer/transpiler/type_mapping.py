"""
Type mapping utilities for Python to Go transpilation.

Maps Python types to their Go equivalents.
"""

from typing import Optional, Dict
import re


class TypeMapper:
    """Maps Python type annotations to Go types."""
    
    # Basic type mappings
    BASIC_TYPES: Dict[str, str] = {
        "str": "string",
        "int": "int",
        "float": "float64",
        "bool": "bool",
        "bytes": "[]byte",
        "None": "",
        "NoneType": "",
        "Any": "interface{}",
        "object": "interface{}",
    }
    
    # Collection type patterns
    COLLECTION_PATTERNS = [
        (r"^list\[(.+)\]$", "[]{}"),
        (r"^List\[(.+)\]$", "[]{}"),
        (r"^set\[(.+)\]$", "map[{}]struct{}"),
        (r"^Set\[(.+)\]$", "map[{}]struct{}"),
        (r"^dict\[(.+),\s*(.+)\]$", "map[{}]{}"),
        (r"^Dict\[(.+),\s*(.+)\]$", "map[{}]{}"),
        (r"^tuple\[(.+)\]$", "struct{{ {} }}"),
        (r"^Tuple\[(.+)\]$", "struct{{ {} }}"),
        (r"^Optional\[(.+)\]$", "*{}"),
        (r"^Union\[(.+),\s*None\]$", "*{}"),
        (r"^Union\[None,\s*(.+)\]$", "*{}"),
    ]
    
    def __init__(self):
        """Initialize the type mapper."""
        self.custom_types: Dict[str, str] = {}
    
    def register_custom_type(self, python_type: str, go_type: str) -> None:
        """Register a custom type mapping."""
        self.custom_types[python_type] = go_type
    
    def map_type(self, python_type: Optional[str]) -> str:
        """
        Map a Python type annotation to a Go type.
        
        Args:
            python_type: Python type annotation string
            
        Returns:
            Equivalent Go type string
        """
        if not python_type:
            return ""
        
        # Clean up the type string
        python_type = python_type.strip()
        
        # Check basic types first
        if python_type in self.BASIC_TYPES:
            return self.BASIC_TYPES[python_type]
        
        # Check custom types
        if python_type in self.custom_types:
            return self.custom_types[python_type]
        
        # Check collection patterns
        for pattern, go_template in self.COLLECTION_PATTERNS:
            match = re.match(pattern, python_type, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    inner_type = self.map_type(groups[0])
                    return go_template.format(inner_type)
                elif len(groups) == 2:
                    key_type = self.map_type(groups[0])
                    val_type = self.map_type(groups[1])
                    return go_template.format(key_type, val_type)
        
        # Handle Callable types
        if python_type.startswith("Callable"):
            return "func"  # Simplified - Go function types are more complex
        
        # Assume it's a custom class/struct type - use pointer
        if python_type[0].isupper():
            return f"*{python_type}"
        
        # Unknown type - return as interface{}
        return "interface{}"
    
    def get_zero_value(self, go_type: str) -> str:
        """Get the zero value for a Go type."""
        if not go_type:
            return ""
        
        zero_values = {
            "string": '""',
            "int": "0",
            "int8": "0",
            "int16": "0",
            "int32": "0",
            "int64": "0",
            "uint": "0",
            "uint8": "0",
            "uint16": "0",
            "uint32": "0",
            "uint64": "0",
            "float32": "0.0",
            "float64": "0.0",
            "bool": "false",
            "interface{}": "nil",
        }
        
        if go_type in zero_values:
            return zero_values[go_type]
        
        if go_type.startswith("*") or go_type.startswith("[]") or go_type.startswith("map["):
            return "nil"
        
        return "{}"  # Struct zero value
    
    def needs_pointer(self, python_type: Optional[str]) -> bool:
        """Check if the type should be a pointer in Go."""
        if not python_type:
            return False
        
        return python_type.startswith("Optional") or "None" in python_type
