import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# إعداد الصلاحيات
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

# استخدام commands.Bot بدلاً من discord.Client
bot = commands.Bot(command_prefix=".", intents=intents)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def add_role(self, interaction, role_name):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message(f"أنت تملك رتبة **{role_name}** بالفعل!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ تم إعطاؤك رتبة: **{role_name}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ الرتبة غير موجودة بالسيرفر!", ephemeral=True)

    @discord.ui.button(label="Among Us", style=discord.ButtonStyle.primary, custom_id="btn1")
    async def b1(self, interaction, button): await self.add_role(interaction, "Among Us")

    @discord.ui.button(label="PES", style=discord.ButtonStyle.primary, custom_id="btn2")
    async def b2(self, interaction, button): await self.add_role(interaction, "PES")

    @discord.ui.button(label="FIFA", style=discord.ButtonStyle.primary, custom_id="btn3")
    async def b3(self, interaction, button): await self.add_role(interaction, "FIFA")

    @discord.ui.button(label="Stumble Guys", style=discord.ButtonStyle.secondary, custom_id="btn4")
    async def b4(self, interaction, button): await self.add_role(interaction, "Stumble Guys")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.primary, custom_id="btn5")
    async def b5(self, interaction, button): await self.add_role(interaction, "GTA")

    @discord.ui.button(label="مشاهدة أفلام", style=discord.ButtonStyle.success, custom_id="btn6")
    async def b6(self, interaction, button): await self.add_role(interaction, "Movies")

    @discord.ui.button(label="دراسة", style=discord.ButtonStyle.danger, custom_id="btn7")
    async def b7(self, interaction, button): await self.add_role(interaction, "Study")

@bot.event
async def on_ready():
    print(f'✅ البوت متصل باسم: {bot.user}')
    bot.add_view(RoleView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="🎮 اختيار الرتب والاهتمامات",
        description="اضغط على الأزرار أدناه للحصول على الرتب:",
        color=0x2ecc71
    )
    await ctx.send(embed=embed, view=RoleView())
    await ctx.message.delete()

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1498483280478081194)
    if channel:
        embed = discord.Embed(title="أهلاً بك!", description="اختر رتبك من هنا:", color=0x2ecc71)
        await channel.send(content=f"مرحباً {member.mention}", embed=embed, view=RoleView())

bot.run(os.environ['TOKEN'])
