import subprocess
import time
import requests
import os
import psutil
from datetime import datetime

# --- AYARLAR ---
BOT_DOSYASI = "main.py" 
WEBHOOK_URL = "BURAYA_WEBHOOK_GİR"

def eski_botlari_temizle():
    """Çakışma olmaması için arkada açık kalan diğer tüm botları kapatır."""
    current_pid = os.getpid()
    temizlendi_mi = False
    print("🧹 Eski süreçler kontrol ediliyor...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Python işlemini bul
            if "python" in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline') or []
                # Eğer süreç main.py'yi çalıştırıyorsa ve bu guardian değilse öldür
                if any(BOT_DOSYASI in s for s in cmdline) and proc.info['pid'] != current_pid:
                    proc.terminate()
                    print(f"✔️ Hayalet Bot Temizlendi: PID {proc.info['pid']}")
                    temizlendi_mi = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not temizlendi_mi:
        print("✅ Temizlenecek hayalet süreç bulunamadı.")

def discord_bildirim_gonder(baslik, mesaj, renk):
    payload = {
        "username": "TTD Guardian Pro",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/1063/1063376.png",
        "embeds": [{
            "title": baslik,
            "description": mesaj,
            "color": renk,
            "footer": {"text": "🛡️ TTD Waxsi INC. Tarafından Korunuyor"},
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Discord Hatası: {e}")

def baslat():
    # 1. Önce arkada kalanları süpür
    eski_botlari_temizle()
    
    print("\n" + "="*45)
    print(" 🛡️  GUARDIAN SİSTEMİ AKTİF (OTOMATİK RESET)")
    print(f" 🎯 Hedef Dosya: {BOT_DOSYASI}")
    print("="*45 + "\n")
    
    while True:
        simdi = datetime.now().strftime('%H:%M:%S')
        print(f"[{simdi}] 🚀 {BOT_DOSYASI} ayağa kaldırılıyor...")
        
        # Botu alt süreç olarak başlat
        # subprocess.PIPE kullanarak çakışmaları önleyelim
        process = subprocess.Popen(["python", BOT_DOSYASI])
        
        discord_bildirim_gonder(
            "🚀 Sistem Başlatıldı", 
            f"**{BOT_DOSYASI}** şu an aktif.\nHerhangi bir çökmede otomatik yeniden başlayacak.", 
            3066993 # Yeşil
        )

        # Bot kapanana kadar burada bekler
        process.wait()

        # Kod buraya geçtiyse bot çökmüş demektir
        hata_zamani = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{hata_zamani}] ⚠️ KRİTİK: {BOT_DOSYASI} kapandı!")
        
        discord_bildirim_gonder(
            "⚠️ Bot Kapandı!", 
            f"**{BOT_DOSYASI}** bir hata nedeniyle durdu.\n\n**Durum:** 5 saniye içinde tekrar açılacak.", 
            15158332 # Kırmızı
        )
        
        time.sleep(5)

if __name__ == "__main__":
    baslat()