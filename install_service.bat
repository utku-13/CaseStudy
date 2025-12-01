@echo off
REM Bu script, main.py'yi Windows Servisi olarak kurar ve başlatır.
REM Yonetici olarak calistirmayi unutmayin!

cd /d "%~dp0"

set "EXE_PATH=%BASE_DIR%dist\case_study_app\case_study_app.exe"

echo Servis kuruluyor...
%EXE_PATH% install

echo Servis otomatik baslatma moduna aliniyor...
%EXE_PATH% --startup auto update

echo Servis baslatiliyor...
%EXE_PATH% start

echo.
echo Islem tamamlandi! Servis durumu icin 'services.msc'ye bakabilirsin.
pause

