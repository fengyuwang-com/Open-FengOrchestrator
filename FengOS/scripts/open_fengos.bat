@echo off
rem FengOS desktop entry: probe backend over HTTP, heal zombie, start on demand, open page.
rem Probe truth = HTTP 200 (TCP connect lies when a wedged server still accepts).
rem Zombie rule: port held by a uvicorn python but HTTP dead -> kill that PID, then restart.
rem Diagnostic log: %TEMP%\fengos_open.log (append). Pure ASCII, CRLF.
setlocal enableextensions
set "BASE=http://127.0.0.1:8765"
set "PROBE_PORT=8765"
set "HERE=%~dp0"
set "LOG=%TEMP%\fengos_open.log"

call :LOG "==== RUN start ===="
call :LOG "BASE=%BASE% HERE=%HERE%"

rem ---- 1) HTTP probe (truth). TCP probe only used to detect zombie (held port, dead HTTP).
call :PROBE
if "%PROBE_OK%"=="1" (
  call :LOG "probe: backend ALIVE, skip autostart"
  goto OPEN
)
call :ZOMBIE
call :LOG "probe: backend DOWN, launching start_fengos.bat"

rem ---- 2) Backend down: launch minimized (stdout to logs\uvicorn_stdout.log), wait up to ~25s ----
start "FengOS" /min "%HERE%start_fengos.bat"
set "N=0"
:WAIT
call :SLEEP 2
call :PROBE
if "%PROBE_OK%"=="1" (
  call :LOG "probe: backend came up after %N% waits"
  goto OPEN
)
set /a N+=1
if %N% LSS 12 goto WAIT
call :LOG "probe: backend still down after 12 waits, opening anyway"

rem ---- 3) Open Web UI: triple fallback, never abort on failure ----
:OPEN
call :LOG "open step 1: start url"
start "" "%BASE%/"
if %errorlevel%==0 (call :LOG "open step 1 rc=0") else (call :LOG "open step 1 rc=%errorlevel%")
call :SLEEP 1
call :LOG "open step 2: rundll32 FileProtocolHandler"
rundll32 url.dll,FileProtocolHandler %BASE%/
if %errorlevel%==0 (call :LOG "open step 2 rc=0") else (call :LOG "open step 2 rc=%errorlevel%")
call :SLEEP 1
call :LOG "open step 3: explorer"
start "" explorer.exe "%BASE%/"
if %errorlevel%==0 (call :LOG "open step 3 rc=0") else (call :LOG "open step 3 rc=%errorlevel%")
call :LOG "DONE ==== RUN end ===="
endlocal
exit /b 0

rem ================= subroutines =================
:LOG
>>"%LOG%" echo [%date% %time%] %~1
exit /b 0

:SLEEP
powershell -NoProfile -Command "Start-Sleep -Seconds %~1" >nul 2>&1
if %errorlevel%==0 exit /b 0
ping -n %~1 127.0.0.1 >nul 2>&1
exit /b 0

:PROBE
rem Truth: curl HTTP GET; fallback: powershell HTTP download (not TCP connect).
set "PROBE_OK=0"
curl.exe -s -o nul --max-time 4 "http://127.0.0.1:%PROBE_PORT%/" >nul 2>&1
if %errorlevel%==0 (
  set "PROBE_OK=1"
  call :LOG "probe method=curl-http result=alive"
  exit /b 0
)
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing -TimeoutSec 4 'http://127.0.0.1:%PROBE_PORT%/'|Out-Null;exit 0}catch{exit 1}" >nul 2>&1
if %errorlevel%==0 (
  set "PROBE_OK=1"
  call :LOG "probe method=ps-http result=alive"
  exit /b 0
)
powershell -NoProfile -Command "$c=New-Object Net.Sockets.TcpClient;try{$c.Connect('127.0.0.1',%PROBE_PORT%);if($c.Connected){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
if %errorlevel%==0 (
  set "TCP_HELD=1"
  call :LOG "probe: http dead but tcp HELD (zombie suspect)"
) else (
  set "TCP_HELD=0"
  call :LOG "probe method=http+tcp result=down"
)
exit /b 0

:ZOMBIE
rem Only when HTTP dead: kill python processes listening on PROBE_PORT whose
rem command line contains uvicorn (scoped self-heal, never touches other python).
if not "%TCP_HELD%"=="1" exit /b 0
call :LOG "zombie: scanning for uvicorn python holding port %PROBE_PORT%"
powershell -NoProfile -Command "$port=%PROBE_PORT%;$rows=Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue;foreach($r in $rows){$p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$r.OwningProcess);if($p -and $p.Name -like 'python*' -and $p.CommandLine -match 'uvicorn'){Stop-Process -Id $p.ProcessId -Force;Write-Output ('zombie killed '+$p.ProcessId)}}" >>"%LOG%" 2>&1
call :SLEEP 1
exit /b 0
