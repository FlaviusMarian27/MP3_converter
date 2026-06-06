"""
app.py — YTMP3 Downloader
Interfata grafica cross-platform (Linux + Windows)
Foloseste procesare.py pentru logica de descarcare.
"""

import sys
import os
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QFrame,
    QButtonGroup, QScrollArea, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QIcon, QFont, QClipboard, QCursor

from procesare import download_mp3, download_mp4, DEFAULT_FOLDER, is_valid_youtube_url

# ─── Constante ────────────────────────────────────────────────────────────────

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".history.json")
MAX_HISTORY  = 10

# ─── Stil QSS ─────────────────────────────────────────────────────────────────

QSS = """
QMainWindow, QWidget#root {
    background-color: #0f0f15;
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    background: #1a1a24;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #3a3a55;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Label generic ── */
QLabel {
    color: #f0f0ff;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: transparent;
}

/* ── Header ── */
QLabel#logo_box {
    background-color: #a81cff;
    border-radius: 18px;
    font-size: 32px;
    font-weight: bold;
    color: white;
}
QLabel#lbl_title {
    font-size: 38px;
    font-weight: 900;
    letter-spacing: 2px;
    color: #f0f0ff;
}
QLabel#lbl_subtitle {
    font-size: 15px;
    color: #6b6b80;
}

/* ── Card ── */
QFrame#card {
    background-color: #1a1a24;
    border-radius: 20px;
    border: 1px solid #2a2a38;
}

/* ── Tab-uri ── */
QPushButton#tab_mp3, QPushButton#tab_mp4 {
    background-color: transparent;
    color: #555570;
    border: none;
    font-size: 18px;
    font-weight: bold;
    padding: 18px 30px;
    border-radius: 14px;
}
QPushButton#tab_mp3:checked, QPushButton#tab_mp4:checked {
    background-color: #a81cff;
    color: white;
}
QPushButton#tab_mp3:hover:!checked, QPushButton#tab_mp4:hover:!checked {
    background-color: #2a2a38;
    color: #9090bb;
}

/* ── Label mic ── */
QLabel#lbl_small {
    color: #555570;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
}

/* ── Input URL ── */
QLineEdit#url_input {
    background-color: #111118;
    border: 2px solid #222230;
    border-radius: 14px;
    color: #f0f0ff;
    padding: 16px 18px;
    font-size: 16px;
    selection-background-color: #a81cff;
}
QLineEdit#url_input:focus {
    border: 2px solid #a81cff;
}

/* ── Buton paste ── */
QPushButton#btn_paste {
    background-color: #222230;
    color: #9090bb;
    border: none;
    border-radius: 10px;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 18px;
}
QPushButton#btn_paste:hover {
    background-color: #a81cff;
    color: white;
}

/* ── Folder ── */
QLabel#lbl_folder {
    color: #6b6b80;
    font-size: 14px;
}
QPushButton#btn_folder {
    background-color: #111118;
    color: #888899;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#btn_folder:hover {
    background-color: #2a2a38;
    color: white;
    border-color: #a81cff;
}

/* ── Progress bar ── */
QProgressBar#progress {
    background-color: #111118;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar#progress::chunk {
    background-color: #a81cff;
    border-radius: 4px;
}

/* ── Buton download ── */
QPushButton#btn_dl {
    background-color: #a81cff;
    color: white;
    border: none;
    border-radius: 16px;
    font-size: 20px;
    font-weight: bold;
    padding: 22px;
    letter-spacing: 1px;
}
QPushButton#btn_dl:hover {
    background-color: #8f11e0;
}
QPushButton#btn_dl:disabled {
    background-color: #2e2e3e;
    color: #555570;
}

/* ── Status ── */
QLabel#lbl_status {
    font-size: 14px;
    color: #6b6b80;
}

/* ── Zona Recente ── */
QFrame#recent_box {
    background-color: #111118;
    border-radius: 16px;
    border: 1px solid #1e1e2e;
}
QLabel#lbl_recent_title {
    color: #555570;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
}
QPushButton#btn_clear {
    background: transparent;
    color: #444460;
    border: none;
    font-size: 12px;
}
QPushButton#btn_clear:hover {
    color: #f87171;
}
QLabel#recent_empty {
    color: #444460;
    font-size: 14px;
}
QLabel#recent_item_title {
    color: #9090aa;
    font-size: 13px;
}
QLabel#recent_item_badge {
    color: #a81cff;
    background-color: #1e0e30;
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    padding: 2px 8px;
}
QFrame#recent_sep {
    background-color: #1e1e2e;
}
"""

# ─── Helper: history ──────────────────────────────────────────────────────────

