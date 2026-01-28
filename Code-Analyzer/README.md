<div align="center">

# 🔬 Enterprise Code Analyzer

### AI-Powered Code Intelligence Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-00C853?style=for-the-badge)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000?style=for-the-badge)](https://black.readthedocs.io)

*Transform your Python codebase into actionable intelligence with deep analysis, RAG-powered AI assistance, and Python→Go transpilation.*

---

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Transpiler](#-python-to-go-transpiler)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Deep Analysis** | AST-based parsing, multi-language support, type annotation analysis |
| 📊 **Smart Metrics** | Cyclomatic & Cognitive Complexity, Halstead Metrics, Maintainability Index |
| 🛡️ **Security Scan** | SQL/Command Injection detection, hardcoded secrets, vulnerable patterns |
| 🎯 **Pattern Detection** | Design patterns, anti-patterns, code smells, dead code analysis |
| 🤖 **RAG AI Assistant** | Natural language Q&A, semantic code search, multi-provider LLMs |
| 🔄 **Code Transpiler** | Python → Go conversion with type mapping and control flow translation |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                               │
│    ┌──────────┐    ┌──────────────┐    ┌─────────────────┐      │
│    │  Files   │    │  Directories │    │  Code Strings   │      │
│    └────┬─────┘    └──────┬───────┘    └────────┬────────┘      │
└─────────┼─────────────────┼─────────────────────┼───────────────┘
          │                 │                     │
          └─────────────────┼─────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CORE ENGINE                               │
│  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌────────────────┐   │
│  │ Parsers  │  │ Metrics │  │ Security │  │ Pattern Detect │   │
│  └────┬─────┘  └────┬────┘  └────┬─────┘  └───────┬────────┘   │
└───────┼─────────────┼───────────┼─────────────────┼─────────────┘
        │             │           │                 │
        └─────────────┼───────────┼─────────────────┘
                      ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SPECIALIZED MODULES                          │
│  ┌─────────────────────┐       ┌─────────────────────────────┐  │
│  │    RAG AI Layer     │       │    Python→Go Transpiler     │  │
│  │  ┌───────┐ ┌─────┐  │       │  ┌───────┐ ┌─────┐ ┌─────┐  │  │
│  │  │Vector │ │ LLM │  │       │  │ Types │ │Body │ │ Gen │  │  │
│  │  │ Store │ │     │  │       │  │ Map   │ │Trans│ │     │  │  │
│  │  └───────┘ └─────┘  │       │  └───────┘ └─────┘ └─────┘  │  │
│  └─────────────────────┘       └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                      │                       │
                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                              │
│         ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│         │   JSON   │    │ Markdown │    │ Go Code  │            │
│         └──────────┘    └──────────┘    └──────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
analyzer/
├── parsers/          # Python & Go code parsing
├── models/           # Data structures (Module, Class, Function)
├── metrics/          # Complexity & maintainability calculations
├── security/         # Vulnerability & secret scanning
├── patterns/         # Design pattern & code smell detection
├── dependencies/     # Import & call graph analysis
├── rag/              # RAG pipeline with vector store
├── ai/               # LLM integration & summarization
├── transpiler/       # Python to Go code conversion
├── engine.py         # Main orchestration
├── cli.py            # Command-line interface
└── menu.py           # Interactive menu system
```

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/code-analyzer.git
cd code-analyzer
pip install -e ".[dev,rag]"
```

### Interactive Menu

```bash
python -m analyzer.menu
```

```
╔════════════════════════════════════════════════════════════╗
║               🔬 ENTERPRISE CODE ANALYZER                   ║
║                 AI-Powered Code Intelligence                 ║
╠════════════════════════════════════════════════════════════╣
║  [1] 📂 Analyze File       [6] 🔗 Dependency Analysis       ║
║  [2] 📁 Analyze Directory  [7] 🔍 Query Code               ║
║  [3] 📊 Quick Metrics      [8] 📝 Generate Summary         ║
║  [4] 🔐 Security Scan      [A] 🤖 RAG AI Assistant         ║
║  [5] 🎯 Pattern Detection  [B] 🔄 Python→Go Transpiler     ║
╚════════════════════════════════════════════════════════════╝
```

### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze Python code | `code-analyzer analyze ./src` |
| `query` | Natural language query | `code-analyzer query ./src "find async"` |
| `summary` | Generate summary | `code-analyzer summary ./src` |
| `transpile` | Convert Python→Go | `code-analyzer transpile main.py` |
| `rag index` | Index for RAG | `code-analyzer rag index ./src` |
| `rag ask` | Ask AI about code | `code-analyzer rag ask "How does X work?"` |

---

## 📊 Analysis Capabilities

### Code Quality Metrics

| Metric | Description | Good Threshold |
|--------|-------------|----------------|
| **Cyclomatic Complexity** | Control flow paths | < 10 |
| **Cognitive Complexity** | Human readability | < 15 |
| **Maintainability Index** | Overall health score | > 65 |
| **Lines per Function** | Code organization | < 50 |

### Security Analysis

| Vulnerability Type | Severity | Detection |
|-------------------|----------|-----------|
| SQL Injection | 🔴 Critical | String concatenation in queries |
| Command Injection | 🔴 Critical | Shell=True, os.system() |
| Hardcoded Secrets | 🟠 High | API keys, passwords in code |
| Dangerous eval() | 🟠 High | Dynamic code execution |
| Unsafe Pickle | 🟡 Medium | Deserialization attacks |

### Pattern Detection

**Design Patterns:** Singleton, Factory, Observer, Decorator, Strategy, Builder

**Anti-Patterns:** God Class, Long Method, Long Parameter List, Feature Envy

**Code Smells:** Magic Numbers, Empty Except, Mutable Defaults, Duplicate Code

---

## 🤖 RAG AI Assistant

### How It Works

```
1. INDEX PHASE
   Python Code → Parse AST → Chunk Entities → Generate Embeddings → ChromaDB

2. QUERY PHASE  
   User Question → Query Embedding → Retrieve Top-K → Build Context → LLM Response
```

### Supported Providers

| Provider | Embeddings | LLM | Status |
|----------|------------|-----|--------|
| **OpenAI** | ✅ text-embedding-3 | ✅ GPT-4 | Production |
| **Anthropic** | — | ✅ Claude 3 | Production |
| **Google** | ✅ Gemini | ✅ Gemini Pro | Production |
| **Local** | ✅ SentenceTransformers | — | Development |

### Usage

```bash
# Index your codebase
code-analyzer rag index ./src

# Ask questions
code-analyzer rag ask "How does authentication work?"

# Semantic search
code-analyzer rag search "error handling patterns"
```

---

## 🔄 Python to Go Transpiler

### Type Mapping

| Python | Go |
|--------|-----|
| `str` | `string` |
| `int` | `int` |
| `float` | `float64` |
| `bool` | `bool` |
| `list[T]` | `[]T` |
| `dict[K,V]` | `map[K]V` |
| `Optional[T]` | `*T` |

### Construct Mapping

| Python | Go | Support |
|--------|-----|---------|
| `class` | `struct` + methods | ✅ Full |
| `def function()` | `func Function()` | ✅ Full |
| `self.method()` | Receiver methods | ✅ Full |
| `__init__` | `NewType()` constructor | ✅ Full |
| `for x in items` | `for _, x := range items` | ✅ Full |
| `if/elif/else` | `if {} else if {} else {}` | ✅ Full |
| `while` | `for condition {}` | ✅ Full |
| `try/except` | `defer`/`recover` | ⚠️ Partial |

### Example

**Input: Python**
```python
def calculate_sum(numbers: list[int]) -> int:
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    def __init__(self, precision: int):
        self.precision = precision
    
    def add(self, a: float, b: float) -> float:
        return round(a + b, self.precision)
```

**Output: Go**
```go
package main

func CalculateSum(numbers []int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}

type Calculator struct {
    Precision int
}

func NewCalculator(precision int) *Calculator {
    return &Calculator{
        Precision: precision,
    }
}

func (c *Calculator) Add(a float64, b float64) float64 {
    return math.Round((a + b) * math.Pow10(c.Precision)) / math.Pow10(c.Precision)
}
```

### Usage

```bash
# Transpile a single file
code-analyzer transpile main.py --output ./go/main.go

# Transpile entire directory
code-analyzer transpile ./python_project --output ./go_project

# With custom package name
code-analyzer transpile main.py --package myapp
```

---

## ⚙️ Configuration

Create a `.code-analyzer.yaml` file:

```yaml
parser:
  max_file_size_mb: 10
  encoding: utf-8

metrics:
  complexity_threshold_high: 20
  max_function_lines: 50

patterns:
  detect_design_patterns: true
  detect_anti_patterns: true

security:
  check_sql_injection: true
  check_hardcoded_secrets: true

rag:
  embedding_provider: openai
  llm_provider: anthropic
  persist_directory: .analyzer_rag
```

---

## 📈 Performance

| Codebase Size | Analysis Time | Memory Usage |
|---------------|---------------|--------------|
| 1K LOC | < 1 sec | ~50 MB |
| 10K LOC | ~5 sec | ~100 MB |
| 100K LOC | ~30 sec | ~500 MB |
| 1M LOC | ~5 min | ~2 GB |

---

## 🔌 Python API

```python
from analyzer import analyze_file, analyze_directory

# Analyze single file
result = analyze_file("main.py")
print(result.get_summary())

# Analyze directory
result = analyze_directory("./src")
print(f"Found {len(result.vulnerabilities)} security issues")
```

### Transpiler API

```python
from analyzer.transpiler import PythonToGoTranspiler

transpiler = PythonToGoTranspiler("mypackage")
go_code = transpiler.transpile_file("main.py", "main.go")
```

### RAG API

```python
from analyzer.rag import RAGPipeline

pipeline = RAGPipeline()
pipeline.index(modules, "./src")
response = pipeline.query("How does authentication work?")
print(response.answer)
```

---

<div align="center">

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Built with ❤️ for developers who value code quality**

</div>
