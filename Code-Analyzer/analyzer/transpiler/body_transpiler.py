"""
Advanced code transpilation for Python to Go.

Handles transpilation of Python function bodies, control flow,
and complex constructs into equivalent Go code.
"""

import ast
import re
from typing import List, Optional, Set, Dict, Union


class BodyTranspiler:
    """
    Transpiles Python function/method bodies to Go code.
    
    Handles:
    - Variable assignments
    - Control flow (if/elif/else, for, while)
    - Return statements
    - Function calls
    - Error handling (try/except to error returns)
    - List comprehensions (converted to loops)
    """
    
    # Python to Go operator mappings
    OPERATOR_MAP = {
        'and': '&&',
        'or': '||',
        'not': '!',
        'True': 'true',
        'False': 'false',
        'None': 'nil',
        '==': '==',
        '!=': '!=',
        '<': '<',
        '>': '>',
        '<=': '<=',
        '>=': '>=',
        '+': '+',
        '-': '-',
        '*': '*',
        '/': '/',
        '%': '%',
        '//': '/',  # Integer division - Go / on ints is already int division
        '**': '',   # Power - needs math.Pow
    }
    
    # Python built-in to Go equivalent
    BUILTIN_MAP = {
        'print': 'fmt.Println',
        'len': 'len',
        'range': '',  # Handled specially in for loops
        'str': 'fmt.Sprintf("%v", {})',
        'int': 'int({})',
        'float': 'float64({})',
        'bool': 'bool({})',
        'append': 'append',
        'abs': 'math.Abs',
        'min': 'min',  # Go 1.21+
        'max': 'max',  # Go 1.21+
    }
    
    def __init__(self, type_mapper, indent: str = "\t"):
        """Initialize the body transpiler."""
        self.type_mapper = type_mapper
        self.indent = indent
        self.current_indent = 0
        self.local_vars: Set[str] = set()
        self.imports_needed: Set[str] = set()
    
    def transpile_body(self, source_code: str, func_name: str = "") -> List[str]:
        """
        Transpile a Python function body to Go.
        
        Args:
            source_code: Complete Python source code containing the function
            func_name: Optional function name to extract body from
            
        Returns:
            List of Go code lines for the function body
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return ["// TODO: Could not parse Python source"]
        
        # Find the function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not func_name or node.name == func_name:
                    return self._transpile_statements(node.body)
        
        # If no function found, try to transpile the whole thing as statements
        if hasattr(tree, 'body'):
            return self._transpile_statements(tree.body)
        
        return ["// TODO: Could not extract function body"]
    
    def _transpile_statements(self, statements: List[ast.stmt]) -> List[str]:
        """Transpile a list of AST statements to Go code lines."""
        lines = []
        for stmt in statements:
            stmt_lines = self._transpile_statement(stmt)
            lines.extend(stmt_lines)
        return lines
    
    def _transpile_statement(self, stmt: ast.stmt) -> List[str]:
        """Transpile a single statement to Go code."""
        lines = []
        indent = self.indent * self.current_indent
        
        if isinstance(stmt, ast.Return):
            if stmt.value:
                value = self._transpile_expr(stmt.value)
                lines.append(f"{indent}return {value}")
            else:
                lines.append(f"{indent}return")
        
        elif isinstance(stmt, ast.Assign):
            lines.extend(self._transpile_assign(stmt))
        
        elif isinstance(stmt, ast.AugAssign):
            lines.extend(self._transpile_aug_assign(stmt))
        
        elif isinstance(stmt, ast.AnnAssign):
            lines.extend(self._transpile_ann_assign(stmt))
        
        elif isinstance(stmt, ast.If):
            lines.extend(self._transpile_if(stmt))
        
        elif isinstance(stmt, ast.For):
            lines.extend(self._transpile_for(stmt))
        
        elif isinstance(stmt, ast.While):
            lines.extend(self._transpile_while(stmt))
        
        elif isinstance(stmt, ast.Expr):
            # Expression statement (e.g., function call)
            expr = self._transpile_expr(stmt.value)
            if expr:
                lines.append(f"{indent}{expr}")
        
        elif isinstance(stmt, ast.Pass):
            lines.append(f"{indent}// pass")
        
        elif isinstance(stmt, ast.Break):
            lines.append(f"{indent}break")
        
        elif isinstance(stmt, ast.Continue):
            lines.append(f"{indent}continue")
        
        elif isinstance(stmt, ast.Raise):
            lines.extend(self._transpile_raise(stmt))
        
        elif isinstance(stmt, ast.Try):
            lines.extend(self._transpile_try(stmt))
        
        elif isinstance(stmt, ast.With):
            lines.extend(self._transpile_with(stmt))
        
        elif isinstance(stmt, ast.FunctionDef):
            # Nested function - convert to closure
            lines.append(f"{indent}// Nested function: {stmt.name}")
            lines.append(f"{indent}{stmt.name} := func() {{")
            lines.append(f"{indent}{self.indent}// TODO: Implement nested function")
            lines.append(f"{indent}}}")
        
        else:
            lines.append(f"{indent}// TODO: Unhandled statement type: {type(stmt).__name__}")
        
        return lines
    
    def _transpile_assign(self, stmt: ast.Assign) -> List[str]:
        """Transpile an assignment statement."""
        lines = []
        indent = self.indent * self.current_indent
        value = self._transpile_expr(stmt.value)
        
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if var_name in self.local_vars:
                    lines.append(f"{indent}{var_name} = {value}")
                else:
                    lines.append(f"{indent}{var_name} := {value}")
                    self.local_vars.add(var_name)
            
            elif isinstance(target, ast.Tuple):
                # Multiple assignment: a, b = 1, 2
                names = [self._transpile_expr(elt) for elt in target.elts]
                lines.append(f"{indent}{', '.join(names)} := {value}")
                for name in names:
                    if name.isidentifier():
                        self.local_vars.add(name)
            
            elif isinstance(target, ast.Subscript):
                # Index assignment: arr[0] = value
                target_expr = self._transpile_expr(target)
                lines.append(f"{indent}{target_expr} = {value}")
            
            elif isinstance(target, ast.Attribute):
                # Attribute assignment: self.x = value
                target_expr = self._transpile_expr(target)
                lines.append(f"{indent}{target_expr} = {value}")
        
        return lines
    
    def _transpile_aug_assign(self, stmt: ast.AugAssign) -> List[str]:
        """Transpile an augmented assignment (+=, -=, etc.)."""
        indent = self.indent * self.current_indent
        target = self._transpile_expr(stmt.target)
        value = self._transpile_expr(stmt.value)
        op = self._get_aug_op(stmt.op)
        
        return [f"{indent}{target} {op}= {value}"]
    
    def _transpile_ann_assign(self, stmt: ast.AnnAssign) -> List[str]:
        """Transpile an annotated assignment."""
        indent = self.indent * self.current_indent
        
        if isinstance(stmt.target, ast.Name):
            var_name = stmt.target.id
            go_type = self.type_mapper.map_type(
                self._get_annotation_str(stmt.annotation)
            ) or "interface{}"
            
            if stmt.value:
                value = self._transpile_expr(stmt.value)
                return [f"{indent}var {var_name} {go_type} = {value}"]
            else:
                return [f"{indent}var {var_name} {go_type}"]
        
        return []
    
    def _transpile_if(self, stmt: ast.If) -> List[str]:
        """Transpile an if statement."""
        lines = []
        indent = self.indent * self.current_indent
        
        condition = self._transpile_expr(stmt.test)
        lines.append(f"{indent}if {condition} {{")
        
        self.current_indent += 1
        lines.extend(self._transpile_statements(stmt.body))
        self.current_indent -= 1
        
        # Handle elif and else
        if stmt.orelse:
            if len(stmt.orelse) == 1 and isinstance(stmt.orelse[0], ast.If):
                # elif
                elif_stmt = stmt.orelse[0]
                elif_cond = self._transpile_expr(elif_stmt.test)
                lines.append(f"{indent}}} else if {elif_cond} {{")
                
                self.current_indent += 1
                lines.extend(self._transpile_statements(elif_stmt.body))
                self.current_indent -= 1
                
                # Recursively handle more elif/else
                if elif_stmt.orelse:
                    nested = self._transpile_if(ast.If(
                        test=elif_stmt.test,
                        body=[],
                        orelse=elif_stmt.orelse
                    ))
                    # Skip the initial if, just get elif/else parts
                    for line in nested:
                        if line.strip().startswith("} else"):
                            lines.append(line)
                        elif self.current_indent > 0 or not line.strip().startswith("if"):
                            lines.append(line)
            else:
                # else
                lines.append(f"{indent}}} else {{")
                self.current_indent += 1
                lines.extend(self._transpile_statements(stmt.orelse))
                self.current_indent -= 1
        
        lines.append(f"{indent}}}")
        return lines
    
    def _transpile_for(self, stmt: ast.For) -> List[str]:
        """Transpile a for loop."""
        lines = []
        indent = self.indent * self.current_indent
        
        target = self._transpile_expr(stmt.target)
        iter_expr = stmt.iter
        
        # Handle range()
        if isinstance(iter_expr, ast.Call) and isinstance(iter_expr.func, ast.Name):
            if iter_expr.func.id == 'range':
                range_args = [self._transpile_expr(a) for a in iter_expr.args]
                
                if len(range_args) == 1:
                    # range(n)
                    lines.append(f"{indent}for {target} := 0; {target} < {range_args[0]}; {target}++ {{")
                elif len(range_args) == 2:
                    # range(start, end)
                    lines.append(f"{indent}for {target} := {range_args[0]}; {target} < {range_args[1]}; {target}++ {{")
                elif len(range_args) == 3:
                    # range(start, end, step)
                    step = range_args[2]
                    lines.append(f"{indent}for {target} := {range_args[0]}; {target} < {range_args[1]}; {target} += {step} {{")
                
                self.current_indent += 1
                lines.extend(self._transpile_statements(stmt.body))
                self.current_indent -= 1
                lines.append(f"{indent}}}")
                return lines
            
            elif iter_expr.func.id == 'enumerate':
                # enumerate(iterable)
                if iter_expr.args:
                    iterable = self._transpile_expr(iter_expr.args[0])
                    if isinstance(stmt.target, ast.Tuple) and len(stmt.target.elts) == 2:
                        idx = self._transpile_expr(stmt.target.elts[0])
                        val = self._transpile_expr(stmt.target.elts[1])
                        lines.append(f"{indent}for {idx}, {val} := range {iterable} {{")
                    else:
                        lines.append(f"{indent}for {target} := range {iterable} {{")
                    
                    self.current_indent += 1
                    lines.extend(self._transpile_statements(stmt.body))
                    self.current_indent -= 1
                    lines.append(f"{indent}}}")
                    return lines
        
        # Default: for ... range
        iterable = self._transpile_expr(iter_expr)
        
        if isinstance(stmt.target, ast.Tuple):
            # for k, v in dict.items()
            parts = [self._transpile_expr(elt) for elt in stmt.target.elts]
            lines.append(f"{indent}for {', '.join(parts)} := range {iterable} {{")
        else:
            lines.append(f"{indent}for _, {target} := range {iterable} {{")
        
        self.current_indent += 1
        lines.extend(self._transpile_statements(stmt.body))
        self.current_indent -= 1
        lines.append(f"{indent}}}")
        
        return lines
    
    def _transpile_while(self, stmt: ast.While) -> List[str]:
        """Transpile a while loop."""
        lines = []
        indent = self.indent * self.current_indent
        
        condition = self._transpile_expr(stmt.test)
        
        # while True -> for {}
        if condition == "true":
            lines.append(f"{indent}for {{")
        else:
            lines.append(f"{indent}for {condition} {{")
        
        self.current_indent += 1
        lines.extend(self._transpile_statements(stmt.body))
        self.current_indent -= 1
        lines.append(f"{indent}}}")
        
        return lines
    
    def _transpile_try(self, stmt: ast.Try) -> List[str]:
        """Transpile try/except to Go error handling pattern."""
        lines = []
        indent = self.indent * self.current_indent
        
        lines.append(f"{indent}// Python try/except converted to Go error handling")
        lines.append(f"{indent}func() {{")
        lines.append(f"{indent}{self.indent}defer func() {{")
        lines.append(f"{indent}{self.indent}{self.indent}if r := recover(); r != nil {{")
        
        # Add except handlers
        if stmt.handlers:
            for handler in stmt.handlers:
                if handler.name:
                    lines.append(f"{indent}{self.indent}{self.indent}{self.indent}{handler.name} := r")
                lines.append(f"{indent}{self.indent}{self.indent}{self.indent}// Handle: {self._get_exception_type(handler)}")
        
        lines.append(f"{indent}{self.indent}{self.indent}}}")
        lines.append(f"{indent}{self.indent}}}()")
        
        # Add try body
        self.current_indent += 1
        lines.extend(self._transpile_statements(stmt.body))
        self.current_indent -= 1
        
        lines.append(f"{indent}}}()")
        
        return lines
    
    def _transpile_raise(self, stmt: ast.Raise) -> List[str]:
        """Transpile raise to panic."""
        indent = self.indent * self.current_indent
        
        if stmt.exc:
            exc = self._transpile_expr(stmt.exc)
            return [f"{indent}panic({exc})"]
        return [f"{indent}panic(\"error\")"]
    
    def _transpile_with(self, stmt: ast.With) -> List[str]:
        """Transpile with statement to defer pattern."""
        lines = []
        indent = self.indent * self.current_indent
        
        for item in stmt.items:
            ctx = self._transpile_expr(item.context_expr)
            if item.optional_vars:
                var = self._transpile_expr(item.optional_vars)
                lines.append(f"{indent}{var} := {ctx}")
                lines.append(f"{indent}defer {var}.Close()")
            else:
                lines.append(f"{indent}defer {ctx}.Close()")
        
        lines.extend(self._transpile_statements(stmt.body))
        return lines
    
    def _transpile_expr(self, expr: ast.expr) -> str:
        """Transpile an expression to Go code."""
        if isinstance(expr, ast.Constant):
            return self._transpile_constant(expr.value)
        
        elif isinstance(expr, ast.Name):
            name = expr.id
            # Map Python builtins
            if name in ('True', 'False', 'None'):
                return self.OPERATOR_MAP.get(name, name)
            # Handle self -> receiver
            if name == 'self':
                return 's'  # Default receiver name
            return name
        
        elif isinstance(expr, ast.Attribute):
            value = self._transpile_expr(expr.value)
            attr = expr.attr
            # self.x -> s.X (capitalize for export)
            if value in ('s', 'self'):
                attr = attr[0].upper() + attr[1:] if attr else attr
                return f"s.{attr}"
            return f"{value}.{attr}"
        
        elif isinstance(expr, ast.BinOp):
            left = self._transpile_expr(expr.left)
            right = self._transpile_expr(expr.right)
            op = self._get_bin_op(expr.op)
            
            # Handle power operator
            if isinstance(expr.op, ast.Pow):
                self.imports_needed.add("math")
                return f"math.Pow({left}, {right})"
            
            return f"({left} {op} {right})"
        
        elif isinstance(expr, ast.UnaryOp):
            operand = self._transpile_expr(expr.operand)
            if isinstance(expr.op, ast.Not):
                return f"!{operand}"
            elif isinstance(expr.op, ast.USub):
                return f"-{operand}"
            elif isinstance(expr.op, ast.UAdd):
                return f"+{operand}"
            return operand
        
        elif isinstance(expr, ast.Compare):
            left = self._transpile_expr(expr.left)
            parts = [left]
            for op, comp in zip(expr.ops, expr.comparators):
                op_str = self._get_cmp_op(op)
                comp_str = self._transpile_expr(comp)
                parts.append(f"{op_str} {comp_str}")
            return " ".join(parts)
        
        elif isinstance(expr, ast.BoolOp):
            op = "&&" if isinstance(expr.op, ast.And) else "||"
            values = [self._transpile_expr(v) for v in expr.values]
            return f"({' {0} '.format(op).join(values)})"
        
        elif isinstance(expr, ast.Call):
            return self._transpile_call(expr)
        
        elif isinstance(expr, ast.Subscript):
            value = self._transpile_expr(expr.value)
            slice_val = self._transpile_slice(expr.slice)
            return f"{value}[{slice_val}]"
        
        elif isinstance(expr, ast.List):
            elts = [self._transpile_expr(e) for e in expr.elts]
            return f"[]interface{{{{{', '.join(elts)}}}}}"
        
        elif isinstance(expr, ast.Dict):
            pairs = []
            for k, v in zip(expr.keys, expr.values):
                if k:
                    key = self._transpile_expr(k)
                    val = self._transpile_expr(v)
                    pairs.append(f"{key}: {val}")
            return f"map[interface{{}}]interface{{{{{', '.join(pairs)}}}}}"
        
        elif isinstance(expr, ast.Tuple):
            # Go doesn't have tuples, use struct or multiple return
            elts = [self._transpile_expr(e) for e in expr.elts]
            return ", ".join(elts)
        
        elif isinstance(expr, ast.IfExp):
            # Ternary: x if cond else y
            test = self._transpile_expr(expr.test)
            body = self._transpile_expr(expr.body)
            orelse = self._transpile_expr(expr.orelse)
            return f"func() interface{{ if {test} {{ return {body} }} else {{ return {orelse} }} }}()"
        
        elif isinstance(expr, ast.Lambda):
            return "func() { /* lambda */ }"
        
        elif isinstance(expr, ast.ListComp):
            return self._transpile_list_comp(expr)
        
        elif isinstance(expr, ast.FormattedValue):
            # f-string part
            return self._transpile_expr(expr.value)
        
        elif isinstance(expr, ast.JoinedStr):
            # f-string
            return self._transpile_fstring(expr)
        
        return f"/* {type(expr).__name__} */"
    
    def _transpile_call(self, expr: ast.Call) -> str:
        """Transpile a function call."""
        args = [self._transpile_expr(a) for a in expr.args]
        
        if isinstance(expr.func, ast.Name):
            func_name = expr.func.id
            
            # Map Python builtins
            if func_name == 'print':
                self.imports_needed.add("fmt")
                return f"fmt.Println({', '.join(args)})"
            
            elif func_name == 'len':
                return f"len({args[0]})" if args else "0"
            
            elif func_name == 'str':
                self.imports_needed.add("fmt")
                return f'fmt.Sprintf("%v", {args[0]})' if args else '""'
            
            elif func_name == 'int':
                return f"int({args[0]})" if args else "0"
            
            elif func_name == 'float':
                return f"float64({args[0]})" if args else "0.0"
            
            elif func_name == 'append':
                if len(args) >= 2:
                    return f"append({args[0]}, {', '.join(args[1:])}...)"
                return f"append({', '.join(args)})"
            
            elif func_name == 'range':
                # Handled in for loop
                return f"/* range({', '.join(args)}) */"
            
            elif func_name == 'open':
                self.imports_needed.add("os")
                return f"os.Open({args[0]})" if args else "os.Open()"
            
            elif func_name in ('abs', 'min', 'max'):
                if func_name == 'abs':
                    self.imports_needed.add("math")
                    return f"math.Abs(float64({args[0]}))" if args else "0"
                return f"{func_name}({', '.join(args)})"
            
            # Default: capitalize function name
            return f"{func_name[0].upper()}{func_name[1:]}({', '.join(args)})"
        
        elif isinstance(expr.func, ast.Attribute):
            obj = self._transpile_expr(expr.func.value)
            method = expr.func.attr
            
            # String methods
            if method == 'strip':
                self.imports_needed.add("strings")
                return f"strings.TrimSpace({obj})"
            elif method == 'upper':
                self.imports_needed.add("strings")
                return f"strings.ToUpper({obj})"
            elif method == 'lower':
                self.imports_needed.add("strings")
                return f"strings.ToLower({obj})"
            elif method == 'split':
                self.imports_needed.add("strings")
                if args:
                    return f"strings.Split({obj}, {args[0]})"
                return f'strings.Fields({obj})'
            elif method == 'join':
                self.imports_needed.add("strings")
                if args:
                    return f"strings.Join({args[0]}, {obj})"
                return f"strings.Join(nil, {obj})"
            elif method == 'replace':
                self.imports_needed.add("strings")
                return f"strings.ReplaceAll({obj}, {', '.join(args)})"
            elif method == 'format':
                self.imports_needed.add("fmt")
                return f'fmt.Sprintf({obj}, {", ".join(args)})'
            elif method == 'append':
                if args:
                    return f"{obj} = append({obj}, {', '.join(args)})"
                return f"append({obj})"
            elif method == 'items':
                return obj
            elif method == 'keys':
                return obj
            elif method == 'values':
                return obj
            
            # Default method call
            method_name = method[0].upper() + method[1:] if method else method
            return f"{obj}.{method_name}({', '.join(args)})"
        
        # Generic call
        func = self._transpile_expr(expr.func)
        return f"{func}({', '.join(args)})"
    
    def _transpile_fstring(self, expr: ast.JoinedStr) -> str:
        """Transpile an f-string to fmt.Sprintf."""
        self.imports_needed.add("fmt")
        format_parts = []
        args = []
        
        for value in expr.values:
            if isinstance(value, ast.Constant):
                format_parts.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                format_parts.append("%v")
                args.append(self._transpile_expr(value.value))
        
        format_str = "".join(format_parts)
        if args:
            return f'fmt.Sprintf("{format_str}", {", ".join(args)})'
        return f'"{format_str}"'
    
    def _transpile_list_comp(self, expr: ast.ListComp) -> str:
        """Transpile a list comprehension (returns comment, actual expanded in body)."""
        return "nil /* list comprehension - expand to loop */"
    
    def _transpile_slice(self, slice_node) -> str:
        """Transpile a slice expression."""
        if isinstance(slice_node, ast.Slice):
            lower = self._transpile_expr(slice_node.lower) if slice_node.lower else ""
            upper = self._transpile_expr(slice_node.upper) if slice_node.upper else ""
            return f"{lower}:{upper}"
        return self._transpile_expr(slice_node)
    
    def _transpile_constant(self, value) -> str:
        """Transpile a constant value."""
        if value is None:
            return "nil"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, str):
            # Escape special characters
            escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            return f'"{escaped}"'
        return str(value)
    
    def _get_bin_op(self, op: ast.operator) -> str:
        """Get Go binary operator."""
        ops = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.FloorDiv: '/',
            ast.Pow: '**',
            ast.LShift: '<<',
            ast.RShift: '>>',
            ast.BitOr: '|',
            ast.BitXor: '^',
            ast.BitAnd: '&',
        }
        return ops.get(type(op), '+')
    
    def _get_aug_op(self, op: ast.operator) -> str:
        """Get Go augmented assignment operator."""
        return self._get_bin_op(op)
    
    def _get_cmp_op(self, op: ast.cmpop) -> str:
        """Get Go comparison operator."""
        ops = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: '==',
            ast.IsNot: '!=',
            ast.In: '/* in */',
            ast.NotIn: '/* not in */',
        }
        return ops.get(type(op), '==')
    
    def _get_annotation_str(self, node: ast.expr) -> str:
        """Get type annotation as string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            base = self._get_annotation_str(node.value)
            arg = self._get_annotation_str(node.slice)
            return f"{base}[{arg}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ""
    
    def _get_exception_type(self, handler: ast.ExceptHandler) -> str:
        """Get exception type name."""
        if handler.type:
            if isinstance(handler.type, ast.Name):
                return handler.type.id
        return "Exception"
