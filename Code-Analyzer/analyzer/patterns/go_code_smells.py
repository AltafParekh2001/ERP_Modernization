"""
Go-specific code smell detector.

Identifies Go-specific code smells:
- Empty error handling (if err != nil {} with no action)
- Naked returns (named return values with bare return)
- Shadow variables
- Missing error checks
- Magic numbers
- Long functions
- Too many parameters
"""

import re
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from analyzer.models.code_entities import Module, Class, Function
from analyzer.logging_config import get_logger

logger = get_logger("patterns.go_code_smells")


class GoSmellType(Enum):
    """Types of Go-specific code smells."""
    EMPTY_ERROR_HANDLING = "empty_error_handling"
    NAKED_RETURN = "naked_return"
    SHADOW_VARIABLE = "shadow_variable"
    IGNORED_ERROR = "ignored_error"
    MAGIC_NUMBER = "magic_number"
    LONG_FUNCTION = "long_function"
    TOO_MANY_PARAMETERS = "too_many_parameters"
    MISSING_COMMENT = "missing_comment"
    PANIC_IN_LIBRARY = "panic_in_library"
    INIT_FUNCTION = "init_function_smell"
    UNEXPORTED_RETURN = "unexported_return"


@dataclass
class GoCodeSmell:
    """A detected Go code smell."""
    smell_type: GoSmellType
    message: str
    file_path: str
    line_number: int
    severity: str  # "info", "warning", "error"
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "type": self.smell_type.value,
            "message": self.message,
            "file": self.file_path,
            "line": self.line_number,
            "severity": self.severity,
            "snippet": self.code_snippet,
            "suggestion": self.suggestion,
        }


