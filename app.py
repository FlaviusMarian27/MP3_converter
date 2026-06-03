"""
app.py — interfata grafica in stil YTMP3
Foloseste procesare.py pentru logica de descarcare.
"""

import tkinter as tk
from tkinter import filedialog
import threading
import os

from procesare import download_mp3, download_mp4, DEFAULT_FOLDER, is_valid_youtube_url

# ─── Culori ───────────────────────────────────────────────────────────────────
BG          = "#2b2b3b"
CARD        = "#3a3a4e"
TAB_ACTIVE  = "#4a4a60"
TAB_IDLE    = "#2e2e40"
INPUT_BG    = "#1e1e2e"
BTN_BLUE    = "#3b82f6"
BTN_HOVER   = "#2563eb"
BTN_DIS     = "#4b5563"
TEXT        = "#f1f1f1"
TEXT_DIM    = "#9090aa"
TEXT_PLACE  = "#555570"
SUCCESS     = "#22c55e"
ERROR       = "#ef4444"
BORDER      = "#55557a"

PLACEHOLDER = "youtube.com/watch?v=..."
FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_BODY   = ("Helvetica", 12)
FONT_SMALL  = ("Helvetica", 10)
FONT_BTN    = ("Helvetica", 13, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YTMP3")
        self.geometry("660x420")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.selected_fmt = tk.StringVar(value="mp3")
        self.folder = DEFAULT_FOLDER
        self.downloading = False

        self._build()

    # ── Constructie UI ────────────────────────────────────────────────────────

    def _build(self):
        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=40, pady=(30, 20))

        tk.Label(header, text="YTMP3", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")

        # ── Card principal ───────────────────────────────────────────────────
        card = tk.Frame(self, bg=CARD, bd=0)
        card.pack(fill="x", padx=40)

        # Tab-uri MP3 / MP4
        tab_row = tk.Frame(card, bg=CARD)
        tab_row.pack(fill="x")

        self.tab_mp3 = self._make_tab(tab_row, "MP3", "mp3")
        self.tab_mp4 = self._make_tab(tab_row, "MP4", "mp4")
        self._update_tabs()

        # Separator sub tab-uri
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x")

        # Label + input URL
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=24, pady=(18, 14))

        tk.Label(inner, text="Paste your YouTube link",
                 bg=CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w", pady=(0, 8))

        # Input URL
        entry_frame = tk.Frame(inner, bg=INPUT_BG,
                                highlightbackground=BORDER,
                                highlightthickness=1)
        entry_frame.pack(fill="x")

        self.url_entry = tk.Entry(
            entry_frame,
            bg=INPUT_BG, fg=TEXT_PLACE,
            insertbackground=TEXT,
            relief="flat", font=FONT_BODY,
            bd=0
        )
        self.url_entry.pack(fill="x", ipady=11, ipadx=14)
        self.url_entry.insert(0, PLACEHOLDER)
        self.url_entry.bind("<FocusIn>",  self._clear_placeholder)
        self.url_entry.bind("<FocusOut>", self._restore_placeholder)

        # Folder destinatie
        folder_row = tk.Frame(inner, bg=CARD)
        folder_row.pack(fill="x", pady=(10, 0))

        self.folder_label = tk.Label(
            folder_row,
            text=f"📁  {self.folder}",
            bg=CARD, fg=TEXT_DIM, font=FONT_SMALL,
            cursor="hand2"
        )
        self.folder_label.pack(side="left")
        self.folder_label.bind("<Button-1>", lambda e: self._choose_folder())

        tk.Label(folder_row, text="(click pentru a schimba)",
                 bg=CARD, fg=TEXT_PLACE, font=("Helvetica", 9)).pack(side="left", padx=6)

        # Buton Convert
        self.btn = tk.Button(
            inner,
            text="Convert",
            bg=BTN_BLUE, fg=TEXT,
            activebackground=BTN_HOVER, activeforeground=TEXT,
            relief="flat", font=FONT_BTN,
            cursor="hand2", bd=0,
            command=self._start
        )
        self.btn.pack(fill="x", ipady=12, pady=(14, 0))
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=BTN_HOVER) if not self.downloading else None)
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=BTN_BLUE)  if not self.downloading else None)

        # ── Status / progress ────────────────────────────────────────────────
        status_frame = tk.Frame(self, bg=BG)
        status_frame.pack(fill="x", padx=40, pady=(16, 0))

        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=BG, fg=TEXT_DIM, font=FONT_SMALL,
            wraplength=580, justify="left"
        )
        self.status_lbl.pack(anchor="w")

        # Progress bar custom (canvas)
        self.progress_canvas = tk.Canvas(
            self, bg=BG, height=4,
            highlightthickness=0
        )
        self.progress_canvas.pack(fill="x", padx=40, pady=(6, 0))
        self._progress_anim_id = None
        self._progress_x = 0

    # ── Tab-uri ───────────────────────────────────────────────────────────────

    def _make_tab(self, parent, label, fmt):
        btn = tk.Label(
            parent,
            text=label,
            bg=TAB_IDLE, fg=TEXT_DIM,
            font=FONT_BODY,
            padx=30, pady=12,
            cursor="hand2"
        )
        btn.pack(side="left")
        btn.bind("<Button-1>", lambda e, f=fmt: self._switch_tab(f))
        return btn

    def _switch_tab(self, fmt):
        if self.downloading:
            return
        self.selected_fmt.set(fmt)
        self._update_tabs()

    def _update_tabs(self):
        fmt = self.selected_fmt.get()
        if fmt == "mp3":
            self.tab_mp3.config(bg=TAB_ACTIVE, fg=TEXT)
            self.tab_mp4.config(bg=TAB_IDLE,   fg=TEXT_DIM)
        else:
            self.tab_mp4.config(bg=TAB_ACTIVE, fg=TEXT)
            self.tab_mp3.config(bg=TAB_IDLE,   fg=TEXT_DIM)

    # ── Placeholder ───────────────────────────────────────────────────────────

    def _clear_placeholder(self, _):
        if self.url_entry.get() == PLACEHOLDER:
            self.url_entry.delete(0, "end")
            self.url_entry.config(fg=TEXT)

    def _restore_placeholder(self, _):
        if not self.url_entry.get().strip():
            self.url_entry.insert(0, PLACEHOLDER)
            self.url_entry.config(fg=TEXT_PLACE)

    # ── Folder ────────────────────────────────────────────────────────────────

    def _choose_folder(self):
        if self.downloading:
            return
        folder = filedialog.askdirectory(
            initialdir=self.folder,
            title="Alege folderul de descarcare"
        )
        if folder:
            self.folder = folder
            short = folder if len(folder) < 50 else "..." + folder[-47:]
            self.folder_label.config(text=f"📁  {short}")

    # ── Progress bar animat ───────────────────────────────────────────────────

    def _start_progress(self):
        self._progress_x = 0
        self._animate_progress()

    def _animate_progress(self):
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width() or 580
        bar_w = 120
        x = self._progress_x % (w + bar_w) - bar_w
        self.progress_canvas.create_rectangle(
            x, 0, x + bar_w, 4,
            fill=BTN_BLUE, outline=""
        )
        self._progress_x += 8
        self._progress_anim_id = self.after(16, self._animate_progress)

    def _stop_progress(self):
        if self._progress_anim_id:
            self.after_cancel(self._progress_anim_id)
            self._progress_anim_id = None
        self.progress_canvas.delete("all")

    # ── Download ──────────────────────────────────────────────────────────────

    def _start(self):
        url = self.url_entry.get().strip()

        if not url or url == PLACEHOLDER:
            self._set_status("⚠  Lipsa link. Da paste la un link YouTube.", ERROR)
            return

        if not is_valid_youtube_url(url):
            self._set_status("⚠  Link invalid. Exemplu: https://www.youtube.com/watch?v=...", ERROR)
            return

        self.downloading = True
        self.btn.config(text="Se descarca...", bg=BTN_DIS, state="disabled")
        self._set_status("Se prelucreaza...", TEXT_DIM)
        self._start_progress()

        fmt = self.selected_fmt.get()
        thread = threading.Thread(
            target=self._worker,
            args=(url, fmt),
            daemon=True
        )
        thread.start()

    def _worker(self, url, fmt):
        def hook(d):
            if d.get("status") == "downloading":
                pct = d.get("_percent_str", "").strip()
                spd = d.get("_speed_str", "").strip()
                if pct:
                    self.after(0, self._set_status,
                               f"Se descarca...  {pct}  {spd}", TEXT_DIM)
            elif d.get("status") == "finished":
                self.after(0, self._set_status, "Se converteste in MP3...", TEXT_DIM)

        if fmt == "mp4":
            succes, mesaj = download_mp4(url, self.folder, progress_hook=hook)
        else:
            succes, mesaj = download_mp3(url, self.folder, progress_hook=hook)

        self.after(0, self._done, succes, mesaj)

    def _done(self, succes, mesaj):
        self._stop_progress()
        self.downloading = False
        self.btn.config(text="Convert", bg=BTN_BLUE, state="normal")

        if succes:
            self._set_status(f"✅  {mesaj}", SUCCESS)
        else:
            self._set_status(f"❌  {mesaj}", ERROR)

    def _set_status(self, msg, color=TEXT_DIM):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()