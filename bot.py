import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# 1. إعداد الصلاحيات (Intents)
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
            await interaction.response.send_message(f"❌ الرتبة **{role_name}** غير موجودة في إعدادات السيرفر.", ephemeral=True)

    @discord.ui.button(label="Among Us", style=discord.ButtonStyle.primary, custom_id="r_among")
    async def b1(self, interaction, button): await self.add_role(interaction, "Among Us")

    @discord.ui.button(label="PES", style=discord.ButtonStyle.primary, custom_id="r_pes")
    async def b2(self, interaction, button): await self.add_role(interaction, "PES")

    @discord.ui.button(label="FIFA", style=discord.ButtonStyle.primary, custom_id="r_fifa")
    async def b3(self, interaction, button): await self.add_role(interaction, "FIFA")

    @discord.ui.button(label="Stumble Guys", style=discord.ButtonStyle.secondary, custom_id="r_stumble")
    async def b4(self, interaction, button): await self.add_role(interaction, "Stumble Guys")

    @discord.ui.button(label="GTA", style=discord.ButtonStyle.primary, custom_id="r_gta")
    async def b5(self, interaction, button): await self.add_role(interaction, "GTA")

    @discord.ui.button(label="مشاهدة أفلام", style=discord.ButtonStyle.success, custom_id="r_movies")
    async def b6(self, interaction, button): await self.add_role(interaction, "Movies")

    @discord.ui.button(label="دراسة", style=discord.ButtonStyle.danger, custom_id="r_study")
    async def b7(self, interaction, button): await self.add_role(interaction, "Study")

@bot.event
async def on_ready():
    print(f'✅ البوت متصل الآن: {bot.user}')
    bot.add_view(RoleView())

# 3. إرسال الرسالة تلقائياً عند دخول عضو جديد
@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title=f"مرحباً بك في {member.guild.name}!",
        description="اختر اهتماماتك من الأزرار أدناه للحصول على الرتب الخاصة بك والدخول للقنوات المخصصة:",
        color=0x2ecc71
    )
    
    # محاولة الإرسال في الخاص أولاً
    try:
        await member.send(embed=embed, view=RoleView())
        print(f"✅ تم إرسال رسالة خاصة لـ {member.name}")
    except Exception as e:
        # إذا فشل الإرسال في الخاص (مثلاً العضو مغلق الخاص)، يرسل في القناة العامة
        print(f"❌ فشل الإرسال لـ {member.name} في الخاص. المحاولة في القناة العامة...")
        channel = bot.get_channel(1498483280478081194) # ID القناة الخاصة بك
        if channel:
            await channel.send(content=f"مرحباً {member.mention}، لم أستطع مراسلتك في الخاص! يمكنك اختيار رتبك من هنا:", embed=embed, view=RoleView())

bot.run(os.environ['TOKEN'])
