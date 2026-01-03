import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import json
import os
import asyncio

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "cezalar.json"
        self.MUTE_ROL_ID = 1438232975526592634  # Susturulan rol ID
        self.LOG_KANAL_ID = 1438233023526076446 # Log kanal ID
        self.OTO_TEMIZLIK_KANAL_ID = 1438233069831192707 # Temizlenecek kanal ID

        self.ceza_kontrol.start()
        self.oto_temizlik_dongusu.start()

    def veri_oku(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        try:
            with open(self.db_path, "r", encoding="utf-8") as f: 
                return json.load(f)
        except:
            return {}

    def veri_yaz(self, data):
        with open(self.db_path, "w", encoding="utf-8") as f: 
            json.dump(data, f, indent=4, ensure_ascii=False)

    @app_commands.command(name="ceza-sorgula", description="Aktif ceza durumunu elite panelde görüntüler.")
    async def ceza_sorgula(self, itn: discord.Interaction, kullanici: discord.Member = None):
        target = kullanici or itn.user
        data = self.veri_oku()
        user_id = str(target.id)

        if user_id not in data:
            embed_temiz = discord.Embed(
                description=f"✨ {target.mention} **için aktif bir kısıtlama bulunamadı. Sicil temiz!**",
                color=0x2b2d31
            )
            return await itn.response.send_message(embed=embed_temiz, ephemeral=True)

        raw_bitis = data[user_id].get("bitis", 0)
        bitis_ts = int(float(raw_bitis))
        raw_sebep = data[user_id].get("sebep", "Belirtilmedi")
        sebep = raw_sebep.replace("Bitiş:", "").strip()

        embed = discord.Embed(title="⚖️ CEZA YÖNETİM SİSTEMİ", color=0x2b2d31)
        embed.set_author(name=f"{target.name}", icon_url=target.display_avatar.url)
        embed.add_field(name="🛡️ Durum", value="`🔴 KISITLANDI`", inline=True)
        embed.add_field(name="⏳ Kalan Süre", value=f"<t:{bitis_ts}:R>", inline=True)
        embed.add_field(name="📅 Tahliye Tarihi", value=f"<t:{bitis_ts}:F>", inline=False)
        embed.add_field(name="📝 Ceza Sebebi", value=f"```yaml\n{sebep}```", inline=False)
        embed.set_footer(text=f"Sorgulayan: {itn.user.name}", icon_url=itn.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await itn.response.send_message(embed=embed, ephemeral=True)

    # --- DÜZELTİLEN BÖLÜM: Fonksiyon adı ceza_ver yapıldı ---
    @app_commands.command(name="ceza-ver", description="Kullanıcıya süreli kısıtlama verir (Tüm alanlar zorunludur).")
    @app_commands.describe(kullanici="Cezalandırılacak üye", gun="Süre yoksa 0 yazın", saat="Süre yoksa 0 yazın", dakika="Süre yoksa 0 yazın", sebep="Ceza sebebi girmek zorunludur")
    async def ceza_ver(self, itn: discord.Interaction, kullanici: discord.Member, gun: int, saat: int, dakika: int, sebep: str):
        if not itn.user.guild_permissions.manage_roles:
            return await itn.response.send_message("❌ Yetkiniz yetersiz!", ephemeral=True)

        saniye = (gun * 86400) + (saat * 3600) + (dakika * 60)
        if saniye <= 0: 
            return await itn.response.send_message("❌ **Hata:** Süre girmelisiniz!", ephemeral=True)

        bitis_ts = int((datetime.datetime.now() + datetime.timedelta(seconds=saniye)).timestamp())
        rol = itn.guild.get_role(self.MUTE_ROL_ID)
        if rol: 
            try:
                await kullanici.add_roles(rol)
            except:
                return await itn.response.send_message("❌ Botun yetkisi bu kullanıcıya yetmiyor!", ephemeral=True)

        data = self.veri_oku()
        data[str(kullanici.id)] = {"bitis": bitis_ts, "sebep": sebep, "yetkili": itn.user.name}
        self.veri_yaz(data)

        log_kanali = self.bot.get_channel(self.LOG_KANAL_ID)
        if log_kanali:
            log_embed = discord.Embed(title="📝 Ceza İşlendi", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="👤 Kullanıcı", value=f"{kullanici.mention}", inline=True)
            log_embed.add_field(name="👮 Yetkili", value=f"{itn.user.mention}", inline=True)
            log_embed.add_field(name="⏳ Süre", value=f"{gun}g {saat}s {dakika}d", inline=True)
            log_embed.add_field(name="📝 Sebep", value=sebep, inline=False)
            await log_kanali.send(embed=log_embed)

        await itn.response.send_message(f"✅ {kullanici.mention} için ceza işlendi. Tahliye: <t:{bitis_ts}:R>", ephemeral=True)

    @app_commands.command(name="cezayi-kaldir", description="Kullanıcının cezasını manuel olarak kaldırır.")
    async def cezayi_kaldir(self, itn: discord.Interaction, kullanici: discord.Member):
        if not itn.user.guild_permissions.manage_roles:
            return await itn.response.send_message("❌ Yetkiniz yetersiz!", ephemeral=True)

        rol = itn.guild.get_role(self.MUTE_ROL_ID)
        if rol: 
            try: await kullanici.remove_roles(rol)
            except: pass

        data = self.veri_oku()
        if str(kullanici.id) in data:
            del data[str(kullanici.id)]
            self.veri_yaz(data)

        log_kanali = self.bot.get_channel(self.LOG_KANAL_ID)
        if log_kanali:
            log_embed = discord.Embed(title="🔓 Ceza Kaldırıldı", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="👤 Kullanıcı", value=f"{kullanici.mention}", inline=True)
            log_embed.add_field(name="👮 Yetkili", value=f"{itn.user.mention}", inline=True)
            await log_kanali.send(embed=log_embed)

        await itn.response.send_message(f"✅ {kullanici.mention} kısıtlaması kaldırıldı.", ephemeral=True)

    @app_commands.command(name="temizle", description="Kanaldaki mesajları elite bir şekilde temizler.")
    async def temizle(self, itn: discord.Interaction, miktar: int):
        if not itn.user.guild_permissions.manage_messages:
            return await itn.response.send_message("❌ Yetkiniz yetersiz!", ephemeral=True)
        
        await itn.response.defer(ephemeral=True)
        silinen = await itn.channel.purge(limit=miktar)
        
        embed = discord.Embed(description=f"🧹 **Kanal temizliği tamamlandı.**\n> Silinen mesaj: `{len(silinen)}`", color=0x2b2d31)
        duyuru = await itn.channel.send(embed=embed)
        await itn.followup.send(f"✅ `{len(silinen)}` mesaj silindi.", ephemeral=True)
        await asyncio.sleep(5)
        try: await duyuru.delete()
        except: pass

    @tasks.loop(hours=24)
    async def oto_temizlik_dongusu(self):
        await self.bot.wait_until_ready()
        kanal = self.bot.get_channel(self.OTO_TEMIZLIK_KANAL_ID)
        if kanal:
            try:
                await kanal.purge(limit=None, bulk=True)
                embed = discord.Embed(title="✨ OTOMATİK SİSTEM TEMİZLİĞİ", description="Kanal düzeni için tüm mesajlar temizlendi.", color=0x2b2d31)
                await kanal.send(embed=embed, delete_after=30)
            except: pass

    @tasks.loop(minutes=1)
    async def ceza_kontrol(self):
        data = self.veri_oku()
        simdi = int(datetime.datetime.now().timestamp())
        degisiklik = False
        
        for uid, info in list(data.items()):
            if simdi >= info.get("bitis", 0):
                for guild in self.bot.guilds:
                    member = guild.get_member(int(uid))
                    rol = guild.get_role(self.MUTE_ROL_ID)
                    if member and rol:
                        try: await member.remove_roles(rol)
                        except: pass
                del data[uid]
                degisiklik = True
        if degisiklik: self.veri_yaz(data)

async def setup(bot):
    await bot.add_cog(Moderasyon(bot))