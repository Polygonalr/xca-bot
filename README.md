<h1 align="center">
  XCA Bot
</h1>

Yet another Discord bot that mainly offers utility for HoYoverse games.

## Requirements

* Python 3.9

## Deployment

First, install the required pip modules.

```
pip install -r requirements.txt
```

Then, setup your configuration file.

```
cp ./.env.example ./.env
```

| Config Name | Description |
|---|---|
|`DATABASE_FILE`| Filename of the SQLite database. Default is `app.sqlite`|
|`DISCORD_TOKEN`| Secret token of your Discord bot. This can be found in Discord's developers portal > your application > Bot > Token.|
|`OWNER_ID`| Discord User ID of the owner of the bot. This is used for admin commands (which is still in development!). You can find out your Discord account ID by sending a message anywhere mentioning yourself, while adding a backslash `\` in front of your mention (i.e. `\@polygonalr`). Copy out only the numbers from the message (without `@` and angle brackets `<>`).|

Add your cookies from HoYoLab to your SQLite database. You may want to run the `bot/src/database.py` to initialise the database file first. (Note: A more intuitive interface via admin commands is still under development.)

Create a `crontab` to run `bot/src/checkin.py` everyday to perform daily check in for all the accounts within the database. Below is an example `crontab` job with `venv` configured for Python.

```30 4 * * * cd /home/root/xca-bot && ./venv/bin/python3 ./bot/src/checkin.py```

To run the bot Discord,

```
python3.9 bot/src/app.py
```

