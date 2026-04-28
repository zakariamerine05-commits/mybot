import discord
from discord.ext import commands
from discord.ui import Select, View
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class RoleDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Among Us", emoji="🚀"),
            discord.SelectOption(label="PES", emoji="⚽"),
            discord.SelectOption(label="FIFA", emoji="🎮"),
        ]
        super().__init__(placeholder="اختر لعبتك المفضلة...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"✅ اخترت {self.values[0]}! سيتم إنشاء قناتك.", ephemeral=True)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleDropdown())

@bot.event
async def on_ready():
    print(f"✅ {bot.user} متصل الآن!")

# هذا الأمر سيعمل فوراً عند كتابة !setup حتى لو لم يظهر الـ Slash
@bot.command()
async def setup(ctx):
    embed = discord.Embed(title="🎮 لوحة الألعاب", description="اختر لعبتك:", color=0x9b59b6)
    await ctx.send(embed=embed, view=RoleView())

bot.run(os.environ.get('TOKEN'))
