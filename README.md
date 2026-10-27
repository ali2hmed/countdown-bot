# Countdown Bot ⏳

A Telegram bot that posts live countdowns in English and Arabic.

Send it a date and a message (`31/12 New Year 🎆`, `2h30m Match`) in private, use it in any chat with
`@yourbot 31/12 Party`, or run `/set` in a group.

## Run it

1. Copy `.env.example` to `.env` and fill in your keys.
2. In @BotFather turn on `/setinline` and set `/setinlinefeedback` to 100%.
3. Set up and start the bot:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run.sh
```

Messages are in `texts.py`.

Made by [@ali2hmed](https://t.me/ali2hmed) · [@aliahmedbots](https://t.me/aliahmedbots)

## Credits
- [Countdown Timer Telegram bot by TeLe TiPs](https://github.com/teletips/CountdownTimer-TeLeTiPs)
