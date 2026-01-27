"""Tests for the Go parser module."""

import pytest
from analyzer.parsers import GoParser, FileParser
from analyzer.models.code_entities import EntityType, Visibility


class TestGoParser:
    """Tests for GoParser."""
    
    def test_parse_simple_function(self):
        """Test parsing a simple Go function."""
        code = '''
package main

// Greet returns a greeting message
func Greet(name string) string {
    return "Hello, " + name
}
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        assert module.package == "main"
        assert len(module.functions) == 1
        func = module.functions[0]
        assert func.name == "Greet"
        assert len(func.parameters) == 1
        assert func.parameters[0].name == "name"
        assert func.parameters[0].type_annotation == "string"
        assert func.return_type == "string"
        assert func.visibility == Visibility.PUBLIC  # Starts with capital
    
    def test_parse_struct(self):
        """Test parsing a Go struct."""
        code = '''
package models

// Person represents a human being
type Person struct {
    Name string
    Age  int
}
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        assert len(module.classes) == 1
        cls = module.classes[0]
        assert cls.name == "Person"
        assert cls.visibility == Visibility.PUBLIC
        assert len(cls.instance_variables) == 2
        assert cls.instance_variables[0].name == "Name"
        assert cls.instance_variables[1].name == "Age"
    
    def test_parse_method(self):
        """Test parsing a Go method with receiver."""
        code = '''
package models

type Person struct {
    Name string
}

// Greet returns a greeting from the person
func (p *Person) Greet() string {
    return "Hello, I am " + p.Name
}
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        assert len(module.classes) == 1
        cls = module.classes[0]
        assert cls.name == "Person"
        assert len(cls.methods) == 1
        method = cls.methods[0]
        assert method.name == "Greet"
        assert method.return_type == "string"
    
    def test_parse_imports(self):
        """Test parsing import statements."""
        code = '''
package main

import "fmt"

import (
    "os"
    "strings"
    myalias "path/to/something"
)
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        # Should have 4 imports: fmt, os, strings, myalias
        assert len(module.imports) >= 3
        
        # Check single import
        fmt_import = next((i for i in module.imports if i.module == "fmt"), None)
        assert fmt_import is not None
        
        # Check aliased import
        aliased_import = next((i for i in module.imports if i.alias == "myalias"), None)
        assert aliased_import is not None
    
    def test_parse_interface(self):
        """Test parsing an interface definition."""
        code = '''
package io

// Reader is the interface for reading
type Reader interface {
    Read(p []byte) (n int, err error)
}
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        assert len(module.classes) == 1
        cls = module.classes[0]
        assert cls.name == "Reader"
        assert cls.is_abstract == True  # Interfaces are abstract
        assert len(cls.methods) == 1
        assert cls.methods[0].name == "Read"
    
    def test_parse_visibility(self):
        """Test visibility detection (exported vs unexported)."""
        code = '''
package utils

func PublicFunc() {}
func privateFunc() {}

type PublicStruct struct {
    PublicField  string
    privateField int
}
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        # Check function visibility
        public_func = next((f for f in module.functions if f.name == "PublicFunc"), None)
        private_func = next((f for f in module.functions if f.name == "privateFunc"), None)
        
        assert public_func is not None
        assert public_func.visibility == Visibility.PUBLIC
        assert private_func is not None
        assert private_func.visibility == Visibility.PRIVATE
        
        # Check struct visibility
        cls = module.classes[0]
        assert cls.visibility == Visibility.PUBLIC
        
        # Check field visibility
        public_field = next((v for v in cls.instance_variables if v.name == "PublicField"), None)
        private_field = next((v for v in cls.instance_variables if v.name == "privateField"), None)
        
        assert public_field is not None
        assert public_field.visibility == Visibility.PUBLIC
        assert private_field is not None
        assert private_field.visibility == Visibility.PRIVATE
    
    def test_parse_constants(self):
        """Test parsing constant definitions."""
        code = '''
package config

const Version = "1.0.0"

const (
    MaxRetries = 3
    Timeout    = 30
)
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        assert len(module.constants) >= 1
        version_const = next((c for c in module.constants if c.name == "Version"), None)
        assert version_const is not None
        assert version_const.is_constant == True
    
    def test_parse_async_function(self):
        """Test that Go functions are not marked as async (Go uses goroutines differently)."""
        code = '''
package main

func processData(data string) {
    // Processing
}
'''
        parser = GoParser()
        module = parser.parse_code(code)
        
        assert len(module.functions) == 1
        func = module.functions[0]
        assert func.is_async == False


class TestGoParserWithFileParser:
    """Tests for Go parsing via FileParser."""
    
    def test_file_parser_supports_go(self):
        """Test that FileParser has Go parser registered."""
        parser = FileParser()
        go_parser = parser.get_parser("test.go")
        
        assert go_parser is not None
        assert go_parser.language == "go"
    
    def test_parse_code_with_language(self):
        """Test parsing Go code using language parameter."""
        parser = FileParser()
        code = '''
package main

func main() {
    println("Hello, World!")
}
'''
        module = parser.parse_code(code, language="go")
        
        assert module.package == "main"
        assert len(module.functions) == 1
        assert module.functions[0].name == "main"


class TestGoComplexityMetrics:
    """Tests for Go complexity calculations."""
    
    def test_cyclomatic_complexity(self):
        """Test cyclomatic complexity calculation."""
        from analyzer.metrics import calculate_go_complexity
        
        code = '''
func example(x int) int {
    if x > 0 {
        return x
    } else if x < 0 {
        return -x
    }
    return 0
}
'''
        metrics = calculate_go_complexity(code)
        
        # Base 1 + if + else if = 3
        assert metrics.cyclomatic >= 3
    
    def test_nesting_depth(self):
        """Test nesting depth calculation."""
        from analyzer.metrics import calculate_go_complexity
        
        code = '''
func nested() {
    for i := 0; i < 10; i++ {
        if i > 5 {
            for j := 0; j < i; j++ {
                println(j)
            }
        }
    }
}
'''
        metrics = calculate_go_complexity(code)
        
        # Should detect nested structures
        assert metrics.max_nesting_depth >= 3


class TestGoCodeSmells:
    """Tests for Go code smell detection."""
    
    def test_detect_missing_comment(self):
        """Test detection of missing documentation comments."""
        from analyzer.patterns import detect_go_code_smells
        from analyzer.parsers import GoParser
        
        code = '''
package utils

func ExportedFunction() {
    // No doc comment
}
'''
        parser = GoParser()
        module = parser.parse_code(code, filename="utils.go")
        
        smells = detect_go_code_smells([module])
        
        # Should detect missing comment on exported function
        missing_comment_smells = [s for s in smells if s.smell_type.value == "missing_comment"]
        assert len(missing_comment_smells) > 0
    
    def test_detect_too_many_parameters(self):
        """Test detection of functions with too many parameters."""
        from analyzer.patterns import detect_go_code_smells
        from analyzer.parsers import GoParser
        
        code = '''
package utils

// TooManyParams has too many parameters
func TooManyParams(a int, b int, c int, d int, e int, f int, g int) {
    // This is excessive
}
'''
        parser = GoParser()
        module = parser.parse_code(code, filename="utils.go")
        
        smells = detect_go_code_smells([module])
        
        # Should detect too many parameters
        param_smells = [s for s in smells if s.smell_type.value == "too_many_parameters"]
        assert len(param_smells) > 0
