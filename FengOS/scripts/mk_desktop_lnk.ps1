$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$name = 'FengOS' + [char]0x89C2 + [char]0x666F + [char]0x53F0 + '.lnk'
$d = Join-Path $desk $name
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut($d)
$lnk.TargetPath = '~/FengOrchestrator/FengOS/scripts/open_fengos.bat'
$lnk.WorkingDirectory = '~/FengOrchestrator/FengOS'
$lnk.Description = 'FengOS desktop entry'
$lnk.Save()
Write-Host "LNK-OK $d"
