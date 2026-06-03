#!/bin/bash

echo "=== Verificăm cerințele sistemului... ==="

# 1. Verificăm dacă avem pip3 instalat
if ! command -v pip3 &> /dev/null; then
    echo "[!] Instalez python3-pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# 2. Verificăm dacă avem ffmpeg (vital pentru formatul MP3)
if ! command -v ffmpeg &> /dev/null; then
    echo "[!] Instalez ffmpeg..."
    sudo apt update
    sudo apt install -y ffmpeg
fi

# 3. Verificăm dacă modulul yt_dlp este instalat în Python
python3 -c "import yt_dlp" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[!] Instalez biblioteca yt-dlp..."
    # Folosim comanda de instalare standard pentru utilizatorul curent
    pip3 install yt-dlp --user --break-system-packages 2>/dev/null || pip3 install yt-dlp --user
fi

echo "=== Totul este pregătit! === "
echo "Pornim procesarea..."
echo "---------------------------------"

# Aici pornește efectiv fișierul tău Python
python3 procesare.py