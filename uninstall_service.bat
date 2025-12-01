@echo off
REM bu script önce servisi durdurur sonra kaldırır.

cd /d "%~dp0"

set "EXE_PATH=%BASE_DIR%dist\case_study_app\case_study_app.exe"

%EXE_PATH% stop

%EXE_PATH% remove