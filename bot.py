import asyncio
import html
import logging
import os
import secrets
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.errors import FloodWait, MessageNotModified, RPCError
from pyrogram.raw.functions.bots import SetBotInfo
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    LinkPreviewOptions,
    ReplyParameters,
)

import countdown
from countdown import ParseError
from db import DB, Countdown
from texts import CHOOSE_LANG, LANGS, t

CHANNEL = "aliahmedbots"
DEVELOPER = "ali2hmed"
MAX_ACTIVE = 10  # running countdowns per person
TZ = ZoneInfo(os.environ.get("TIMEZONE", "Asia/Baghdad"))
FOOTER = os.environ.get("FOOTER_MESSAGE", "")
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)
DATA_DIR = os.environ.get("DATA_DIR", ".")  # where bot.db and the login session live

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
log = logging.getLogger("bot")

bot = Client(
    "countdown-bot",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"],
    parse_mode=ParseMode.HTML,
    workdir=DATA_DIR,
)
db = DB(os.path.join(DATA_DIR, "bot.db"))
active: dict[str, Countdown] = {}


# ---------- helpers ----------

def user_lang(user):
    """The language the user picked, or a guess from their Telegram app language."""
    if user is None:
        return "en"
    return db.get_lang(user.id) or ("ar" if (user.language_code or "").startswith("ar") else "en")


def tz_name():
    return f"{TZ.key.split('/')[-1].replace('_', ' ')} (UTC{datetime.now(TZ).strftime('%:z')})"


def welcome_text(lang, user):
    return t(lang, "welcome", name=html.escape(user.first_name or ""),
             bot=bot.me.username, channel=CHANNEL, developer=DEVELOPER)


def help_text(lang):
    return t(lang, "help", bot=bot.me.username, tz=tz_name())


def main_menu(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_inline"), switch_inline_query="")],
        [InlineKeyboardButton(t(lang, "btn_group"), url=f"https://t.me/{bot.me.username}?startgroup=true")],
        [InlineKeyboardButton(t(lang, "btn_help"), callback_data="help"),
         InlineKeyboardButton(t(lang, "btn_lang"), callback_data="lang")],
        [InlineKeyboardButton(t(lang, "btn_channel"), url=f"https://t.me/{CHANNEL}"),
         InlineKeyboardButton(t(lang, "btn_dev"), url=f"https://t.me/{DEVELOPER}")],
    ])


def lang_menu():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
        InlineKeyboardButton("🇮🇶 العربية", callback_data="lang:ar"),
    ]])


def back_menu(lang):
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang, "btn_back"), callback_data="home")]])


def stop_menu(lang, cd_id):
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang, "btn_stop"), callback_data=f"stop:{cd_id}")]])


async def is_admin(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except RPCError:
        return False
    return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)


async def can_manage(message):
    """Anyone in a private chat; only admins in groups."""
    if message.chat.type == ChatType.PRIVATE:
        return True
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True  # an anonymous admin
    return bool(message.from_user) and await is_admin(message.chat.id, message.from_user.id)


def owner_of(message):
    return message.from_user.id if message.from_user else message.chat.id


def running_for(owner_id):
    return sum(1 for cd in active.values() if cd.owner_id == owner_id)


# ---------- the live countdown ----------

def render(cd, now):
    return countdown.render(cd.lang, cd.title, cd.start, cd.end, now, TZ, FOOTER)


def register(cd):
    active[cd.id] = cd
    db.add(cd)


def unregister(cd):
    active.pop(cd.id, None)
    db.remove(cd.id)


async def edit(cd, text, markup):
    if cd.inline_id:
        await bot.edit_inline_text(cd.inline_id, text, reply_markup=markup, link_preview_options=NO_PREVIEW)
    else:
        await bot.edit_message_text(cd.chat_id, cd.message_id, text, reply_markup=markup,
                                    link_preview_options=NO_PREVIEW)


async def tick(cd, now):
    if now >= cd.end:
        unregister(cd)
        asyncio.create_task(finish(cd))
        return
    cd.next_edit = min(now + countdown.update_every(cd.end - now), cd.end)
    text = render(cd, now)
    if text == cd.last_text:
        return
    try:
        await edit(cd, text, stop_menu(cd.lang, cd.id))
        cd.last_text, cd.fails = text, 0
    except MessageNotModified:
        cd.last_text = text
    except FloodWait as e:
        cd.next_edit = now + e.value
    except RPCError as e:
        cd.fails += 1
        log.warning("Couldn't update countdown %s (%s): %s", cd.id, cd.fails, e)
        if cd.fails >= 5:  # message deleted or bot removed from the chat
            unregister(cd)


