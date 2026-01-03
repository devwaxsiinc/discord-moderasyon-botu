import discord
from discord.ext import commands
import os
import asyncio

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/", 
            intents=discord.Intents.all(), 
            help_command=None
        )

    async def setup_hook(self):
        print("-" * 40)
        print("🛠️  SİSTEMLER YÜKLENİYOR...")
        
        # Cogs klasörünün varlığını kontrol et
        if not os.path.exists('./cogs'):
            print("❌ HATA: 'cogs' klasörü bulunamadı!")
        else:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"✔️  Modül Yüklendi: {filename}")
                    except Exception as e:
                        print(f"❌ Modül Hatası {filename}: {e}")

    async def on_ready(self):
        print("\n" + "=" * 40)
        print(f'✅ Bot Başlatıldı: {self.user.name}')
        print("=" * 40)
        print("💎 Dm Duyuru Aktif")
        print("⚖️ Ceza Sistemi Aktif")
        print("🕒 Yetkili Mesai Sistemi Aktif")
        print("🎫 Ticket Sistemi Aktif")
        print("🛡️ Yetkili Başvuru Aktif")
        print("🧹 Otomatik Temizlik Aktif")
        print("-" * 40)
        print("🚀 Development By TTD Waxsi INC.")
        print("=" * 40)

        try:
            await self.tree.sync()
            print("🚀 Slash Komutları Senkronize Edildi.")
        except Exception as e:
            print(f"❌ Senkronizasyon Hatası: {e}")

        await self.change_presence(activity=discord.Game(name="TTD Waxsi INC. Farkıyla"))

# Botu oluştur
bot = MyBot()

# --- TOKEN AYARI (Burayı Değiştirme!) ---
# Koyeb panelindeki "Environment Variables" kısmına eklediğin TOKEN'ı okur.
TOKEN = os.getenv("TOKEN")

if __name__ == "__main__":
    if TOKEN:
        # Botu başlat
        bot.run(TOKEN, log_handler=None)
    else:
        print("❌ HATA: TOKEN bulunamadı!")
        print("LÜTFEN ŞUNU YAPIN: Koyeb panelinde 'Environment Variables' kısmına gidin.")
        print("Key (İsim) kısmına: TOKEN")
        print("Value (Değer) kısmına: Discord'dan aldığınız tokenı yapıştırın.")