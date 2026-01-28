"""
Go code generator utilities.

Provides utilities for generating properly formatted Go source code.
"""

from typing import List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class GoImport:
    """Represents a Go import."""
    path: str
    alias: Optional[str] = None
    
    def __hash__(self):
        return hash((self.path, self.alias))
    
    def __eq__(self, other):
        if not isinstance(other, GoImport):
            return False
        return self.path == other.path and self.alias == other.alias


class GoCodeGenerator:
    """Generates properly formatted Go source code."""
    
    # Python stdlib to Go stdlib mappings
    STDLIB_MAPPINGS = {
        "os": "os",
        "sys": "os",
        "json": "encoding/json",
        "re": "regexp",
        "math": "math",
        "time": "time",
        "random": "math/rand",
        "io": "io",
        "pathlib": "path/filepath",
        "collections": None,  # No direct equivalent
        "typing": None,  # No import needed
        "abc": None,  # Interfaces instead
    }
    
    def __init__(self, package_name: str = "main"):
        """Initialize the code generator."""
        self.package_name = package_name
        self.imports: Set[GoImport] = set()
        self.indent_level = 0
        self.indent_char = "\t"
    
    def add_import(self, import_path: str, alias: Optional[str] = None) -> None:
        """Add an import statement."""
        self.imports.add(GoImport(path=import_path, alias=alias))
    
    def add_fmt_import(self) -> None:
        """Add fmt import (commonly needed)."""
        self.add_import("fmt")
    
    def map_python_import(self, python_import: str) -> Optional[str]:
        """Map a Python import to Go equivalent."""
        return self.STDLIB_MAPPINGS.get(python_import)
    
    def indent(self) -> str:
        """Get current indentation string."""
        return self.indent_char * self.indent_level
    
    def increase_indent(self) -> None:
        """Increase indentation level."""
        self.indent_level += 1
    
    def decrease_indent(self) -> None:
        """Decrease indentation level."""
        if self.indent_level > 0:
            self.indent_level -= 1
    
    def generate_package_declaration(self) -> str:
        """Generate the package declaration."""
        return f"package {self.package_name}\n"
    
    def generate_imports(self) -> str:
        """Generate import statements."""
        if not self.imports:
            return ""
        
        lines = ["import ("]
        for imp in sorted(self.imports, key=lambda x: x.path):
            if imp.alias:
                lines.append(f'\t{imp.alias} "{imp.path}"')
            else:
                lines.append(f'\t"{imp.path}"')
        lines.append(")")
        return "\n".join(lines) + "\n"
    
    def generate_struct(
        self,
        name: str,
        fields: List[tuple],  # List of (name, type, tag) tuples
        comment: Optional[str] = None
    ) -> str:
        """
        Generate a Go struct definition.
        
        Args:
            name: Struct name
            fields: List of (field_name, field_type, optional_tag) tuples
            comment: Optional doc comment
        """
        lines = []
        
        if comment:
            lines.append(f"// {name} {comment}")
        
        lines.append(f"type {name} struct {{")
        
        for field_info in fields:
            field_name = field_info[0]
            field_type = field_info[1]
            field_tag = field_info[2] if len(field_info) > 2 else None
            
            # Capitalize field name for export
            go_field_name = field_name[0].upper() + field_name[1:] if field_name else field_name
            
            if field_tag:
                lines.append(f"\t{go_field_name} {field_type} `{field_tag}`")
            else:
                lines.append(f"\t{go_field_name} {field_type}")
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_function(
        self,
        name: str,
        params: List[tuple],  # List of (name, type) tuples
        return_type: Optional[str],
        body: List[str],
        receiver: Optional[tuple] = None,  # (var_name, type) for methods
        comment: Optional[str] = None
    ) -> str:
        """
        Generate a Go function or method.
        
        Args:
            name: Function name
            params: List of (param_name, param_type) tuples
            return_type: Return type or None
            body: List of body lines
            receiver: Optional (var_name, type) for methods
            comment: Optional doc comment
        """
        lines = []
        
        if comment:
            lines.append(f"// {name} {comment}")
        
        # Build function signature
        param_str = ", ".join(f"{p[0]} {p[1]}" for p in params)
        
        if receiver:
            recv_str = f"({receiver[0]} {receiver[1]}) "
        else:
            recv_str = ""
        
        if return_type:
            sig = f"func {recv_str}{name}({param_str}) {return_type} {{"
        else:
            sig = f"func {recv_str}{name}({param_str}) {{"
        
        lines.append(sig)
        
        # Add body with indentation
        for line in body:
            if line.strip():
                lines.append(f"\t{line}")
            else:
                lines.append("")
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_interface(
        self,
        name: str,
        methods: List[tuple],  # List of (name, params, return_type) tuples
        comment: Optional[str] = None
    ) -> str:
        """Generate a Go interface definition."""
        lines = []
        
        if comment:
            lines.append(f"// {name} {comment}")
        
        lines.append(f"type {name} interface {{")
        
        for method_info in methods:
            method_name = method_info[0]
            params = method_info[1]
            return_type = method_info[2] if len(method_info) > 2 else None
            
            param_str = ", ".join(f"{p[0]} {p[1]}" for p in params)
            
            if return_type:
                lines.append(f"\t{method_name}({param_str}) {return_type}")
            else:
                lines.append(f"\t{method_name}({param_str})")
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_const(
        self,
        name: str,
        value: str,
        const_type: Optional[str] = None,
        comment: Optional[str] = None
    ) -> str:
        """Generate a Go constant declaration."""
        lines = []
        
        if comment:
            lines.append(f"// {name} {comment}")
        
        if const_type:
            lines.append(f"const {name} {const_type} = {value}")
        else:
            lines.append(f"const {name} = {value}")
        
        return "\n".join(lines)
    
    def generate_var(
        self,
        name: str,
        var_type: str,
        value: Optional[str] = None,
        comment: Optional[str] = None
    ) -> str:
        """Generate a Go variable declaration."""
        lines = []
        
        if comment:
            lines.append(f"// {name} {comment}")
        
        if value:
            lines.append(f"var {name} {var_type} = {value}")
        else:
            lines.append(f"var {name} {var_type}")
        
        return "\n".join(lines)
    
    def format_string_literal(self, value: str) -> str:
        """Format a string literal for Go."""
        # Escape special characters
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        value = value.replace("\t", "\\t")
        return f'"{value}"'
    
    def generate_full_file(self, content_blocks: List[str]) -> str:
        """Generate a complete Go source file."""
        parts = [
            self.generate_package_declaration(),
            "",
            self.generate_imports() if self.imports else "",
        ]
        
        # Add content blocks
        for block in content_blocks:
            if block.strip():
                parts.append(block)
                parts.append("")
        
        return "\n".join(parts)
