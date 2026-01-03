import discord
from discord import app_commands, ui
from discord.ext import commands
import asyncio
from datetime import datetime
import io

# --- AYARLAR ---
TICKET_KATEGORI_ID = 1456253433253199884 
YETKILI_ROL_ID = 1438232910720143461      
LOG_KANAL_ID = 1456255110207504394       

# Buraya etiketlenmesini istediğin 2 kişinin ID'sini yaz
EKSTRA_YETKILI_1_ID = 1107603491419074560 # 1. Kişi ID
EKSTRA_YETKILI_2_ID = 769245977890127923 # 2. Kişi ID

class TicketIslemButonlari(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Ticketi Üstlen", style=discord.ButtonStyle.success, emoji="🛡️", custom_id="claim_btn")
    async def claim(self, itn: discord.Interaction, button: ui.Button):
        if itn.guild.get_role(YETKILI_ROL_ID) not in itn.user.roles:
            return await itn.response.send_message("❌ Sadece yetkililer üstlenebilir.", ephemeral=True)
        
        button.disabled = True
        button.label = "Üstlenildi"
        embed = itn.message.embeds[0]
        embed.add_field(name="💼 Sorumlu Yetkili", value=itn.user.mention, inline=False)
        embed.color = discord.Color.green()
        
        await itn.response.edit_message(embed=embed, view=self)
        await itn.followup.send(f"⚡ **{itn.user.name}** bu talebi devraldı!")

    # --- DÜZELTİLMİŞ VE EKSTRA ETİKETLİ YETKİLİ ÇAĞIRMA ---
    @ui.button(label="Yetkili Çağır", style=discord.ButtonStyle.secondary, emoji="🔔", custom_id="call_staff_btn")
    async def call_staff(self, itn: discord.Interaction, button: ui.Button):
        button.disabled = True
        button.label = "Yetkili Çağrıldı"
        button.style = discord.ButtonStyle.success
        
        await itn.response.edit_message(view=self)
        
        embed = discord.Embed(
            description=f"📢 {itn.user.mention} şu an yetkili bekliyor!\n\n**Etiketlenen Yetkililer:**\n<@&{YETKILI_ROL_ID}>\n<@{EKSTRA_YETKILI_1_ID}>\n<@{EKSTRA_YETKILI_2_ID}>",
            color=0x2b2d31
        )
        embed.set_footer(text="TTD Waxsi INC. Destek Sistemi")
        
        # Hem Rolü hem de 2 Özel Kişiyi etiketler
        ping_mesaji = f"<@&{YETKILI_ROL_ID}> <@{EKSTRA_YETKILI_1_ID}> <@{EKSTRA_YETKILI_2_ID}>"
        await itn.channel.send(content=f"{ping_mesaji} 🔔", embed=embed)

    @ui.button(label="Kapat & Arşivle", style=discord.ButtonStyle.danger, emoji="💾", custom_id="close_btn")
    async def close(self, itn: discord.Interaction, button: ui.Button):
        await itn.response.send_message("📂 Görüşme sonlandırılıyor, arşiv oluşturuluyor...")
        
        log_kanali = itn.guild.get_channel(LOG_KANAL_ID)
        transcript = f"--- TICKET KAYDI: {itn.channel.name} ---\nKapatan: {itn.user.name}\nTarih: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        async for msg in itn.channel.history(limit=None, oldest_first=True):
            time = msg.created_at.strftime('%H:%M')
            transcript += f"[{time}] {msg.author.name}: {msg.content}\n"

        buffer = io.BytesIO(transcript.encode('utf-8'))
        file = discord.File(fp=buffer, filename=f"arsiv-{itn.channel.name}.txt")

        if log_kanali:
            log_embed = discord.Embed(title="📁 Talep Kapatıldı", color=discord.Color.red(), timestamp=datetime.now())
            log_embed.add_field(name="Kanal", value=itn.channel.name)
            log_embed.add_field(name="Kapatan", value=itn.user.mention)
            await log_kanali.send(embed=log_embed, file=file)

        await asyncio.sleep(3)
        await itn.channel.delete()

class TicketMenu(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Genel Destek", description="Genel sorular ve yardım.", emoji="🆘", value="genel"),
            discord.SelectOption(label="Şikayet & Rapor", description="Kural ihlallerini bildir.", emoji="🚫", value="sikayet"),
            discord.SelectOption(label="Sponsor & İş Birliği", description="Reklam ve ortaklık.", emoji="🤝", value="partner"),
            discord.SelectOption(label="Teknik Sorun", description="Yazılımsal destek.", emoji="⚙️", value="teknik")
        ]
        super().__init__(placeholder="Departman seçmek için buraya tıkla...", min_values=1, max_values=1, options=options, custom_id="ticket_select_pro")

    async def callback(self, itn: discord.Interaction):
        guild = itn.guild
        kategori = guild.get_channel(TICKET_KATEGORI_ID)
        
        check_name = f"{self.values[0]}-{itn.user.name.lower()}".replace(" ", "-")
        mevcut = discord.utils.get(kategori.text_channels, name=check_name)
        
        if mevcut:
            return await itn.response.send_message(f"⚠️ Zaten aktif bir **{self.values[0]}** talebiniz var: {mevcut.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            itn.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.get_role(YETKILI_ROL_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        kanal = await guild.create_text_channel(f"{self.values[0]}-{itn.user.name}", category=kategori, overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"✨ {self.values[0].capitalize()} Departmanı",
            description=f"Merhaba {itn.user.mention}, talebin başarıyla açıldı.\n\nYetkililerimiz konuyu inceleyip seninle burada iletişime geçecek.\n\n**Acil bir durum varsa aşağıdaki butonu kullanarak yetkili çağırabilirsin.**",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=itn.user.display_avatar.url)
        
        await kanal.send(content=f"{itn.user.mention} | <@&{YETKILI_ROL_ID}>", embed=embed, view=TicketIslemButonlari())
        await itn.response.send_message(f"✅ Kanalın oluşturuldu: {kanal.mention}", ephemeral=True)

class TicketAnaView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketMenu())

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket-kur", description="Açıklamalı Premium Ticket Panelini kurar.")
    async def setup(self, itn: discord.Interaction):
        if not itn.user.guild_permissions.administrator: return
        
        embed = discord.Embed(
            title="🏮 MERKEZİ DESTEK SİSTEMİ",
            description=(
                "Sunucumuzla ilgili tüm işlemlerinizi aşağıdaki menüden **departman seçerek** gerçekleştirebilirsiniz.\n\n"
                "**DEPARTMANLAR VE GÖREVLERİ:**\n"
                "> 🆘 **Genel Destek:** Sunucuyla ilgili her türlü genel soru.\n"
                "> 🚫 **Şikayet:** Kural ihlalleri ve kullanıcı şikayetleri.\n"
                "> 🤝 **İş Birliği:** Sponsorluk ve ortaklık görüşmeleri.\n"
                "> ⚙️ **Teknik Sorun:** Bot ve yazılımsal hatalar.\n\n"
                "🛡️ **Bilgi:** Talepleriniz arşivlenmekte ve yetkililerce izlenmektedir."
            ),
            color=0x2b2d31
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1446563387231310055/1447157913108873299/cevommmm.gif?ex=69578fd5&is=69563e55&hm=9d329480dd747e81674e6211c917e0a6197664f549c3eee388c08c0be016b278")
        embed.set_footer(text="Profesyonel Yönetim Paneli", icon_url=itn.guild.icon.url if itn.guild.icon else None)
        
        await itn.channel.send(embed=embed, view=TicketAnaView())
        await itn.response.send_message("🔥 Premium Panel Aktif!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))