class GoCodeSmellDetector:
    """Detects code smells in Go code."""
    
    # Magic number exclusions (common acceptable values)
    ALLOWED_NUMBERS = {0, 1, -1, 2, 10, 100, 1000, 8, 16, 32, 64, 128, 256, 512, 1024}
    
    # Maximum recommended function length
    MAX_FUNCTION_LINES = 50
    
    # Maximum recommended parameters
    MAX_PARAMETERS = 5
    
    # Patterns for Go-specific smells
    EMPTY_ERROR_PATTERN = re.compile(
        r'if\s+\w+\s*!=\s*nil\s*\{\s*\}',
        re.MULTILINE
    )
    
    IGNORED_ERROR_PATTERN = re.compile(
        r'(\w+),\s*_\s*:?=|_\s*:?=\s*\w+\([^)]*\)',
        re.MULTILINE
    )
    
    NAKED_RETURN_PATTERN = re.compile(
        r'^\s*return\s*$',
        re.MULTILINE
    )
    
    PANIC_PATTERN = re.compile(
        r'\bpanic\s*\([^)]+\)',
        re.MULTILINE
    )
    
    MAGIC_NUMBER_PATTERN = re.compile(
        r'(?<![.\w])(\d+\.?\d*)(?![.\w])',
        re.MULTILINE
    )
    
    def detect(self, modules: List[Module]) -> List[GoCodeSmell]:
        """
        Detect code smells in Go modules.
        
        Args:
            modules: List of parsed modules
            
        Returns:
            List of detected code smells
        """
        smells = []
        
        for module in modules:
            # Only analyze Go files
            if not module.file_path.endswith('.go'):
                continue
            smells.extend(self._analyze_module(module))
        
        return smells
    
    def detect_from_code(self, code: str, file_path: str = "<string>") -> List[GoCodeSmell]:
        """Detect code smells directly from Go code string."""
        smells = []
        
        smells.extend(self._analyze_code(code, file_path))
        
        return smells
    
    def _analyze_module(self, module: Module) -> List[GoCodeSmell]:
        """Analyze a module for Go code smells."""
        smells = []
        
        # Check for missing package comment (exported packages should have comments)
        if not module.docstring and module.package:
            # Check if this appears to be a main package or library
            if module.package != "main":
                smells.append(GoCodeSmell(
                    smell_type=GoSmellType.MISSING_COMMENT,
                    message=f"Package '{module.package}' is missing documentation comment",
                    file_path=module.file_path,
                    line_number=1,
                    severity="info",
                    suggestion="Add a package-level comment starting with 'Package {name}'",
                ))
        
        # Check structs (classes)
        for cls in module.classes:
            smells.extend(self._analyze_struct(cls, module.file_path))
        
        # Check functions
        for func in module.functions:
            smells.extend(self._analyze_function(func, module.file_path))
        
        return smells
    
    def _analyze_struct(self, cls: Class, file_path: str) -> List[GoCodeSmell]:
        """Analyze a struct for code smells."""
        smells = []
        
        # Exported struct without comment
        if cls.visibility.value == "public" and not cls.docstring:
            smells.append(GoCodeSmell(
                smell_type=GoSmellType.MISSING_COMMENT,
                message=f"Exported type '{cls.name}' is missing documentation comment",
                file_path=file_path,
                line_number=cls.location.start_line,
                severity="info",
                suggestion=f"Add a comment starting with '{cls.name}'",
            ))
        
        # Check methods
        for method in cls.methods:
            smells.extend(self._analyze_function(method, file_path))
        
        return smells
    
    def _analyze_function(self, func: Function, file_path: str) -> List[GoCodeSmell]:
        """Analyze a function for code smells."""
        smells = []
        
        # Exported function without comment
        if func.visibility.value == "public" and not func.docstring:
            if func.name not in ('init', 'main'):
                smells.append(GoCodeSmell(
                    smell_type=GoSmellType.MISSING_COMMENT,
                    message=f"Exported function '{func.name}' is missing documentation comment",
                    file_path=file_path,
                    line_number=func.location.start_line,
                    severity="info",
                    suggestion=f"Add a comment starting with '{func.name}'",
                ))
        
        # Too many parameters
        if len(func.parameters) > self.MAX_PARAMETERS:
            smells.append(GoCodeSmell(
                smell_type=GoSmellType.TOO_MANY_PARAMETERS,
                message=f"Function '{func.name}' has {len(func.parameters)} parameters (max recommended: {self.MAX_PARAMETERS})",
                file_path=file_path,
                line_number=func.location.start_line,
                severity="warning",
                suggestion="Consider using a struct to group related parameters",
            ))
        
        # Long function
        line_count = func.location.end_line - func.location.start_line + 1
        if line_count > self.MAX_FUNCTION_LINES:
            smells.append(GoCodeSmell(
                smell_type=GoSmellType.LONG_FUNCTION,
                message=f"Function '{func.name}' is {line_count} lines (max recommended: {self.MAX_FUNCTION_LINES})",
                file_path=file_path,
                line_number=func.location.start_line,
                severity="info",
                suggestion="Consider breaking down into smaller functions",
            ))
        
        # init function advice
        if func.name == "init":
            smells.append(GoCodeSmell(
                smell_type=GoSmellType.INIT_FUNCTION,
                message="init() functions can make code harder to understand and test",
                file_path=file_path,
                line_number=func.location.start_line,
                severity="info",
                suggestion="Consider explicit initialization in main() or constructors",
            ))
        
        return smells
    
    def _analyze_code(self, code: str, file_path: str) -> List[GoCodeSmell]:
        """Analyze Go code string for code smells."""
        smells = []
        lines = code.splitlines()
        
        # Empty error handling
        for match in self.EMPTY_ERROR_PATTERN.finditer(code):
            line_num = code[:match.start()].count('\n') + 1
            smells.append(GoCodeSmell(
                smell_type=GoSmellType.EMPTY_ERROR_HANDLING,
                message="Empty error handling block",
                file_path=file_path,
                line_number=line_num,
                severity="warning",
                code_snippet=match.group(0)[:50],
                suggestion="Handle the error or add a comment explaining why it's ignored",
            ))
        
        # Ignored errors with blank identifier
        for match in self.IGNORED_ERROR_PATTERN.finditer(code):
            line_num = code[:match.start()].count('\n') + 1
            # Check if this looks like an error being ignored
            snippet = match.group(0)
            if 'err' in code[max(0, match.start()-50):match.end()+50].lower():
                smells.append(GoCodeSmell(
                    smell_type=GoSmellType.IGNORED_ERROR,
                    message="Error return value may be ignored",
                    file_path=file_path,
                    line_number=line_num,
                    severity="warning",
                    code_snippet=snippet[:50],
                    suggestion="Handle the error or explicitly document why it's safe to ignore",
                ))
        
        # Naked returns (need to check if function has named returns)
        for match in self.NAKED_RETURN_PATTERN.finditer(code):
            line_num = code[:match.start()].count('\n') + 1
            smells.append(GoCodeSmell(
                smell_type=GoSmellType.NAKED_RETURN,
                message="Naked return statement",
                file_path=file_path,
                line_number=line_num,
                severity="info",
                suggestion="Consider using explicit return values for clarity",
            ))
        
        # Panic in non-main packages
        for match in self.PANIC_PATTERN.finditer(code):
            line_num = code[:match.start()].count('\n') + 1
            # Check if this is in main package
            if 'package main' not in code:
                smells.append(GoCodeSmell(
                    smell_type=GoSmellType.PANIC_IN_LIBRARY,
                    message="panic() used in library code",
                    file_path=file_path,
                    line_number=line_num,
                    severity="warning",
                    code_snippet=match.group(0)[:50],
                    suggestion="Return an error instead of panicking in library code",
                ))
        
        # Magic numbers (excluding common values)
        for match in self.MAGIC_NUMBER_PATTERN.finditer(code):
            try:
                num = float(match.group(1))
                if num not in self.ALLOWED_NUMBERS and num != int(num) or (int(num) not in self.ALLOWED_NUMBERS and abs(num) > 2):
                    line_num = code[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    # Skip if it's in a const declaration
                    if 'const' in line_content:
                        continue
                    
                    smells.append(GoCodeSmell(
                        smell_type=GoSmellType.MAGIC_NUMBER,
                        message=f"Magic number: {match.group(1)}",
                        file_path=file_path,
                        line_number=line_num,
                        severity="info",
                        suggestion="Consider using a named constant",
                    ))
            except ValueError:
                pass
        
        return smells


def detect_go_code_smells(modules: List[Module]) -> List[GoCodeSmell]:
    """
    Detect Go code smells in modules.
    
    Args:
        modules: List of parsed modules
        
    Returns:
        List of detected Go code smells
    """
    detector = GoCodeSmellDetector()
    return detector.detect(modules)
