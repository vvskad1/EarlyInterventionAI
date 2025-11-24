# Early Intervention GenAI FastAPI Backend

Backend-only FastAPI app for Early Intervention GenAI prototype. Uses Groq's OpenAI-compatible API with naive RAG over a single knowledge base file.

## Quick Start

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Create knowledge base (optional - will be created automatically)
mkdir kb
echo "Paste your Early Intervention notes here." > kb/knowledge_base.txt

# Run the server
uvicorn app.main:app --reload --port 8080
```

## API Endpoints

### 1. Upload Knowledge Base
Upload a `.txt` or `.md` file to use as the RAG knowledge base.

```bash
curl -X POST http://localhost:8080/api/rag/upload \
  -F "file=@./my_ei_notes.txt"
```

**Response:**
```json
{
  "ok": true,
  "kb_file": "C:\\path\\to\\kb\\knowledge_base.txt"
}
```

### 2. Generate Intervention Plan
Generate age-appropriate, domain-specific intervention plans.

```bash
curl -X POST http://localhost:8080/api/plan \
  -H "Content-Type: application/json" \
  -d "{\"age_months\":24,\"domain\":\"communication\",\"extra_info\":\"struggles to follow one-step directions; bilingual home\"}"
```

**Request Fields:**
- `age_months` (int, required): Child's age in months (0-36)
- `domain` (str, required): Development domain (e.g., `fine_motor`, `gross_motor`, `social`, `communication`, `cognitive`, `adaptive`)
- `extra_info` (str, optional): Additional context

**Response:**
```json
{
  "Goals": "Follow 1-step play-based directions (e.g., \"push car\") in 4/5 tries; sustain joint attention 8–10s; use 2-word combos during routines.",
  "Strategies": "Short cues + gestures; model–pause–wait; embed practice in play; offer choices; repeat & expand child's words.",
  "Advice for Parents": "Play daily in short bursts. Say one short direction, then wait. Celebrate attempts. Reuse the same words in snack/bath/cleanup."
}
```

### 3. Chat Interface
Conversational interface with session memory.

```bash
# Start new chat session
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"How do I reduce frustration during cleanup?\",\"age_months\":24,\"domain\":\"communication\"}"

# Continue existing session
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"What about mealtime?\",\"session_id\":\"<session_id_from_previous_response>\"}"
```

**Request Fields:**
- `message` (str, required): User's message
- `session_id` (str, optional): Session ID for conversation continuity (auto-generated if missing)
- `age_months` (int, optional): Child's age for RAG context
- `domain` (str, optional): Development domain for RAG context

**Response:**
```json
{
  "response": "To reduce frustration during cleanup with a 24-month-old...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Architecture

### Tech Stack
- **FastAPI** + **Uvicorn** - Modern async web framework
- **Pydantic** - Request/response validation
- **python-dotenv** - Environment configuration
- **httpx** - Async HTTP client for Groq API
- **python-multipart** - File upload support

### Project Structure
```
ei-genai-fastapi/
├─ app/
│  ├─ main.py          # FastAPI app, routes, startup logic
│  ├─ rag.py           # Chunking, scoring, retrieval helpers
│  ├─ groq.py          # Async client for Groq chat completions
│  ├─ schemas.py       # Pydantic request/response models
│  ├─ prompts.py       # System prompts for plan + chat
│  └─ utils.py         # JSON repair and helpers
├─ kb/
│  └─ knowledge_base.txt  # Single-file knowledge base
├─ .env.example
├─ requirements.txt
└─ README.md
```

### RAG Implementation (Naive)
1. **Single-file knowledge base** at `./kb/knowledge_base.txt`
2. **Chunking**: Splits KB into ~1000 character slices
3. **Scoring**: Simple token overlap between query and chunks
4. **Retrieval**: Top chunks concatenated up to budget (default 6000 chars)
5. **Context injection**: Passed as `[RAG CONTEXT]...[/RAG CONTEXT]` in system message

### Groq API Integration
- Uses OpenAI-compatible endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Supports JSON mode for structured plan generation
- Configurable model via `GROQ_MODEL` env variable
- Default: `llama3-70b-8192`

### Chat Memory
- **In-memory storage** per `session_id`
- Keeps last **12 messages** per session
- Auto-generates UUID for new sessions
- No persistence (cleared on restart)

## Configuration

Edit `.env` file:

```env
GROQ_API_KEY=your_groq_key_here    # Required: Get from console.groq.com
GROQ_MODEL=llama3-70b-8192         # Optional: Model to use
PORT=8080                          # Optional: Server port
KB_FILE=./kb/knowledge_base.txt    # Optional: KB file path
RAG_CONTEXT_BUDGET=6000            # Optional: Max RAG context chars
```

## Features

✅ Upload and replace knowledge base file  
✅ Generate structured intervention plans with RAG  
✅ JSON mode with fallback repair  
✅ Conversational chat with session memory  
✅ Age and domain-aware context retrieval  
✅ CORS enabled for frontend integration  
✅ Graceful handling of missing KB  
✅ Input validation with detailed error messages  

## Limitations & Future Extensions

**Current Limitations:**
- Single-file knowledge base only
- Naive token overlap scoring (no embeddings)
- In-memory chat history (no persistence)
- No authentication/authorization
- CORS open to all origins

**Planned Extensions:**
- PDF ingestion and parsing
- Multi-file knowledge base support
- Vector embeddings for semantic search
- Redis for persistent chat sessions
- PostgreSQL for knowledge base indexing
- User authentication and rate limiting

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8080

# Run in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4

# Check logs
# Server logs startup info: port, KB path, whether KB loaded
```

## Error Handling

- **422 Unprocessable Entity**: Invalid request payload (Pydantic validation errors included)
- **400 Bad Request**: Invalid file type, age out of range, etc.
- **500 Internal Server Error**: Groq API failure (includes full error response)

## Notes

- KB file is created automatically on first startup if missing
- Empty KB = empty RAG context (still functional)
- Plan generation enforces strict JSON structure
- Chat sessions are temporary (restart clears all history)
- All endpoints accept both JSON and form-data

## Support

For issues or questions, refer to the inline code comments or check the Groq API documentation at https://console.groq.com/docs
