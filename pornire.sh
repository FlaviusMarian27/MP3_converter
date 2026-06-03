#!/bin/bash

echo "=== Verificăm cerințele sistemului... ==="

# 1. pip3
if ! command -v pip3 &> /dev/null; then
    echo "[!] Instalez python3-pip..."
    sudo apt update && sudo apt install -y python3-pip
fi

# 2. ffmpeg (vital pentru conversia audio/video)
if ! command -v ffmpeg &> /dev/null; then
    echo "[!] Instalez ffmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
fi

# 3. yt-dlp
python3 -c "import yt_dlp" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[!] Instalez yt-dlp..."
    pip3 install yt-dlp --user --break-system-packages 2>/dev/null || pip3 install yt-dlp --user
fi

# 4. PySide6 (Interfața grafică supremă)
python3 -c "import PySide6" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[!] Instalez PySide6..."
    pip3 install PySide6 --user --break-system-packages 2>/dev/null || pip3 install PySide6 --user
fi

echo ""
echo "=== Totul e pregătit! Pornim YTMP3... ==="
echo "-----------------------------------------"

python3 app.py