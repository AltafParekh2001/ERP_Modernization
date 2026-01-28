"""
Python to Go transpiler.

Converts Python source code into equivalent Go code.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union, Dict, Set

from analyzer.parsers import PythonParser, FileParser
from analyzer.models.code_entities import Module, Class, Function, Method, Variable
from analyzer.transpiler.type_mapping import TypeMapper
from analyzer.transpiler.code_generator import GoCodeGenerator
from analyzer.transpiler.body_transpiler import BodyTranspiler
from analyzer.logging_config import get_logger
from analyzer.utils import read_file

logger = get_logger("transpiler.python_to_go")


class PythonToGoTranspiler:
    """
    Transpiles Python source code to Go.
    
    Converts Python constructs to their Go equivalents:
    - Classes -> Structs with methods
    - Functions -> Functions
    - Methods -> Receiver methods
    - Type annotations -> Go types
    """
    
    def __init__(self, package_name: str = "main"):
        """
        Initialize the transpiler.
        
        Args:
            package_name: Default Go package name to use
        """
        self.package_name = package_name
        self.type_mapper = TypeMapper()
        self.parser = PythonParser()
        self.body_transpiler = BodyTranspiler(self.type_mapper)
        self._current_source: Optional[str] = None  # Store source for body transpilation
    
    def transpile_file(
        self,
        source_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        package_name: Optional[str] = None
    ) -> str:
        """
        Transpile a single Python file to Go.
        
        Args:
            source_path: Path to the Python source file
            output_path: Optional output path for the Go file
            package_name: Optional package name override
            
        Returns:
            Generated Go source code
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if not source_path.suffix == ".py":
            raise ValueError(f"Expected .py file, got: {source_path}")
        
        logger.info(f"Transpiling {source_path}")
        
        # Read source code for body transpilation
        self._current_source = read_file(source_path)
        
        # Parse the Python source
        module = self.parser.parse_file(source_path)
        
        # Generate Go code
        go_code = self._transpile_module(
            module,
            package_name or self.package_name
        )
        
        # Write to output file if specified
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(go_code, encoding="utf-8")
            logger.info(f"Wrote Go code to {output_path}")
        
        return go_code
    
    def transpile_directory(
        self,
        source_dir: Union[str, Path],
        output_dir: Union[str, Path],
        package_name: Optional[str] = None,
        recursive: bool = True
    ) -> Dict[str, str]:
        """
        Transpile all Python files in a directory to Go.
        
        Args:
            source_dir: Source directory containing Python files
            output_dir: Output directory for Go files
            package_name: Optional base package name
            recursive: Whether to process subdirectories
            
        Returns:
            Dict mapping source paths to output paths
        """
        source_dir = Path(source_dir)
        output_dir = Path(output_dir)
        
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        pattern = "**/*.py" if recursive else "*.py"
        
        for py_file in source_dir.glob(pattern):
            # Skip __pycache__ and hidden files
            if "__pycache__" in str(py_file) or py_file.name.startswith("."):
                continue
            
            # Skip __init__.py files (handled differently in Go)
            if py_file.name == "__init__.py":
                continue
            
            # Calculate relative path and output path
            rel_path = py_file.relative_to(source_dir)
            go_file = output_dir / rel_path.with_suffix(".go")
            
            # Determine package name from directory
            if py_file.parent == source_dir:
                pkg = package_name or self.package_name
            else:
                pkg = py_file.parent.name.replace("-", "_")
            
            try:
                self.transpile_file(py_file, go_file, pkg)
                results[str(py_file)] = str(go_file)
                logger.info(f"Transpiled: {py_file} -> {go_file}")
            except Exception as e:
                logger.error(f"Failed to transpile {py_file}: {e}")
                results[str(py_file)] = f"ERROR: {e}"
        
        return results
    
    def transpile_code(
        self,
        code: str,
        package_name: Optional[str] = None
    ) -> str:
        """
        Transpile Python code string to Go.
        
        Args:
            code: Python source code
            package_name: Optional package name
            
        Returns:
            Generated Go source code
        """
        # Store source for body transpilation
        self._current_source = code
        
        module = self.parser.parse_code(code)
        return self._transpile_module(module, package_name or self.package_name)
    
    def _transpile_module(self, module: Module, package_name: str) -> str:
        """Transpile a parsed Python module to Go code."""
        generator = GoCodeGenerator(package_name)
        content_blocks = []
        
        # Register custom types from classes in the module
        for cls in module.classes:
            self.type_mapper.register_custom_type(cls.name, f"*{cls.name}")
        
        # Process imports - add fmt by default for error handling
        generator.add_import("fmt")
        
        for imp in module.imports:
            go_import = generator.map_python_import(imp.module.split(".")[0])
            if go_import:
                generator.add_import(go_import)
        
        # Process constants/module-level variables
        for const in module.constants:
            block = self._transpile_constant(const, generator)
            if block:
                content_blocks.append(block)
        
        for var in module.variables:
            # Skip if already in constants
            if not any(c.name == var.name for c in module.constants):
                block = self._transpile_variable(var, generator)
                if block:
                    content_blocks.append(block)
        
        # Process classes (structs)
        for cls in module.classes:
            block = self._transpile_class(cls, generator)
            content_blocks.append(block)
        
        # Process standalone functions
        for func in module.functions:
            block = self._transpile_function(func, generator)
            content_blocks.append(block)
        
        return generator.generate_full_file(content_blocks)
    
    def _transpile_class(self, cls: Class, generator: GoCodeGenerator) -> str:
        """Transpile a Python class to a Go struct with methods."""
        parts = []
        
        # Build struct fields from instance variables and __init__ params
        fields = []
        seen_fields: Set[str] = set()
        
        for var in cls.instance_variables:
            if var.name not in seen_fields:
                go_type = self.type_mapper.map_type(var.type_annotation) or "interface{}"
                fields.append((var.name, go_type))
                seen_fields.add(var.name)
        
        # Generate struct
        doc = cls.docstring.summary if cls.docstring else None
        struct_code = generator.generate_struct(cls.name, fields, doc)
        parts.append(struct_code)
        
        # Generate constructor function
        constructor = self._generate_constructor(cls, generator)
        if constructor:
            parts.append(constructor)
        
        # Generate methods
        for method in cls.methods:
            if method.name.startswith("__") and method.name.endswith("__"):
                # Skip dunder methods except __str__
                if method.name == "__str__":
                    method_code = self._transpile_str_method(cls, method, generator)
                    parts.append(method_code)
                continue
            
            method_code = self._transpile_method(cls, method, generator)
            parts.append(method_code)
        
        return "\n\n".join(parts)
    
    def _generate_constructor(self, cls: Class, generator: GoCodeGenerator) -> Optional[str]:
        """Generate a New* constructor function for a struct."""
        init_method = next(
            (m for m in cls.methods if m.name == "__init__"),
            None
        )
        
        # Build constructor parameters (skip 'self')
        params = []
        if init_method:
            for param in init_method.parameters:
                if param.name != "self":
                    go_type = self.type_mapper.map_type(param.type_annotation) or "interface{}"
                    params.append((param.name, go_type))
        
        # Build struct initialization
        body_lines = [f"return &{cls.name}{{"]
        
        for param_name, _ in params:
            # Capitalize for struct field
            field_name = param_name[0].upper() + param_name[1:] if param_name else param_name
            body_lines.append(f"\t{field_name}: {param_name},")
        
        body_lines.append("}")
        
        return generator.generate_function(
            name=f"New{cls.name}",
            params=params,
            return_type=f"*{cls.name}",
            body=body_lines,
            comment=f"creates a new {cls.name} instance"
        )
    
    def _transpile_method(
        self,
        cls: Class,
        method: Method,
        generator: GoCodeGenerator
    ) -> str:
        """Transpile a Python method to a Go receiver method."""
        # Skip 'self' parameter
        params = []
        for param in method.parameters:
            if param.name != "self":
                go_type = self.type_mapper.map_type(param.type_annotation) or "interface{}"
                params.append((param.name, go_type))
        
        # Get return type
        return_type = self.type_mapper.map_type(method.return_type) if method.return_type else None
        
        # Build method body (placeholder)
        body = self._build_function_body(method, return_type)
        
        # Receiver
        receiver_var = cls.name[0].lower()
        receiver = (receiver_var, f"*{cls.name}")
        
        # Capitalize method name for export
        method_name = method.name[0].upper() + method.name[1:] if method.name else method.name
        
        doc = method.docstring.summary if method.docstring else None
        
        return generator.generate_function(
            name=method_name,
            params=params,
            return_type=return_type,
            body=body,
            receiver=receiver,
            comment=doc
        )
    
    def _transpile_str_method(
        self,
        cls: Class,
        method: Method,
        generator: GoCodeGenerator
    ) -> str:
        """Transpile __str__ to String() method."""
        receiver_var = cls.name[0].lower()
        receiver = (receiver_var, f"*{cls.name}")
        
        # Build a basic string representation
        body = [f'return fmt.Sprintf("%s{{}}", {receiver_var})']
        
        return generator.generate_function(
            name="String",
            params=[],
            return_type="string",
            body=body,
            receiver=receiver,
            comment="returns string representation"
        )
    
    def _transpile_function(self, func: Function, generator: GoCodeGenerator) -> str:
        """Transpile a Python function to a Go function."""
        # Build parameters
        params = []
        for param in func.parameters:
            go_type = self.type_mapper.map_type(param.type_annotation) or "interface{}"
            params.append((param.name, go_type))
        
        # Get return type
        return_type = self.type_mapper.map_type(func.return_type) if func.return_type else None
        
        # Build function body
        body = self._build_function_body(func, return_type)
        
        # Capitalize if should be exported (public Python functions)
        func_name = func.name
        if not func_name.startswith("_"):
            func_name = func_name[0].upper() + func_name[1:] if func_name else func_name
        
        doc = func.docstring.summary if func.docstring else None
        
        return generator.generate_function(
            name=func_name,
            params=params,
            return_type=return_type,
            body=body,
            comment=doc
        )
    
    def _build_function_body(
        self,
        func: Union[Function, Method],
        return_type: Optional[str],
        receiver_name: Optional[str] = None
    ) -> List[str]:
        """
        Build function body by transpiling Python source.
        
        Attempts to transpile the actual Python function body to Go.
        Falls back to placeholder if source is unavailable or transpilation fails.
        """
        # Try to transpile actual function body
        if self._current_source:
            try:
                # Reset body transpiler state
                self.body_transpiler.local_vars.clear()
                self.body_transpiler.current_indent = 1  # Start with one level of indent
                
                # Update receiver name for self references
                if receiver_name:
                    # Dynamically update how 'self' is mapped
                    pass
                
                body_lines = self.body_transpiler.transpile_body(
                    self._current_source,
                    func.name
                )
                
                if body_lines and not all(
                    line.strip().startswith("// TODO") for line in body_lines
                ):
                    return body_lines
            except Exception as e:
                logger.debug(f"Body transpilation failed for {func.name}: {e}")
        
        # Fallback to placeholder
        if not return_type:
            return ["\t// TODO: Implement function logic"]
        
        zero_value = self.type_mapper.get_zero_value(return_type)
        
        return [
            "\t// TODO: Implement function logic",
            f"\treturn {zero_value}"
        ]
    
    def _transpile_constant(self, const: Variable, generator: GoCodeGenerator) -> str:
        """Transpile a Python constant to a Go const."""
        go_type = self.type_mapper.map_type(const.type_annotation)
        value = self._convert_value(const.value)
        
        doc = None
        if const.name.isupper():
            # Standard Python constant naming
            pass
        
        return generator.generate_const(const.name, value, go_type)
    
    def _transpile_variable(self, var: Variable, generator: GoCodeGenerator) -> str:
        """Transpile a Python variable to a Go var."""
        go_type = self.type_mapper.map_type(var.type_annotation) or "interface{}"
        value = self._convert_value(var.value) if var.value else None
        
        return generator.generate_var(var.name, go_type, value)
    
    def _convert_value(self, value: Optional[str]) -> str:
        """Convert a Python value literal to Go."""
        if value is None:
            return "nil"
        
        value = str(value).strip()
        
        # Boolean conversion
        if value == "True":
            return "true"
        if value == "False":
            return "false"
        if value == "None":
            return "nil"
        
        # String detection (simple)
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            # Convert to double quotes for Go
            inner = value[1:-1]
            return f'"{inner}"'
        
        # List to slice
        if value.startswith("[") and value.endswith("]"):
            # Simplified - just mark as TODO
            return "nil // TODO: convert list"
        
        # Dict to map
        if value.startswith("{") and value.endswith("}"):
            return "nil // TODO: convert dict"
        
        # Numbers and other literals pass through
        return value
