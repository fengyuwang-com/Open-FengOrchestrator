@echo off
rem FengOS autostart: launch uvicorn minimized, stdout/stderr to a persistent log.
rem Note: pythonw crashes uvicorn (stderr is None under pythonw), so use python + start /min.
rem Log: FengOS\logs\uvicorn_stdout.log (overwritten per start) for crash diagnosis.
cd /d ~/FengOrchestrator/FengOS
if not exist logs mkdir logs
start "FengOS" /min cmd /c "python -m uvicorn server.main:app --host 0.0.0.0 --port 8765 > logs\uvicorn_stdout.log 2>&1"
