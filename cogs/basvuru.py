import discord
from discord import app_commands, ui
from discord.ext import commands
import json
import os
from datetime import datetime

# --- KONFİGÜRASYON ---
BASVURU_LOG_KANAL =1456223800176939172  # Başvuruların düşeceği kanal ID
YETKILI_ROL_ID = 1456228358026297405     # Onaylanınca verilecek rol ID

class BasvuruSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklist_file = "basvuru_kara_liste.json"

    def kara_liste_oku(self):
        if not os.path.exists(self.blacklist_file): return []
        with open(self.blacklist_file, "r") as f: return json.load(f)

    def kara_liste_ekle(self, user_id):
        data = self.kara_liste_oku()
        if user_id not in data:
            data.append(user_id)
            with open(self.blacklist_file, "w") as f: json.dump(data, f)

    @app_commands.command(name="basvuru-kur", description="Elite başvuru panelini kurar.")
    async def kur(self, itn: discord.Interaction):
        if not itn.user.guild_permissions.administrator: return
        
        embed = discord.Embed(
            title="💠 YETKİLİ ALIM DEPARTMANI",
            description=(
                "**Ekibimize katılmak için büyük bir fırsat!**\n\n"
                "Aşağıdaki butona basarak resmi başvuru formuna ulaşabilirsiniz.\n\n"
                "⚠️ **UYARI:** Başvurusu reddedilen adaylar kara listeye alınır."
            ),
            color=0x2b2d31
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1446563387231310055/1447157913108873299/cevommmm.gif?ex=69578fd5&is=69563e55&hm=9d329480dd747e81674e6211c917e0a6197664f549c3eee388c08c0be016b278")
        
        view = ui.View(timeout=None)
        btn = ui.Button(label="Başvuruyu Başlat", style=discord.ButtonStyle.blurple, emoji="🛡️", custom_id="start_apply_elite")
        
        async def callback(interaction: discord.Interaction):
            if interaction.user.id in self.kara_liste_oku():
                return await interaction.response.send_message("❌ Daha önce reddedildiğiniz için başvurunuz engellenmiştir.", ephemeral=True)
            # Modal'a cog (self) örneğini gönderiyoruz
            await interaction.response.send_modal(EliteBasvuruModal(self))
            
        btn.callback = callback
        view.add_item(btn)
        await itn.channel.send(embed=embed, view=view)
        await itn.response.send_message("✅ Panel Kuruldu!", ephemeral=True)

class EliteBasvuruModal(ui.Modal, title="🛡️ Yetkili Başvuru Formu"):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    ad = ui.TextInput(label="Adınız", placeholder="Haydar Armağan", min_length=2, max_length=50)
    yas = ui.TextInput(label="Yaşınız", placeholder="31", min_length=2, max_length=2)
    aktiflik = ui.TextInput(label="Günlük Aktiflik Süreniz", placeholder="5-8 Saat")
    katki = ui.TextInput(label="Sunucuya ne gibi katkıların olacak?", style=discord.TextStyle.paragraph, min_length=10)
    tecrube = ui.TextInput(label="Daha önceki tecrübelerin?", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, itn: discord.Interaction):
        log_kanali = itn.guild.get_channel(BASVURU_LOG_KANAL)
        if not log_kanali:
            return await itn.response.send_message("❌ Log kanalı bulunamadı, yetkililere bildirin.", ephemeral=True)

        embed = discord.Embed(title="📨 YENİ BAŞVURU DOSYASI", color=0x5865f2, timestamp=datetime.now())
        embed.set_thumbnail(url=itn.user.display_avatar.url)
        embed.add_field(name="👤 Aday Bilgisi", value=f"{itn.user.mention}\n`{itn.user.id}`", inline=True)
        embed.add_field(name="📛 Ad / Yaş", value=f"{self.ad.value} / {self.yas.value}", inline=True)
        embed.add_field(name="🕒 Aktiflik", value=f"{self.aktiflik.value}", inline=True)
        embed.add_field(name="🚀 Sunucu Katkısı", value=f"```yaml\n{self.katki.value}```", inline=False)
        embed.add_field(name="📚 Tecrübe", value=f"```\n{self.tecrube.value if self.tecrube.value else 'Belirtilmedi'}```", inline=False)
        
        # Karar butonları
        view = BasvuruKararView(itn.user.id, self.cog)
        await log_kanali.send(embed=embed, view=view)
        await itn.response.send_message("✨ Form iletildi. Yetkililer inceleyecektir.", ephemeral=True)

class BasvuruKararView(ui.View):
    def __init__(self, aday_id, cog):
        super().__init__(timeout=None)
        self.aday_id = aday_id
        self.cog = cog

    @ui.button(label="Dosyayı Onayla", style=discord.ButtonStyle.success, emoji="✅")
    async def approve(self, itn: discord.Interaction, btn: ui.Button):
        aday = itn.guild.get_member(self.aday_id)
        rol = itn.guild.get_role(YETKILI_ROL_ID)
        if aday and rol:
            await aday.add_roles(rol)
            try: await aday.send(f"🎉 **{itn.guild.name}** başvurunuz onaylandı!")
            except: pass
        await itn.message.edit(content=f"✅ **{itn.user.name}** tarafından onaylandı.", view=None)
        await itn.response.send_message("Aday onaylandı.", ephemeral=True)

    @ui.button(label="Dosyayı Reddet", style=discord.ButtonStyle.danger, emoji="❌")
    async def reject(self, itn: discord.Interaction, btn: ui.Button):
        self.cog.kara_liste_ekle(self.aday_id)
        aday = itn.guild.get_member(self.aday_id)
        if aday:
            try: await aday.send(f"❌ **{itn.guild.name}** başvurunuz reddedildi.")
            except: pass
        await itn.message.edit(content=f"❌ **{itn.user.name}** tarafından reddedildi.", view=None)
        await itn.response.send_message("Aday reddedildi.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BasvuruSistemi(bot))