<h1 align="center">
  XCA Bot
</h1>

Yet another Discord bot (bundled with an optional Telegram bot) that mainly offers utility for HoYoverse games.

## Requirements

* Python 3.12
* SQLite3

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
|`TELEGRAM_TOKEN`| Secret token of your Telegram bot. For now, the Telegram bot is only used for broadcasting of game redemption codes.|

Add your cookies from HoYoLab to your SQLite database. You may want to run the `bot/src/database.py` to initialise the database file first. Alternatively, you can start adding accounts and cookies using the `$register`, `$add_hoyolab_acc`, `$add_genshin_uid`, `$add_starrail_uid` commands.

Create a `crontab` to run `bot/src/checkin.py` everyday to perform daily check in for all the accounts within the database. Below is an example `crontab` job with `venv` configured for Python.

```bash
30 4 * * * cd /home/root/xca-bot && ./venv/bin/python3 ./bot/src/checkin.py
```

To run the bot,

```
./run.sh
```

