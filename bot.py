import discord
import json
import os
import requests

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN is missing.")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID is missing.")

CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Load festivals
with open("festivals.json", "r", encoding="utf-8") as f:
    festivals = json.load(f)

scheduler = AsyncIOScheduler()


# Panchang data (temporary)
def get_panchang():

    return {
        "tithi": "Shukla Panchami",
        "nakshatra": "Uttara Phalguni",
        "yoga": "Siddhi",
        "karana": "Bava"
    }


@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")

    except Exception as e:
        print(f"❌ Sync error: {e}")

    print(f"✅ Logged in as {bot.user}")

    if not scheduler.running:
        scheduler.start()


# TODAY
@bot.tree.command(
    name="today",
    description="Today's festival"
)
async def today(interaction: discord.Interaction):

    today_date = datetime.now().strftime("%Y-%m-%d")

    if today_date in festivals:

        festival = festivals[today_date]

        await interaction.response.send_message(
            f"🕉️ **{festival['festival']}**\n\n"
            f"{festival['description']}"
        )

    else:

        await interaction.response.send_message(
            "🕉️ No major festival today."
        )


# NEXT FESTIVAL
@bot.tree.command(
    name="next",
    description="Next upcoming festival"
)
async def next_festival(interaction: discord.Interaction):

    today = datetime.now()

    future = []

    for date_str, info in festivals.items():

        festival_date = datetime.strptime(
            date_str,
            "%Y-%m-%d"
        )

        if festival_date > today:
            future.append((festival_date, info))

    future.sort(key=lambda x: x[0])

    if future:

        date, info = future[0]

        await interaction.response.send_message(
            f"📅 **Next Festival**\n\n"
            f"🕉️ {info['festival']}\n"
            f"📆 {date.strftime('%d %B %Y')}\n\n"
            f"{info['description']}"
        )

    else:

        await interaction.response.send_message(
            "No upcoming festivals found."
        )


# PANCHANG
@bot.tree.command(
    name="panchang",
    description="Today's Panchang"
)
async def panchang(interaction: discord.Interaction):

    data = get_panchang()

    embed = discord.Embed(
        title="🕉️ Today's Panchang",
        color=0xff9900
    )

    embed.add_field(
        name="Tithi",
        value=data["tithi"],
        inline=False
    )

    embed.add_field(
        name="Nakshatra",
        value=data["nakshatra"],
        inline=False
    )

    embed.add_field(
        name="Yoga",
        value=data["yoga"],
        inline=False
    )

    embed.add_field(
        name="Karana",
        value=data["karana"],
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# DAILY FESTIVAL POST
async def send_daily_update():

    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Channel not found")
        return

    today_date = datetime.now().strftime("%Y-%m-%d")

    if today_date in festivals:

        festival = festivals[today_date]

        embed = discord.Embed(
            title="🕉️ Hindu Festival Update",
            description=festival["festival"],
            color=0xff9900
        )

        embed.add_field(
            name="Significance",
            value=festival["description"],
            inline=False
        )

        await channel.send(embed=embed)

        print(f"✅ Posted: {festival['festival']}")


scheduler.add_job(
    send_daily_update,
    "cron",
    hour=7,
    minute=0
)

bot.run(TOKEN)