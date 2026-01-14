# Blog Post Manager

A simple blog post management application for AI-assisted content creation. This application allows users to create, edit, delete, and search blog posts, with the ability to generate new posts using a local LLM.

## Tech Stack

- **Frontend**: React with TypeScript, Material UI, Vite
- **Backend**: Python with FastAPI
- **Database**: Qdrant (vector database)
- **LLM**: Ollama (local LLM)

## Features

- Create, read, update, and delete blog posts
- Search posts using semantic search
- Generate new blog posts based on a topic using LLM
- 10 pre-seeded example blog posts

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

## Quick Start with Docker

1. Start all services:
```bash
docker compose up -d
```

2. Pull required Ollama models (run once after first start):
```bash
docker exec -it recruitment-ollama-1 ollama pull llama3.2
docker exec -it recruitment-ollama-1 ollama pull nomic-embed-text
```

3. Seed the database with example posts:
```bash
cd backend
uv sync
uv run python seed_data.py
```

4. Then go to next section to run backend and frontend

## Local Development

### Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

Backend:
```bash
cd backend
uv sync --extra dev
uv run pytest
```

Frontend:
```bash
cd frontend
npm test
```

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | Get all blog posts |
| GET | `/api/posts/{id}` | Get a single post by ID |
| POST | `/api/posts` | Create a new post |
| POST | `/api/posts/update` | Update an existing post |
| GET | `/api/posts/delete/{id}` | Delete a post |
| GET | `/api/posts/search/{query}` | Search posts by text |
| POST | `/api/generate` | Generate a new post from topic |
| GET | `/api/health` | Health check |

### Request/Response Examples

#### Create Post
```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "My Post", "content": "Post content here", "topic": "technology"}'
```

#### Update Post
```bash
curl -X POST http://localhost:8000/api/posts/update \
  -H "Content-Type: application/json" \
  -d '{"id": "post-uuid", "title": "Updated Title", "content": "Updated content", "topic": "technology"}'
```

#### Delete Post
```bash
curl http://localhost:8000/api/posts/delete/post-uuid
```

#### Search Posts
```bash
curl http://localhost:8000/api/posts/search/machine%20learning
```

#### Generate Post
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence"}'
```

## Architecture

```
ai-recruitment/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── seed_data.py      # Database seeding script
│   ├── test_main.py      # Backend tests
│   ├── pyproject.toml    # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx       # Main React component
│   │   ├── App.test.tsx  # Frontend tests
│   │   └── main.tsx      # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Environment Variables

### Backend
- `QDRANT_HOST`: Qdrant server host (default: localhost)
- `QDRANT_PORT`: Qdrant server port (default: 6333)
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)

## Potential Improvements

This codebase has been intentionally designed with certain patterns that could be improved. Consider the following areas for enhancement:

1. **API Design**: Review the HTTP methods used for each endpoint
2. **Code Organization**: Consider breaking down large components
3. **LLM Integration**: Evaluate the architecture of LLM calls
4. **Prompt Engineering**: Review how prompts are structured
5. **Code Quality**: Consider adding formatters and linters

### Additional Feature Ideas

- Tagging blog posts with keywords using LLM
- Keyword-based search functionality
- Style matching to existing posts
- Integration with external knowledge sources
