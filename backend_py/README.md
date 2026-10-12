# 🎬 AI Storytelling Platform — Story Generation & Self-Hosted TTS Module

## Architecture Overview

```
D:\VIDEO AI\
├── index.html                 # Frontend Studio Interface
├── app.js                     # Frontend Engine & API Connectors
├── style.css                  # Dark mode Cinematic Design System
├── serve-client.js            # Frontend Server (Port 3000)
└── backend_py/                # Python FastAPI Backend (Port 8000)
    ├── app/
    │   ├── config.py          # Pydantic Settings (DB, Gemini, TTS, Output Root)
    │   ├── database.py        # SQLAlchemy Engine, SessionLocal, get_db dependency
    │   ├── main.py            # FastAPI Entrypoint, CORS, Router Registrations
    │   ├── security.py        # Argon2id password hashing & JWT token management
    │   ├── models/
    │   │   ├── user.py        # User SQLAlchemy Model
    │   │   ├── project.py     # Project SQLAlchemy Model
    │   │   ├── story.py       # Story SQLAlchemy Model
    │   │   ├── scene.py       # Scene SQLAlchemy Model (Unique story_id + scene_num)
    │   │   └── job.py         # GenerationJob SQLAlchemy Model
    │   ├── schemas/
    │   │   ├── auth.py        # Pydantic Auth Schemas (UserCreate, UserLogin, UserResponse)
    │   │   └── story.py       # Pydantic Story Schemas (StoryGenerateRequest, SceneSchema, LTXExportSchema)
    │   ├── routes/
    │   │   ├── auth.py        # /api/auth (signup, login, me, logout)
    │   │   ├── health.py      # /api/health/db
    │   │   ├── projects.py    # /api/projects (story generation, TTS, export, audio stream)
    │   │   └── jobs.py        # /api/jobs/{job_id}
    │   └── services/
    │       ├── story_service.py # Gemini AI structured story generation & duration balancing
    │       └── tts_service.py   # Self-Hosted TTS engine abstraction (Kokoro/VibeVoice/Thunder Compute)
    ├── alembic/
    │   ├── env.py             # Alembic migration hook
    │   └── versions/
    │       ├── 001_create_users_table.py
    │       └── 002_create_story_generation_tables.py
    ├── alembic.ini            # Alembic configuration
    ├── .env                   # Active environment configuration
    ├── .env.example           # Environment template
    ├── test_api_auth.py       # Auth verification test suite (7 tests)
    └── test_story_tts_suite.py# Story generation, Gemini JSON, TTS & LTX test suite (9 tests)
```

---

## ⚡ Quick Start Commands

### 1. Activate Virtual Environment (PowerShell)
```powershell
& "d:\VIDEO AI\.venv\Scripts\Activate.ps1"
```

### 2. Run Database Migrations
```powershell
cd "d:\VIDEO AI\backend_py"
& "d:\VIDEO AI\.venv\Scripts\alembic.exe" upgrade head
```

### 3. Start FastAPI Backend (Port 8000)
```powershell
cd "d:\VIDEO AI\backend_py"
& "d:\VIDEO AI\.venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run Automated Test Suites
```powershell
cd "d:\VIDEO AI\backend_py"
& "d:\VIDEO AI\.venv\Scripts\python.exe" test_story_tts_suite.py
& "d:\VIDEO AI\.venv\Scripts\python.exe" test_api_auth.py
```

---

## 🔑 Environment Configuration (`backend_py/.env`)

```env
DATABASE_URL=postgresql+psycopg://storytelling_app:storytelling_pass_2026@localhost:5432/storytelling_db
FRONTEND_ORIGIN=http://localhost:3000
ENVIRONMENT=development
JWT_SECRET=sivacine_storytelling_super_secret_jwt_key_2026
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OUTPUT_ROOT=./outputs
TTS_PROVIDER=mock
TTS_MODEL_PATH=
```

---

## 📡 API Contract Reference

### 1. Generate Story
`POST /api/projects/{project_id}/story`
- **Auth Required**: `Bearer <token>` or Session Cookie
- **Request Body**:
```json
{
  "idea": "An astronaut discovers a glowing ancient obelisk on Mars.",
  "genre": "science_fiction",
  "language": "en",
  "target_duration_seconds": 60,
  "visual_style": "cinematic realism",
  "narration_enabled": true,
  "dialogue_enabled": true
}
```

### 2. Generate Narration (TTS)
`POST /api/projects/{project_id}/tts`
- **Request Body**:
```json
{
  "voice_id": "arun",
  "language": "en"
}
```

### 3. Export for LTX-2.5 AI Video Generator
`GET /api/projects/{project_id}/export`

---

## 🎥 LTX-2.5 Video Generation Handoff Schema

The video generation team consumes this exact JSON contract without requiring database models or TTS dependencies:

```json
{
  "schema_version": "1.0.0",
  "project_id": "6e168fd4-e981-41cb-92f6-5c2a367b6c69",
  "story_id": "5efb7187-f805-4f4c-b02e-2c7cdb6485b0",
  "title": "The Mars Transmission",
  "language": "en",
  "genre": "science_fiction",
  "target_duration_seconds": 60,
  "visual_style": "cinematic realism",
  "scenes": [
    {
      "scene_id": "1f4912a9-725f-4acb-a695-9b4e6fa40ae9",
      "scene_number": 1,
      "duration_seconds": 15,
      "visual_prompt": "Cinematic wide 8k drone shot of a solitary astronaut in an illuminated EVA suit walking across desolate red sand dunes on Mars, dust storms swirling under a cobalt sky.",
      "narration": "Commander Arun had spent eighty sols searching the Martian craters in complete isolation.",
      "dialogue": [
        {
          "character": "Arun",
          "text": "Base, telemetry sensors are picking up harmonic frequencies from sector 4.",
          "voice_id": "arun"
        }
      ],
      "visual_style": "cinematic realism",
      "status": "audio_generated",
      "audio_path": "outputs/6e168fd4-e981-41cb-92f6-5c2a367b6c69/5efb7187-f805-4f4c-b02e-2c7cdb6485b0/audio/1f4912a9-725f-4acb-a695-9b4e6fa40ae9.wav"
    }
  ]
}
```
