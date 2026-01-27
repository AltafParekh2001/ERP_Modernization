import logging
import sys

# Configure logging to see details
logging.basicConfig(level=logging.DEBUG)

from analyzer.rag.pipeline import create_rag_pipeline as get_rag_pipeline
from analyzer.parsers import GoParser
from analyzer.rag.vector_store import ChromaVectorStore, InMemoryVectorStore

print("1. Testing RAG Pipeline Initialization...")
pipeline = get_rag_pipeline()
print(f"Vector Store Type: {type(pipeline.vector_store)}")

if isinstance(pipeline.vector_store, InMemoryVectorStore):
    print("⚠️  WARNING: Using InMemoryVectorStore. Index will be lost on exit.")
    try:
        import chromadb
        print("   chromadb IS installed but not used?")
    except ImportError:
        print("   chromadb is NOT installed.")

print("\n2. Testing Indexing with Go Code...")
go_code = '''
package main
func Hello() string { return "Hello" }
'''
parser = GoParser()
module = parser.parse_code(go_code, "test.go")

stats = pipeline.index([module], clear_existing=True)
print(f"Indexing Stats: {stats}")

print("\n3. Verifying Index...")
current_stats = pipeline.get_stats()
print(f"Current Stats: {current_stats}")

if current_stats.total_chunks == 0:
    print("❌ Error: Index count is 0 after indexing!")
else:
    print(f"✅ Success: Index contains {current_stats.total_chunks} chunks.")
