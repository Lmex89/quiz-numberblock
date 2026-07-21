# AGENTS.md

## Project overview

Educational quiz web app (Spanish) for children: count objects or sum their values. FastAPI backend + vanilla JS frontend. No build step, no test/lint/typecheck.

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

## Structure

| Path | Role |
|---|---|
| `backend/main.py` | FastAPI entrypoint |
| `backend/game_logic.py` | Quiz generation ("count" / "sum") |
| `backend/session_manager.py` | In-memory per-browser session store |
| `backend/config.py` | Loads `config.json` with defaults |
| `config.json` | Game tuning knobs (count/sum ranges, TOTAL_IMAGES, gallery settings) |
| `frontend/` | `index.html`, `galeria.html`, `sum.html`, `css/styles.css` |
| `frontend/js/` | `api.js` (fetch wrapper), `audio.js` (Web Audio SFX), `count.js`, `sum.js` |
| `static/images/` | `1.jpg`/`.jpeg`–`32.jpg`/`.jpeg` (filename = value for sum/gallery game) |

## Key details

- **Session**: Via `X-Session-Id` header. Backend returns `session_id` in every response; frontend stores & resends it. Streaks reset on wrong answers. State is in-memory (lost on restart).
- **Image serving**: FastAPI mounts `/static` directly. For the Python HTTP server (port 9093), create `frontend/static -> ../static` symlink. Run `python static/images/generate_placeholders.py` if images missing (reads `TOTAL_IMAGES` from `config.json`). For WebP/PNG, run `python static/images/convert_webp_to_jpg.py`.
- **Audio**: `audio.js` uses Web Audio API (no external files). Auto-starts on quiz load, stops on `beforeunload`.
- **Gallery**: Shows numbers 1..`GALLERY_CONTINUOUS_MAX` continuously (placeholder if file missing), plus `GALLERY_EXTRAS` (only if file exists on disk). Sorted numerically. Independent of `TOTAL_IMAGES` — does not affect sum/count games.
- **Spanish UI**: All visible strings in Spanish. Keep `game_type` strings in English (`"count"`, `"sum"`).
- **No tests, no CI, no formatter** — none configured. Logging via `loguru` (stderr, DEBUG+).

## Commit best practices (MANDATORY — sourced from Git docs via context7)

- **Atomic commits**: each commit is a single logical change. If a description gets long, split the commit.
- **Multiple areas**: if changes span unrelated areas, commit them separately.
- **Subject line (first line)**: max 50 chars, imperative mood (`"add foo"` not `"added foo"`), no trailing period. Prefix with area: e.g. `backend:`, `frontend:`, `config:`, `images:`.
- **Body** (optional but encouraged): blank line after subject. Wrap at 72 columns. Explain *why* the change was made, not *what* (the diff shows what). Be explicit even if the reason seems obvious.
- **Signed-off-by**: include a `Signed-off-by` trailer via `git commit -s` for accountability.
