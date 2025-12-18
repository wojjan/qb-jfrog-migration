@echo off
setlocal

:: --- Configuration constants ---
set SERVER_ID=igk-artifactory
set REMOTE_ROOT=pact_sps_prod-igk-local
set LOCAL_ROOT=c:/repository/qb-jenkins-migration/download-jenkins/%REMOTE_ROOT%

:: --- Validate required argument ---
if "%~1"=="" (
    echo Usage: %~nx0 Subfolder
    echo Example: %~nx0 Jacobsville-PC/SPS_SoC-A_05.00.03.077.0
    exit /b 1
)

:: --- Subfolder argument ---
set SUBFOLDER=%~1

:: --- Invoke JFrog CLI download ---
C:\JF\jf.exe rt dl ^
  --server-id=%SERVER_ID% ^
  --detailed-summary ^
  --include-dirs=true ^
  --threads=16 ^
  "%REMOTE_ROOT%/%SUBFOLDER%/(**/*)" ^
  "%LOCAL_ROOT%/%SUBFOLDER%/{1}"
