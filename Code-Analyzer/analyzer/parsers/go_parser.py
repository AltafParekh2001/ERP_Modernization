"""
Go language parser.

Parses Go source code to extract code entities like:
- Packages
- Imports
- Structs (mapped to Class)
- Interfaces
- Functions and Methods
- Variables and Constants
"""

import re
from pathlib import Path
from typing import Optional, Union, List, Tuple

from analyzer.parsers.base import BaseParser
from analyzer.models.code_entities import (
    Module, Class, Function, Method, Variable, Parameter,
    Import, Decorator, Docstring, CodeLocation,
    EntityType, Visibility
)
from analyzer.exceptions import ParsingError, SyntaxParsingError, EncodingError
from analyzer.utils import read_file
from analyzer.logging_config import get_logger

logger = get_logger("parsers.go")


class GoParser(BaseParser):
    """Parser for Go source code using regex-based parsing."""
    
    @property
    def supported_extensions(self) -> list[str]:
        return [".go"]
    
    @property
    def language(self) -> str:
        return "go"
    
    def parse_file(self, path: Union[str, Path]) -> Module:
        """Parse a Go source file."""
        path = Path(path).resolve()
        
        try:
            source = read_file(path)
        except UnicodeDecodeError as e:
            raise EncodingError(f"Cannot decode file {path}: {e}")
        
        module = self.parse_code(source, filename=str(path))
        module.file_path = str(path)
        return module
    
    def parse_code(self, code: str, filename: str = "<string>") -> Module:
        """Parse Go source code string."""
        try:
            visitor = GoCodeVisitor(code, filename)
            return visitor.parse()
        except Exception as e:
            logger.error(f"Failed to parse Go code in {filename}: {e}")
            raise SyntaxParsingError(f"Go parsing error: {e}")


