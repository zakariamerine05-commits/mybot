
import discord
from discord.ui import Button, View
import os
import random
import asyncio
import math
import io
import time
import logging
import traceback
from collections import defaultdict, deque
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger('mafia-bot')

COMMAND_COOLDOWN_SECONDS = 3
SPAM_WINDOW_SECONDS = 10
SPAM_MAX_MESSAGES = 8
MAX_MESSAGE_LENGTH = 500
TIMEOUT_DURATION_SECONDS = 300  # 5 دقائق

_last_command_time = defaultdict(float)
_recent_messages = defaultdict(lambda: deque(maxlen=SPAM_MAX_MESSAGES))
_timed_out_users = {}  # user_id -> unblock_timestamp


def is_timed_out(user_id):
    """تحقق إذا كان المستخدم في تايم آوت حالياً"""
    until = _timed_out_users.get(user_id)
    if not until:
        return 0
    remaining = until - time.time()
    if remaining <= 0:
        _timed_out_users.pop(user_id, None)
        return 0
    return remaining


def is_rate_limited(user_id):
    """تحقق من تجاوز المستخدم لحد الأوامر المتسارعة"""
    now = time.time()
    last = _last_command_time.get(user_id, 0)
    if now - last < COMMAND_COOLDOWN_SECONDS:
        return True
    _last_command_time[user_id] = now
    return False


def is_spamming(user_id):
    """تحقق من السبام: عدد رسائل عالٍ في وقت قصير"""
    now = time.time()
    q = _recent_messages[user_id]
    q.append(now)
    if len(q) >= SPAM_MAX_MESSAGES and (now - q[0]) < SPAM_WINDOW_SECONDS:
        return True
    return False

IMAGE_FOLDER = "./images"
VALID_IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

