# Neuro Agent

Desktop app that combines:
- **Obsidian-style knowledge management** (notes, canvas, graph, slides, tables)
- **Hermes Agent autonomous AI** (self-improving skills, persistent memory, multi-platform)
- **Gentle AI methodology** (SDD workflow, code review, mentor persona)

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Tauri + React + TypeScript |
| Backend | Python (FastAPI, sidecar) |
| Storage | SQLite + FTS5 + local Markdown |
| Communication | WebSocket + HTTP |

## Development

### Frontend
```sh
cd frontend
npm install
npm run tauri dev
```

### Backend
```sh
cd backend
pip install -r requirements.txt
python -m src.main
```