def load_history():
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(items):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(items[:MAX_HISTORY], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ─── Worker thread ────────────────────────────────────────────────────────────

class DownloadWorker(QThread):
    progress  = Signal(str, int)   # mesaj, procent (0-100, -1 = indeterminate)
    finished  = Signal(bool, str, str)  # ok, mesaj, titlu

    def __init__(self, url, fmt, folder):
        super().__init__()
        self.url    = url
        self.fmt    = fmt
        self.folder = folder
        self._title = url

    def run(self):
        def hook(d):
            info = d.get("info_dict", {})
            if info.get("title"):
                self._title = info["title"]

            if d["status"] == "downloading":
                pct_str = d.get("_percent_str", "").strip().replace("%", "")
                spd     = d.get("_speed_str", "").strip()
                try:
                    pct = int(float(pct_str))
                except (ValueError, TypeError):
                    pct = -1
                self.progress.emit(f"Se descarcă...  {d.get('_percent_str','').strip()}  {spd}", pct)

            elif d["status"] == "finished":
                lbl = "MP3" if self.fmt == "mp3" else "MP4"
                self.progress.emit(f"Se convertește în {lbl}...", 99)

        if self.fmt == "mp4":
            ok, msg = download_mp4(self.url, self.folder, progress_hook=hook)
        else:
            ok, msg = download_mp3(self.url, self.folder, progress_hook=hook)

        title = self._title
        if len(title) > 60:
            title = title[:57] + "..."
        self.finished.emit(ok, msg, title)

# ─── Fereastra principala ─────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YTMP3 Downloader")
        self.setMinimumSize(720, 820)
        self.resize(820, 860)

        self.folder  = DEFAULT_FOLDER
        self.history = load_history()
        self.worker  = None

        # Iconita
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        # Scroll area pentru ecrane mici
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: #0f0f15; border: none; }")

        inner = QWidget()
        inner.setObjectName("root")
        scroll.setWidget(inner)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(28)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(18)

        logo = QLabel("▶")
        logo.setObjectName("logo_box")
        logo.setFixedSize(68, 68)
        logo.setAlignment(Qt.AlignCenter)
        header.addWidget(logo)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        lbl_title = QLabel("YTMP3")
        lbl_title.setObjectName("lbl_title")
        lbl_sub = QLabel("YouTube → MP3 · Rapid · Local")
        lbl_sub.setObjectName("lbl_subtitle")
        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_sub)
        header.addLayout(title_col)
        header.addStretch()
        layout.addLayout(header)

        # ── Card ──────────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 32)
        card_layout.setSpacing(22)

        # Tab-uri
        tabs = QHBoxLayout()
        tabs.setSpacing(8)
        self.btn_mp3 = QPushButton("♪  MP3")
        self.btn_mp3.setObjectName("tab_mp3")
        self.btn_mp3.setCheckable(True)
        self.btn_mp3.setChecked(True)
        self.btn_mp3.setCursor(Qt.PointingHandCursor)

        self.btn_mp4 = QPushButton("▶  MP4")
        self.btn_mp4.setObjectName("tab_mp4")
        self.btn_mp4.setCheckable(True)
        self.btn_mp4.setCursor(Qt.PointingHandCursor)

        grp = QButtonGroup(self)
        grp.addButton(self.btn_mp3)
        grp.addButton(self.btn_mp4)

        tabs.addWidget(self.btn_mp3)
        tabs.addWidget(self.btn_mp4)
        tabs.addStretch()
        card_layout.addLayout(tabs)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #2a2a38;")
        card_layout.addWidget(sep)

        # Label + URL row
        lbl_link = QLabel("LINK YOUTUBE")
        lbl_link.setObjectName("lbl_small")
        card_layout.addWidget(lbl_link)

        url_row = QHBoxLayout()
        url_row.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setObjectName("url_input")
        self.url_input.setPlaceholderText("https://youtube.com/watch?v=...")
        self.url_input.returnPressed.connect(self._start_download)
        url_row.addWidget(self.url_input)

        btn_paste = QPushButton("📋 Paste")
        btn_paste.setObjectName("btn_paste")
        btn_paste.setCursor(Qt.PointingHandCursor)
        btn_paste.clicked.connect(self._paste_url)
        url_row.addWidget(btn_paste)
        card_layout.addLayout(url_row)

        # Folder row
        folder_row = QHBoxLayout()
        self.lbl_folder = QLabel(f"📁  {self._short(self.folder)}")
        self.lbl_folder.setObjectName("lbl_folder")
        folder_row.addWidget(self.lbl_folder)
        folder_row.addStretch()

        btn_folder = QPushButton("Schimbă")
        btn_folder.setObjectName("btn_folder")
        btn_folder.setCursor(Qt.PointingHandCursor)
        btn_folder.clicked.connect(self._choose_folder)
        folder_row.addWidget(btn_folder)
        card_layout.addLayout(folder_row)

        # Progress bar (ascuns initial)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress")
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        card_layout.addWidget(self.progress_bar)

        # Buton download
        self.btn_dl = QPushButton("Descarcă  ➔")
        self.btn_dl.setObjectName("btn_dl")
        self.btn_dl.setCursor(Qt.PointingHandCursor)
        self.btn_dl.clicked.connect(self._start_download)
        card_layout.addWidget(self.btn_dl)

        # Status
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("lbl_status")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_status)

        layout.addWidget(card)

        # ── Recente ───────────────────────────────────────────────────────────
        rec_header = QHBoxLayout()
        lbl_rec = QLabel("RECENTE")
        lbl_rec.setObjectName("lbl_recent_title")
        rec_header.addWidget(lbl_rec)
        rec_header.addStretch()

        self.btn_clear = QPushButton("Șterge tot")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_history)
        rec_header.addWidget(self.btn_clear)
        layout.addLayout(rec_header)

        self.recent_box = QFrame()
        self.recent_box.setObjectName("recent_box")
        self.recent_layout = QVBoxLayout(self.recent_box)
        self.recent_layout.setContentsMargins(20, 16, 20, 16)
        self.recent_layout.setSpacing(6)
        layout.addWidget(self.recent_box)

        layout.addStretch()

        self._render_history()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _short(self, path):
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
        return path if len(path) < 50 else "..." + path[-47:]

    def _paste_url(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self.url_input.setFocus()

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Alege folderul de descărcare", self.folder)
        if folder:
            self.folder = folder
            self.lbl_folder.setText(f"📁  {self._short(folder)}")

    def _set_status(self, msg, color="#6b6b80"):
        self.lbl_status.setText(msg)
        self.lbl_status.setStyleSheet(f"color: {color}; font-size: 14px;")

    # ── History ───────────────────────────────────────────────────────────────

    def _render_history(self):
        # Sterge widgeturile existente
        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.history:
            empty = QLabel("Nicio conversie încă.")
            empty.setObjectName("recent_empty")
            empty.setAlignment(Qt.AlignCenter)
            self.recent_layout.addWidget(empty)
            self.btn_clear.hide()
            return

        self.btn_clear.show()
        for i, item in enumerate(self.history[:8]):
            row = QHBoxLayout()
            row.setSpacing(10)

            icon = QLabel("🎵")
            icon.setFixedWidth(22)
            row.addWidget(icon)

            title = item.get("title", "Necunoscut")
            if len(title) > 54:
                title = title[:51] + "..."
            lbl = QLabel(title)
            lbl.setObjectName("recent_item_title")
            row.addWidget(lbl)
            row.addStretch()

            badge = QLabel(f"  {item['fmt'].upper()}  ")
            badge.setObjectName("recent_item_badge")
            row.addWidget(badge)

            row_widget = QWidget()
            row_widget.setObjectName("root")
            row_widget.setLayout(row)
            self.recent_layout.addWidget(row_widget)

            if i < len(self.history) - 1 and i < 7:
                sep = QFrame()
                sep.setObjectName("recent_sep")
                sep.setFrameShape(QFrame.HLine)
                sep.setFixedHeight(1)
                self.recent_layout.addWidget(sep)

    def _add_history(self, title, fmt):
        self.history = [h for h in self.history if h.get("title") != title]
        self.history.insert(0, {"title": title, "fmt": fmt})
        save_history(self.history)
        self._render_history()

    def _clear_history(self):
        self.history = []
        save_history([])
        self._render_history()

    # ── Download ──────────────────────────────────────────────────────────────

    def _start_download(self):
        url = self.url_input.text().strip()

        if not url:
            self._set_status("⚠  Lipsește linkul.", "#f87171")
            return
        if not is_valid_youtube_url(url):
            self._set_status("⚠  Link invalid. Exemplu: https://www.youtube.com/watch?v=...", "#f87171")
            return

        fmt = "mp3" if self.btn_mp3.isChecked() else "mp4"

        self.btn_dl.setEnabled(False)
        self.btn_dl.setText("Se pregătește...")
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)   # indeterminate
        self._set_status("Se inițializează descărcarea...")

        self.worker = DownloadWorker(url, fmt, self.folder)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, msg, pct):
        self.btn_dl.setText(msg)
        if pct >= 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(pct)
        else:
            self.progress_bar.setRange(0, 0)
        self._set_status(msg)

    def _on_finished(self, ok, msg, title):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if ok else 0)

        self.btn_dl.setEnabled(True)
        self.btn_dl.setText("Descarcă  ➔")

        if ok:
            self.progress_bar.setValue(100)
            self._set_status(f"✅  {msg}", "#22c55e")
            self.url_input.clear()
            fmt = "mp3" if self.btn_mp3.isChecked() else "mp4"
            self._add_history(title, fmt)
            # Resetam progress dupa 2 secunde
            QTimer.singleShot(2000, lambda: (
                self.progress_bar.setValue(0),
                self.progress_bar.hide()
            ))
        else:
            self._set_status(f"❌  {msg}", "#f87171")
            self.progress_bar.hide()


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 11)
    app.setFont(font)
    app.setStyleSheet(QSS)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())