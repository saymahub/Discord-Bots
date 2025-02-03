import discord
import random
import asyncio
import os
import time
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN_tts_bot')
TEXT_FILE = "messages.txt" 
LEAVE_DELAY = 1  
COMMAND_COOLDOWN = 5 

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.messages = True 
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)
last_immediate_time = 0 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(randomly_join_vc())

async def randomly_join_vc():
    """Bot randomly joins a voice channel and speaks a message from a file."""
    await bot.wait_until_ready()

    while True:
        for guild in bot.guilds:
            voice_channels = [vc for vc in guild.voice_channels if len(vc.members) > 0]
            if voice_channels:
                channel = random.choice(voice_channels)
                message = get_random_message()

                await speak_in_vc(channel, message)

        wait_time = random.randint(600, 5400)
        await asyncio.sleep(wait_time)

def get_random_message():
    """Get a random message from messages.txt"""
    try:
        with open(TEXT_FILE, "r") as f:
            lines = f.readlines()
            return random.choice(lines).strip() if lines else "why do you look like that"
    except FileNotFoundError:
        return "why do you look like that"

async def speak_in_vc(channel, message, effect=None):
    """Joins a voice channel, applies voice effects, and speaks the message."""
    try:
        vc = await channel.connect()
        print(f"Saying: {message}")

        os.system(f'gtts-cli "{message}" --output speech.mp3')

        filters = {
            "normal": "",
            "robotic": "asetrate=44100*1.5,atempo=0.7,highpass=f=1000",
            "echo": "aecho=0.8:0.9:1000:0.3",
            "deep": "asetrate=44100*0.8,atempo=1.2",
            "fast": "atempo=1.5",
            "slow": "atempo=0.7"
        }

        filter_cmd = filters.get(effect, "") 
        ffmpeg_cmd = f'ffmpeg -i speech.mp3 -af "{filter_cmd}" -y output.mp3' if filter_cmd else "copy speech.mp3 output.mp3"
        os.system(ffmpeg_cmd)

        vc.play(discord.FFmpegPCMAudio("output.mp3"))

        while vc.is_playing():
            await asyncio.sleep(1)

        await asyncio.sleep(LEAVE_DELAY)
        await vc.disconnect()
    except Exception as e:
        print(f"Error: {e}")

    finally:
        try:
            os.remove("speech.mp3")
            os.remove("output.mp3")
            print("Deleted speech files.")
        except FileNotFoundError:
            print("File already deleted or not found.")
        except Exception as e:
            print(f"Error deleting files: {e}")

@bot.command(name="say")
async def say(ctx, effect: str = None, *, message: str):
    """Allows users to make the bot speak immediately with optional effects."""
    global last_immediate_time

    if time.time() - last_immediate_time < COMMAND_COOLDOWN:
        await ctx.send("❌ Please wait a few seconds before using !say again.")
        return

    if ctx.author.voice and ctx.author.voice.channel:
        if effect and effect.lower() not in ["normal", "robotic", "echo", "deep", "fast", "slow"]:
            await ctx.send("❌ Invalid effect! Choose from: normal, robotic, echo, deep, fast, slow.")
            return

        last_immediate_time = time.time()
        await speak_in_vc(ctx.author.voice.channel, message, effect.lower() if effect else None)
    else:
        await ctx.send("❌ You must be in a voice channel to use this command.")

@bot.command(name="sayhelp")
async def sayhelp(ctx):
    """Displays instructions on how to use the !say command."""
    help_message = """
    **🗣️ How to Use `!say` Command:**
    
    **Basic Usage:**
    `!say [effect] Your message here!`
    
    **Available Effects:**
    🔹 `normal` → no effect
    🔹 `robotic` → Robotic voice
    🔹 `echo` → Adds an echo effect
    🔹 `deep` → Deepens the voice
    🔹 `fast` → Speaks faster
    🔹 `slow` → Speaks slower

    **Examples:**
    `!say normal Hello, world!`
    `!say robotic I am a robot!`
    `!say deep This sounds deeper!`

    🔄 Cooldown for `!say`: **5 seconds**
    """
    await ctx.send(help_message)

bot.run(TOKEN)
