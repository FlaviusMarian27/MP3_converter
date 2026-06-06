#!/bin/bash
# ============================================================
#  pornire.sh — Setup & Launcher pentru YTMP3 (Linux/Ubuntu)
# ============================================================

clear
echo "╔══════════════════════════════════╗"
echo "║        YTMP3 Downloader          ║"
echo "║   YouTube → MP3/MP4 · Local      ║"
echo "╚══════════════════════════════════╝"
echo ""

CALE_CURENTA="$(cd "$(dirname "$0")" && pwd)"
EROARE=0

# ── 1. Python 3 ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[!] Python3 nu este instalat. Instalez..."
    sudo apt update -qq && sudo apt install -y python3 python3-pip
fi
PYTHON_VER=$(python3 -c "import sys; print(sys.version_info.major * 10 + sys.version_info.minor)")
if [ "$PYTHON_VER" -lt 38 ]; then
    echo "[EROARE] Python 3.8+ este necesar. Versiunea ta este prea veche."
    exit 1
fi
echo "[✓] Python3 OK"

# ── 2. pip ───────────────────────────────────────────────────
if ! command -v pip3 &>/dev/null; then
    echo "[!] Instalez pip..."
    sudo apt install -y python3-pip -qq
fi
echo "[✓] pip OK"

# ── 3. ffmpeg ────────────────────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo "[!] Instalez ffmpeg..."
    sudo apt update -qq && sudo apt install -y ffmpeg -qq
fi
echo "[✓] ffmpeg OK"

# ── 4. Pachete Python ─────────────────────────────────────────
instaleaza_python_pkg() {
    PKG=$1
    if ! python3 -c "import $PKG" &>/dev/null; then
        echo "[!] Instalez $PKG..."
        pip3 install "$PKG" --break-system-packages -q 2>/dev/null \
            || pip3 install "$PKG" --user -q
    fi
}

instaleaza_python_pkg "yt_dlp"
instaleaza_python_pkg "PySide6"
echo "[✓] Biblioteci Python OK"

# ── 5. Iconita ────────────────────────────────────────────────
if [ ! -f "$CALE_CURENTA/icon.svg" ]; then
    echo "[*] Generez iconita..."
    cat > "$CALE_CURENTA/icon.svg" << 'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="64" fill="#a81cff"/>
  <path d="M96 72 L196 128 L96 184 Z" fill="white"/>
</svg>
SVG
fi

# ── 6. Shortcut in meniu ──────────────────────────────────────
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR"
cat > "$APP_DIR/YTMP3.desktop" << DESKTOP
[Desktop Entry]
Version=1.0
Name=YTMP3 Downloader
Comment=Descarca muzica si video de pe YouTube
Exec=python3 "$CALE_CURENTA/app.py"
WorkingDirectory=$CALE_CURENTA
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Network;
Icon=$CALE_CURENTA/icon.svg
DESKTOP
chmod +x "$APP_DIR/YTMP3.desktop"
echo "[✓] Scurtatura adaugata in meniu (cauta 'YTMP3')"

echo ""
echo "╔══════════════════════════════════╗"
echo "║        Totul e pregatit!         ║"
echo "╚══════════════════════════════════╝"
echo ""
echo "Pornesc aplicatia..."
echo ""

python3 "$CALE_CURENTA/app.py"