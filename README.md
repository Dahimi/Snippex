# Snipex - Search Snippet Extraction API

Snipex is a production-ready API that extracts relevant text passages from search results using LLM-guided anchors.

## Features
- **Deterministic Snippet Extraction**: Uses LLM-identified anchors to reconstruct passages verbatim from source content, eliminating hallucinations.
- **Provider Abstraction**: Easily swap between different search and LLM backends.
- **Async & Parallel**: High-performance orchestration with FastAPI and `asyncio.gather`.

## Getting Started

### 1. Prerequisites
- Python 3.12+
- Perplexity API key
- Cerebras API key

### 2. Configuration
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```

### 3. Installation & Running

#### Using `uv` (Recommended)
If you have `uv` installed:
```bash
# Install dependencies
uv sync

# Run the API
uv run uvicorn main:app --reload
```

#### Using `venv` (Standard)
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r pyproject.toml

# Run the API
uvicorn main:app --reload
```

## API Usage
Once the server is running, visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore the interactive API documentation.

### Example Request
```json
POST /search
{
  "query": "best open source LLMs 2025",
  "num_results": 5,
  "max_snippets_per_result": 3
}
```

## Testing
Run unit tests using `pytest`:
```bash
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```
