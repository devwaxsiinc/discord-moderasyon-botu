import discord
from discord.ext import commands, tasks
import json
import os

class SesSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.veritabani = "ses_sureleri.json"
        self.SAYAC_KANAL_ID = 1234567890 # Sayacın görüneceği Ses Kanalı ID
        
        # ROL VE SAAT AYARLARI (Saatleri dakikaya çevirerek kontrol edeceğiz)
        # ID'leri kendi sunucuna göre doldurmalısın.
        self.ROLLER = {
            500: 1439008055273717951, # @La familia es todo
            300: 1438232920304123986, # @BOTLOADER
            270: 1438232921965199380, # @GATEKAPPER
            250: 1438232924536180787, # @5 TILL I DİE
            210: 1438232925807054990, # @FUR DIE FAM
            180: 1438232931704504351, # @HIZLIYSAN YAKALA
            150: 1438232932669067506, # @C'EST LA VİA
            120: 1438232933612781579, # @İCQ
            100: 1438232934518624428  # @BİNANCE
        }
        
        if not os.path.exists(self.veritabani):
            with open(self.veritabani, "w") as f: json.dump({}, f)
            
        self.dakika_sayaci.start()
        self.sayac_guncelle.start()

    def veriyi_oku(self):
        with open(self.veritabani, "r") as f: return json.load(f)

    def veriyi_yaz(self, data):
        with open(self.veritabani, "w") as f: json.dump(data, f, indent=4)

    # 1. HER DAKİKA SESDEKİLERİ KONTROL ET VE PUAN VER
    @tasks.loop(minutes=1)
    async def dakika_sayaci(self):
        data = self.veriyi_oku()
        
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    if member.bot: continue # Botları sayma
                    
                    uid = str(member.id)
                    data[uid] = data.get(uid, 0) + 1 # 1 dakika ekle
                    
                    # Rol Kontrolü (Dakikayı Saate Çevir: dakika / 60)
                    toplam_saat = data[uid] / 60
                    
                    for saat, rol_id in self.ROLLER.items():
                        if toplam_saat >= saat:
                            rol = guild.get_role(rol_id)
                            if rol and rol not in member.roles:
                                try:
                                    await member.add_roles(rol)
                                    print(f"✅ {member.name} {saat} saat sınırına ulaştı, rol verildi.")
                                except:
                                    pass
        
        self.veriyi_yaz(data)

    # 2. ÜYE SAYACI (SES KANALI ADINI GÜNCELLEME)
    @tasks.loop(minutes=10) # API sınırı nedeniyle 10 dakikada bir idealdir
    async def sayac_guncelle(self):
        for guild in self.bot.guilds:
            kanal = guild.get_channel(self.SAYAC_KANAL_ID)
            if kanal:
                uye_sayisi = guild.member_count
                await kanal.edit(name=f"📊 Üye Sayısı: {uye_sayisi}")

    @dakika_sayaci.before_loop
    @sayac_guncelle.before_loop
    async def before_loops(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(SesSistemi(bot))