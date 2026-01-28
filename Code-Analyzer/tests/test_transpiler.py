"""Tests for the Python to Go transpiler module."""

import pytest
from pathlib import Path
from textwrap import dedent

from analyzer.transpiler import PythonToGoTranspiler, TypeMapper, GoCodeGenerator
from analyzer.transpiler.type_mapping import TypeMapper
from analyzer.transpiler.code_generator import GoCodeGenerator


class TestTypeMapper:
    """Tests for TypeMapper."""
    
    def test_basic_type_mapping(self):
        """Test basic type mappings."""
        mapper = TypeMapper()
        
        assert mapper.map_type("str") == "string"
        assert mapper.map_type("int") == "int"
        assert mapper.map_type("float") == "float64"
        assert mapper.map_type("bool") == "bool"
        assert mapper.map_type("bytes") == "[]byte"
    
    def test_collection_type_mapping(self):
        """Test collection type mappings."""
        mapper = TypeMapper()
        
        assert mapper.map_type("list[int]") == "[]int"
        assert mapper.map_type("List[str]") == "[]string"
        assert mapper.map_type("dict[str, int]") == "map[string]int"
        assert mapper.map_type("Dict[str, bool]") == "map[string]bool"
    
    def test_optional_type_mapping(self):
        """Test optional/nullable type mappings."""
        mapper = TypeMapper()
        
        assert mapper.map_type("Optional[str]") == "*string"
        assert mapper.map_type("Optional[int]") == "*int"
    
    def test_custom_type_registration(self):
        """Test custom type registration."""
        mapper = TypeMapper()
        mapper.register_custom_type("MyClass", "*MyClass")
        
        assert mapper.map_type("MyClass") == "*MyClass"
    
    def test_zero_values(self):
        """Test zero value generation."""
        mapper = TypeMapper()
        
        assert mapper.get_zero_value("string") == '""'
        assert mapper.get_zero_value("int") == "0"
        assert mapper.get_zero_value("bool") == "false"
        assert mapper.get_zero_value("*int") == "nil"
        assert mapper.get_zero_value("[]string") == "nil"


class TestGoCodeGenerator:
    """Tests for GoCodeGenerator."""
    
    def test_package_declaration(self):
        """Test package declaration generation."""
        gen = GoCodeGenerator("main")
        result = gen.generate_package_declaration()
        assert result == "package main\n"
    
    def test_struct_generation(self):
        """Test struct generation."""
        gen = GoCodeGenerator()
        result = gen.generate_struct(
            "Person",
            [("name", "string"), ("age", "int")],
            "represents a person"
        )
        
        assert "type Person struct {" in result
        assert "Name string" in result
        assert "Age int" in result
        assert "// Person represents a person" in result
    
    def test_function_generation(self):
        """Test function generation."""
        gen = GoCodeGenerator()
        result = gen.generate_function(
            "Greet",
            [("name", "string")],
            "string",
            ['return "Hello, " + name'],
            comment="greets a person"
        )
        
        assert "func Greet(name string) string {" in result
        assert 'return "Hello, " + name' in result
    
    def test_method_generation(self):
        """Test method generation with receiver."""
        gen = GoCodeGenerator()
        result = gen.generate_function(
            "Greet",
            [],
            "string",
            ['return "Hello"'],
            receiver=("p", "*Person")
        )
        
        assert "func (p *Person) Greet() string {" in result
    
    def test_import_management(self):
        """Test import statement generation."""
        gen = GoCodeGenerator()
        gen.add_import("fmt")
        gen.add_import("strings")
        
        result = gen.generate_imports()
        
        assert 'import (' in result
        assert '"fmt"' in result
        assert '"strings"' in result


