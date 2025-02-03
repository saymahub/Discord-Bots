import discord
import random
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv('TOKEN_audio_bot')

AUDIO_FOLDER = "./audio"  
LEAVE_DELAY = 1  

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_random_audio():
    audio_files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith(('.mp3', '.wav'))]
    if not audio_files:
        return None
    return os.path.join(AUDIO_FOLDER, random.choice(audio_files))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await randomly_join_and_play()

async def randomly_join_and_play():
    await bot.wait_until_ready()
    
    while True:
        for guild in bot.guilds:
            voice_channels = [vc for vc in guild.voice_channels if len(vc.members) > 0]
            if voice_channels:
                channel = random.choice(voice_channels)
                audio_file = get_random_audio()

                if audio_file:
                    try:
                        vc = await channel.connect()
                        vc.play(discord.FFmpegPCMAudio(audio_file))
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        await asyncio.sleep(LEAVE_DELAY)
                        await vc.disconnect()
                    except Exception as e:
                        print(f"Error: {e}")
        
        wait_time = random.randint(600, 5400)  
        await asyncio.sleep(wait_time)

bot.run(TOKEN)