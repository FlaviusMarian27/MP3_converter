# 🎵 YTMP3 Downloader

**YTMP3 Downloader** is a modern Linux application that allows you to quickly download audio (MP3) or video (MP4) content from YouTube directly to your computer.

Built with **PySide6** for the graphical interface and powered by **yt-dlp**, the application offers a fast, simple, and user-friendly experience.

---

## 🚀 Features

* Download YouTube videos as **MP3 audio files**
* Download YouTube videos as **MP4 video files**
* Clean and intuitive graphical interface
* Automatic dependency installation
* Desktop menu integration
* Automatic application icon setup
* No terminal usage required after installation

---

## 📥 How It Works

1. Copy the YouTube video URL.
2. Paste it into the application.
3. Select the desired format:

   * **MP3** – audio only
   * **MP4** – video
4. Click **Download**.
5. The file will be saved automatically to your selected folder.

---

## 🛠 Installation (Linux)

Open a terminal in the folder containing the application files.

### 1. Make the launcher executable

```bash
chmod +x pornire.sh
```

### 2. Run the installation script

```bash
./pornire.sh
```

---

## ⚙️ What the Installation Script Does

The installation script automatically:

* Verifies that Python is installed
* Checks and installs required dependencies
* Installs FFmpeg if missing
* Installs graphical libraries required by the application
* Creates a desktop launcher
* Integrates the application into your system menu
* Generates and applies the official YTMP3 icon

---

## 📱 Launching the Application

After the first installation, the terminal is no longer required.

Simply open your system menu and search for:

**YTMP3 Downloader**

You can also:

* Pin it to your favorites
* Add it to the dock
* Launch it like any other desktop application

---

## ✅ Requirements

### Operating System

* Ubuntu
* Linux Mint
* Debian
* Other Debian-based distributions

### Dependencies

* Internet connection
* Python 3
* FFmpeg

> Most dependencies are installed automatically by the installation script.

---

## 🔧 Technologies Used

* Python 3
* PySide6
* yt-dlp
* FFmpeg

---

## 📄 License

This project is distributed under the license specified in the repository.
