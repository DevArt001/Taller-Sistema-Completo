@echo off
title ARM Racing Performance
cd /d C:\Users\Arturo_638\desktop\taller-sistema
call venv\Scripts\activate.bat
echo.
echo ================================
echo   ARM Racing Performance
echo   Servidor iniciando...
echo ================================
echo.
python manage.py runserver
pause