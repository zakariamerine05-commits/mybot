import discord
from discord.ext import commands
from discord.ui import Select, View
import os

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# --- الواجهة الرسومية (نفسها بدون تغيير) ---
class RoleDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Among Us", description="رتبة أمونج أس + غرفة خاصة", emoji="🚀"),
            discord.SelectOption(label="PES", description="رتبة بيس + غرفة خاصة", emoji="⚽"),
            discord.SelectOption(label="FIFA", description="رتبة فيفا + غرفة خاصة", emoji="🎮"),
        ]
        super().__init__(placeholder="اضغط هنا لاختيار لعبتك وتلقي رتبتك...", options=options, custom_id="role_select_menu")

    async def callback(self, interaction: discord.Interaction):
        # ... (نفس الكود الداخلي السابق) ...
        await interaction.response.send_message(f"✅ تم تنفيذ الطلب بنجاح!", ephemeral=True)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleDropdown())

# --- جزء مراقبة الأخطاء (هذا ما سيكشف المشكلة) ---

@bot.event
async def on_ready():
    print(f"✅ البوت شغال باسم: {bot.user}")
    bot.add_view(RoleView())

@bot.event
async def on_message(message):
    # هذا السطر سيطبع في Railway أي شيء يكتب في السيرفر
    print(f"📩 رسالة جديدة من {message.author}: {message.content}")
    
    # ضروري جداً لكي تعمل الأوامر مع on_message
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    await ctx.send("✅ أنا أسمعك! البوت يعمل والأوامر شغالة.")

@bot.command()
@commands.has_permissions(administrator=True)
async def menu(ctx):
    await ctx.send(content="🎮 اختر لعبتك:", view=RoleView())

bot.run(os.environ.get('TOKEN'))
