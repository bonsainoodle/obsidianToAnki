import repackage

repackage.up()

import json

import random

import datetime
import time

import discord
from discord.ext import commands

from libs.GoogleDriveManager import GoogleDriveManager

with open("config.json", "r") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config["bot_prefix"], intents=intents)

google_drive_manager = GoogleDriveManager(
    credentials_file_path=config["credentials_file_path"],
    data_folder_path=config["data_folder_path"],
)


@bot.event
async def on_ready() -> None:
    print("------")
    print("DiscordBot: Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def ping(ctx) -> None:
    await ctx.send("pong")


@bot.command()
async def update(ctx) -> None:
    google_drive_manager.get_files(folder_id=config["folder_id"])

    embed = discord.Embed(
        title="Database updated",
        color=discord.Color.purple(),
    )

    embed.set_footer(text="Made with 💜 by Bonsaï#8521")

    await ctx.send(embed=embed)


@bot.command()
async def rev(ctx, num_cards: int, *, args: str) -> None:
    with open(f"{config['data_folder_path']}/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    random.shuffle(data)

    selected_cards = []
    tags = []
    backlinks = []
    include_tags = False
    include_backlinks = False

    for arg in args.split():
        if arg.isdigit():
            num_cards = int(arg)
        elif arg.startswith("#"):
            tags.append(arg[1:])
        elif arg.startswith("[["):
            backlinks.append(arg[2:-2])
        elif arg == "include_tags":
            include_tags = True
        elif arg == "include_backlinks":
            include_backlinks = True

    for card in data:
        if (not tags or any(tag in card["tags"] for tag in tags)) and (
            not backlinks
            or any(backlink in card["backlinks"] for backlink in backlinks)
        ):
            if (include_tags and all(tag in card["tags"] for tag in tags)) or (
                include_backlinks
                and all(backlink in card["backlinks"] for backlink in backlinks)
            ):
                selected_cards.append(card)

        if len(selected_cards) >= num_cards:
            break

    if len(selected_cards) == 0:
        embed = discord.Embed(
            title="No card found",
            description="Try to change your parameters",
            color=discord.Color.purple(),
        )

        embed.set_footer(text="Made with 💜 by Bonsaï#8521")

        await ctx.send(embed=embed)

        return

    now = datetime.datetime.now()
    file_name = f"{now.strftime('%Y-%m-%d-%H-%M-%S')}.md"

    content = f"Titre: {file_name} - {len(selected_cards)} cartes\n"

    for card in selected_cards:
        content += f"\n![[{card['name'].split('.')[0]}]]"

    google_drive_manager.upload_text_file(
        parent_folder_id=config["rev_folder_id"], file_name=file_name, content=content
    )

    time.sleep(1)

    file_link = google_drive_manager.get_file_link(
        parent_folder_id=config["rev_folder_id"], file_name=file_name
    )

    embed = discord.Embed(
        title=f"Created a new file with {len(selected_cards)} cards",
        description=f"[{file_name}]({file_link})",
        color=discord.Color.purple(),
    )

    embed.set_footer(text="Made with 💜 by Bonsaï#8521")

    await ctx.send(embed=embed)


bot.run(config["bot_token"])
