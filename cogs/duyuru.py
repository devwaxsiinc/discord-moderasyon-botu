import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class Duyuru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # --- ÖZEL AYAR ---
        self.SAHIP_ID = 697106524581003474  # <--- BURAYA KENDİ ID'Nİ YAZ
        # -----------------

    @app_commands.command(name="dm-duyuru", description="Sunucudaki herkese özel tasarım bir duyuru ulaştırır.")
    @app_commands.describe(mesaj="Duyuru içeriğini buraya yazın.")
    async def dm_duyuru(self, itn: discord.Interaction, mesaj: str):
        # Güvenlik Kontrolü
        if itn.user.id != self.SAHIP_ID:
            return await itn.response.send_message("❌ Bu komut sistem mimarına özeldir.", ephemeral=True)

        await itn.response.send_message("💠 **Kimlik doğrulandı. Elite duyuru paketleri hazırlanıyor...**", ephemeral=True)

        # TASARIM BURADA BAŞLIYOR
        embed = discord.Embed(
            title="💠 MERKEZİ DUYURU SİSTEMİ",
            description=f"\n{mesaj.replace('\\n', '\n')}\n",
            color=0x2b2d31 # En cool koyu gri tonu
        )
        
        # Üst Kısım: Sunucu Adı ve İkonu
        embed.set_author(
            name=itn.guild.name.upper(), 
            icon_url=itn.guild.icon.url if itn.guild.icon else None
        )
        
        # Alt Kısım: Kurumsal İmzalar
        embed.set_footer(
            text=f"Yönetim Özel Tebligatı • {itn.user.name}", 
            icon_url=itn.user.display_avatar.url
        )
        
        # Zaman Damgası
        embed.timestamp = discord.utils.utcnow()

        basarili = 0
        hatali = 0
        
        # Gönderim Süreci
        for member in itn.guild.members:
            if member.bot: continue
            
            try:
                await member.send(embed=embed)
                basarili += 1
                await asyncio.sleep(0.4) # Discord koruması
            except:
                hatali += 1

        # Final Raporu (Sadece Sana)
        rapor = discord.Embed(
            title="✅ İŞLEM TAMAMLANDI",
            description=(
                f"```yaml\n"
                f"Toplam Başarılı: {basarili}\n"
                f"Toplam Başarısız: {hatali}\n"
                f"```"
            ),
            color=0x00ff00
        )
        await itn.followup.send(embed=rapor, ephemeral=True)

# Extension yükleme fonksiyonu
async def setup(bot):
    await bot.add_cog(Duyuru(bot))