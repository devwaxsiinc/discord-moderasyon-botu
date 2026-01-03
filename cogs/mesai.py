import discord
from discord import app_commands, ui
from discord.ext import commands
import datetime
import json
import os

class MesaiSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "mesai_verileri.json"

    def veri_oku(self):
        if not os.path.exists(self.db_path): return {}
        with open(self.db_path, "r") as f: return json.load(f)

    def veri_yaz(self, data):
        with open(self.db_path, "w") as f: json.dump(data, f, indent=4)

    @app_commands.command(name="mesai-paneli", description="Yetkililer için mesai kontrol panelini kurar.")
    async def mesai_kur(self, itn: discord.Interaction):
        if not itn.user.guild_permissions.administrator: return
        
        embed = discord.Embed(
            title="🕒 YETKİLİ MESAİ TAKİP SİSTEMİ",
            description=(
                "**Mesaiye başlamadan önce ve bitirirken lütfen aşağıdaki butonları kullanın.**\n\n"
                "🔹 **Mesai Başlat:** Çalışma sürenizi başlatır.\n"
                "🔹 **Mesai Bitir:** Süreyi durdurur ve veritabanına kaydeder.\n"
                "🔹 **İstatistik:** Toplam çalışma sürenizi gösterir."
            ),
            color=0x2b2d31
        )
        embed.set_footer(text="Yetkili Performans Takip Sistemi")
        await itn.channel.send(embed=embed, view=MesaiButonlari(self))
        await itn.response.send_message("✅ Mesai paneli kuruldu.", ephemeral=True)

class MesaiButonlari(ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @ui.button(label="Mesai Başlat", style=discord.ButtonStyle.success, emoji="🟢", custom_id="mesai_start")
    async def start(self, itn: discord.Interaction, button: ui.Button):
        data = self.cog.veri_oku()
        uid = str(itn.user.id)
        
        if uid in data and data[uid].get("aktif_mesai"):
            return await itn.response.send_message("❌ Zaten aktif bir mesainiz bulunuyor!", ephemeral=True)
        
        if uid not in data: data[uid] = {"toplam_sure": 0, "ticket_sayisi": 0}
        
        data[uid]["aktif_mesai"] = datetime.datetime.now().timestamp()
        self.cog.veri_yaz(data)
        
        embed = discord.Embed(description=f"✅ {itn.user.mention} için mesai **başlatıldı.** İyi çalışmalar!", color=discord.Color.green())
        await itn.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Mesai Bitir", style=discord.ButtonStyle.danger, emoji="🔴", custom_id="mesai_stop")
    async def stop(self, itn: discord.Interaction, button: ui.Button):
        data = self.cog.veri_oku()
        uid = str(itn.user.id)
        
        if uid not in data or not data[uid].get("aktif_mesai"):
            return await itn.response.send_message("❌ Başlatılmış bir mesainiz bulunmuyor!", ephemeral=True)
        
        baslangic = data[uid]["aktif_mesai"]
        bitis = datetime.datetime.now().timestamp()
        fark = bitis - baslangic
        
        data[uid]["toplam_sure"] += fark
        data[uid]["aktif_mesai"] = None
        self.cog.veri_yaz(data)
        
        dakika = int(fark / 60)
        embed = discord.Embed(
            title="🔴 Mesai Tamamlandı",
            description=f"Bu oturumdaki çalışma süreniz: **{dakika} dakika.**\nVerileriniz sicilinize işlendi.",
            color=discord.Color.red()
        )
        await itn.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="İstatistiklerim", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="mesai_stats")
    async def stats(self, itn: discord.Interaction, button: ui.Button):
        data = self.cog.veri_oku()
        uid = str(itn.user.id)
        
        if uid not in data:
            return await itn.response.send_message("Henüz bir mesai kaydınız bulunmuyor.", ephemeral=True)
            
        toplam_dakika = int(data[uid]["toplam_sure"] / 60)
        saat = toplam_dakika // 60
        dakika = toplam_dakika % 60
        
        embed = discord.Embed(title=f"📊 {itn.user.name} - Mesai Raporu", color=discord.Color.blue())
        embed.add_field(name="Toplam Süre", value=f"**{saat} Saat, {dakika} Dakika**", inline=False)
        embed.set_footer(text="Performansınız yönetim tarafından takip edilmektedir.")
        await itn.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MesaiSistemi(bot))