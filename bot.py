import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# 1. إعداد الصلاحيات (Intents) - ضرورية جداً لكي يرى البوت الأعضاء الجدد
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

bot = commands.Bot(command_prefix=".", intents=intents)

# 2. كلاس الأزرار والرتب
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
            await interaction.response.send_message(f"❌ الرتبة غير موجودة، تأكد من إنشائها في السيرفر بنفس الاسم.", ephemeral=True)

    @discord.ui.button(label="Among Us", style=discord.ButtonStyle.primary, custom_id="btn_among")
    async def b1(self, interaction, button): await self.add_role(interaction, "Among Us")

    @discord.ui.button(label="PES", style=discord.ButtonStyle.primary, custom_id="btn_pes")
    async def b2(self, interaction, button): await self.add_role(interaction, "PES")

    @discord.ui.button(label="FIFA", style=discord.ButtonStyle.primary, custom_id="btn_fifa")
    async def b3(self, interaction, button): await self.add_role(interaction, "FIFA")

    @discord.ui.button(label="Stumble Guys", style=discord.ButtonStyle.secondary, custom_id="btn_stumble")
    async def b4(self, interaction, button): await self.add_role(interaction, "Stumble Guys")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.primary, custom_id="btn_gta")
    async def b5(self, interaction, button): await self.add_role(interaction, "GTA")

    @discord.ui.button(label="مشاهدة أفلام", style=discord.ButtonStyle.success, custom_id="btn_movies")
    async def b6(self, interaction, button): await self.add_role(interaction, "Movies")

    @discord.ui.button(label="دراسة", style=discord.ButtonStyle.danger, custom_id="btn_study")
    async def b7(self, interaction, button): await self.add_role(interaction, "Study")

@bot.event
async def on_ready():
    print(f'✅ البوت شغال الآن باسم: {bot.user}')
    bot.add_view(RoleView())

# 3. الإرسال التلقائي في الخاص عند دخول عضو جديد
@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title=f"مرحباً بك في {member.guild.name}!",
        description="اختر اهتماماتك من الأزرار أدناه للحصول على الرتب الخاصة بك:",
        color=0x2ecc71
    )
    try:
        await member.send(embed=embed, view=RoleView())
        print(f"✅ أرسلت بنجاح إلى خاص: {member.name}")
    except:
        # إذا كان الخاص مغلق، يرسل في القناة التي أعطيتني الأيدي الخاص بها
        channel = bot.get_channel(1498483280478081194)
        if channel:
            await channel.send(f"مرحباً {member.mention}، حاولت مراسلتك في الخاص لإعطائك الرتب لكنه مغلق! يمكنك الاختيار من هنا:", embed=embed, view=RoleView())

bot.run(os.environ['TOKEN'])