class TestPythonToGoTranspiler:
    """Tests for PythonToGoTranspiler."""
    
    def test_transpile_simple_function(self):
        """Test transpiling a simple function."""
        code = dedent('''
            def greet(name: str) -> str:
                """Greet someone by name."""
                return f"Hello, {name}!"
        ''').strip()
        
        transpiler = PythonToGoTranspiler("main")
        go_code = transpiler.transpile_code(code)
        
        assert "package main" in go_code
        assert "func Greet(name string) string" in go_code
    
    def test_transpile_class_to_struct(self):
        """Test transpiling a Python class to Go struct."""
        code = dedent('''
            class Person:
                """Represents a person."""
                
                def __init__(self, name: str, age: int):
                    self.name = name
                    self.age = age
                
                def greet(self) -> str:
                    return f"Hi, I'm {self.name}"
        ''').strip()
        
        transpiler = PythonToGoTranspiler("main")
        go_code = transpiler.transpile_code(code)
        
        assert "package main" in go_code
        assert "type Person struct {" in go_code
        assert "func NewPerson(" in go_code
        assert "func (p *Person) Greet() string" in go_code
    
    def test_transpile_with_types(self):
        """Test transpiling with various type annotations."""
        code = dedent('''
            def process(items: list[int], count: int) -> dict[str, int]:
                """Process items."""
                pass
        ''').strip()
        
        transpiler = PythonToGoTranspiler()
        go_code = transpiler.transpile_code(code)
        
        assert "[]int" in go_code
        assert "map[string]int" in go_code
    
    def test_transpile_constants(self):
        """Test transpiling Python constants."""
        code = dedent('''
            MAX_SIZE = 100
            DEFAULT_NAME = "test"
        ''').strip()
        
        transpiler = PythonToGoTranspiler()
        go_code = transpiler.transpile_code(code)
        
        assert "const MAX_SIZE" in go_code or "var MAX_SIZE" in go_code
    
    def test_transpile_file(self, tmp_path):
        """Test transpiling a Python file."""
        # Create a temp Python file
        py_file = tmp_path / "test_module.py"
        py_file.write_text(dedent('''
            def hello() -> str:
                """Say hello."""
                return "Hello"
        ''').strip())
        
        output_file = tmp_path / "output" / "test_module.go"
        
        transpiler = PythonToGoTranspiler()
        go_code = transpiler.transpile_file(py_file, output_file)
        
        assert output_file.exists()
        assert "func Hello() string" in go_code
    
    def test_transpile_directory(self, tmp_path):
        """Test transpiling a directory."""
        # Create temp Python files
        (tmp_path / "file1.py").write_text("def foo(): pass")
        (tmp_path / "file2.py").write_text("def bar(): pass")
        
        output_dir = tmp_path / "go_output"
        
        transpiler = PythonToGoTranspiler()
        results = transpiler.transpile_directory(tmp_path, output_dir)
        
        assert len(results) == 2
        assert (output_dir / "file1.go").exists()
        assert (output_dir / "file2.go").exists()


class TestTranspilerEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_private_functions_stay_lowercase(self):
        """Test that private functions stay lowercase."""
        code = "def _private_helper(): pass"
        
        transpiler = PythonToGoTranspiler()
        go_code = transpiler.transpile_code(code)
        
        assert "func _private_helper()" in go_code
    
    def test_dunder_methods_handled(self):
        """Test that dunder methods are handled properly."""
        code = dedent('''
            class MyClass:
                def __init__(self): pass
                def __str__(self) -> str:
                    return "MyClass"
                def __repr__(self): pass
        ''').strip()
        
        transpiler = PythonToGoTranspiler()
        go_code = transpiler.transpile_code(code)
        
        # __init__ becomes NewMyClass constructor
        assert "NewMyClass" in go_code
        # __str__ becomes String()
        assert "String()" in go_code
        # __repr__ should be skipped
        assert "__repr__" not in go_code
    
    def test_empty_module(self):
        """Test transpiling an empty module."""
        code = "# Just a comment"
        
        transpiler = PythonToGoTranspiler()
        go_code = transpiler.transpile_code(code)
        
        assert "package main" in go_code
