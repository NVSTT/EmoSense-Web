# Copilot / AI Assistant Instructions for EmoSense-Web

This file gives focused, actionable guidance for AI coding agents working in this repository.

Summary
- Project: Flask web app for Russian sentiment/emotion analysis (`EmoSense-Web`).
- Backend: `app.py` (Flask) with blueprints in `routes/`.
- ML: two modes — RuBERT (transformers) in `model/rubert.py` and LLM via Ollama in `model/ollama.py`.

Quick architecture notes
- Entry point: `app.py` — config, DB init (`schema/db_main.py`), JWT setup and blueprint registration.
- Routes: `routes/main_routes.py` (public UI and analysis logic) and `routes/auth_routes.py` (JSON API for registration/login).
- ML helpers: `model/rubert.py` exposes `get_rubert_pipeline()`; `model/ollama.py` provides `OllamaClient` with defaults from `OLLAMA_HOST` and `OLLAMA_MODEL` env vars.
- Business logic / utilities: `servises/` (note the spelling) contains `analyze.py`, `generate.py`, `chunk.py`, `resize.py`.
- Templates/static: `templates/` and `static/` hold UI; `templates/index.html` and `login.html` are used by routes.

Developer workflows & important commands
- Install deps: `pip install -r requirements.txt`.
- Run locally (dev): `python app.py` — Flask runs in debug mode by default.
- Ollama (LLM mode): run local Ollama server and set env vars if needed. Example:
  - `ollama serve` and `ollama pull <model>`
  - Optionally set `OLLAMA_HOST` and `OLLAMA_MODEL` in environment to override defaults.
- DB: the app uses SQLite (`SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'`) — `db.create_all()` is called at startup.

Project-specific conventions & patterns
- Blueprint-based routes: add endpoints by registering new blueprints in `app.py` and using `Blueprint` objects in `routes/`.
- JWT via cookies: JWTs are stored in a cookie named `access_token_cookie`; CSRF protection is disabled (`JWT_COOKIE_CSRF_PROTECT = False`). Be careful when modifying auth flows.
- Input sanitization: user text is cleaned with `bleach.clean(..., tags=[], attributes={}, strip=True)` and trimmed to max 1000 characters in routes.
- ML selection: `servises.analyze.analyze_sentiment(text, choose, ollama)` — `choose` True → Ollama (LLM), False → RuBERT.
- Ollama usage:
  - `model/ollama.py` expects the Ollama HTTP API to return a JSON or text block; `analyze_with_ollama` regex-parses a JSON object from the response.
  - Prompts in `servises/generate.py` and `servises/analyze.py` follow the pattern: instruct the model, include the `post_text`, and ask for JSON or short text.
  - OllamaClient.generate returns `None` on error; callers use sensible defaults (e.g., fallback scores or messages).
- RuBERT usage: `model/rubert.py` instantiates a HF `pipeline` with model `blanchefort/rubert-base-cased-sentiment-rusentiment`; results are aggregated over chunks (see `servises/chunk.py`).

Error handling & defensive choices to mirror
- Services return fallbacks rather than raising for transient LLM errors: e.g., default scores `{0.33,0.33,0.34}` and default messages when LLM fails.
- `analyze_with_ollama` extracts JSON with a regex and then validates keys `positive`, `negative`, `neutral` before using the values. Maintain that parsing pattern if changing prompts.

Where to add features
- New ML models or wrappers: add to `model/` and expose a simple function/class similar to `get_rubert_pipeline()` or `OllamaClient`.
- New analysis utilities: place in `servises/` and keep external integrations (requests to Ollama, HF pipeline instantiation) inside `model/` or `servises/` wrappers.
- Frontend changes: update `templates/*.html` and assets under `static/`.

Examples & concrete snippets
- To call Ollama from code (pattern already used in `routes/main_routes.py`):
  - `ollama = OllamaClient(DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL)`
  - `comment = generate_ai_comment_with_ollama(post_text, ollama)`
- To add route-protected dashboard endpoint use `@jwt_required()` and fetch user via `get_jwt_identity()` (see `routes/main_routes.py`).

Notes for AI agents editing the code
- Preserve existing prompt formats and output expectations when editing `servises/generate.py` or `servises/analyze.py` — other code depends on those exact response shapes.
- When changing JWT/cookie behavior, update `app.py` and `routes/auth_routes.py` together; tests (none present) are manual — always run the app to smoke-test.
- Avoid leaking secrets: `app.config['SECRET_KEY']` and `JWT_SECRET_KEY` in `app.py` are placeholders. Use environment variables for real deployments.

Missing or non-discoverable items to ask the maintainer
- Intended Ollama host/IP used in default `model/ollama.py` (`192.168.134.216:11434`) — confirm whether to keep as default or require env var.
- Any preferred LLM prompt templates or safety constraints beyond what's in `servises/generate.py`.

If anything here is unclear or you want more examples (e.g., adding a new model wrapper, example unit test, or a CI run), tell me which area to expand. 