class GoCodeVisitor:
    """Regex-based visitor that extracts all code entities from Go source."""
    
    # Regex patterns for Go constructs
    PACKAGE_PATTERN = re.compile(r'^package\s+(\w+)', re.MULTILINE)
    
    # Single import: import "fmt"
    SINGLE_IMPORT_PATTERN = re.compile(r'^import\s+"([^"]+)"', re.MULTILINE)
    
    # Grouped imports: import ( "fmt" \n "os" )
    GROUPED_IMPORT_PATTERN = re.compile(
        r'^import\s*\(\s*((?:[^)]+))\)',
        re.MULTILINE | re.DOTALL
    )
    
    # Struct definition
    STRUCT_PATTERN = re.compile(
        r'^type\s+(\w+)\s+struct\s*\{([^}]*)\}',
        re.MULTILINE | re.DOTALL
    )
    
    # Interface definition
    INTERFACE_PATTERN = re.compile(
        r'^type\s+(\w+)\s+interface\s*\{([^}]*)\}',
        re.MULTILINE | re.DOTALL
    )
    
    # Function definition (not a method)
    FUNCTION_PATTERN = re.compile(
        r'^func\s+(\w+)\s*\(([^)]*)\)\s*(?:\(([^)]*)\)|(\w+))?\s*\{',
        re.MULTILINE
    )
    
    # Method definition (has receiver)
    METHOD_PATTERN = re.compile(
        r'^func\s*\((\w+)\s+\*?(\w+)\)\s+(\w+)\s*\(([^)]*)\)\s*(?:\(([^)]*)\)|(\w+))?\s*\{',
        re.MULTILINE
    )
    
    # Constant definitions
    CONST_PATTERN = re.compile(
        r'^const\s+(\w+)(?:\s+\w+)?\s*=\s*(.+)$',
        re.MULTILINE
    )
    
    # Const block
    CONST_BLOCK_PATTERN = re.compile(
        r'^const\s*\(\s*((?:[^)]+))\)',
        re.MULTILINE | re.DOTALL
    )
    
    # Variable definitions
    VAR_PATTERN = re.compile(
        r'^var\s+(\w+)(?:\s+(\w+))?\s*(?:=\s*(.+))?$',
        re.MULTILINE
    )
    
    # Var block
    VAR_BLOCK_PATTERN = re.compile(
        r'^var\s*\(\s*((?:[^)]+))\)',
        re.MULTILINE | re.DOTALL
    )
    
    # Comment patterns
    LINE_COMMENT_PATTERN = re.compile(r'//\s*(.*)$', re.MULTILINE)
    BLOCK_COMMENT_PATTERN = re.compile(r'/\*\s*(.*?)\s*\*/', re.DOTALL)
    
    def __init__(self, source: str, filename: str):
        self.source = source
        self.source_lines = source.splitlines()
        self.filename = filename
        self.current_class: Optional[Class] = None
        
        # Store parsed entities
        self.package_name: str = ""
        self.imports: List[Import] = []
        self.classes: List[Class] = []  # Structs and interfaces
        self.functions: List[Function] = []
        self.variables: List[Variable] = []
        self.constants: List[Variable] = []
    
    def parse(self) -> Module:
        """Parse the Go source and return a Module."""
        self._parse_package()
        self._parse_imports()
        self._parse_structs()
        self._parse_interfaces()
        self._parse_methods()
        self._parse_functions()
        self._parse_constants()
        self._parse_variables()
        
        # Create module
        location = CodeLocation(
            file_path=self.filename,
            start_line=1,
            end_line=len(self.source_lines),
            start_col=0,
            end_col=len(self.source_lines[-1]) if self.source_lines else 0,
        )
        
        module = Module(
            name=self.package_name or Path(self.filename).stem,
            entity_type=EntityType.MODULE,
            location=location,
            file_path=self.filename,
            package=self.package_name,
            imports=self.imports,
            classes=self.classes,
            functions=self.functions,
            variables=self.variables,
            constants=self.constants,
        )
        
        # Parse module docstring (comment at top before package)
        module.docstring = self._extract_module_docstring()
        
        return module
    
    def _parse_package(self) -> None:
        """Parse package declaration."""
        match = self.PACKAGE_PATTERN.search(self.source)
        if match:
            self.package_name = match.group(1)
    
    def _parse_imports(self) -> None:
        """Parse import statements."""
        # Single imports
        for match in self.SINGLE_IMPORT_PATTERN.finditer(self.source):
            import_path = match.group(1)
            line_num = self._get_line_number(match.start())
            
            self.imports.append(Import(
                module=import_path,
                name=import_path.split("/")[-1],  # Last part is usually the package name
                is_from_import=False,
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=line_num,
                ),
            ))
        
        # Grouped imports
        for match in self.GROUPED_IMPORT_PATTERN.finditer(self.source):
            imports_block = match.group(1)
            base_line = self._get_line_number(match.start())
            
            for i, line in enumerate(imports_block.strip().splitlines()):
                line = line.strip()
                if not line:
                    continue
                
                # Handle aliased imports: alias "path"
                alias_match = re.match(r'(\w+)\s+"([^"]+)"', line)
                if alias_match:
                    alias = alias_match.group(1)
                    import_path = alias_match.group(2)
                else:
                    # Regular import: "path"
                    path_match = re.match(r'"([^"]+)"', line)
                    if path_match:
                        import_path = path_match.group(1)
                        alias = None
                    else:
                        continue
                
                self.imports.append(Import(
                    module=import_path,
                    name=import_path.split("/")[-1],
                    alias=alias,
                    is_from_import=False,
                    location=CodeLocation(
                        file_path=self.filename,
                        start_line=base_line + i,
                        end_line=base_line + i,
                    ),
                ))
    
    def _parse_structs(self) -> None:
        """Parse struct definitions."""
        for match in self.STRUCT_PATTERN.finditer(self.source):
            name = match.group(1)
            body = match.group(2)
            line_num = self._get_line_number(match.start())
            end_line = self._get_line_number(match.end())
            
            # Parse struct fields as instance variables
            instance_vars = self._parse_struct_fields(body, line_num)
            
            # Get docstring (comment immediately before struct)
            docstring = self._get_preceding_comment(line_num)
            
            struct_class = Class(
                name=name,
                entity_type=EntityType.CLASS,
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=end_line,
                ),
                visibility=self._get_visibility(name),
                docstring=docstring,
                instance_variables=instance_vars,
                bases=[],
                methods=[],
            )
            
            self.classes.append(struct_class)
    
    def _parse_interfaces(self) -> None:
        """Parse interface definitions."""
        for match in self.INTERFACE_PATTERN.finditer(self.source):
            name = match.group(1)
            body = match.group(2)
            line_num = self._get_line_number(match.start())
            end_line = self._get_line_number(match.end())
            
            # Parse interface method signatures
            methods = self._parse_interface_methods(body, line_num, name)
            
            # Get docstring
            docstring = self._get_preceding_comment(line_num)
            
            interface_class = Class(
                name=name,
                entity_type=EntityType.CLASS,
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=end_line,
                ),
                visibility=self._get_visibility(name),
                docstring=docstring,
                is_abstract=True,  # Interfaces are abstract
                methods=methods,
                bases=[],
            )
            
            self.classes.append(interface_class)
    
    def _parse_functions(self) -> None:
        """Parse standalone function definitions."""
        for match in self.FUNCTION_PATTERN.finditer(self.source):
            # Skip if this is actually a method (has receiver)
            # Check if there's a receiver pattern before this
            prefix = self.source[max(0, match.start()-20):match.start()]
            if ')' in prefix and '(' in prefix:
                continue
            
            name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3) or match.group(4) or ""
            
            line_num = self._get_line_number(match.start())
            end_line = self._find_function_end(match.end())
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Get docstring
            docstring = self._get_preceding_comment(line_num)
            
            func = Function(
                name=name,
                entity_type=EntityType.FUNCTION,
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=end_line,
                ),
                visibility=self._get_visibility(name),
                docstring=docstring,
                parameters=parameters,
                return_type=return_type.strip() if return_type else None,
                is_async=False,
            )
            
            self.functions.append(func)
    
    def _parse_methods(self) -> None:
        """Parse method definitions (functions with receivers)."""
        for match in self.METHOD_PATTERN.finditer(self.source):
            receiver_name = match.group(1)
            receiver_type = match.group(2)
            method_name = match.group(3)
            params_str = match.group(4)
            return_type = match.group(5) or match.group(6) or ""
            
            line_num = self._get_line_number(match.start())
            end_line = self._find_function_end(match.end())
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Get docstring
            docstring = self._get_preceding_comment(line_num)
            
            method = Method(
                name=method_name,
                entity_type=EntityType.METHOD,
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=end_line,
                ),
                visibility=self._get_visibility(method_name),
                docstring=docstring,
                parameters=parameters,
                return_type=return_type.strip() if return_type else None,
                is_async=False,
            )
            
            # Find and attach to the correct struct/class
            for cls in self.classes:
                if cls.name == receiver_type:
                    cls.methods.append(method)
                    break
            else:
                # If no matching class found, add as standalone function
                # This can happen with forward declarations
                self.functions.append(Function(
                    name=f"{receiver_type}.{method_name}",
                    entity_type=EntityType.FUNCTION,
                    location=method.location,
                    visibility=method.visibility,
                    docstring=method.docstring,
                    parameters=method.parameters,
                    return_type=method.return_type,
                    is_async=False,
                ))
    
    def _parse_constants(self) -> None:
        """Parse constant definitions."""
        # Single constants
        for match in self.CONST_PATTERN.finditer(self.source):
            name = match.group(1)
            value = match.group(2).strip()
            line_num = self._get_line_number(match.start())
            
            self.constants.append(Variable(
                name=name,
                value=value,
                is_constant=True,
                visibility=self._get_visibility(name),
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=line_num,
                ),
            ))
        
        # Const blocks
        for match in self.CONST_BLOCK_PATTERN.finditer(self.source):
            block = match.group(1)
            base_line = self._get_line_number(match.start())
            
            for i, line in enumerate(block.strip().splitlines()):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                
                # Parse: name = value or name Type = value
                const_match = re.match(r'(\w+)(?:\s+\w+)?\s*=\s*(.+)', line)
                if const_match:
                    name = const_match.group(1)
                    value = const_match.group(2).strip()
                    
                    self.constants.append(Variable(
                        name=name,
                        value=value,
                        is_constant=True,
                        visibility=self._get_visibility(name),
                        location=CodeLocation(
                            file_path=self.filename,
                            start_line=base_line + i,
                            end_line=base_line + i,
                        ),
                    ))
    
    def _parse_variables(self) -> None:
        """Parse variable definitions."""
        # Single variables
        for match in self.VAR_PATTERN.finditer(self.source):
            name = match.group(1)
            type_ann = match.group(2)
            value = match.group(3)
            line_num = self._get_line_number(match.start())
            
            self.variables.append(Variable(
                name=name,
                type_annotation=type_ann,
                value=value.strip() if value else None,
                visibility=self._get_visibility(name),
                location=CodeLocation(
                    file_path=self.filename,
                    start_line=line_num,
                    end_line=line_num,
                ),
            ))
        
        # Var blocks
        for match in self.VAR_BLOCK_PATTERN.finditer(self.source):
            block = match.group(1)
            base_line = self._get_line_number(match.start())
            
            for i, line in enumerate(block.strip().splitlines()):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                
                var_match = re.match(r'(\w+)(?:\s+(\w+))?\s*(?:=\s*(.+))?', line)
                if var_match:
                    name = var_match.group(1)
                    type_ann = var_match.group(2)
                    value = var_match.group(3)
                    
                    self.variables.append(Variable(
                        name=name,
                        type_annotation=type_ann,
                        value=value.strip() if value else None,
                        visibility=self._get_visibility(name),
                        location=CodeLocation(
                            file_path=self.filename,
                            start_line=base_line + i,
                            end_line=base_line + i,
                        ),
                    ))
    
    def _parse_struct_fields(self, body: str, base_line: int) -> List[Variable]:
        """Parse struct fields into variables."""
        fields = []
        for i, line in enumerate(body.strip().splitlines()):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            
            # Parse: name Type `tag`
            field_match = re.match(r'(\w+)\s+(\S+)(?:\s+`([^`]+)`)?', line)
            if field_match:
                name = field_match.group(1)
                type_ann = field_match.group(2)
                
                fields.append(Variable(
                    name=name,
                    type_annotation=type_ann,
                    is_instance_variable=True,
                    visibility=self._get_visibility(name),
                    location=CodeLocation(
                        file_path=self.filename,
                        start_line=base_line + i + 1,
                        end_line=base_line + i + 1,
                    ),
                ))
        
        return fields
    
    def _parse_interface_methods(self, body: str, base_line: int, interface_name: str) -> List[Method]:
        """Parse interface method signatures."""
        methods = []
        for i, line in enumerate(body.strip().splitlines()):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            
            # Parse: MethodName(params) returnType
            method_match = re.match(r'(\w+)\s*\(([^)]*)\)\s*(?:\(([^)]*)\)|(\w+))?', line)
            if method_match:
                name = method_match.group(1)
                params_str = method_match.group(2)
                return_type = method_match.group(3) or method_match.group(4) or ""
                
                parameters = self._parse_parameters(params_str)
                
                methods.append(Method(
                    name=name,
                    entity_type=EntityType.METHOD,
                    location=CodeLocation(
                        file_path=self.filename,
                        start_line=base_line + i + 1,
                        end_line=base_line + i + 1,
                    ),
                    visibility=self._get_visibility(name),
                    parameters=parameters,
                    return_type=return_type.strip() if return_type else None,
                    is_abstract=True,
                ))
        
        return methods
    
    def _parse_parameters(self, params_str: str) -> List[Parameter]:
        """Parse function/method parameters."""
        params = []
        if not params_str.strip():
            return params
        
        # Split by comma, handling complex types
        parts = []
        depth = 0
        current = ""
        for char in params_str:
            if char in "([{":
                depth += 1
            elif char in ")]}":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append(current.strip())
                current = ""
                continue
            current += char
        if current.strip():
            parts.append(current.strip())
        
        # Parse each parameter
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Handle: name type or name, name type (grouped)
            tokens = part.split()
            if len(tokens) >= 2:
                # Last token is type, others are names
                type_ann = tokens[-1]
                names = tokens[:-1]
                for name in names:
                    name = name.rstrip(",")
                    params.append(Parameter(
                        name=name,
                        type_annotation=type_ann,
                    ))
            elif len(tokens) == 1:
                # Just a type (like in interface methods) or just a name
                params.append(Parameter(
                    name=tokens[0],
                ))
        
        return params
    
    def _find_function_end(self, start_pos: int) -> int:
        """Find the end line of a function by matching braces."""
        depth = 1
        pos = start_pos
        while pos < len(self.source) and depth > 0:
            char = self.source[pos]
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            pos += 1
        
        return self._get_line_number(pos)
    
    def _get_line_number(self, char_pos: int) -> int:
        """Get line number for character position."""
        return self.source[:char_pos].count('\n') + 1
    
    def _get_visibility(self, name: str) -> Visibility:
        """Determine visibility from name (Go uses capitalization)."""
        if name and name[0].isupper():
            return Visibility.PUBLIC
        return Visibility.PRIVATE
    
    def _get_preceding_comment(self, line_num: int) -> Optional[Docstring]:
        """Get comment immediately preceding a line."""
        if line_num <= 1:
            return None
        
        comments = []
        for i in range(line_num - 2, -1, -1):
            line = self.source_lines[i].strip()
            if line.startswith("//"):
                comments.insert(0, line[2:].strip())
            elif line.startswith("/*"):
                # Block comment start
                break
            elif line:
                # Non-comment, non-empty line
                break
        
        if comments:
            raw = "\n".join(comments)
            return Docstring(
                raw=raw,
                summary=comments[0] if comments else "",
                description="\n".join(comments[1:]) if len(comments) > 1 else "",
            )
        
        return None
    
    def _extract_module_docstring(self) -> Optional[Docstring]:
        """Extract package-level docstring (comment before package declaration)."""
        comments = []
        for line in self.source_lines:
            stripped = line.strip()
            if stripped.startswith("//"):
                comments.append(stripped[2:].strip())
            elif stripped.startswith("/*"):
                # Block comment - extract content
                match = self.BLOCK_COMMENT_PATTERN.search(self.source)
                if match:
                    comments.append(match.group(1).strip())
                break
            elif stripped.startswith("package"):
                break
            elif stripped:
                break
        
        if comments:
            raw = "\n".join(comments)
            return Docstring(
                raw=raw,
                summary=comments[0] if comments else "",
                description="\n".join(comments[1:]) if len(comments) > 1 else "",
            )
        
        return None
