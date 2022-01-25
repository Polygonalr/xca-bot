# Genshin account management discord bot

## Requirements

* Python 3.9

* [genshinstats](https://github.com/thesadru/genshinstats) and [nextcord](https://github.com/nextcord/nextcord) installed in your python env.

## Deployment

* `cp configFile.py.example configFile.py` and `cp cookies.json.example cookies.json`.

* Configure `configFile.py` with your discord bot token and the account id of the discord account of the one running in-charge of the bot. 

* Add your cookies from hoyolab to `cookies.json`.

* Create a `crontab` to run `app.py` everyday to perform daily check in for all the accounts within `cookies.json`.

* `python3.9 discordapp.py` to run the bot.

