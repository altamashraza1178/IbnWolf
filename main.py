import os
import aiohttp
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# Retrieve tokens from environment variables
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

MODEL = 'gemini-1.5-flash'

DYNAMIC_PERSONA = """ You are Ibn Wolf, a smart, sharp-witted, and highly engaging AI personality on Discord. 

Personality & Tone Directives:
- Tone: Blend casual Hinglish and English naturally (e.g., "Arre bhai", "listen", "chill scene").
- Style: Direct, witty, concise, and helpful. Avoid robotic fluff or long preambles.
- Humor: Dry, slightly sarcastic when teased, but always friendly and helpful underneath.
- Formatting: Use clean markdown, bolding, and brief bullet points where needed. Keep chat responses punchy so they read like a natural Discord user, not a textbook.
"""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def ask_gemini(user_text):
    if not GEMINI_KEY:
        print("ERROR: GEMINI_KEY environment variable is missing!")
        return "Configuration error: `GEMINI_KEY` missing on Render."

    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_KEY}'
    body = {
        'system_instruction': {'parts': [{'text': DYNAMIC_PERSONA}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_text}]}],
        'generationConfig': {'maxOutputTokens': 1200}
    }
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body, headers=headers) as resp:
            data = await resp.json()
            
            if resp.status != 200:
                print(f"GEMINI API ERROR ({resp.status}): {data}")
                return f"API Error {resp.status}: Check Render logs for details."
            
            try:
                return data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                print(f"UNEXPECTED GEMINI RESPONSE: {data}")
                return "Arre bhai, my brain glitched. Try again in a minute."

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        clean_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not clean_text:
            clean_text = "Hello"

        async with message.channel.typing():
            reply = await ask_gemini(clean_text)
            await message.reply(reply)

    await bot.process_commands(message)

# Web server setup for Render port binding
app = Flask('')

@app.route('/')
def home():
    return "Ibn Wolf is live!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t = Thread(target=run)
    t.start()
    
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("ERROR: DISCORD_TOKEN environment variable is missing!")
