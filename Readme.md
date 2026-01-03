🚀 TTD Waxsi INC. - Bot Kurulum Rehberi
Bu bot, TTD Waxsi INC. tarafından geliştirilmiş elite bir moderasyon ve sistem botudur. Kurulum için aşağıdaki adımları sırasıyla uygulayın:

1️⃣ Gereksinimlerin Kurulması
Bilgisayarınızda Python yüklü olmalıdır. Ardından terminali (CMD) açıp şu komutu yapıştırın:

Bash

pip install discord.py python-dotenv
2️⃣ Dosya Yapısı
Dosyaların şu düzende olduğundan emin olun:

main.py (Ana dosya)

cezalar.json (Veritabanı - boş bir {} içermeli)

📂 cogs/ (Klasör)

moderasyon.py

koruma.py

ticket.py

basvuru.py

duyuru.py

3️⃣ Bot Ayarları (ID Değişimi)
Botun çalışması için dosyalardaki ID'leri kendi sunucuna göre düzenlemelisin:

main.py: En alttaki TOKEN kısmına Discord Developer Portal'dan aldığın bot tokenini yaz.

cogs/moderasyon.py: * MUTE_ROL_ID: Sunucundaki "Muted" rolünün ID'si.

LOG_KANAL_ID: Ceza kayıtlarının gideceği kanal ID'si.

OTO_TEMIZLIK_KANAL_ID: 24 saatte bir temizlenecek kanalın ID'si.

cogs/koruma.py: MUTE_ROL_ID kısmını moderasyondakiyle aynı yap.

4️⃣ Discord Developer Portal Ayarları
Botun düzgün çalışması için Discord Developer Portal'da şunları yapın:

Botun sayfasına gidin.

"Privileged Gateway Intents" bölümüne gelin.

Presence Intent, Server Members Intent ve Message Content Intent seçeneklerinin hepsini AÇIK (ON) konuma getirin. (Yoksa bot kimseyi susturamaz ve mesajları okuyamaz).

5️⃣ Botu Başlatma
Her şey hazırsa main.py dosyasını çalıştırın. Terminalde şu yazıyı gördüğünüzde bot aktif demektir:

🚀 Development By TTD Waxsi INC. 🤍 TTD ODUL 🤍 TTD Waxsi INC.