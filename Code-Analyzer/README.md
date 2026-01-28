<div align="center">

# 🔬 Enterprise Code Analyzer

### AI-Powered Code Intelligence Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-00C853?style=for-the-badge)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000?style=for-the-badge)](https://black.readthedocs.io)

*Transform your Python codebase into actionable intelligence with deep analysis, RAG-powered AI assistance, and Python→Go transpilation.*

---

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Usage](#-usage) • [Transpiler](#-python-to-go-transpiler)

</div>

---

## ✨ Features

<table>
<tr>
<td width="33%">

### 🔍 Deep Analysis
- AST-based parsing
- Multi-language support
- Type annotation analysis
- Full codebase indexing

</td>
<td width="33%">

### 📊 Smart Metrics
- Cyclomatic Complexity
- Cognitive Complexity
- Halstead Metrics
- Maintainability Index

</td>
<td width="33%">

### 🛡️ Security Scan
- SQL/Command Injection
- Hardcoded Secrets
- Vulnerable Patterns
- CVE Detection

</td>
</tr>
<tr>
<td width="33%">

### 🎯 Pattern Detection
- Design Patterns
- Anti-Patterns
- Code Smells
- Dead Code Analysis

</td>
<td width="33%">

### 🤖 RAG AI Assistant
- Natural Language Q&A
- Semantic Code Search
- Multi-Provider LLMs
- Persistent Vector Index

</td>
<td width="33%">

### 🔄 Code Transpiler
- Python → Go Conversion
- Type Mapping
- Control Flow Translation
- Directory Processing

</td>
</tr>
</table>

---

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    subgraph Input["📥 Input Layer"]
        F[("📄 Files")]
        D[("📁 Directories")]
        C[("💻 Code Strings")]
    end
    
    subgraph Core["⚙️ Core Engine"]
        PA["🔍 Parsers"]
        ME["📊 Metrics"]
        SE["🛡️ Security"]
        PT["🎯 Patterns"]
        DP["🔗 Dependencies"]
    end
    
    subgraph AI["🤖 AI Layer"]
        RA["RAG Pipeline"]
        VE["Vector Store"]
        LL["LLM Provider"]
    end
    
    subgraph Trans["🔄 Transpiler"]
        TM["Type Mapper"]
        BT["Body Transpiler"]
        CG["Code Generator"]
    end
    
    subgraph Output["📤 Output Layer"]
        JS[("📋 JSON")]
        MD[("📝 Markdown")]
        GO[("🐹 Go Code")]
    end
    
    F --> PA
    D --> PA
    C --> PA
    
    PA --> ME
    PA --> SE
    PA --> PT
    PA --> DP
    PA --> RA
    PA --> TM
    
    ME --> JS
    SE --> JS
    PT --> JS
    DP --> MD
    
    RA --> VE
    VE --> LL
    LL --> MD
    
    TM --> BT
    BT --> CG
    CG --> GO
    
    style Input fill:#e3f2fd,stroke:#1976d2
    style Core fill:#fff3e0,stroke:#f57c00
    style AI fill:#f3e5f5,stroke:#7b1fa2
    style Trans fill:#e8f5e9,stroke:#388e3c
    style Output fill:#fce4ec,stroke:#c2185b
```

---

### Module Architecture

```mermaid
graph LR
    subgraph Parsers["🔍 Parsers"]
        PY["Python Parser"]
        GO_P["Go Parser"]
        FP["File Parser"]
    end
    
    subgraph Models["📦 Models"]
        MOD["Module"]
        CLS["Class"]
        FUN["Function"]
        VAR["Variable"]
    end
    
    subgraph Metrics["📊 Metrics"]
        CYC["Cyclomatic"]
        COG["Cognitive"]
        HAL["Halstead"]
        MAI["Maintainability"]
    end
    
    subgraph Security["🛡️ Security"]
        VUL["Scanner"]
        SEC["Secrets"]
    end
    
    subgraph RAG["🤖 RAG"]
        IDX["Indexer"]
        RET["Retriever"]
        GEN["Generator"]
    end
    
    subgraph Transpiler["🔄 Transpiler"]
        P2G["Python→Go"]
        TYPE["Types"]
        BODY["Body"]
    end
    
    Parsers --> Models
    Models --> Metrics
    Models --> Security
    Models --> RAG
    Models --> Transpiler
    
    style Parsers fill:#e3f2fd,stroke:#1976d2
    style Models fill:#fff8e1,stroke:#ffa000
    style Metrics fill:#fff3e0,stroke:#f57c00
    style Security fill:#ffebee,stroke:#c62828
    style RAG fill:#f3e5f5,stroke:#7b1fa2
    style Transpiler fill:#e8f5e9,stroke:#388e3c
```

---

### Data Flow Pipeline

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant CLI as 💻 CLI/Menu
    participant E as ⚙️ Engine
    participant P as 🔍 Parser
    participant A as 📊 Analyzers
    participant AI as 🤖 RAG
    participant O as 📤 Output
    
    U->>CLI: code-analyzer analyze ./src
    CLI->>E: analyze_directory()
    E->>P: parse_directory()
    P-->>E: Module[]
    
    par Parallel Analysis
        E->>A: calculate_metrics()
        E->>A: scan_security()
        E->>A: detect_patterns()
        E->>A: analyze_dependencies()
    end
    
    A-->>E: AnalysisResult
    E->>O: format_output()
    O-->>CLI: JSON/Markdown
    CLI-->>U: 📊 Results
    
    Note over U,O: Optional: RAG Integration
    
    U->>CLI: code-analyzer rag ask "How does auth work?"
    CLI->>AI: query()
    AI->>AI: retrieve_context()
    AI->>AI: generate_answer()
    AI-->>CLI: 💬 Response
    CLI-->>U: Answer + Sources
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/code-analyzer.git
cd code-analyzer

# Install with all features
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

---

## 📊 Analysis Capabilities

### Code Quality Metrics

```mermaid
pie showData
    title Code Quality Distribution
    "Excellent (A)" : 30
    "Good (B)" : 40
    "Moderate (C)" : 20
    "Needs Work (D)" : 10
```

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **Cyclomatic Complexity** | Control flow paths | < 10 ✅ |
| **Cognitive Complexity** | Human readability | < 15 ✅ |
| **Maintainability Index** | Overall health | > 65 ✅ |
| **Lines per Function** | Code organization | < 50 ✅ |

---

### Security Analysis

```mermaid
graph TD
    subgraph Detection["🛡️ Security Detection"]
        SQL["SQL Injection"]
        CMD["Command Injection"]
        SEC["Hardcoded Secrets"]
        XSS["XSS Patterns"]
        EVAL["Dangerous eval()"]
        PICKLE["Unsafe Pickle"]
    end
    
    subgraph Severity["⚠️ Severity Levels"]
        CRIT["🔴 Critical"]
        HIGH["🟠 High"]
        MED["🟡 Medium"]
        LOW["🟢 Low"]
    end
    
    SQL --> CRIT
    CMD --> CRIT
    SEC --> HIGH
    EVAL --> HIGH
    XSS --> MED
    PICKLE --> MED
    
    style CRIT fill:#ffcdd2,stroke:#c62828
    style HIGH fill:#ffe0b2,stroke:#ef6c00
    style MED fill:#fff9c4,stroke:#f9a825
    style LOW fill:#c8e6c9,stroke:#388e3c
```

---

### Pattern Detection

```mermaid
mindmap
  root((Patterns))
    Design Patterns
      Singleton
      Factory
      Observer
      Decorator
      Strategy
      Builder
    Anti-Patterns
      God Class
      Long Method
      Long Parameters
      Feature Envy
    Code Smells
      Magic Numbers
      Empty Except
      Mutable Defaults
      Duplicate Code
```

---

## 🤖 RAG AI Assistant

### Architecture

```mermaid
graph LR
    subgraph Indexing["📥 Indexing Phase"]
        CODE["Python Code"]
        PARSE["Parse AST"]
        CHUNK["Chunk Entities"]
        EMBED["Generate Embeddings"]
        STORE["ChromaDB"]
    end
    
    subgraph Query["🔍 Query Phase"]
        Q["User Question"]
        QEMB["Query Embedding"]
        RET["Retrieve Top-K"]
        CTX["Build Context"]
        LLM["LLM Response"]
    end
    
    CODE --> PARSE --> CHUNK --> EMBED --> STORE
    Q --> QEMB --> RET
    STORE --> RET
    RET --> CTX --> LLM
    
    style Indexing fill:#e8f5e9,stroke:#388e3c
    style Query fill:#e3f2fd,stroke:#1976d2
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

### Transpilation Flow

```mermaid
graph TB
    subgraph Input["📥 Python Input"]
        PY_FILE["Python File"]
        PY_CODE["Python Code"]
    end
    
    subgraph Parse["🔍 Parse Phase"]
        AST["AST Analysis"]
        ENTITIES["Extract Entities"]
    end
    
    subgraph Map["🗺️ Mapping Phase"]
        TYPES["Type Mapping"]
        IMPORTS["Import Mapping"]
    end
    
    subgraph Generate["⚙️ Generation Phase"]
        STRUCT["Struct Generation"]
        FUNC["Function Generation"]
        BODY["Body Transpilation"]
    end
    
    subgraph Output["📤 Go Output"]
        GO_FILE["Go File"]
    end
    
    PY_FILE --> AST
    PY_CODE --> AST
    AST --> ENTITIES
    ENTITIES --> TYPES
    ENTITIES --> IMPORTS
    TYPES --> STRUCT
    TYPES --> FUNC
    FUNC --> BODY
    STRUCT --> GO_FILE
    BODY --> GO_FILE
    
    style Input fill:#fff3e0,stroke:#f57c00
    style Parse fill:#e3f2fd,stroke:#1976d2
    style Map fill:#f3e5f5,stroke:#7b1fa2
    style Generate fill:#e8f5e9,stroke:#388e3c
    style Output fill:#e0f2f1,stroke:#00897b
```

### Type Mapping

```mermaid
graph LR
    subgraph Python["🐍 Python Types"]
        P_STR["str"]
        P_INT["int"]
        P_FLOAT["float"]
        P_BOOL["bool"]
        P_LIST["list[T]"]
        P_DICT["dict[K,V]"]
        P_OPT["Optional[T]"]
    end
    
    subgraph Go["🐹 Go Types"]
        G_STR["string"]
        G_INT["int"]
        G_FLOAT["float64"]
        G_BOOL["bool"]
        G_SLICE["[]T"]
        G_MAP["map[K]V"]
        G_PTR["*T"]
    end
    
    P_STR --> G_STR
    P_INT --> G_INT
    P_FLOAT --> G_FLOAT
    P_BOOL --> G_BOOL
    P_LIST --> G_SLICE
    P_DICT --> G_MAP
    P_OPT --> G_PTR
    
    style Python fill:#fff3e0,stroke:#f57c00
    style Go fill:#e0f2f1,stroke:#00897b
```

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
| List comprehensions | Loop expansion | ⚠️ Partial |

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

## 💻 CLI Reference

### Commands

```mermaid
graph TD
    CLI["code-analyzer"]
    
    CLI --> analyze["analyze"]
    CLI --> query["query"]
    CLI --> summary["summary"]
    CLI --> rag["rag"]
    CLI --> transpile["transpile"]
    CLI --> init["init"]
    
    rag --> index["index"]
    rag --> ask["ask"]
    rag --> search["search"]
    rag --> stats["stats"]
    rag --> clear["clear"]
    
    style CLI fill:#e3f2fd,stroke:#1976d2
    style analyze fill:#c8e6c9,stroke:#388e3c
    style rag fill:#f3e5f5,stroke:#7b1fa2
    style transpile fill:#e0f2f1,stroke:#00897b
```

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze code | `code-analyzer analyze ./src` |
| `query` | Natural language query | `code-analyzer query ./src "find async"` |
| `summary` | Generate summary | `code-analyzer summary ./src` |
| `transpile` | Convert Python→Go | `code-analyzer transpile main.py` |
| `rag index` | Index for RAG | `code-analyzer rag index ./src` |
| `rag ask` | Ask AI about code | `code-analyzer rag ask "How does X work?"` |
| `init` | Create config | `code-analyzer init --format yaml` |

---

## ⚙️ Configuration

### Config File (`.code-analyzer.yaml`)

```yaml
# Parser Settings
parser:
  max_file_size_mb: 10
  encoding: utf-8
  languages:
    - python
    - go

# Metrics Thresholds
metrics:
  complexity_threshold_high: 20
  max_function_lines: 50
  maintainability_threshold: 65

# Pattern Detection
patterns:
  detect_design_patterns: true
  detect_anti_patterns: true
  detect_code_smells: true

# Security Scanning
security:
  check_sql_injection: true
  check_hardcoded_secrets: true
  check_dangerous_functions: true

# RAG Configuration
rag:
  embedding_provider: openai
  llm_provider: anthropic
  persist_directory: .analyzer_rag
  chunk_size: 1500
  top_k: 10

# AI Output
ai:
  max_context_tokens: 8000
  output_format: json
```

---

## 📁 Project Structure

```mermaid
graph TD
    ROOT["📁 code-analyzer"]
    
    ROOT --> ANALYZER["📁 analyzer/"]
    ROOT --> TESTS["📁 tests/"]
    ROOT --> SAMPLES["📁 samples/"]
    ROOT --> DOCS["📁 docs/"]
    
    ANALYZER --> PARSERS["📁 parsers/"]
    ANALYZER --> MODELS["📁 models/"]
    ANALYZER --> METRICS["📁 metrics/"]
    ANALYZER --> SECURITY["📁 security/"]
    ANALYZER --> PATTERNS["📁 patterns/"]
    ANALYZER --> DEPS["📁 dependencies/"]
    ANALYZER --> RAG_DIR["📁 rag/"]
    ANALYZER --> AI["📁 ai/"]
    ANALYZER --> TRANS["📁 transpiler/"]
    
    ANALYZER --> ENGINE["⚙️ engine.py"]
    ANALYZER --> CLI_F["💻 cli.py"]
    ANALYZER --> MENU["📋 menu.py"]
    
    style ROOT fill:#e3f2fd,stroke:#1976d2
    style ANALYZER fill:#fff3e0,stroke:#f57c00
    style TRANS fill:#e8f5e9,stroke:#388e3c
    style RAG_DIR fill:#f3e5f5,stroke:#7b1fa2
```

---

## 📈 Performance

```mermaid
xychart-beta
    title "Analysis Performance (files/second)"
    x-axis ["10 files", "50 files", "100 files", "500 files", "1000 files"]
    y-axis "Processing Speed" 0 --> 100
    bar [95, 88, 82, 65, 52]
```

| Codebase Size | Analysis Time | Memory Usage |
|---------------|---------------|--------------|
| 1K LOC | < 1 sec | ~50 MB |
| 10K LOC | ~5 sec | ~100 MB |
| 100K LOC | ~30 sec | ~500 MB |
| 1M LOC | ~5 min | ~2 GB |

---

## 🔌 Python API

### Basic Usage

```python
from analyzer import analyze_file, analyze_directory

# Analyze single file
result = analyze_file("main.py")
print(result.get_summary())

# Analyze directory
result = analyze_directory("./src")
print(f"Found {len(result.vulnerabilities)} security issues")
```

### With Configuration

```python
from analyzer import CodeAnalyzer
from analyzer.config import AnalyzerConfig

config = AnalyzerConfig(
    metrics={"complexity_threshold_high": 15},
    security={"check_sql_injection": True}
)

analyzer = CodeAnalyzer(config)
result = analyzer.analyze_directory("./project")
```

### RAG Integration

```python
from analyzer.rag import RAGPipeline
from analyzer.parsers import FileParser

# Parse and index
parser = FileParser()
modules = parser.parse_directory("./src")

pipeline = RAGPipeline()
pipeline.index(modules, "./src")

# Query
response = pipeline.query("How does authentication work?")
print(response.answer)
print(response.format_sources())
```

### Transpiler API

```python
from analyzer.transpiler import PythonToGoTranspiler

transpiler = PythonToGoTranspiler("mypackage")

# Transpile file
go_code = transpiler.transpile_file("main.py", "main.go")

# Transpile code string
go_code = transpiler.transpile_code('''
def hello(name: str) -> str:
    return f"Hello, {name}!"
''')
```

---

<div align="center">

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Built with ❤️ for developers who value code quality**

</div>
