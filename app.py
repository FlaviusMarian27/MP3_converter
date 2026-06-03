import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QFrame, QButtonGroup, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal
from procesare import download_mp3, download_mp4, DEFAULT_FOLDER, is_valid_youtube_url

# --- Stilizarea Interfeței (ZOOM MAXIM) ---
STIL_QSS = """
QMainWindow {
    background-color: #0f0f15;
}
QLabel {
    color: white;
    font-family: 'Segoe UI', Helvetica, sans-serif;
}

/* Header / Logo */
QLabel#logo {
    background-color: #a81cff;
    border-radius: 20px;
    font-size: 36px;
    font-weight: bold;
}
QLabel#title {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 2px;
}
QLabel#subtitle {
    color: #6b6b80;
    font-size: 18px;
}

/* Cardul Principal */
QFrame#card {
    background-color: #1a1a24;
    border-radius: 20px;
}

/* Tab-urile MP3 / MP4 */
QPushButton#tab_mp3, QPushButton#tab_mp4 {
    background-color: transparent;
    color: #6b6b80;
    border: none;
    font-size: 20px;
    font-weight: bold;
    padding: 20px;
}
QPushButton#tab_mp3:checked, QPushButton#tab_mp4:checked {
    background-color: #a81cff;
    color: white;
    border-radius: 14px;
}

/* Texte mici */
QLabel#small_label {
    color: #6b6b80;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 1px;
}

/* Input URL */
QLineEdit {
    background-color: #111118;
    border: 2px solid #111118;
    border-radius: 14px;
    color: white;
    padding: 20px;
    font-size: 18px;
}
QLineEdit:focus {
    border: 2px solid #a81cff;
}

/* Butoane */
QPushButton#btn_folder {
    background-color: #111118;
    color: #888899;
    border-radius: 10px;
    padding: 14px 24px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton#btn_folder:hover {
    background-color: #2a2a35;
    color: white;
}

QPushButton#btn_dl {
    background-color: #a81cff;
    color: white;
    border-radius: 16px;
    font-size: 24px;
    font-weight: bold;
    padding: 24px;
}
QPushButton#btn_dl:hover {
    background-color: #8f11e0;
}
QPushButton#btn_dl:disabled {
    background-color: #3a3a45;
    color: #888888;
}

/* Zona Recente */
QFrame#recent_box {
    background-color: #111118;
    border-radius: 16px;
}
QLabel#recent_text {
    color: #6b6b80;
    font-size: 18px;
}
"""

# --- Motorul de descărcare ---
class DownloadWorker(QThread):
    progress_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, url, fmt, folder):
        super().__init__()
        self.url = url
        self.fmt = fmt
        self.folder = folder

    def run(self):
        def hook(d):
            if d.get("status") == "downloading":
                pct = d.get("_percent_str", "").strip()
                spd = d.get("_speed_str", "").strip()
                self.progress_signal.emit(f"Se descarcă... {pct}  {spd}")
            elif d.get("status") == "finished":
                lbl = "MP3" if self.fmt == "mp3" else "MP4"
                self.progress_signal.emit(f"Se convertește în {lbl}...")

        if self.fmt == "mp4":
            ok, msg = download_mp4(self.url, self.folder, progress_hook=hook)
        else:
            ok, msg = download_mp3(self.url, self.folder, progress_hook=hook)

        self.finished_signal.emit(ok, msg)


