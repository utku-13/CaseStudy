@echo off
REM Bu script, case_study_app.exe'yi Windows Servisi olarak kurar ve Task Scheduler gorevini olusturur.
REM Bu dosyayi proje ana dizininde calistirin (dist klasorunun yaninda).
REM Yonetici olarak calistirmayi unutmayin!

REM Calisma dizinini bat dosyasinin oldugu yere al
cd /d "%~dp0"

REM Exe dosyasinin yolu
set EXE_PATH=%CD%\dist\case_study_app\case_study_app.exe

echo 1. Servis kuruluyor...
"%EXE_PATH%" install

echo 2. Servis otomatik baslatma moduna aliniyor...
"%EXE_PATH%" --startup auto update

echo 3. GUI icin Windows Zamanlanmis Gorevi (Task) olusturuluyor...
REM Mevcut gorev varsa once silelim (temiz kurulum icin)
schtasks /Delete /TN "CaseStudyWorker" /F >nul 2>&1

REM Yeni gorevi olusturalim.
REM /SC ONCE : Tek seferlik (servis tetikleyecek)
REM /RL HIGHEST : Yonetici haklariyla calissin
REM /TR : Calistirilacak komut
REM /F : Zorla olustur
schtasks /Create /SC ONCE /TN "CaseStudyWorker" /TR "\"%EXE_PATH%\" --gui-worker" /ST 00:00 /F /RL HIGHEST

powershell -Command "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Compatibility Win8; Set-ScheduledTask -TaskName 'CaseStudyWorker' -Settings $settings"

echo.
echo 4. Servis baslatiliyor...
"%EXE_PATH%" start

echo.
echo Islem tamamlandi!
echo - Servis durumu icin 'services.msc'ye bakabilirsin.
echo - GUI penceresi kisa sure icinde acilacaktir.
echo.
pause