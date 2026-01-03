import discord
import asyncio

# BURAYA BOTUNUN TOKENİNİ YAZ
TOKEN = "BURAYA_BOT_TOKENINI_YAZ"

class StatusBot(discord.Client):
    def __init__(self):
        # Durum değiştirmek için gerekli izinleri tanımlıyoruz
        intents = discord.Intents.default()
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'{self.user} olarak giriş yapıldı!')
        
        # GÖRSELDEKİ DURUMU AYARLAYAN KISIM
        # status: Rahatsız Etmeyin (dnd)
        # name: Yazacak olan metin
        activity = discord.CustomActivity(name="TTD ODUL🤍TTD Waxsi INC.")
        
        await self.change_presence(status=discord.Status.dnd, activity=activity)
        
        print("✅ Durum başarıyla güncellendi!")
        print("Bu pencereyi kapatabilirsin, botun durumu Discord sunucularında güncel kalacaktır.")
        # Durumu güncelledikten sonra botu kapatmak istersen bu satırı bırakabilirsin.
        # await self.close() 

client = StatusBot()
client.run(TOKEN)