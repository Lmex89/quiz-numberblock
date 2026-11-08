import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Match the app: backend/ on the path for top-level config/game_logic/sesion,
# repo root for the backend package.
for path in (ROOT / "backend", ROOT):
    sys.path.insert(0, str(path))
