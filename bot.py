import discord
from discord.ext import commands
from discord.ui import Select, View
import os

# 1. إعدادات الأذونات (Intents)
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

# تعريف البوت وعلامة الأمر (Prefix)
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. الواجهة الرسومية: تعريف القائمة المنسدلة
class RoleDropdown(Select):
    def __init__(self):
        # يمكنك إضافة خيارات أكثر هنا بنفس الطريقة
        options = [
            discord.SelectOption(label="Among Us", description="رتبة أمونج أس + غرفة خاصة", emoji="🚀"),
            discord.SelectOption(label="PES", description="رتبة بيس + غرفة خاصة", emoji="⚽"),
            discord.SelectOption(label="FIFA", description="رتبة فيفا + غرفة خاصة", emoji="🎮"),
        ]
        super().__init__(placeholder="اضغط هنا لاختيار لعبتك وتلقي رتبتك...", options=options, custom_id="role_select_menu")

    async def callback(self, interaction: discord.Interaction):
        role_name = self.values[0]
        guild = interaction.guild
        member = interaction.user
        
        # البحث عن الرتبة في السيرفر
        role = discord.utils.get(guild.roles, name=role_name)

        # أ- إعطاء الرتبة للعضو
        if role:
            try:
                await member.add_roles(role)
            except:
                return await interaction.response.send_message("❌ فشلت في إعطاء الرتبة، تأكد أن رتبتي أعلى من الرتب المطلوبة.", ephemeral=True)
        else:
            return await interaction.response.send_message(f"❌ لم أجد رتبة باسم {role_name} في السيرفر.", ephemeral=True)

        # ب- إنشاء الغرفة الخاصة (صلاحيات مخصصة)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), # الجميع ممنوع
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True), # العضو مسموح
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True) # البوت مسموح
        }
        
        channel_name = f"🎮-{role_name}-{member.name}"
        new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        # ج- رسالة ترحيب داخل الغرفة الجديدة
        embed_room = discord.Embed(
            title=f"غرفة ألعاب: {role_name}",
            description=f"أهلاً بك {member.mention} في غرفتك المخصصة! يمكنك الآن الدردشة هنا.",
            color=0x3498db
        )
        await new_channel.send(embed=embed_room)

        # د- الرد النهائي للعضو (يراه هو فقط)
        await interaction.response.send_message(f"✅ تم! حصلت على رتبة **{role_name}** وفتحت لك قناة: {new_channel.mention}", ephemeral=True)

# 3. الواجهة التي تحمل القائمة (View)
class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None) # لتعمل القائمة للأبد
        self.add_item(RoleDropdown())

# 4. الأحداث (Events)
@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت بنجاح: {bot.user}")
    # مهم جداً: جعل البوت "يتذكر" القائمة حتى بعد إعادة التشغيل
    bot.add_view(RoleView())

@bot.event
async def on_member_join(member):
    # استبدل هذا الرقم بالـ ID الخاص بقناتك (الذي أرسلته لي سابقاً)
    ID_CHANNEL = 1498483280478081194 
    channel = bot.get_channel(ID_CHANNEL)
    
    if channel:
        embed = discord.Embed(
            title="✨ نورت السيرفر يا بطل!",
            description="مرحباً بك! اختر اللعبة التي تحبها من القائمة بالأسفل لفتح قناتك الخاصة فوراً.",
            color=0x2ecc71
        )
        await channel.send(content=f"حياك الله {member.mention}", embed=embed, view=RoleView())

# 5. الأوامر (Commands)
@bot.command()
@commands.has_permissions(administrator=True)
async def menu(ctx):
    """أمر لاستدعاء القائمة يدوياً في أي قناة"""
    embed = discord.Embed(
        title="🎮 لوحة اختيار الألعاب",
        description="اختر من القائمة أدناه للحصول على الرتبة وفتح القناة المخصصة لك.",
        color=0x9b59b6
    )
    await ctx.send(embed=embed, view=RoleView())

# تشغيل البوت
bot.run(os.environ.get('TOKEN'))
