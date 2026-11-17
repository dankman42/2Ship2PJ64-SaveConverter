#!/bin/sh
# Builds the Linux app (2ship-to-pj64) from gui.py + convert.py.
# Needs Python 3 with Tk (Debian/Ubuntu: sudo apt install python3-tk python3-venv).
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q pyinstaller
.venv/bin/python make_icon.py
.venv/bin/pyinstaller --onefile --windowed --clean --noconfirm --name 2ship-to-pj64 --add-data "moon.png:." gui.py
cp dist/2ship-to-pj64 ./2ship-to-pj64-linux-x86_64
chmod +x ./2ship-to-pj64-linux-x86_64
echo "Built 2ship-to-pj64-linux-x86_64"