async def finish(cd):
    log.info("Countdown %s finished", cd.id)
    for _ in range(3):
        try:
            await edit(cd, countdown.render_done(cd.lang, cd.title, cd.end, TZ, FOOTER), None)
            if cd.chat_id:
                # Edits don't notify anyone, so send a new message too.
                note = t(cd.lang, "done_notify")
                if cd.title:
                    note += f"\n{html.escape(cd.title)}"
                await bot.send_message(cd.chat_id, note, reply_parameters=ReplyParameters(message_id=cd.message_id))
            return
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except RPCError as e:
            log.warning("Couldn't finish countdown %s: %s", cd.id, e)
            return


async def stop(cd):
    unregister(cd)
    try:
        await edit(cd, countdown.render_stopped(cd.lang, cd.title, cd.end, TZ, FOOTER), None)
    except RPCError as e:
        log.warning("Couldn't mark countdown %s as stopped: %s", cd.id, e)


async def ticker():
    while True:
        now = time.time()
        for cd in list(active.values()):
            if now >= cd.next_edit:
                try:
                    await tick(cd, now)
                except Exception:
                    log.exception("Countdown %s crashed", cd.id)
        await asyncio.sleep(1)


async def start_countdown(message, text, lang):
    owner = owner_of(message)
    if running_for(owner) >= MAX_ACTIVE:
        return await message.reply(t(lang, "limit", max=MAX_ACTIVE))
    now = datetime.now(TZ)
    try:
        end, title = countdown.parse(text, now)
    except ParseError as e:
        return await message.reply(t(lang, e.args[0]))

    cd = Countdown(id=secrets.token_hex(6), owner_id=owner, lang=lang, title=title,
                   start=now.timestamp(), end=end.timestamp(), chat_id=message.chat.id)
    cd.last_text = render(cd, time.time())
    sent = await message.reply(cd.last_text, reply_markup=stop_menu(lang, cd.id), link_preview_options=NO_PREVIEW)
    cd.message_id = sent.id
    cd.next_edit = time.time() + countdown.update_every(cd.end - time.time())
    register(cd)
    log.info("Started countdown %s in chat %s", cd.id, cd.chat_id)


# ---------- commands ----------

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message):
    lang = user_lang(message.from_user)
    if len(message.command) > 1 and message.command[1] == "help":
        return await message.reply(help_text(lang), reply_markup=back_menu(lang), link_preview_options=NO_PREVIEW)
    if db.get_lang(message.from_user.id) is None:
        return await message.reply(CHOOSE_LANG, reply_markup=lang_menu())
    await message.reply(welcome_text(lang, message.from_user), reply_markup=main_menu(lang),
                        link_preview_options=NO_PREVIEW)


@bot.on_message(filters.command("help"))
async def help_cmd(_, message):
    lang = user_lang(message.from_user)
    markup = back_menu(lang) if message.chat.type == ChatType.PRIVATE else None
    await message.reply(help_text(lang), reply_markup=markup, link_preview_options=NO_PREVIEW)


@bot.on_message(filters.command("lang"))
async def lang_cmd(_, message):
    await message.reply(CHOOSE_LANG, reply_markup=lang_menu())


@bot.on_message(filters.command("set"))
async def set_cmd(_, message):
    lang = user_lang(message.from_user)
    args = (message.text or message.caption or "").split(None, 1)
    if len(args) < 2:
        return await message.reply(t(lang, "set_usage"))
    if not await can_manage(message):
        return await message.reply(t(lang, "admins_only"))
    await start_countdown(message, args[1], lang)


@bot.on_message(filters.command("stop"))
async def stop_cmd(_, message):
    lang = user_lang(message.from_user)
    if not await can_manage(message):
        return await message.reply(t(lang, "admins_only"))
    here = [cd for cd in active.values() if cd.chat_id == message.chat.id]
    for cd in here:
        await stop(cd)
    await message.reply(t(lang, "stopped_n", n=len(here)) if here else t(lang, "none_running"))


# In private chat, any plain text is treated as a new countdown.
@bot.on_message(filters.private & filters.text & ~filters.via_bot & ~filters.regex(r"^/"))
async def private_text(_, message):
    await start_countdown(message, message.text, user_lang(message.from_user))


# ---------- buttons ----------

