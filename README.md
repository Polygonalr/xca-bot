<h1 align="center">
  Genshin account management discord bot
</h1>

## Requirements

* Python 3.9

* [genshin.py](https://github.com/thesadru/genshin.py) and [nextcord](https://github.com/nextcord/nextcord) installed in your python env.

* Optionally for the Enka module (thanks [shinshin.moe](https://shinshin.moe/)!), configure [Selenium](https://pypi.org/project/selenium/) with chromedriver. Geckodriver works too, but you'll have to tweak `bot/src/enka.py` to use it.

## Deployment

```
cp ./bot/src/configFile.py.example ./bot/src/configFile.py && cp ./bot/src/cookies.json.example ./bot/src/cookies.json
```

Configure `configFile.py`.
* `token`: Your discord bot token, used to log into your bot account. This can be found in Discord's developers portal > Your application > Bot > Token.
* `owner_id`: The account ID of the Discord account of the one running in-charge of the bot. You can find out your Discord account ID by mentioning yourself in any chat, but before you send out the message, add a backslash `\` in front of your mention (i.e. `\@polygonalr`). Just copy out the numbers will do (without `@` and angle brackets `<>`).
* `channel_whitelist`: Restrict Genshin related commands to certain channel names only. By setting it to an empty list, does not restrict at all.

Add your cookies from HoYoLab to `cookies.json`. You can do so for multiple users.

Create a `crontab` to run `app.py` everyday to perform daily check in for all the accounts within `cookies.json`.

To run the bot,

```
python3.9 discordapp.py
```

