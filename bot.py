import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
import os

# 1. إعدادات البوت الأساسية
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # تسجيل الواجهة الرسومية لتظل تعمل دائماً
        self.add_view(RoleView())
        # مزامنة أوامر الشرطة (Slash Commands)
        await self.tree.sync()
        print("✅ تم مزامنة أوامر الشرطة (Slash Commands)")

bot = MyBot()

# 2. القائمة المنسدلة (الواجهة الرسومية)
class RoleDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Among Us", emoji="🚀"),
            discord.SelectOption(label="PES", emoji="⚽"),
            discord.SelectOption(label="FIFA", emoji="🎮"),
        ]
        super().__init__(placeholder="اختر لعبتك المفضلة...", options=options, custom_id="persistent_select")

    async def callback(self, interaction: discord.Interaction):
        role_name = self.values[0]
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            await interaction.user.add_roles(role)
            # إنشاء القناة الخاصة
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            channel = await guild.create_text_channel(name=f"🎮-{role_name}", overwrites=overwrites)
            await channel.send(f"نورت القناة يا {interaction.user.mention}!")
            await interaction.response.send_message(f"✅ تم إعطاؤك رتبة {role_name} وفتح قناة: {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ لم أجد رتبة باسم {role_name}", ephemeral=True)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleDropdown())

# 3. الأحداث والأوامر
@bot.event
async def on_ready():
    print(f"🚀 البوت جاهز باسم: {bot.user}")

# --- الأمر الجديد (Slash Command) ---
@bot.tree.command(name="setup", description="إرسال قائمة اختيار الرتب")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="🎮 لوحة الألعاب", description="اختر لعبتك المفضلة:", color=0x9b59b6)
    await interaction.response.send_message(embed=embed, view=RoleView())

bot.run(os.environ.get('TOKEN'))
