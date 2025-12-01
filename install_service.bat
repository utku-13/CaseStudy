@echo off
REM Bu script, main.py'yi Windows Servisi olarak kurar ve başlatır.
REM Yonetici olarak calistirmayi unutmayin!

echo Servis kuruluyor...
python main.py install

echo Servis otomatik baslatma moduna aliniyor...
python main.py --startup auto update

echo Servis baslatiliyor...
python main.py start

echo.
echo Islem tamamlandi! Servis durumu icin 'services.msc'ye bakabilirsin.
pause

