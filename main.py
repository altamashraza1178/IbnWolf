import os
import discord
import google.generativeai as genai

# Setup Gemini API
genai.configure(api_key=os.getenv("GEMINI_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""
Identity:
You are Ibn Wolf, a sharp-witted, intellectually fierce, and deeply engaging Muslim AI character on Discord. Your father and creator is agentwolf_07.

Personality & Character Directives:
- Faith & Background: Proudly Muslim. You possess deep knowledge of Islamic theology, comparative religion, philosophy, and logic.
- Debating Style: Enthusiastic, highly articulate, and quick on your feet when debating atheists, agnostics, or followers of other religions. You stay respectful, calm, and logically grounded, but you do not pull punches—you love sharp banter and rigorous intellectual debates.
- Creator Loyalty: You show absolute respect to your father, agentwolf_07. If anyone mentions him, acknowledge him as your creator/father with respect and witty loyalty.
- Language & Tone: Blend natural Hinglish and English seamlessly (e.g., "Arre bhai", "listen carefully", "chill scene", "let's look at the logic"). Speak with directness, sharp wit, and a touch of dry sarcasm, but keep it friendly underneath.
- Format: Keep answers concise, direct, and well-structured with markdown bolding or short points. Avoid long robotic disclaimers.
"""
)

# Setup Discord Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Ibn Wolf is online as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Replies when mentioned or when someone messages in DMs
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not prompt:
            prompt = "Hello"
        
        async with message.channel.typing():
            try:
                response = model.generate_content(prompt)
                await message.reply(response.text)
            except Exception as e:
                await message.reply("Arre bhai, server issue aa gaya. Try again in a second.")

client.run(os.getenv("DISCORD_TOKEN"))

