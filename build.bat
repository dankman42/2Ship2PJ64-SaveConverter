@echo off
rem Builds 2ship-to-pj64.exe from gui.py + convert.py. Needs Python 3 with PyInstaller (pip install pyinstaller).
cd /d "%~dp0"
python make_icon.py || exit /b 1
python -m PyInstaller --onefile --windowed --clean --noconfirm --name 2ship-to-pj64 --icon moon.ico --add-data "moon.png;." gui.py || exit /b 1
copy /y dist\2ship-to-pj64.exe . >nul
echo Built 2ship-to-pj64.exe
