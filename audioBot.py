import discord
import random
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('TOKEN_audio_bot')

AUDIO_FOLDER = "./audio"
MIN_INTERVAL = 600  
MAX_INTERVAL = 3600 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def get_random_audio():
    audio_files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith(('.mp3', '.wav'))]
    return os.path.join(AUDIO_FOLDER, random.choice(audio_files)) if audio_files else None

async def get_random_active_voice_channel():
    active_channels = [
        vc for guild in bot.guilds for vc in guild.voice_channels
        if any(not member.bot for member in vc.members) 
    ]
    return random.choice(active_channels) if active_channels else None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(voice_channel_watcher())

async def voice_channel_watcher():
    await bot.wait_until_ready()
    wait_time = 0
    while True:
        channel = await get_random_active_voice_channel()
        if channel:
            vc = await channel.connect()
            print(f"Connected to {channel.name}")

            while True:
                if not any(not member.bot for member in vc.channel.members):
                    print("No human members left, disconnecting...")
                    await vc.disconnect()
                    break

                vc.play(discord.FFmpegPCMAudio("silent.mp3"))
                await asyncio.sleep(45) 

                time_elapsed = 0
                time_elapsed += 45

                
                print(f"Timer: {wait_time}")

                if time_elapsed >= wait_time:
                    time_elapsed = 0
                    audio_file = get_random_audio()
                    if audio_file:
                        print(f"Playing: {audio_file}")
                        
                        vc.play(discord.FFmpegPCMAudio(audio_file))
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        wait_time = random.randint(MIN_INTERVAL, MAX_INTERVAL)

        else:
            await asyncio.sleep(60)

bot.run(TOKEN)