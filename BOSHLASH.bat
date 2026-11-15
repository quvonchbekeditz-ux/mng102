@echo off
chcp 65001 >nul
echo =======================================================
echo    CYBER UNIVERSITY - ORALIQ NAZORAT PLATFORMASI
echo =======================================================
echo 1. Web App platformasini brauzerda ochish (Laptop)
echo 2. Telegram Botni ishga tushirish (aiogram)
echo 3. Chiqish
echo =======================================================
set /p choice=Tanlovingizni kiriting (1, 2 yoki 3): 

if "%choice%"=="1" (
    echo Brauzerda ochilmoqda...
    start "" "index.html"
    exit
)
if "%choice%"=="2" (
    echo Telegram Bot ishga tushirilmoqda...
    python telegram_bot.py
    pause
    exit
)
exit
