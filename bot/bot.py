import repackage

repackage.up()

import os

import json

import random

import datetime
import time

import discord
from discord.ext import commands

import genanki

import tempfile

from libs.GoogleDriveManager import GoogleDriveManager
from libs.tools import replace_latex_delimiters, remove_text

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
    print("Discord Bot: Logged in as")
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
async def rev(ctx, num_cards: int, *args: str) -> None:
    with open(f"{config['data_folder_path']}/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    random.shuffle(data)

    selected_cards = []
    tags = []
    backlinks = []
    include_tags = False
    include_backlinks = False

    for arg in args:
        arg = arg.replace("-", " ")
        arg = arg.lower()

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
        if len(args) == 0:
            selected_cards.append(card)

        if (not tags or any(tag in card["tags"] for tag in tags)) and (
            not backlinks
            or any(backlink in card["backlinks"] for backlink in backlinks)
        ):
            if (include_tags and any(tag in card["tags"] for tag in tags)) or (
                include_backlinks
                and any(backlink in card["backlinks"] for backlink in backlinks)
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
    file_name = f"{now.strftime('%Y-%m-%d-%H-%M-%S')}.apkg"

    anki_model = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        file_name,
        fields=[
            {"name": "ContentBefore"},
            {"name": "ContentAfter"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{ContentBefore}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{ContentAfter}}',
            },
        ],
    )

    anki_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), file_name)

    for card in selected_cards:
        my_note = genanki.Note(
            model=anki_model,
            fields=[
                remove_text(replace_latex_delimiters(card["content_before"])),
                remove_text(replace_latex_delimiters(card["content_after"])),
            ],
            tags=card["tags"],
        )

        anki_deck.add_note(my_note)

    anki_package = genanki.Package(anki_deck)

    temp_dir = tempfile.mkdtemp(prefix="anki_export_")

    output_file_path = os.path.join(temp_dir, file_name)

    anki_package.write_to_file(output_file_path)

    with open(output_file_path, "rb") as apkg_file:
        apkg_content = apkg_file.read()

    os.remove(output_file_path)

    os.rmdir(temp_dir)

    google_drive_manager.upload_file(
        parent_folder_id=config["rev_folder_id"],
        file_name=file_name,
        content=apkg_content,
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

    embed.set_footer(text="Made with 💜 by bonsainoodle")

    await ctx.send(embed=embed)


bot.run(config["bot_token"])
