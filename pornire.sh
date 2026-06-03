#!/bin/bash

clear
echo "=== YTMP3 - Setup & Launcher ==="

# 1. Instalarea dependințelor de sistem
PACHETE_LIPSA=""
if ! command -v pip3 &> /dev/null; then PACHETE_LIPSA+=" python3-pip"; fi
if ! command -v ffmpeg &> /dev/null; then PACHETE_LIPSA+=" ffmpeg"; fi

if [ -n "$PACHETE_LIPSA" ]; then
    echo "[!] Prima rulare: Se instalează componentele de sistem necesare..."
    sudo apt update -qq
    sudo apt install -y -qq $PACHETE_LIPSA > /dev/null 2>&1
fi

# 2. Instalarea pachetelor Python
LIBRARII_LIPSA=""
python3 -c "import yt_dlp" &> /dev/null || LIBRARII_LIPSA+=" yt-dlp"
python3 -c "import PySide6" &> /dev/null || LIBRARII_LIPSA+=" PySide6"

if [ -n "$LIBRARII_LIPSA" ]; then
    echo "[!] Se instalează motorul aplicației..."
    pip3 install $LIBRARII_LIPSA --user --break-system-packages -q 2>/dev/null || pip3 install $LIBRARII_LIPSA --user -q
fi

CALE_CURENTA=$(pwd)

# Curățăm vechea poză de pe net (dacă există)
rm -f "$CALE_CURENTA/icon.png"

# 3. Generăm automat iconița mov personalizată (SVG - Vectorială)
if [ ! -f "$CALE_CURENTA/icon.svg" ]; then
    echo "[*] Generez iconița mov YTMP3..."
    cat <<EOF > "$CALE_CURENTA/icon.svg"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="64" fill="#a81cff"/>
  <path d="M100 80 L180 128 L100 176 Z" fill="white"/>
</svg>
EOF
fi

# 4. Integrarea în Meniul Ubuntu
APP_DIR="$HOME/.local/share/applications"
FISIER_DESKTOP="$APP_DIR/YTMP3.desktop"

mkdir -p "$APP_DIR"

echo "[*] Integrez aplicația în meniul sistemului (App Drawer)..."
cat <<EOF > "$FISIER_DESKTOP"
[Desktop Entry]
Version=1.0
Name=YTMP3 Downloader
Comment=Descarcă muzică și videoclipuri de pe YouTube rapid și sigur
Exec=python3 "$CALE_CURENTA/app.py"
WorkingDirectory=$CALE_CURENTA
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Video;Utility;
Icon=$CALE_CURENTA/icon.svg
EOF

chmod +x "$FISIER_DESKTOP"
echo "[*] Instalare completă! Caută 'YTMP3' în meniul Ubuntu."

echo "=== Pornim aplicația... ==="
echo "-----------------------------------------"

python3 app.py