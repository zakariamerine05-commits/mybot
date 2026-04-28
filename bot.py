import discord
from discord.ui import Button, View
import os

# 1. إعداد الصلاحيات
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

client = discord.Client(intents=intents)

# 2. كلاس الأزرار والرتب
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
            await interaction.response.send_message(f"❌ خطأ: الرتبة **{role_name}** غير موجودة بالسيرفر!", ephemeral=True)

    @discord.ui.button(label="Among Us", style=discord.ButtonStyle.primary, custom_id="among_us")
    async def among_us(self, interaction, button): await self.add_role_to_member(interaction, "Among Us")

    @discord.ui.button(label="PES", style=discord.ButtonStyle.primary, custom_id="pes")
    async def pes(self, interaction, button): await self.add_role_to_member(interaction, "PES")

    @discord.ui.button(label="FIFA", style=discord.ButtonStyle.primary, custom_id="fifa")
    async def fifa(self, interaction, button): await self.add_role_to_member(interaction, "FIFA")

    @discord.ui.button(label="Stumble Guys", style=discord.ButtonStyle.secondary, custom_id="stumble")
    async def stumble(self, interaction, button): await self.add_role_to_member(interaction, "Stumble Guys")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.primary, custom_id="gta")
    async def gta(self, interaction, button): await self.add_role_to_member(interaction, "GTA")

    @discord.ui.button(label="مشاهدة أفلام", style=discord.ButtonStyle.success, custom_id="movies")
    async def movies(self, interaction, button): await self.add_role_to_member(interaction, "Movies")

    @discord.ui.button(label="دراسة", style=discord.ButtonStyle.danger, custom_id="study")
    async def study(self, interaction, button): await self.add_role_to_member(interaction, "Study")

@client.event
async def on_ready():
    print(f'✅ {client.user} جاهز للعمل!')
    client.add_view(RoleView())

# إرسال الرسالة عند دخول عضو جديد تلقائياً للقناة المحددة
@client.event
async def on_member_join(member):
    channel_id = 1498483280478081194  # الأيدي الخاص بك
    channel = client.get_channel(channel_id)
    if channel:
        embed = discord.Embed(
            title="🎮 أهلاً بك في سيرفرنا!",
            description=f"مرحباً {member.mention}\nيرجى اختيار اهتماماتك من الأزرار أدناه للحصول على الرتبة المخصصة لك:",
            color=0x2ecc71
        )
        await channel.send(content=f"مرحباً {member.mention}", embed=embed, view=RoleView())

# أمر .setup لاستدعاء القائمة يدوياً
@client.event
async def on_message(message):
    if message.author.bot: return
    if message.content == ".setup":
        if message.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="🎮 اختيار الرتب والاهتمامات",
                description="اضغط على الأزرار أدناه للحصول على الرتب:",
                color=0x2ecc71
            )
            await message.channel.send(embed=embed, view=RoleView())
            await message.delete()

client.run(os.environ['TOKEN'])