@bot.on_callback_query()
async def buttons(_, query):
    data = query.data or ""
    lang = user_lang(query.from_user)

    if data.startswith("stop:"):
        cd = active.get(data.split(":", 1)[1])
        if cd is None:
            return await query.answer(t(lang, "already_over"))
        allowed = query.from_user.id == cd.owner_id
        if not allowed and cd.chat_id and cd.chat_id < 0:
            allowed = await is_admin(cd.chat_id, query.from_user.id)
        if not allowed:
            return await query.answer(t(lang, "not_yours"), show_alert=True)
        await stop(cd)
        return await query.answer()

    toast = None
    if data.startswith("lang:"):
        lang = data.split(":", 1)[1]
        if lang not in LANGS:
            return await query.answer()
        db.set_lang(query.from_user.id, lang)
        toast = t(lang, "lang_set")
        if query.message.chat.type == ChatType.PRIVATE:
            text, markup = welcome_text(lang, query.from_user), main_menu(lang)
        else:
            text, markup = toast, None
    elif data == "lang":
        text, markup = CHOOSE_LANG, lang_menu()
    elif data == "help":
        text, markup = help_text(lang), back_menu(lang)
    elif data == "home":
        text, markup = welcome_text(lang, query.from_user), main_menu(lang)
    else:
        return await query.answer()

    try:
        await query.edit_message_text(text, reply_markup=markup, link_preview_options=NO_PREVIEW)
    except MessageNotModified:
        pass
    await query.answer(toast)


# ---------- inline mode: @bot 31/12 New Year ----------

@bot.on_inline_query()
async def inline_query(_, query):
    lang = user_lang(query.from_user)
    if not query.query.strip():
        return await query.answer([], cache_time=0, is_personal=True,
                                  switch_pm_text=t(lang, "inline_how"), switch_pm_parameter="help")
    now = datetime.now(TZ)
    try:
        end, title = countdown.parse(query.query, now)
    except ParseError:
        return await query.answer([], cache_time=0, is_personal=True,
                                  switch_pm_text=t(lang, "inline_bad"), switch_pm_parameter="help")

    cd_id = secrets.token_hex(6)
    preview = countdown.render(lang, title, now.timestamp(), end.timestamp(), now.timestamp(), TZ, FOOTER)
    result = InlineQueryResultArticle(
        id=cd_id,
        title=title or t(lang, "inline_untitled"),
        description=t(lang, "inline_desc", date=countdown.fmt_date(end.timestamp(), TZ)),
        input_message_content=InputTextMessageContent(preview, parse_mode=ParseMode.HTML,
                                                      link_preview_options=NO_PREVIEW),
        # The button is also what makes Telegram give us an id to edit the message later.
        reply_markup=stop_menu(lang, cd_id),
    )
    await query.answer([result], cache_time=0, is_personal=True)


@bot.on_chosen_inline_result()
async def inline_chosen(_, result):
    if not result.inline_message_id:
        return
    lang = user_lang(result.from_user)
    now = datetime.now(TZ)
    try:
        end, title = countdown.parse(result.query, now)
    except ParseError:
        return
    cd = Countdown(id=result.result_id, owner_id=result.from_user.id, lang=lang, title=title,
                   start=now.timestamp(), end=end.timestamp(), inline_id=result.inline_message_id)
    if running_for(cd.owner_id) >= MAX_ACTIVE:
        try:
            await edit(cd, t(lang, "limit", max=MAX_ACTIVE), None)
        except RPCError:
            pass
        return
    register(cd)
    log.info("Started inline countdown %s", cd.id)


# ---------- startup ----------

async def setup_profile():
    """Command menus and the 'What can this bot do?' text, in both languages."""
    for lang in LANGS:
        code = "" if lang == "en" else lang
        private = [BotCommand(c, t(lang, f"cmd_{c}")) for c in ("start", "help", "lang", "stop")]
        groups = [BotCommand(c, t(lang, f"cmd_{c}")) for c in ("set", "stop", "help", "lang")]
        await bot.set_bot_commands(private, scope=BotCommandScopeAllPrivateChats(), language_code=code)
        await bot.set_bot_commands(groups, scope=BotCommandScopeAllGroupChats(), language_code=code)
        await bot.invoke(SetBotInfo(
            lang_code=code,
            about=t(lang, "bot_about", channel=CHANNEL),
            description=t(lang, "bot_description", channel=CHANNEL, developer=DEVELOPER),
        ))


async def main():
    await bot.start()
    for cd in db.load():
        active[cd.id] = cd
    try:
        await setup_profile()
    except RPCError as e:
        log.warning("Couldn't set up the bot profile: %s", e)
    task = asyncio.create_task(ticker())
    log.info("@%s is running with %d countdown(s)", bot.me.username, len(active))
    await idle()
    task.cancel()
    await bot.stop()


bot.loop.run_until_complete(main())