WORD_GAME_DATA = {
    "الجزائر": "دولة عربية في شمال أفريقيا",
    "برشلونة": "نادي كرة قدم إسباني شهير",
    "بايثون": "لغة برمجة قوية وسهلة",
    "البيتزا": "أكلة إيطالية مشهورة عالمياً",
    "المريخ": "الكوكب الأحمر في مجموعتنا الشمسية",
    "الأسد": "حيوان يلقب بملك الغابة",
    "مصر": "بلد الأهرامات ونهر النيل",
    "السعودية": "دولة بها مكة المكرمة والمدينة المنورة",
    "المغرب": "دولة عربية في أقصى شمال غرب أفريقيا",
    "اليابان": "دولة الساموراي وعاصمتها طوكيو",
    "فرنسا": "دولة برج إيفل وعاصمتها باريس",
    "تركيا": "دولة عاصمتها أنقرة وأكبر مدنها إسطنبول",
    "ريال مدريد": "نادي كرة قدم إسباني منافس برشلونة",
    "ليفربول": "نادي كرة قدم إنجليزي شعاره الطائر الأحمر",
    "ميسي": "أسطورة كرة القدم الأرجنتيني رقم 10",
    "رونالدو": "نجم كرة قدم برتغالي رقم 7",
    "صلاح": "نجم كرة قدم مصري يلعب لليفربول",
    "نيمار": "نجم كرة قدم برازيلي",
    "الفيل": "أكبر حيوان بري على وجه الأرض",
    "الزرافة": "حيوان معروف بطول رقبته",
    "النمر": "حيوان مفترس مخطط",
    "الدلفين": "حيوان بحري ذكي ومرح",
    "الصقر": "طائر جارح سريع جداً",
    "البطريق": "طائر لا يطير يعيش في القطب الجنوبي",
    "الشمس": "مصدر الضوء والحرارة في النهار",
    "القمر": "يضيء السماء في الليل",
    "الزهرة": "ألمع كوكب في السماء يعرف بنجمة الصباح",
    "المحيط": "أكبر مسطح مائي على الأرض",
    "إيفرست": "أعلى قمة جبلية في العالم",
    "الصحراء": "منطقة جافة جداً قليلة الأمطار",
    "البرتقال": "فاكهة حمضية لونها كاسمها",
    "التفاح": "فاكهة مشهورة قد تكون حمراء أو خضراء",
    "الموز": "فاكهة صفراء طويلة يحبها القرد",
    "الشاي": "مشروب ساخن شعبي جداً",
    "القهوة": "مشروب منبه يشرب صباحاً غالباً",
    "الخبز": "غذاء أساسي يصنع من القمح",
    "السيارة": "وسيلة نقل بأربع عجلات",
    "الطائرة": "وسيلة نقل تطير في السماء",
    "القطار": "وسيلة نقل تسير على قضبان حديدية",
    "الدراجة": "وسيلة نقل بعجلتين تعمل بالقدم",
    "الهاتف": "جهاز للاتصال والتواصل",
    "الحاسوب": "جهاز إلكتروني للحسابات والبرامج",
    "الإنترنت": "شبكة عالمية تربط الأجهزة",
    "جوجل": "أشهر محرك بحث في العالم",
    "يوتيوب": "أشهر منصة لمشاركة الفيديوهات",
    "ديسكورد": "تطبيق دردشة شهير بين اللاعبين",
    "فيسبوك": "أشهر شبكة تواصل اجتماعي أسسها مارك زوكربيرغ",
    "إنستغرام": "تطبيق لمشاركة الصور والفيديوهات القصيرة",
    "تويتر": "شبكة تواصل اجتماعي شعارها العصفور الأزرق سابقاً",
    "الذهب": "معدن نفيس أصفر اللون",
    "الفضة": "معدن نفيس لونه أبيض لامع",
    "الألماس": "أغلى الأحجار الكريمة وأقساها",
    "الطبيب": "من يعالج المرضى",
    "المعلم": "من يعلم الطلاب في المدرسة",
    "المهندس": "من يصمم المباني والأجهزة",
    "الطيار": "من يقود الطائرات",
    "الشرطي": "من يحفظ الأمن في الشارع",
    "كرة القدم": "اللعبة الأكثر شعبية في العالم",
    "الشطرنج": "لعبة لوحية فيها ملك ووزير وجنود",
    "ماين كرافت": "لعبة فيديو شهيرة بناء بمكعبات",
    "فورتنايت": "لعبة فيديو باتل رويال شهيرة",
    "ببجي": "لعبة باتل رويال شهيرة على الجوال",
    "نتفليكس": "أشهر منصة لمشاهدة الأفلام والمسلسلات",
    "هاري بوتر": "سلسلة أفلام عن ساحر صغير",
    "سبايدر مان": "بطل خارق يطلق الشباك",
    "باتمان": "بطل خارق من مدينة جوثام",
    "ناروتو": "أنمي ياباني شهير عن نينجا",
    "ون بيس": "أنمي شهير عن قراصنة يبحثون عن كنز",
    "كونان": "أنمي عن محقق صغير يحل القضايا",
    "القرآن": "كتاب المسلمين المقدس",
    "رمضان": "شهر الصيام عند المسلمين",
    "الكعبة": "أقدس مكان عند المسلمين في مكة",
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# ══════════════════════════════════════════
#  البيانات
# ══════════════════════════════════════════
games = {}  # channel_id -> game

ROLES = {
    'مافيا':    {'emoji': '🔫', 'color': 0x8B0000, 'desc': 'اقتل مواطناً كل ليلة. لا تُكشف!'},
    'محقق':     {'emoji': '🔍', 'color': 0x2980B9, 'desc': 'اكتشف دور لاعب كل ليلة.'},
    'طبيب':     {'emoji': '💉', 'color': 0x27AE60, 'desc': 'احمِ لاعباً من القتل كل ليلة.'},
    'مواطن':    {'emoji': '👤', 'color': 0xF39C12, 'desc': 'صوّت نهاراً لطرد المافيا.'},
}

def assign_roles(players):
    n = len(players)
    roles = []
    mafia_count = max(1, n // 4)
    roles += ['مافيا'] * mafia_count
    if n >= 5: roles.append('محقق')
    if n >= 7: roles.append('طبيب')
    while len(roles) < n:
        roles.append('مواطن')
    random.shuffle(roles)
    return {p: r for p, r in zip(players, roles)}

def alive_list(game):
    return '\n'.join([f"{'💀' if p not in game['alive'] else '🟢'} {p.display_name}"
                      for p in game['players']])

def check_win(game):
    alive = game['alive']
    mafia = [p for p in alive if game['roles'][p] == 'مافيا']
    town  = [p for p in alive if game['roles'][p] != 'مافيا']
    if len(mafia) == 0:
        return 'town'
    if len(mafia) >= len(town):
        return 'mafia'
    return None

# ══════════════════════════════════════════
#  EMBEDS
# ══════════════════════════════════════════
def lobby_embed(game):
    players_text = '\n'.join([f"• {p.display_name}" for p in game['players']]) or '*لا أحد بعد...*'
    embed = discord.Embed(
        title="🎭 لعبة المافيا",
        description="لعبة الخداع والبقاء! من هو المافيا؟",
        color=0xC9A84C
    )
    embed.add_field(
        name=f"👥 اللاعبون ({len(game['players'])})",
        value=players_text,
        inline=False
    )
    embed.add_field(
        name="📋 الأدوار",
        value="🔫 مافيا | 🔍 محقق | 💉 طبيب | 👤 مواطن",
        inline=False
    )
    embed.add_field(
        name="⚠️ ملاحظة",
        value="يلزم 4 لاعبين على الأقل للبدء",
        inline=False
    )
    embed.set_footer(text="اضغط انضم للمشاركة • المنشئ يضغط ابدأ")
    return embed

def night_embed(game):
    embed = discord.Embed(
        title="🌙 الليل حل على المدينة...",
        description="الجميع نائمون. الأدوار الخاصة تعمل في الخفاء!",
        color=0x2C3E50
    )
    embed.add_field(
        name="👥 الأحياء",
        value='\n'.join([f"🟢 {p.display_name}" for p in game['alive']]),
        inline=True
    )
    embed.add_field(
        name="💀 الموتى",
        value='\n'.join([f"💀 {p.display_name}" for p in game['players'] if p not in game['alive']]) or '*لا أحد*',
        inline=True
    )
    embed.add_field(
        name="📩 تعليمات",
        value="راجع **رسائلك الخاصة** للعب دورك!\nعندك **60 ثانية** ⏰",
        inline=False
    )
    embed.set_footer(text=f"الجولة {game['round']} • الليل")
    return embed

def day_embed(game):
    votes = game.get('votes', {})
    vote_count = {}
    for t in votes.values():
        vote_count[t] = vote_count.get(t, 0) + 1

    players_text = ''
    for p in game['alive']:
        v = vote_count.get(p, 0)
        bar = '🟥' * v + '⬛' * (5 - min(v, 5))
        players_text += f"**{p.display_name}** {bar} ({v})\n"

    embed = discord.Embed(
        title="☀️ النهار بدأ!",
        description="ناقشوا وصوّتوا لطرد المشتبه به!",
        color=0xE67E22
    )
    embed.add_field(
        name="🗳️ الأصوات",
        value=players_text or '*لا أصوات بعد*',
        inline=False
    )
    embed.add_field(
        name="💡 تلميح",
        value="اضغط على اسم اللاعب للتصويت ضده!",
        inline=False
    )
    embed.set_footer(text=f"الجولة {game['round']} • النهار • 90 ثانية ⏰")
    return embed

def role_dm_embed(player, role):
    r = ROLES[role]
    embed = discord.Embed(
        title=f"{r['emoji']} أنت {role}!",
        description=r['desc'],
        color=r['color']
    )
    if role == 'مافيا':
        embed.add_field(name="🎯 هدفك", value="اقضِ على جميع المواطنين!", inline=False)
        embed.add_field(name="📨 الأمر", value="`!اقتل @اسم`  في رسائلي الخاصة", inline=False)
    elif role == 'محقق':
        embed.add_field(name="🎯 هدفك", value="اكشف هوية المافيا وأخبر المواطنين!", inline=False)
        embed.add_field(name="📨 الأمر", value="`!تحقق @اسم`  في رسائلي الخاصة", inline=False)
    elif role == 'طبيب':
        embed.add_field(name="🎯 هدفك", value="احمِ المواطنين من القتل!", inline=False)
        embed.add_field(name="📨 الأمر", value="`!احمِ @اسم`  في رسائلي الخاصة", inline=False)
    else:
        embed.add_field(name="🎯 هدفك", value="اكشف المافيا بالتصويت!", inline=False)
        embed.add_field(name="📨 الأمر", value="صوّت في القناة نهاراً", inline=False)
    embed.set_footer(text="🤫 لا تخبر أحداً بدورك!")
    return embed

def win_embed(winner, game):
    if winner == 'town':
        embed = discord.Embed(
            title="🎉 المدينة انتصرت!",
            description="تم القضاء على المافيا كلها! أحسنتم أيها المواطنون!",
            color=0x27AE60
        )
    else:
        embed = discord.Embed(
            title="💀 المافيا انتصرت!",
            description="المافيا سيطرت على المدينة! لم ينجُ أحد...",
            color=0x8B0000
        )

    reveal = '\n'.join([
        f"{ROLES[game['roles'][p]]['emoji']} **{p.display_name}** — {game['roles'][p]}"
        for p in game['players']
    ])
    embed.add_field(name="🎭 كشف الأدوار", value=reveal, inline=False)
    embed.set_footer(text="شكراً للجميع على اللعب!")
    return embed

# ══════════════════════════════════════════
#  VIEWS (الأزرار)
# ══════════════════════════════════════════
class LobbyView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="✅ انضم", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.channel_id)
        if not game or game['phase'] != 'انتظار':
            await interaction.response.send_message("❌ اللعبة غير متاحة الآن!", ephemeral=True)
            return
        if interaction.user in game['players']:
            await interaction.response.send_message("⚠️ أنت منضم بالفعل!", ephemeral=True)
            return
        if len(game['players']) >= 12:
            await interaction.response.send_message("❌ اللعبة ممتلئة!", ephemeral=True)
            return
        game['players'].append(interaction.user)
        await interaction.response.edit_message(embed=lobby_embed(game), view=self)

    @discord.ui.button(label="🚀 ابدأ اللعبة", style=discord.ButtonStyle.primary)
    async def start(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.channel_id)
        if not game:
            await interaction.response.send_message("❌ لا توجد لعبة!", ephemeral=True)
            return
        if interaction.user != game['host']:
            await interaction.response.send_message("❌ فقط المنشئ يبدأ اللعبة!", ephemeral=True)
            return
        if len(game['players']) < 4:
            await interaction.response.send_message(f"❌ يلزم {4 - len(game['players'])} لاعبين أكثر!", ephemeral=True)
            return

        game['roles'] = assign_roles(game['players'])
        game['alive'] = list(game['players'])
        game['phase'] = 'ليل'

        # أرسل الأدوار خاصة
        failed = []
        for p in game['players']:
            try:
                await p.send(embed=role_dm_embed(p, game['roles'][p]))
            except:
                failed.append(p.display_name)

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🎭 اللعبة بدأت!",
                description="تم إرسال الأدوار في الرسائل الخاصة!\n\nالليل يبدأ الآن...",
                color=0xC9A84C
            ),
            view=None
        )

        if failed:
            await interaction.channel.send(
                f"⚠️ لم أستطع إرسال رسائل خاصة لـ: {', '.join(failed)}\n"
                f"تأكدوا من السماح بالرسائل الخاصة في الإعدادات!"
            )

        await asyncio.sleep(3)
        await start_night(interaction.channel, game)

    @discord.ui.button(label="🚪 اخرج", style=discord.ButtonStyle.secondary)
    async def leave(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.channel_id)
        if not game or interaction.user not in game['players']:
            await interaction.response.send_message("❌ أنت لست في اللعبة!", ephemeral=True)
            return
        game['players'].remove(interaction.user)
        await interaction.response.edit_message(embed=lobby_embed(game), view=self)

    @discord.ui.button(label="❌ إلغاء", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        game = games.get(self.channel_id)
        if not game:
            await interaction.response.send_message("❌ لا توجد لعبة!", ephemeral=True)
            return
        if interaction.user != game['host']:
            await interaction.response.send_message("❌ فقط المنشئ يلغي!", ephemeral=True)
            return
        del games[self.channel_id]
        await interaction.response.edit_message(
            embed=discord.Embed(title="🚫 تم إلغاء اللعبة", color=0x8B0000),
            view=None
        )


class VoteView(View):
    def __init__(self, game, channel):
        super().__init__(timeout=90)
        self.game = game
        self.channel = channel
        # أضف زر لكل لاعب حي
        for player in game['alive']:
            btn = Button(
                label=player.display_name,
                style=discord.ButtonStyle.danger,
                custom_id=f"vote_{player.id}"
            )
            btn.callback = self.make_vote_callback(player)
            self.add_item(btn)

        end_btn = Button(label="⚖️ أعلن النتيجة", style=discord.ButtonStyle.primary, row=4)
        end_btn.callback = self.end_vote
        self.add_item(end_btn)

    def make_vote_callback(self, target):
        async def callback(interaction: discord.Interaction):
            game = self.game
            if interaction.user not in game['alive']:
                await interaction.response.send_message("❌ أنت ميت ولا تستطيع التصويت!", ephemeral=True)
                return
            game['votes'][interaction.user] = target
            await interaction.response.send_message(
                f"✅ صوّتَّ ضد **{target.display_name}**!", ephemeral=True
            )
            await interaction.message.edit(embed=day_embed(game), view=self)
        return callback

    async def end_vote(self, interaction: discord.Interaction):
        self.stop()
        await resolve_day(self.channel, self.game, interaction.message)


RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
WHEEL_ORDER = [0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26]


def _load_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "DejaVuSans-Bold.ttf",
        "Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except: pass
    try:
        return ImageFont.load_default(size=size)
    except:
        return ImageFont.load_default()


def draw_roulette_wheel(winning_number):
    """يرسم عجلة الروليت مع تمييز الرقم الفائز"""
    size = 500
    img = Image.new('RGBA', (size, size), (47, 49, 54, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2
    outer_r = 230
    inner_r = 80

    font = _load_font(18)
    big_font = _load_font(48)

    n = len(WHEEL_ORDER)
    seg_angle = 360 / n

    winning_idx = WHEEL_ORDER.index(winning_number)
    pointer_angle = -90
    rotation = pointer_angle - (winning_idx * seg_angle + seg_angle / 2)

    for i, num in enumerate(WHEEL_ORDER):
        start = i * seg_angle + rotation
        end = start + seg_angle

        if num == 0:
            color = (39, 174, 96, 255)
        elif num in RED_NUMBERS:
            color = (192, 30, 30, 255)
        else:
            color = (20, 20, 20, 255)

        draw.pieslice([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
                      start, end, fill=color, outline=(212, 175, 55, 255), width=1)

        mid_angle = math.radians((start + end) / 2)
        text_r = outer_r - 30
        tx = cx + text_r * math.cos(mid_angle)
        ty = cy + text_r * math.sin(mid_angle)
        text = str(num)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((tx - tw / 2, ty - th / 2), text, fill=(255, 255, 255, 255), font=font)

    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 fill=(212, 175, 55, 255), outline=(80, 60, 20, 255), width=3)

    win_text = str(winning_number)
    bbox = draw.textbbox((0, 0), win_text, font=big_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2 - 4), win_text, fill=(20, 20, 20, 255), font=big_font)

    px, py = cx, cy - outer_r - 10
    draw.polygon([
        (px, py + 35),
        (px - 18, py),
        (px + 18, py),
    ], fill=(255, 215, 0, 255), outline=(0, 0, 0, 255))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


async def spin_roulette(interaction, bet_label, bet_check, multiplier, owner):
    if interaction.user != owner:
        await interaction.response.send_message("❌ هذا الرهان ليس لك! اكتب `!روليت` للعب.", ephemeral=True)
        return

    spin_embed = discord.Embed(
        title="🎰 الروليت تدور...",
        description="🔴 ⚫ 🔴 ⚫ 🔴 ⚫\n*انتظر النتيجة...*",
        color=discord.Color.gold()
    )
    await interaction.response.edit_message(embed=spin_embed, view=None, attachments=[])
    await asyncio.sleep(2)

    result = random.randint(0, 36)
    if result == 0:
        color_name, color_key, color_val = "🟢 أخضر", 'green', 0x27AE60
    elif result in RED_NUMBERS:
        color_name, color_key, color_val = "🔴 أحمر", 'red', 0x8B0000
    else:
        color_name, color_key, color_val = "⚫ أسود", 'black', 0x2C3E50

    won = bet_check(result, color_key)

    wheel_buf = draw_roulette_wheel(result)
    file = discord.File(wheel_buf, filename="wheel.png")

    result_embed = discord.Embed(
        title=f"🎰 النتيجة: {result} {color_name}",
        color=color_val
    )
    result_embed.set_image(url="attachment://wheel.png")
    result_embed.add_field(name="🎯 رهانك", value=f"**{bet_label}**", inline=True)
    result_embed.add_field(name="🎲 خرج", value=f"**{result}** {color_name}", inline=True)
    if won:
        result_embed.add_field(name="🎉 النتيجة", value=f"**فزت!** ربحك ×{multiplier} 🏆", inline=False)
    else:
        result_embed.add_field(name="💔 النتيجة", value="**خسرت!** حظ أوفر المرة الجاية 🍀", inline=False)
    result_embed.set_footer(text=f"اللاعب: {owner.display_name} • اكتب !روليت للعب مرة أخرى")
    await interaction.message.edit(embed=result_embed, attachments=[file])


class RouletteNumberSelect(discord.ui.Select):
    def __init__(self, owner, start, end):
        self.owner = owner
        options = []
        for n in range(start, end + 1):
            if n == 0:
                emoji = "🟢"
            elif n in RED_NUMBERS:
                emoji = "🔴"
            else:
                emoji = "⚫"
            options.append(discord.SelectOption(label=str(n), value=str(n), emoji=emoji))
        super().__init__(placeholder=f"اختر رقماً ({start}-{end})", options=options)

    async def callback(self, interaction: discord.Interaction):
        number = int(self.values[0])
        await spin_roulette(
            interaction,
            f"رقم {number}",
            lambda r, c: r == number,
            35,
            self.owner
        )


class RouletteNumberView(View):
    def __init__(self, owner):
        super().__init__(timeout=120)
        self.owner = owner
        self.add_item(RouletteNumberSelect(owner, 0, 12))
        self.add_item(RouletteNumberSelect(owner, 13, 24))
        self.add_item(RouletteNumberSelect(owner, 25, 36))


class RouletteView(View):
    def __init__(self, owner):
        super().__init__(timeout=120)
        self.owner = owner

    @discord.ui.button(label="أحمر", emoji="🔴", style=discord.ButtonStyle.danger, row=0)
    async def red(self, interaction: discord.Interaction, button: Button):
        await spin_roulette(interaction, "🔴 أحمر", lambda r, c: c == 'red', 2, self.owner)

    @discord.ui.button(label="أسود", emoji="⚫", style=discord.ButtonStyle.secondary, row=0)
    async def black(self, interaction: discord.Interaction, button: Button):
        await spin_roulette(interaction, "⚫ أسود", lambda r, c: c == 'black', 2, self.owner)

    @discord.ui.button(label="زوجي", emoji="2️⃣", style=discord.ButtonStyle.primary, row=1)
    async def even(self, interaction: discord.Interaction, button: Button):
        await spin_roulette(interaction, "2️⃣ زوجي", lambda r, c: r != 0 and r % 2 == 0, 2, self.owner)

    @discord.ui.button(label="فردي", emoji="1️⃣", style=discord.ButtonStyle.primary, row=1)
    async def odd(self, interaction: discord.Interaction, button: Button):
        await spin_roulette(interaction, "1️⃣ فردي", lambda r, c: r % 2 == 1, 2, self.owner)

    @discord.ui.button(label="رقم محدد", emoji="🎲", style=discord.ButtonStyle.success, row=2)
    async def number(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ هذا الرهان ليس لك!", ephemeral=True)
            return
        embed = discord.Embed(
            title="🎲 اختر رقمك",
            description="اضغط على الرقم اللي تراهن عليه (ربح ×35)",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"اللاعب: {self.owner.display_name}")
        await interaction.response.edit_message(embed=embed, view=RouletteNumberView(self.owner))


class NightActionView(View):
    """أزرار اختيار الهدف ليلاً في الرسائل الخاصة"""
    def __init__(self, game, actor, action_type, targets):
        super().__init__(timeout=60)
        self.game = game
        self.actor = actor
        self.action_type = action_type  # 'kill' / 'detect' / 'protect'

        for target in targets:
            btn = Button(
                label=target.display_name,
                style=discord.ButtonStyle.danger if action_type == 'kill'
                      else discord.ButtonStyle.primary if action_type == 'detect'
                      else discord.ButtonStyle.success
            )
            btn.callback = self.make_callback(target)
            self.add_item(btn)

    def make_callback(self, target):
        async def callback(interaction: discord.Interaction):
            if self.actor not in self.game.get('alive', []):
                await interaction.response.send_message("❌ أنت لست ضمن الأحياء!", ephemeral=True)
                return

            if self.action_type == 'kill':
                self.game['night_actions']['kill'] = target
                embed = discord.Embed(
                    title="✅ تم الاختيار",
                    description=f"اخترت **{target.display_name}** ضحيتك الليلة! 🔫",
                    color=0x8B0000
                )
            elif self.action_type == 'protect':
                self.game['night_actions']['protect'] = target
                embed = discord.Embed(
                    title="✅ تم الحماية",
                    description=f"ستحمي **{target.display_name}** الليلة! 💉",
                    color=0x27AE60
                )
            elif self.action_type == 'detect':
                target_role = self.game['roles'][target]
                is_mafia = target_role == 'مافيا'
                embed = discord.Embed(
                    title="🔍 نتيجة التحقيق",
                    description=f"**{target.display_name}** هو {'🔴 **مافيا**!' if is_mafia else '🟢 **بريء**!'}",
                    color=0x8B0000 if is_mafia else 0x27AE60
                )

            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(embed=embed)
        return callback


# ══════════════════════════════════════════
#  منطق اللعبة
# ══════════════════════════════════════════
async def start_night(channel, game):
    game['phase'] = 'ليل'
    game['night_actions'] = {'kill': None, 'protect': None, 'detect': None}
    game['votes'] = {}

    msg = await channel.send(embed=night_embed(game))
    game['night_msg'] = msg

    # أرسل تذكير للأدوار الخاصة
    alive_names = '\n'.join([f"• {p.mention}" for p in game['alive']])

    for p in game['alive']:
        role = game['roles'][p]
        others = [x for x in game['alive'] if x != p]
        others_text = ' '.join([x.mention for x in others])

        if role == 'مافيا':
            try:
                embed = discord.Embed(
                    title="🔫 وقت المافيا!",
                    description="اختر ضحيتك بالضغط على الزر:",
                    color=0x8B0000
                )
                view = NightActionView(game, p, 'kill', others)
                await p.send(embed=embed, view=view)
            except: pass

        elif role == 'محقق':
            try:
                embed = discord.Embed(
                    title="🔍 وقت التحقيق!",
                    description="اختر شخصاً لتعرف دوره بالضغط على الزر:",
                    color=0x2980B9
                )
                view = NightActionView(game, p, 'detect', others)
                await p.send(embed=embed, view=view)
            except: pass

        elif role == 'طبيب':
            try:
                embed = discord.Embed(
                    title="💉 وقت الطبيب!",
                    description="اختر شخصاً لحمايته بالضغط على الزر:",
                    color=0x27AE60
                )
                view = NightActionView(game, p, 'protect', game['alive'])
                await p.send(embed=embed, view=view)
            except: pass

    # عداد تنازلي
    for i in range(60, 0, -10):
        await asyncio.sleep(10)
        if games.get(channel.id) != game: return
        if i <= 20:
            try:
                await channel.send(f"⏰ **{i} ثانية** متبقية في الليل!", delete_after=9)
            except: pass

    await resolve_night(channel, game)


async def resolve_night(channel, game):
    if games.get(channel.id) != game: return

    actions = game.get('night_actions', {})
    killed = actions.get('kill')
    protected = actions.get('protect')

    lines = ["🌅 **الصبح جاء...**\n"]

    if killed:
        if killed == protected:
            lines.append("⚕️ **الطبيب أنقذ شخصاً الليلة!** لم يمت أحد! 🙏")
        else:
            game['alive'].remove(killed)
            role_name = game['roles'][killed]
            lines.append(f"💀 **{killed.display_name}** وُجد ميتاً!")
            lines.append(f"كان دوره: **{role_name}** {ROLES[role_name]['emoji']}")
    else:
        lines.append("😴 ليلة هادئة! لم يمت أحد.")

    embed = discord.Embed(
        title="🌅 انتهى الليل",
        description='\n'.join(lines),
        color=0xE67E22
    )

    w = check_win(game)
    if w:
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await channel.send(embed=win_embed(w, game))
        del games[channel.id]
        return

    await channel.send(embed=embed)
    await asyncio.sleep(3)
    await start_day(channel, game)


async def start_day(channel, game):
    game['phase'] = 'نهار'
    game['votes'] = {}
    game['round'] = game.get('round', 1) + 1

    view = VoteView(game, channel)
    msg = await channel.send(embed=day_embed(game), view=view)

    # انتظر 90 ثانية أو حتى ينتهي التصويت
    await asyncio.sleep(90)
    if view.is_finished(): return
    view.stop()
    await resolve_day(channel, game, msg)


async def resolve_day(channel, game, msg=None):
    if games.get(channel.id) != game: return

    votes = game.get('votes', {})
    vote_count = {}
    for t in votes.values():
        vote_count[t] = vote_count.get(t, 0) + 1

    if msg:
        try: await msg.edit(view=None)
        except: pass

    if not vote_count:
        embed = discord.Embed(
            title="🤝 لم يصوت أحد!",
            description="لم يُطرد أحد. الليل يعود...",
            color=0x7F8C8D
        )
        await channel.send(embed=embed)
    else:
        max_v = max(vote_count.values())
        top = [p for p, v in vote_count.items() if v == max_v]

        if len(top) > 1:
            embed = discord.Embed(
                title="🤝 تعادل في الأصوات!",
                description="لم يُطرد أحد. الليل يعود...",
                color=0x7F8C8D
            )
            await channel.send(embed=embed)
        else:
            ejected = top[0]
            game['alive'].remove(ejected)
            role_name = game['roles'][ejected]
            embed = discord.Embed(
                title="⚖️ قرار المدينة",
                description=f"تم طرد **{ejected.display_name}** بـ **{max_v}** أصوات!\n"
                            f"كان دوره: **{role_name}** {ROLES[role_name]['emoji']}",
                color=0x8B0000
            )
            await channel.send(embed=embed)

            w = check_win(game)
            if w:
                await asyncio.sleep(2)
                await channel.send(embed=win_embed(w, game))
                del games[channel.id]
                return

    await asyncio.sleep(3)
    await start_night(channel, game)


# ══════════════════════════════════════════
#  الأوامر
# ══════════════════════════════════════════
@client.event
async def on_ready():
    log.info(f'✅ بوت المافيا شغال: {client.user} (ID: {client.user.id})')
    print(f'✅ بوت المافيا شغال: {client.user}')


@client.event
async def on_error(event_method, *args, **kwargs):
    log.error(f'خطأ في {event_method}:\n{traceback.format_exc()}')


@client.event
async def on_message(message):
    try:
        if message.author.bot:
            return

        if len(message.content) > MAX_MESSAGE_LENGTH:
            return

        msg = message.content.strip()
        channel = message.channel
        author = message.author

        if not msg.startswith('!') and not isinstance(channel, discord.DMChannel):
            return

        if msg.startswith('!'):
            remaining = is_timed_out(author.id)
            if remaining > 0:
                try:
                    mins = int(remaining // 60)
                    secs = int(remaining % 60)
                    time_str = f"{mins}د {secs}ث" if mins else f"{secs}ث"
                    await channel.send(
                        f"⏳ {author.mention} أنت في تايم آوت! حاول بعد {time_str}.",
                        delete_after=5
                    )
                except: pass
                return

            if is_spamming(author.id):
                _timed_out_users[author.id] = time.time() + TIMEOUT_DURATION_SECONDS
                log.warning(f'⏳ تايم آوت للمستخدم {author} ({author.id}) لمدة {TIMEOUT_DURATION_SECONDS} ثانية')
                try:
                    await channel.send(
                        f"⏳ {author.mention} تايم آوت لمدة 5 دقائق بسبب الإكثار من الأوامر!",
                        delete_after=10
                    )
                except: pass
                return

            if is_rate_limited(author.id):
                try:
                    await channel.send(
                        f"⏱️ {author.mention} تمهّل! انتظر قليلاً قبل الأمر التالي.",
                        delete_after=5
                    )
                except: pass
                return
    except Exception as e:
        log.error(f'خطأ في فحص الأمان: {e}')
        return

    try:
        await _handle_message(message, msg, channel, author)
    except Exception as e:
        log.error(f'خطأ في معالجة الأمر "{msg[:50]}":\n{traceback.format_exc()}')
        try:
            await channel.send("❌ حدث خطأ! حاول مرة أخرى.", delete_after=5)
        except: pass


async def _handle_message(message, msg, channel, author):

    # ── لعبة الروليت ──
    if msg == '!روليت':
        embed = discord.Embed(
            title="🎰 لعبة الروليت",
            description="اختر رهانك بالضغط على أحد الأزرار 👇",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="🎯 الرهانات المتاحة",
            value=(
                "🔴 **أحمر** — ربح ×2\n"
                "⚫ **أسود** — ربح ×2\n"
                "2️⃣ **زوجي** — ربح ×2\n"
                "1️⃣ **فردي** — ربح ×2\n"
                "🎲 **رقم محدد** — ربح ×35"
            ),
            inline=False
        )
        embed.set_footer(text=f"اللاعب: {author.display_name}")
        await channel.send(embed=embed, view=RouletteView(author))
        return

    # ── لعبة خمّن الكلمة (تلميح نصي) ──
    if msg == '!خمن_كلمة':
        word, hint = random.choice(list(WORD_GAME_DATA.items()))

        embed = discord.Embed(
            title="🎮 لـعـبـة خـمـن الـكـلـمـة",
            description="حاول معرفة الكلمة الصحيحة من خلال التلميح!",
            color=discord.Color.blue()
        )
        embed.add_field(name="💡 التلميح:", value=f"**{hint}**", inline=False)
        embed.add_field(name="⏳ الوقت:", value="لديك 20 ثانية فقط!", inline=False)
        embed.set_footer(
            text=f"طلبها: {author.name}",
            icon_url=author.avatar.url if author.avatar else None
        )
        await channel.send(embed=embed)

        def check(m):
            return m.author == author and m.channel == channel

        try:
            response = await client.wait_for('message', check=check, timeout=20.0)
            if response.content.strip() == word:
                success_embed = discord.Embed(
                    title="✅ إجابة صحيحة!",
                    description=f"أحسنت يا {author.mention}، الكلمة هي بالفعل **{word}**",
                    color=discord.Color.green()
                )
                await channel.send(embed=success_embed)
            else:
                fail_embed = discord.Embed(
                    title="❌ للأسف خطأ",
                    description=f"الإجابة الصحيحة كانت: **{word}**\nحاول مرة أخرى!",
                    color=discord.Color.red()
                )
                await channel.send(embed=fail_embed)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهى الوقت",
                description=f"لم يتم الرد في الوقت المحدد. الكلمة كانت: **{word}**",
                color=discord.Color.light_grey()
            )
            await channel.send(embed=timeout_embed)
        return

    # ── لعبة خمّن صاحب الصورة ──
    if msg == '!خمن':
        if not os.path.exists(IMAGE_FOLDER) or not os.listdir(IMAGE_FOLDER):
            await channel.send("❌ عذراً، لا توجد صور في مجلد الألعاب حالياً.")
            return

        all_images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(VALID_IMAGE_EXT)]
        if not all_images:
            await channel.send("❌ لا توجد صور مدعومة (.png, .jpg ..) في المجلد.")
            return

        chosen_image_file = random.choice(all_images)
        image_path = os.path.join(IMAGE_FOLDER, chosen_image_file)
        correct_answer = os.path.splitext(chosen_image_file)[0]

        file = discord.File(image_path, filename="image.png")
        embed = discord.Embed(
            title="🎮 خمن صاحب الصورة!",
            description="لديك 15 ثانية للإجابة، اكتب الاسم في الشات.",
            color=discord.Color.gold()
        )
        embed.set_image(url="attachment://image.png")
        await channel.send(file=file, embed=embed)

        def check(m):
            return m.author == author and m.channel == channel

        try:
            response = await client.wait_for('message', check=check, timeout=15.0)
            if response.content.strip().lower() == correct_answer.lower():
                await channel.send(f"🎉 كفووو! إجابتك صحيحة، إنه **{correct_answer}**!")
            else:
                await channel.send(f"❌ للأسف خطأ.. إنه **{correct_answer}**.")
        except asyncio.TimeoutError:
            await channel.send(f"⏰ انتهى الوقت! صاحب الصورة هو **{correct_answer}**.")
        return

    # ── إنشاء لعبة ──
    if msg == '!مافيا':
        if channel.id in games:
            await channel.send("❌ يوجد لعبة جارية! اكتب `!الغِ` لإلغائها.", delete_after=5)
            return

        games[channel.id] = {
            'host': author,
            'players': [author],
            'phase': 'انتظار',
            'roles': {},
            'alive': [],
            'votes': {},
            'night_actions': {},
            'round': 1,
        }

        view = LobbyView(channel.id)
        await channel.send(embed=lobby_embed(games[channel.id]), view=view)

    # ── إلغاء ──
    elif msg == '!الغِ':
        game = games.get(channel.id)
        if not game:
            await channel.send("❌ لا توجد لعبة!", delete_after=5)
            return
        if author != game['host']:
            await channel.send("❌ فقط المنشئ يلغي!", delete_after=5)
            return
        del games[channel.id]
        embed = discord.Embed(title="🚫 تم إلغاء اللعبة", color=0x8B0000)
        await channel.send(embed=embed)

    # ── أوامر الليل (رسائل خاصة) ──
    elif isinstance(channel, discord.DMChannel):
        player_game = None
        player_channel = None

        for cid, g in games.items():
            if author in g.get('alive', []) and g.get('phase') == 'ليل':
                player_game = g
                player_channel_id = cid
                break

        if not player_game:
            return

        role = player_game['roles'].get(author)

        # المافيا تقتل
        if msg.startswith('!اقتل') and role == 'مافيا':
            if not message.mentions:
                await author.send("❌ اذكر اللاعب! مثال: `!اقتل @اسم`")
                return
            target = message.mentions[0]
            if target not in player_game['alive'] or target == author:
                await author.send("❌ هدف غير صالح!")
                return
            player_game['night_actions']['kill'] = target
            embed = discord.Embed(
                title="✅ تم الاختيار",
                description=f"اخترت **{target.display_name}** ضحيتك الليلة! 🔫",
                color=0x8B0000
            )
            await author.send(embed=embed)

        # المحقق يتحقق
        elif msg.startswith('!تحقق') and role == 'محقق':
            if not message.mentions:
                await author.send("❌ اذكر اللاعب!")
                return
            target = message.mentions[0]
            if target not in player_game['alive'] or target == author:
                await author.send("❌ هدف غير صالح!")
                return
            target_role = player_game['roles'][target]
            is_mafia = target_role == 'مافيا'
            embed = discord.Embed(
                title="🔍 نتيجة التحقيق",
                description=f"**{target.display_name}** هو {'🔴 **مافيا**!' if is_mafia else '🟢 **بريء**!'}",
                color=0x8B0000 if is_mafia else 0x27AE60
            )
            await author.send(embed=embed)

        # الطبيب يحمي
        elif msg.startswith('!احمِ') and role == 'طبيب':
            if not message.mentions:
                await author.send("❌ اذكر اللاعب!")
                return
            target = message.mentions[0]
            if target not in player_game['alive']:
                await author.send("❌ هدف غير صالح!")
                return
            player_game['night_actions']['protect'] = target
            embed = discord.Embed(
                title="✅ تم الحماية",
                description=f"ستحمي **{target.display_name}** الليلة! 💉",
                color=0x27AE60
            )
            await author.send(embed=embed)

        else:
            if role and player_game:
                hints = {
                    'مافيا': '`!اقتل @اسم`',
                    'محقق': '`!تحقق @اسم`',
                    'طبيب': '`!احمِ @اسم`',
                    'مواطن': 'صوّت في القناة نهاراً فقط',
                }
                await author.send(f"💡 أمرك: {hints.get(role, '؟')}")

client.run(os.environ['TOKEN'])
