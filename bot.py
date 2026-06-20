import discord
import json
import os

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

with open("festivals.json", "r", encoding="utf-8") as f:
    festivals = json.load(f)

scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():

    synced = await bot.tree.sync()

    print(f"Synced {len(synced)} commands")
    print(f"Logged in as {bot.user}")

    if not scheduler.running:
        scheduler.start()


@bot.tree.command(
    name="today",
    description="Today's festival"
)
async def today(interaction: discord.Interaction):

    today_date = datetime.now().strftime("%Y-%m-%d")

    if today_date in festivals:

        festival = festivals[today_date]

        await interaction.response.send_message(
            f"🕉️ {festival['festival']}\n\n{festival['description']}"
        )

    else:

        await interaction.response.send_message(
            "🕉️ No major festival today."
        )


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
            f"📅 Next Festival\n\n"
            f"{info['festival']}\n"
            f"Date: {date.strftime('%d %B %Y')}\n\n"
            f"{info['description']}"
        )

    else:

        await interaction.response.send_message(
            "No upcoming festivals found."
        )


async def send_daily_update():

    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("Channel not found")
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


scheduler.add_job(
    send_daily_update,
    "cron",
    hour=7,
    minute=0
)

bot.run(TOKEN)