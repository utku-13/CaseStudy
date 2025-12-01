@echo off
REM Bu script, CaseStudyService servisini ve ilgili Task Scheduler gorevini siler.
REM Yonetici olarak calistirmayi unutmayin!

REM Calisma dizinini bat dosyasinin oldugu yere al
cd /d "%~dp0"

REM Exe dosyasinin yolu
set EXE_PATH=%CD%\dist\case_study_app\case_study_app.exe

echo 1. Servis durduruluyor...
"%EXE_PATH%" stop

echo.
echo 2. Servis siliniyor...
"%EXE_PATH%" remove

echo.
echo 3. Task Scheduler gorevi siliniyor...
schtasks /Delete /TN "CaseStudyWorker" /F

echo.
echo Islem tamamlandi.
echo Log dosyalarini silmek istersen 'dist\case_study_app\service_output.txt' dosyasina bakabilirsin.
pause