# AGENTS.md

## Project overview

Educational web app (Spanish) for children: explore numbers in a gallery and practice addition with numberblock images. FastAPI backend + vanilla JS frontend. No build step, no lint/typecheck.

## AGENTS.md updates (MANDATORY)

This file must be updated on every change that affects project structure, setup, configuration, dependencies, conventions, or any other information documented here. Keeping it accurate is required for the AI to work correctly.

## Code exploration (MANDATORY)

Use **codegraph tools (cgc)** as the primary way to explore and understand code:

- `codegraph_context_for_task` — files/symbols relevant to a natural-language task
- `codegraph_find_symbol`, `codegraph_search_symbols` — locate symbols by name/query
- `codegraph_search_semantic` — hybrid semantic + token search
- `codegraph_find_callers`, `codegraph_find_callees`, `codegraph_trace_dependencies` — call graph
- `codegraph_list_files`, `codegraph_get_impact_radius`, `codegraph_find_related_tests`
- `codegraph_architecture_overview`, `codegraph_graph_stats`, `codegraph_detect_frameworks`

Only fall back to `grep`, `read`, or `glob` when a codegraph query does not satisfy the need (e.g. result missing, too coarse, or tool error). Use the active repo's indexed graph; re-index with `codegraph_index_repo` if needed.

## Run (two terminals)

```bash
# Terminal 1 — Backend (port 8000)
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend (port 9093)
ln -s ../static frontend/static   # required once — symlink for image serving
python3 -m http.server 9093 --bind 0.0.0.0 --directory frontend
```

Or use `fish start.fish` to do all of the above automatically.

## Tests

```bash
python -m pytest -q   # from the repo root
```

pytest and `httpx` (for FastAPI `TestClient`) are in `backend/requirements.txt`.
No CI, no lint/typecheck.

## Structure

| Path | Role |
|---|---|
| `backend/main.py` | FastAPI entrypoint |
| `backend/game_logic.py` | Gallery pagination and sum quiz generation; reads config per call |
| `backend/session_manager.py` | In-memory per-browser session store |
| `backend/sesion.py` | Deep Sesión module: storage, fixed schema, Suma rules, verdict |
| `backend/config.py` | Single home for shipped defaults and the `config.json` overlay; `get`/`get_all` read lazily, `reload` drops the cache |
| `config.json` | Game tuning knobs (sum ranges, TOTAL_IMAGES, gallery settings) |
| `frontend/` | `index.html`, `galeria.html`, `sum.html`, `css/styles.css` |
| `frontend/js/` | `api.js` (fetch wrapper), `audio.js` (Web Audio SFX), `count.js` (gallery), `sum.js` |
| `tests/` | pytest: HTTP smoke tests via FastAPI `TestClient`, plus config, Sesión rule, and quiz-generation tests under fixture tuning |
| `static/images/` | `1.jpg`/`.jpeg`–`N.jpg`/`.jpeg` (filename = value for sum and gallery) |

## Key details

- **Game modes**: Galería (`galeria.html`) and Suma (`sum.html`). Count was retired (ADR-0003).
- **Session**: Via `X-Session-Id` header. Backend returns `session_id` in every response; frontend stores & resends it. Three consecutive wrong answers reset the streak; a correct Reto adds two. State is in-memory (lost on restart).
- **Image serving**: FastAPI mounts `/static` directly. For the Python HTTP server (port 9093), create `frontend/static -> ../static` symlink. Run `python static/images/generate_placeholders.py` if images missing (reads `TOTAL_IMAGES` from `config.json`). For WebP/PNG, run `python static/images/convert_webp_to_jpg.py`.
- **Audio**: `audio.js` uses Web Audio API (no external files). Auto-starts on quiz load, stops on `beforeunload`.
- **Gallery**: Shows numbers 1..`GALLERY_CONTINUOUS_MAX` continuously (placeholder if file missing), plus `GALLERY_EXTRAS` (only if file exists on disk). Sorted numerically. Independent of `TOTAL_IMAGES` — does not affect the sum game.
- **Spanish UI**: All visible strings in Spanish. Keep `game_type` strings in English (`"sum"`; `"count"` is legacy).
- **Tests**: `pytest` + FastAPI `TestClient`; run from the repo root with `python -m pytest -q`. No CI, no formatter. Logging via `loguru` (stderr, DEBUG+).

## Commit best practices (MANDATORY — sourced from Git docs via context7)

- **Atomic commits**: each commit is a single logical change. If a description gets long, split the commit.
- **Multiple areas**: if changes span unrelated areas, commit them separately.
- **Subject line (first line)**: max 50 chars, imperative mood (`"add foo"` not `"added foo"`), no trailing period. Prefix with area: e.g. `backend:`, `frontend:`, `config:`, `images:`.
- **Body** (optional but encouraged): blank line after subject. Wrap at 72 columns. Explain *why* the change was made, not *what* (the diff shows what). Be explicit even if the reason seems obvious.
- **Signed-off-by**: include a `Signed-off-by` trailer via `git commit -s` for accountability.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in `Lmex89/quiz-numberblock`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles map to the default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` live at the repo root. See `docs/agents/domain.md`.
