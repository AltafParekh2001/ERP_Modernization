"""
Go-specific complexity metrics.

Calculates complexity metrics for Go code:
- Cyclomatic complexity
- Cognitive complexity
- Nesting depth
- Lines of code (adapted for Go comment syntax)
"""

import re
from typing import Optional

from analyzer.models.metrics import ComplexityMetrics
from analyzer.logging_config import get_logger

logger = get_logger("metrics.go_complexity")


class GoCyclomaticComplexityCalculator:
    """Calculates cyclomatic complexity for Go code."""
    
    # Decision point patterns
    IF_PATTERN = re.compile(r'\bif\s+', re.MULTILINE)
    ELSE_IF_PATTERN = re.compile(r'\}\s*else\s+if\s+', re.MULTILINE)
    FOR_PATTERN = re.compile(r'\bfor\s+', re.MULTILINE)
    SWITCH_PATTERN = re.compile(r'\bswitch\s+', re.MULTILINE)
    CASE_PATTERN = re.compile(r'\bcase\s+', re.MULTILINE)
    SELECT_PATTERN = re.compile(r'\bselect\s*\{', re.MULTILINE)
    AND_PATTERN = re.compile(r'\s&&\s', re.MULTILINE)
    OR_PATTERN = re.compile(r'\s\|\|\s', re.MULTILINE)
    
    def calculate(self, code: str) -> int:
        """Calculate cyclomatic complexity for Go code string."""
        # Base complexity
        complexity = 1
        
        # Remove comments to avoid false matches
        code = self._remove_comments(code)
        
        # Count decision points
        complexity += len(self.IF_PATTERN.findall(code))
        complexity += len(self.FOR_PATTERN.findall(code))
        complexity += len(self.SWITCH_PATTERN.findall(code))
        complexity += len(self.SELECT_PATTERN.findall(code))
        
        # Case statements add to complexity (each case is a branch)
        complexity += len(self.CASE_PATTERN.findall(code))
        
        # Boolean operators add decision points
        complexity += len(self.AND_PATTERN.findall(code))
        complexity += len(self.OR_PATTERN.findall(code))
        
        return complexity
    
    def _remove_comments(self, code: str) -> str:
        """Remove comments from Go code."""
        # Remove line comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        # Remove block comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code


class GoCognitiveComplexityCalculator:
    """Calculates cognitive complexity for Go code."""
    
    # Patterns that increase cognitive complexity
    NESTING_PATTERNS = [
        (re.compile(r'\bif\s+'), 1),
        (re.compile(r'\bfor\s+'), 1),
        (re.compile(r'\bswitch\s+'), 1),
        (re.compile(r'\bselect\s*\{'), 1),
    ]
    
    # Patterns that add but don't increase nesting
    FLAT_PATTERNS = [
        (re.compile(r'\belse\s+if\s+'), 1),  # else if adds 1 but doesn't nest
        (re.compile(r'\belse\s*\{'), 1),
        (re.compile(r'\s&&\s'), 1),
        (re.compile(r'\s\|\|\s'), 1),
        (re.compile(r'\bbreak\b'), 1),
        (re.compile(r'\bcontinue\b'), 1),
        (re.compile(r'\bgoto\b'), 1),
    ]
    
    def calculate(self, code: str) -> int:
        """Calculate cognitive complexity for Go code string."""
        # Remove comments
        code = self._remove_comments(code)
        lines = code.splitlines()
        
        complexity = 0
        nesting_level = 0
        brace_depth = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Track brace depth for nesting
            open_braces = stripped.count('{')
            close_braces = stripped.count('}')
            
            # Check for nesting patterns (add 1 + nesting penalty)
            for pattern, base in self.NESTING_PATTERNS:
                if pattern.search(stripped):
                    complexity += base + nesting_level
            
            # Check for flat patterns (add without nesting penalty)
            for pattern, base in self.FLAT_PATTERNS:
                count = len(pattern.findall(stripped))
                complexity += base * count
            
            # Update brace depth
            brace_depth += open_braces - close_braces
            
            # Update nesting level based on control structures
            if any(pattern.search(stripped) for pattern, _ in self.NESTING_PATTERNS):
                nesting_level += 1
            
            # Decrease nesting when we close braces
            if close_braces > 0 and nesting_level > 0:
                nesting_level = max(0, nesting_level - close_braces)
        
        return complexity
    
    def _remove_comments(self, code: str) -> str:
        """Remove comments from Go code."""
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code


class GoNestingDepthCalculator:
    """Calculates maximum nesting depth for Go code."""
    
    def calculate(self, code: str) -> int:
        """Calculate maximum nesting depth for Go code string."""
        # Remove comments
        code = self._remove_comments(code)
        
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _remove_comments(self, code: str) -> str:
        """Remove comments from Go code."""
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code


class GoLOCCalculator:
    """Calculates lines of code metrics for Go."""
    
    def calculate(self, code: str) -> dict:
        """
        Calculate LOC metrics for Go code.
        
        Returns:
            dict with total, blank, comment, and code line counts
        """
        lines = code.splitlines()
        
        total = len(lines)
        blank = 0
        comment = 0
        code_lines = 0
        
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Empty line
            if not stripped:
                blank += 1
                continue
            
            # Handle block comments
            if in_block_comment:
                comment += 1
                if '*/' in stripped:
                    in_block_comment = False
                continue
            
            # Start of block comment
            if stripped.startswith('/*'):
                comment += 1
                if '*/' not in stripped:
                    in_block_comment = True
                continue
            
            # Line comment
            if stripped.startswith('//'):
                comment += 1
                continue
            
            # Code line
            code_lines += 1
        
        return {
            'total': total,
            'blank': blank,
            'comment': comment,
            'code': code_lines,
        }


def calculate_go_complexity(code: Optional[str] = None) -> ComplexityMetrics:
    """
    Calculate complexity metrics for Go code.
    
    Args:
        code: Go source code string
        
    Returns:
        ComplexityMetrics object
    """
    if code is None:
        return ComplexityMetrics()
    
    cyclomatic_calc = GoCyclomaticComplexityCalculator()
    cognitive_calc = GoCognitiveComplexityCalculator()
    nesting_calc = GoNestingDepthCalculator()
    
    return ComplexityMetrics(
        cyclomatic=cyclomatic_calc.calculate(code),
        cognitive=cognitive_calc.calculate(code),
        max_nesting_depth=nesting_calc.calculate(code),
    )


def calculate_go_loc(code: str) -> dict:
    """
    Calculate LOC metrics for Go code.
    
    Args:
        code: Go source code string
        
    Returns:
        dict with LOC metrics
    """
    calc = GoLOCCalculator()
    return calc.calculate(code)
