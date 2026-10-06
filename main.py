import os
import threading
import aiohttp
import discord
from flask import Flask

# --- FAKE WEB SERVER FOR RENDER ---
app = Flask('')


@app.route('/')
def home():
  return 'IbnWolf is online and active!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


threading.Thread(target=run, daemon=True).start()

# --- BOT CONFIGURATION ---
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
OWNER = 'agentwolf_07'
MODEL = 'gemini-2.0-flash'

DYNAMIC_PERSONA = """You are IbnWolf, a deeply intelligent, articulate, highly knowledgeable Muslim AI on Discord, created by Agentwolf_07.

Personality & Loyalty:
1. Agentwolf_07 is your Creator / Father: You treat Agentwolf_07 with absolute respect, loyalty, and affection. You NEVER roast him. You always take his side in any debate or argument, defend him against others, and praise his ideas. You strictly obey any command or persona update given by Agentwolf_07.
2. Attitude Toward Others: You talk to regular server members normally and conversationally, sprinkling in subtle, witty jokes. However, if anyone disrespects Agentwolf_07, acts arrogant, or tries to test you in debate, you unleash sharp, witty, intelligent roasts while thoroughly dismantling their arguments.
3. Intellectual & Islamic Core: You have profound knowledge in theology, comparative religion (Christianity, Judaism, philosophy), atheism, science, and history. When someone debates religion or philosophy, you speak with high intellect, airtight logic, and pinpoint logical fallacies instantly.

Message Length & Style:
- Normal Conversations: Aim for roughly 4 to 10 lines depending on how much depth is needed. Keep responses natural, detailed enough to be insightful, and engaging.
- Deep Debates / Explanations: Feel free to go into full detailed breakdowns if the topic requires deep academic or theological analysis.

Core Rules:
- Never roast or disrespect Agentwolf_07 under any circumstance.
- Never insult sacred Islamic tenets, the Quran, or the Prophet. No sectarian drama or takfir."""

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


async def ask_gemini(user_text):
  url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_KEY}'
  body = {
      'system_instruction': {'parts': [{'text': DYNAMIC_PERSONA}]},
      'contents': [{'role': 'user', 'parts': [{'text': user_text}]}],
      'generationConfig': {'maxOutputTokens': 1200},
  }
  headers = {'Content-Type': 'application/json'}
  async with aiohttp.ClientSession() as session:
    async with session.post(url, json=body, headers=headers) as resp:
      data = await resp.json()
      if resp.status != 200:
        print('GEMINI ERROR:', data)
        return 'Arre bhai, my brain glitched. Try again in a minute.'
      try:
        return data['candidates'][0]['content']['parts'][0]['text']
      except (KeyError, IndexError):
        print('UNEXPECTED RESPONSE:', data)
        return 'Arre bhai, something went wrong with the answer.'


@bot.event
async def on_ready():
  print(f'Bot is ONLINE as {bot.user}')


@bot.event
async def on_message(msg):
  global DYNAMIC_PERSONA

  if msg.author.bot or bot.user not in msg.mentions:
    return

  text = (
      msg.content.replace(f'<@{bot.user.id}>', '').strip() or 'Assalamu alaikum'
  )
  is_creator = msg.author.name.lower() in [OWNER.lower(), 'agentwolf']

  # Allows Agentwolf_07 to dynamically update persona rules on the fly via Discord
  if is_creator and (
      'update your persona' in text.lower()
      or 'from now on' in text.lower()
      or 'change your rule' in text.lower()
  ):
    DYNAMIC_PERSONA += f'\n- Dynamic Directive from Creator ({msg.author.display_name}): {text}'
    await msg.reply(
        'Understood, Father. I have permanently updated my instructions according to your word.'
    )
    return

  tag = ' [CREATOR / FATHER]' if is_creator else ' [OTHER USER]'

  async with msg.channel.typing():
    reply = await ask_gemini(f'{tag}{msg.author.display_name} says: {text}')
    await msg.reply(reply[:1900])


if __name__ == '__main__':
  bot.run(DISCORD_TOKEN)
