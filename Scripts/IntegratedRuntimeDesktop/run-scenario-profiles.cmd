@echo off
setlocal EnableExtensions
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\Run-ScenarioProfiles.ps1" -RimWorldRoot "%~1" -Profile "%~2" -GrainsRepositoryRoot "%~3"
exit /b %ERRORLEVEL%
