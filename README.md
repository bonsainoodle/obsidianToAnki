# obsidianToAnki

a discord bot that generates Anki decks from your Obsidian notes

## create the discord bot

follow this [tutorial](https://discordpy.readthedocs.io/en/stable/discord.html) to create your discord bot.

then you can either send a message to the bot in dm, or invite it to the discord server of your choice to start interacting with it.

## installation

the bot requires at least python 3.8

```
git clone https://github.com/bonsainoodle/obsidianToAnki
```

then run under the `obsidianToAnki` directory

```
pip install -r requirements.txt
pip install -U git+https://github.com/Rapptz/discord.py
```

in the `obsidianToAnki` directory, you need to create a `config.json` file.

it should look like this:

`config.json` :

```json
{
    "credentials_file_path": "credentials.json",
    "data_folder_path": "data",
    "rev_folder_id": "10A-T7M9oSskKTLTFoF24MpSEIzsxarZU",
    "folder_id": "10A-T7M9oSskKTLTFoF24MpSEIzsxarZU",
    "bot_token": "TOKEN",
    "bot_prefix": "!"
}
```

| Key                   | Description                                                                             | Default | Required |
| --------------------- | --------------------------------------------------------------------------------------- | ------- | -------- |
| credentials_file_path | path to credentials file                                                                | None    | True     |
| data_folder_path      | path to the folder where the Obsidian notes will be downloaded                          | None    | True     |
| rev_folder_id         | google drive id of the folder in which the Anki decks will be stored (last part of url) | None    | True     |
| folder_id             | google drive id of the folder in which the Obsidian notes are stored (last part of url) | None    | True     |
| bot_token             | secret token of the discord bot                                                         | None    | True     |
| bot_prefix            | prefix of the discord bot                                                               | None    | True     |

now you need to create a google service account and download the credentials file.

to do this, follow this [tutorial](https://developers.google.com/workspace/guides/create-credentials?hl=fr#service-account).

make sure to do it with the google account that has access to the google drive folder where your Obsidian notes are stored.

once you have downloaded the credentials file, move it to the `obsidianToAnki` directory.

## run the bot

execute the `start.py` file at the root of the `obsidianToAnki` directory.

```
python start.py
```

## usage

the bot has 2 commands:

-   `!update` : downloads the Obsidian notes from the google drive folder to the `data` folder
-   `!rev` : generates an Anki deck from the Obsidian notes in the `data` folder

each time you modify you Obsidian notes, you need to run the `!update` command before running the `!rev` command.

depending on the number of cards you have, the `!update` command can take a while to execute so wait for the bot to send you a message before sending another command.

the `!rev` command takes the following arguments:

-   the number of cards to generate (required)
-   some backlinks (optional)
-   some tags (optional)
-   whether or not the backlinks should be included in the cards (optional)
-   whether or not the tags should be included in the cards (optional)

Here is an example command:

```
!rev 10 [[Polynomials]] [[Complex-Numbers]] #Series include_tags include_backlinks
```

note that by default `include_tags` and `include_backlinks` are set to `False`.

you can add as many backlinks and tags as you want.

if some backlinks or tags have spaces in them, you need to replace the spaces with `-` when executing the command.

## license

[MIT](https://choosealicense.com/licenses/mit/)
