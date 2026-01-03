import discord
from discord.ext import commands
import datetime
import json
import os

class Koruma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anti_spam = {}
        self.ihlal_sayaci = {}
        self.db_path = "cezalar.json"
        self.MUTE_ROL_ID =1438232975526592634  # Muted rolü ID'si
        self.LOG_KANAL_ID =1438233023526076446  # LOG KANAL ID'SİNİ BURAYA YAZ

    def veri_yaz(self, data):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def veri_oku(self):
        if not os.path.exists(self.db_path): return {}
        with open(self.db_path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
            
        if message.author.guild_permissions.manage_messages:
            return

        user_id = message.author.id
        simdi = datetime.datetime.now()

        self.anti_spam[user_id] = [t for t in self.anti_spam.get(user_id, []) if (simdi - t).total_seconds() < 5]
        self.anti_spam[user_id].append(simdi)

        if len(self.anti_spam[user_id]) > 5:
            self.ihlal_sayaci[user_id] = self.ihlal_sayaci.get(user_id, 0) + 1
            ihlal = self.ihlal_sayaci[user_id]
            
            try: await message.delete()
            except: pass

            if ihlal == 1:
                try:
                    await message.author.timeout(datetime.timedelta(minutes=1), reason="Spam Seviye 1")
                    # Seviye 1 logu istersen buraya da ekleyebiliriz ama kanal kirlenmesin diye eklemedim.
                    await message.channel.send(f"⚠️ {message.author.mention}, spam nedeniyle 1 dakika susturuldun.", delete_after=5)
                except: pass

            elif ihlal >= 2:
                mute_rolu = message.guild.get_role(self.MUTE_ROL_ID)
                bitis_zamani = int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())
                
                # Veritabanı Kaydı
                data = self.veri_oku()
                data[str(user_id)] = {
                    "bitis": bitis_zamani,
                    "sebep": "Otomatik Spam Koruması",
                    "yetkili": "🛡️ SİSTEM"
                }
                self.veri_yaz(data)

                if mute_rolu:
                    try: await message.author.add_roles(mute_rolu)
                    except: pass
                
                # --- LOG KANALINA BİLGİ GÖNDERME ---
                log_kanali = self.bot.get_channel(self.LOG_KANAL_ID)
                if log_kanali:
                    log_embed = discord.Embed(title="🛡️ OTOMATİK CEZA SİSTEMİ", color=0xffa500) # Turuncu
                    log_embed.set_thumbnail(url=message.author.display_avatar.url)
                    log_embed.add_field(name="👤 Kullanıcı", value=f"{message.author.mention}\n`{message.author.id}`", inline=True)
                    log_embed.add_field(name="⚖️ İşlem", value="`MUTE (1 GÜN)`", inline=True)
                    log_embed.add_field(name="📝 Sebep", value="```Spam İhlali (2. Seviye)```", inline=False)
                    log_embed.add_field(name="⏳ Tahliye Tarihi", value=f"<t:{bitis_zamani}:F>", inline=False)
                    log_embed.set_footer(text="TTD Waxsi INC. Koruma Sistemi")
                    log_embed.timestamp = discord.utils.utcnow()
                    await log_kanali.send(embed=log_embed)

                await message.channel.send(f"🚫 {message.author.mention} spam nedeniyle **1 GÜN** susturuldu. Loglar işlendi.", delete_after=10)
            
            self.anti_spam[user_id] = []

async def setup(bot):
    await bot.add_cog(Koruma(bot))