@echo off
echo Starting CamTech University Assistant...
echo.

echo [1/3] Starting PostgreSQL database...
docker compose up -d
timeout /t 5 /nobreak >nul

echo [2/3] Activating Python environment...
call .venv\Scripts\activate

echo [3/3] Starting API server...
echo.
echo Server will be available at: http://127.0.0.1:8000
echo Press CTRL+C to stop the server.
echo.
uvicorn app.main:app --port 8000
