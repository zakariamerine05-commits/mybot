@bot.event
async def on_message(message):
    # هذا السطر سيجعل البوت يرد على أي كلمة تكتبها للاختبار
    if message.author == bot.user:
        return
    
    if message.content == "ping":
        await message.channel.send("pong!")

    # ضروري جداً لكي تعمل الأوامر الأخرى مثل !setup
    await bot.process_commands(message)
