#!/usr/bin/env fish

# ── Contador Dinámico — build, clean & run ──

set SCRIPT_DIR (realpath (dirname (status -f)))
cd $SCRIPT_DIR

# ── Get local IP ──
set LOCAL_IP (ip -4 -br addr show 2>/dev/null | grep -v "127.0.0.1" | head -1 | awk '{print $3}' | cut -d/ -f1)
if test -z "$LOCAL_IP"
    set LOCAL_IP (hostname -I 2>/dev/null | awk '{print $1}')
end
if test -z "$LOCAL_IP"
    set LOCAL_IP "localhost"
end

echo "━━━ Build & Clean ━━━"

# 1. Setup venv + deps
if not test -d venv
    echo "→ Creating venv..."
    python3 -m venv venv
end
echo "→ Activating venv..."
source venv/bin/activate.fish

echo "→ Installing backend deps..."
pip install -q -r backend/requirements.txt 2>&1 | grep -v "already satisfied"

# 2. Generate placeholders if missing
if not test -f static/images/1.jpg
    echo "→ Generating placeholder images..."
    python3 static/images/generate_placeholders.py
end

# 2b. Convert WebP/PNG/SVG images to JPG
echo "→ Converting image files to JPG..."
python3 static/images/convert_webp_to_jpg.py

# 3. Symlink static/ inside frontend/ for image serving on port 9093
if not test -L frontend/static
    echo "→ Linking static/ into frontend/..."
    ln -s ../static frontend/static
end

# 4. Kill leftover processes
echo "→ Cleaning up old processes..."
pkill -f "uvicorn backend.main" 2>/dev/null; true
pkill -f "http.server 9093" 2>/dev/null; true

# ── Run ──
echo ""
echo "━━━ Starting servers ━━━"

# Backend (port 8000, 0.0.0.0 for network access)
set backend_log /tmp/backend-8000.log
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level info > $backend_log 2>&1 &
set backend_pid $last_pid
echo "→ Backend (PID $backend_pid) → http://$LOCAL_IP:8000"

sleep 2

# Frontend (port 9093, 0.0.0.0 for network access)
set frontend_log /tmp/frontend-9093.log
python3 -m http.server 9093 --bind 0.0.0.0 --directory frontend > $frontend_log 2>&1 &
set frontend_pid $last_pid
echo "→ Frontend (PID $frontend_pid) → http://$LOCAL_IP:9093"

echo ""
echo "━━━ Ready ━━━"
echo "  Open:   http://$LOCAL_IP:9093"
echo "  API:    http://$LOCAL_IP:8000/api/quiz/count"
echo "  Local:  http://localhost:9093"
echo "  Logs:"
echo "    Backend  → tail -f $backend_log"
echo "    Frontend → tail -f $frontend_log"
echo "  Stop:  pkill -f uvicorn; pkill -f http.server"
