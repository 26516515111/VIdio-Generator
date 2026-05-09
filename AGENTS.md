# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-09
**Commit:** 59aa270
**Branch:** master

## OVERVIEW

Full-stack voice conversion assistant (语音转换助手). React/TypeScript frontend + Python/FastAPI backend, packaged as single Windows .exe via PyInstaller. Converts text/image input → LLM processing → TTS audio output.

## STRUCTURE

```
语音转换助手/
├── frontend/           # React 19 + Vite + Redux Toolkit + Ant Design
│   └── src/
│       ├── components/ # UI components (Chat*, VoiceSelector, Settings)
│       ├── pages/      # Route pages (Home, Login, Register, Profile)
│       ├── services/   # API client modules (auth, llm, ocr, tts, models)
│       ├── store/      # Redux slices (auth, chat, input, result, settings)
│       ├── types/      # TypeScript type definitions
│       └── styles/     # Global CSS (theme)
├── backend/            # Python 3.11 + FastAPI + SQLAlchemy + SQLite
│   └── app/
│       ├── api/        # REST route handlers (auth, llm, ocr, tts, users)
│       ├── services/   # Business logic (auth, llm, ocr, tts, user, tag_parser)
│       ├── models/     # SQLAlchemy models (user, api_key, history)
│       ├── utils/      # Security utilities (JWT, password hashing)
│       └── static/     # Static file serving (empty in dev)
├── data/               # Runtime data (SQLite DB + generated audio)
└── docs/               # Documentation
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new API endpoint | `backend/app/api/` | Create router, register in `main.py` |
| Add new service | `backend/app/services/` | Business logic layer |
| Add new DB model | `backend/app/models/` | SQLAlchemy ORM, update `database.py` |
| Add new page | `frontend/src/pages/` | Add route in `App.tsx` |
| Add new component | `frontend/src/components/` | Shared UI components |
| Add new Redux slice | `frontend/src/store/` | Register in `store/index.ts` |
| Add new API client | `frontend/src/services/` | Mirror backend routes |
| Modify build | `backend/build.py` | Orchestrates npm + PyInstaller |
| Change config | `backend/app/config.py` | pydantic-settings, reads `.env` |

## CONVENTIONS

- **TypeScript strict**: `noUnusedLocals`, `noUnusedParameters`, `erasableSyntaxOnly`, `verbatimModuleSyntax`
- **Import style**: Use `import type` for type-only imports (enforced)
- **No enums**: Use `const` objects or union types instead (erasableSyntaxOnly)
- **ESM modules**: Frontend uses `"type": "module"`
- **Python deps**: Pinned exact versions in `requirements.txt` (no pyproject.toml)
- **No formatter**: No Prettier or Black configured
- **No type checker**: No mypy/pyright for Python

## ANTI-PATTERNS (THIS PROJECT)

- **Hardcoded SECRET_KEY**: `config.py` has weak default `"dev-secret-key-change-in-production-12345"` - MUST override via `.env`
- **Plaintext API keys**: `api_key.py` stores keys as plaintext Text column - TODO: encrypt before production
- **Duplicate data/audio/**: Two locations exist (`data/audio/` and `backend/data/audio/`) - confusing
- **Loose files in root**: `.wav` and `.png` files scattered in project root
- **No tests**: README claims `tests/` exists but it doesn't - no test infrastructure at all
- **No CI/CD**: No GitHub Actions, no Dockerfile, no automated pipeline
- **CORS hardcoded**: `main.py` hardcodes `allow_origins=["http://localhost:3000"]`
- **Windows-only build**: `build.py` hardcodes Windows npm paths

## COMMANDS

```bash
# Development
cd backend && python run.py          # Start backend (port 8000)
cd frontend && npm run dev           # Start frontend (port 3000)

# Build
python backend/build.py              # Full build (frontend + PyInstaller)

# Lint
cd frontend && npm run lint          # ESLint for TypeScript

# Dependencies
cd frontend && npm install           # Install frontend deps
cd backend && pip install -r requirements.txt  # Install backend deps
```

## NOTES

- **Dev workflow**: Frontend proxies `/api` to `localhost:8000` via Vite config
- **Single exe**: PyInstaller bundles frontend/dist + backend into one .exe
- **SQLite**: Database file at `backend/data/app.db` (gitignored)
- **Audio output**: Generated files in `backend/data/audio/`
- **LLM prompts**: `llm_service.py` has Chinese "不要" (don't) constraints for LLM behavior
- **React 19**: README says "React 18" but package.json has `^19.2.5` - docs drift
