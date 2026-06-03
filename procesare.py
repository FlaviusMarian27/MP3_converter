"""
procesare.py — logica de descarcare, fara GUI
Importat de interfata (app.py), dar poate fi rulat si singur din terminal.
"""

import yt_dlp
import os
import re

# Folder implicit = ~/Downloads
DEFAULT_FOLDER = os.path.expanduser("~/Downloads")


def is_valid_youtube_url(link: str) -> bool:
    """Returneaza True daca link-ul pare un URL YouTube valid."""
    pattern = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+"
    return bool(re.match(pattern, link.strip()))


def download_mp3(link: str, destination_folder: str = None, progress_hook=None):
    """
    Descarca o melodie de pe YouTube in format MP3.

    Parametri:
        link               — URL YouTube
        destination_folder — unde se salveaza (default: ~/Downloads)
        progress_hook      — functie optionala apelata de yt-dlp cu progresul
                             (folosita de interfata grafica pentru progress bar)

    Returneaza:
        (True,  "mesaj succes")
        (False, "mesaj eroare")
    """
    # Validari
    if not link or not link.strip():
        return False, "Link-ul este gol."

    if not is_valid_youtube_url(link):
        return False, "Link invalid. Exemplu: https://www.youtube.com/watch?v=..."

    # Folder destinatie
    if not destination_folder:
        destination_folder = DEFAULT_FOLDER

    os.makedirs(destination_folder, exist_ok=True)

    # Optiuni yt-dlp
    optiuni = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": os.path.join(destination_folder, "%(title)s.%(ext)s"),
        "quiet": False,
        "no_warnings": True,
    }

    if progress_hook:
        optiuni["progress_hooks"] = [progress_hook]

    # Descarcare
    try:
        print(f"Descarcare in: {destination_folder}")
        with yt_dlp.YoutubeDL(optiuni) as ydl:
            ydl.download([link.strip()])
        return True, f"Succes! Melodia este in: {destination_folder}"

    except Exception as e:
        return False, f"Eroare: {str(e)}"


def download_mp4(link: str, destination_folder: str = None, progress_hook=None):
    """
    Descarca un video de pe YouTube in format MP4.
    Aceeasi semnatura ca download_mp3.
    """
    if not link or not link.strip():
        return False, "Link-ul este gol."

    if not is_valid_youtube_url(link):
        return False, "Link invalid. Exemplu: https://www.youtube.com/watch?v=..."

    if not destination_folder:
        destination_folder = DEFAULT_FOLDER

    os.makedirs(destination_folder, exist_ok=True)

    optiuni = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(destination_folder, "%(title)s.%(ext)s"),
        "quiet": False,
        "no_warnings": True,
    }

    if progress_hook:
        optiuni["progress_hooks"] = [progress_hook]

    try:
        print(f"Descarcare in: {destination_folder}")
        with yt_dlp.YoutubeDL(optiuni) as ydl:
            ydl.download([link.strip()])
        return True, f"Succes! Video-ul este in: {destination_folder}"

    except Exception as e:
        return False, f"Eroare: {str(e)}"


# ─── Rulare directa din terminal ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== TESTARE PROCESARE.PY ===\n")

    link_test = input("Da paste la un link YouTube: ").strip()

    fmt = input("Format (mp3/mp4) [default: mp3]: ").strip().lower() or "mp3"

    folder = input(f"Folder destinatie [default: {DEFAULT_FOLDER}]: ").strip() or None

    if fmt == "mp4":
        succes, mesaj = download_mp4(link_test, folder)
    else:
        succes, mesaj = download_mp3(link_test, folder)

    print(f"\nRezultat: {mesaj}")