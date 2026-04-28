import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# 1. إعداد الصلاحيات
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. كلاس الأزرار والرتب (يمكنك إضافة أو تغيير الأسماء هنا مستقبلاً)
class RoleSelection(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def give_role(self, interaction, role_name):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message(f"أنت تملك رتبة **{role_name}** بالفعل!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ تم إعطاؤك رتبة: **{role_name}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ خطأ: لم أجد رتبة باسم '{role_name}' في إعدادات السيرفر.", ephemeral=True)

    @discord.ui.button(label="Among Us", style=discord.ButtonStyle.primary, custom_id="btn_1")
    async def b1(self, interaction, button): await self.give_role(interaction, "Among Us")

    @discord.ui.button(label="PES", style=discord.ButtonStyle.primary, custom_id="btn_2")
    async def b2(self, interaction, button): await self.add_role(interaction, "PES")

    @discord.ui.button(label="FIFA", style=discord.ButtonStyle.primary, custom_id="btn_3")
    async def b3(self, interaction, button): await self.add_role(interaction, "FIFA")

@bot.event
async def on_ready():
    print(f"✅ البوت متصل الآن باسم: {bot.user}")
    bot.add_view(RoleSelection())

# 3. الإرسال التلقائي عند دخول عضو جديد
@bot.event
async def on_member_join(member):
    # الرقم الذي أرسلته لي وضعته هنا
    ID_CHANNEL = 1498483280478081194 
    
    channel = bot.get_channel(ID_CHANNEL)
    
    if channel:
        embed = discord.Embed(
            title="✨ نورت السيرفر يا بطل!",
            description=f"أهلاً بك {member.mention}\nاختر ألعابك المفضلة من الأزرار أدناه لتفتح لك القنوات الخاصة بها:",
            color=0x2ecc71
        )
        await channel.send(content=f"حياك الله {member.mention}", embed=embed, view=RoleSelection())
    else:
        print("❌ لم أستطع العثور على القناة، تأكد من صحة الـ ID ومن وجود البوت في السيرفر.")

bot.run(os.environ.get('TOKEN'))
