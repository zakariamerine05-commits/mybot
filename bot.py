import discord
from discord.ui import Button, View
import os

# إعداد الصلاحيات
intents = discord.Intents.default()
intents.members = True 

client = discord.Client(intents=intents)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def add_role_to_member(self, interaction, role_name):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message(f"أنت تملك رتبة **{role_name}** بالفعل!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ تم إعطاؤك رتبة: **{role_name}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ خطأ: الرتبة **{role_name}** غير موجودة. اطلب من الإدارة إنشائها.", ephemeral=True)

    # أزرار الألعاب
    @discord.ui.button(label="Among Us", style=discord.ButtonStyle.primary, custom_id="among_us")
    async def among_us(self, interaction, button):
        await self.add_role_to_member(interaction, "Among Us")

    @discord.ui.button(label="PES", style=discord.ButtonStyle.primary, custom_id="pes")
    async def pes(self, interaction, button):
        await self.add_role_to_member(interaction, "PES")

    @discord.ui.button(label="FIFA", style=discord.ButtonStyle.primary, custom_id="fifa")
    async def fifa(self, interaction, button):
        await self.add_role_to_member(interaction, "FIFA")

    @discord.ui.button(label="Stumble Guys", style=discord.ButtonStyle.secondary, custom_id="stumble")
    async def stumble(self, interaction, button):
        await self.add_role_to_member(interaction, "Stumble Guys")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.primary, custom_id="gta")
    async def gta(self, interaction, button):
        await self.add_role_to_member(interaction, "GTA")

    # أزرار الاهتمامات الأخرى
    @discord.ui.button(label="مشاهدة أفلام", style=discord.ButtonStyle.success, custom_id="movies")
    async def movies(self, interaction, button):
        await self.add_role_to_member(interaction, "Movies")

    @discord.ui.button(label="دراسة", style=discord.ButtonStyle.danger, custom_id="study")
    async def study(self, interaction, button):
        await self.add_role_to_member(interaction, "Study")

@client.event
async def on_ready():
    print(f'تم تشغيل بوت الرتب بنجاح: {client.user}')
    client.add_view(RoleView())

@client.event
async def on_member_join(member):
    # اختر قناة معينة (مثلاً قناة الترحيب) لإرسال القائمة
    channel = member.guild.system_channel 
    if channel:
        embed = discord.Embed(
            title="🎮 قائمة اختيار الاهتمامات",
            description=f"مرحباً بك {member.mention}!\nمن فضلك اختر الألعاب أو الاهتمامات التي تحبها للحصول على رتبتها:",
            color=0x2ecc71
        )
        embed.set_footer(text="بمجرد الضغط على الزر ستحصل على الرتبة فوراً")
        await channel.send(embed=embed, view=RoleView())

client.run(os.environ['TOKEN'])
