import yt_dlp
import os

def download_mp3(link, destination_folder=None):
    """
    Descarcă o melodie de pe YouTube în format mp3.
    Dacă folder_destinatie nu este specificat, folosește folderul Downloads al sistemului.
    """

    #1. Stabilim unde salvam fisierul
    if not destination_folder:
        destination_folder = os.path.expanduser('~/Downloads')

    #2. Cream folderul daca nu exista
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 3. Setarile pentru yt-dlp
    optiuni = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # Calitate foarte bună
        }],
        # Setăm calea completă unde se va salva fișierul
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'), 
        'quiet': False, # Lăsăm pe False acum ca să vezi în terminal că se descarcă
        'no_warnings': True
    }

    #4. Descarcarea efectiva
    try:
        print(f"Pregătesc descărcarea în: {destination_folder}")
        with yt_dlp.YoutubeDL(optiuni) as ydl:
            ydl.download([link])
            
        return True, f"Succes! Melodia este în: {destination_folder}"

    except Exception as e:
        return False, f"Eroare: {str(e)}"
    

if __name__ == "__main__":
    print("=== TESTARE PROCESARE.PY ===")
    link_test = input("Dă paste la un link de YouTube aici: ")
    
    # Rulăm funcția fără să îi dăm un folder (ca să testăm dacă se duce în Downloads)
    succes, mesaj = download_mp3(link_test)
    
    print("\nRezultat:")
    print(mesaj)