# --- Fereastra Principală ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YTMP3 - Descarcă Muzică")
        
        # Dimensiuni mult mai mari de start
        self.setMinimumSize(800, 900)
        self.resize(1100, 950) 
        
        self.current_folder = DEFAULT_FOLDER
        self.worker = None

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 50, 40, 50)
        main_layout.setSpacing(30)

        # Lărgim containerul central pentru a ocupa mult mai mult din ecran
        content_container = QWidget()
        content_container.setMaximumWidth(1200) 
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(30)

        # --- 1. HEADER (Logo + Titlu) ---
        header_layout = QHBoxLayout()
        
        logo = QLabel("▶")
        logo.setObjectName("logo")
        logo.setFixedSize(80, 80) # Logo masiv
        logo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel("YTMP3")
        title_label.setObjectName("title")
        subtitle_label = QLabel("YouTube → MP3 • Rapid • Local")
        subtitle_label.setObjectName("subtitle")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setAlignment(Qt.AlignVCenter)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        # --- 2. CARDUL PRINCIPAL ---
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 40)
        card_layout.setSpacing(25)

        # Tab-uri MP3 / MP4
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(15)
        
        self.btn_tab_mp3 = QPushButton("♪ MP3")
        self.btn_tab_mp3.setObjectName("tab_mp3")
        self.btn_tab_mp3.setCheckable(True)
        self.btn_tab_mp3.setChecked(True)
        self.btn_tab_mp3.setCursor(Qt.PointingHandCursor)
        
        self.btn_tab_mp4 = QPushButton("▶ MP4")
        self.btn_tab_mp4.setObjectName("tab_mp4")
        self.btn_tab_mp4.setCheckable(True)
        self.btn_tab_mp4.setCursor(Qt.PointingHandCursor)

        self.tab_group = QButtonGroup(self)
        self.tab_group.addButton(self.btn_tab_mp3)
        self.tab_group.addButton(self.btn_tab_mp4)

        tabs_layout.addWidget(self.btn_tab_mp3)
        tabs_layout.addWidget(self.btn_tab_mp4)
        card_layout.addLayout(tabs_layout)

        # Input URL
        input_layout = QVBoxLayout()
        input_layout.setSpacing(12)
        
        lbl_link = QLabel("LINK YOUTUBE")
        lbl_link.setObjectName("small_label")
        input_layout.addWidget(lbl_link)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("🔗 https://youtube.com/watch?v=...")
        input_layout.addWidget(self.url_input)
        card_layout.addLayout(input_layout)

        # Selectare Folder
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel(f"📁 {self.shorten_path(self.current_folder)}")
        self.folder_label.setStyleSheet("color: #6b6b80; font-size: 16px;")
        
        self.btn_folder = QPushButton("Schimbă")
        self.btn_folder.setObjectName("btn_folder")
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.clicked.connect(self.choose_folder)
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addStretch() 
        folder_layout.addWidget(self.btn_folder)
        card_layout.addLayout(folder_layout)

        # Buton Descărcare
        self.btn_download = QPushButton("Descarcă ➔")
        self.btn_download.setObjectName("btn_dl")
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.clicked.connect(self.start_download)
        card_layout.addWidget(self.btn_download)

        content_layout.addWidget(card)

        # --- 3. ZONA RECENTE ---
        content_layout.addSpacing(20)
        
        lbl_recent_title = QLabel("RECENTE")
        lbl_recent_title.setObjectName("small_label")
        content_layout.addWidget(lbl_recent_title)

        self.recent_box = QFrame()
        self.recent_box.setObjectName("recent_box")
        self.recent_box.setFixedHeight(100) # Căsuță foarte generoasă
        recent_layout = QVBoxLayout(self.recent_box)
        
        self.recent_label = QLabel("Nicio conversie încă.")
        self.recent_label.setObjectName("recent_text")
        self.recent_label.setAlignment(Qt.AlignCenter)
        recent_layout.addWidget(self.recent_label)
        
        content_layout.addWidget(self.recent_box)
        
        # Centram containerul în interiorul ferestrei
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(content_container)
        center_layout.addStretch()

        main_layout.addLayout(center_layout)
        main_layout.addStretch()

    def shorten_path(self, path):
        return path if len(path) < 50 else "..." + path[-47:]

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Alege folderul de descărcare", self.current_folder)
        if folder:
            self.current_folder = folder
            self.folder_label.setText(f"📁 {self.shorten_path(folder)}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.btn_download.setText("⚠ Introdu un link valid!")
            return
        if not is_valid_youtube_url(url):
            self.btn_download.setText("⚠ Link invalid!")
            return

        fmt = "mp3" if self.btn_tab_mp3.isChecked() else "mp4"

        self.btn_download.setEnabled(False)
        self.btn_download.setText("Inițializare...")
        
        self.worker = DownloadWorker(url, fmt, self.current_folder)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.download_finished)
        self.worker.start()

    def update_progress(self, msg):
        self.btn_download.setText(msg)

    def download_finished(self, ok, msg):
        self.btn_download.setEnabled(True)
        
        if ok:
            self.btn_download.setText("Descarcă ➔")
            self.url_input.clear()
            tip = "MP3" if self.btn_tab_mp3.isChecked() else "MP4"
            self.recent_label.setText(f"✅ Descărcare {tip} salvată cu succes!")
            self.recent_label.setStyleSheet("color: #22c55e;")
        else:
            self.btn_download.setText("❌ Eroare. Încearcă din nou")
            self.recent_label.setText("Eroare la ultima descărcare.")
            self.recent_label.setStyleSheet("color: #ff4c4c;")

if __name__ == "__main__":
    import os
    from PySide6.QtGui import QIcon

    app = QApplication(sys.argv)
    
    # Font de bază mărit puternic la nivelul întregii aplicații
    font = app.font()
    font.setPointSize(14)
    app.setFont(font)
    
    app.setStyleSheet(STIL_QSS)
    
    # Legăm noua iconiță mov personalizată (SVG)
    icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())