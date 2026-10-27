"""Every message the bot sends, in English and Arabic.

To change what the bot says, edit the text here. Words in {braces} are
filled in by the code, so keep them as they are.
"""

LANGS = ("en", "ar")

# Shown before the user has picked a language, so it's in both.
CHOOSE_LANG = "🌐 <b>Please choose your language</b>\n🌐 <b>الرجاء اختيار لغتك</b>"

TEXTS = {
    "en": {
        "welcome": (
            "👋 Hey <b>{name}</b>!\n\n"
            "I'm a <b>countdown bot</b> ⏳\n"
            "I make live countdowns that tick down right inside your chats.\n\n"
            "<b>How it works:</b>\n"
            "Send me a date and a message, like:\n"
            "<code>31/12/2026 New Year 🎆</code>\n"
            "<code>2h30m The match starts ⚽</code>\n\n"
            "Or use me in <b>any chat</b> by typing:\n"
            "<code>@{bot} 31/12 Party 🎉</code>\n\n"
            "In groups, admins can use /set.\n\n"
            "📣 News: @{channel}\n"
            "👨‍💻 Developer: @{developer}"
        ),
        "help": (
            "ℹ️ <b>Help</b>\n\n"
            "<b>1. Pick when it ends</b>\n"
            "• Date: <code>31/12/2026</code> · <code>2026/12/31</code> · <code>31/12</code>\n"
            "• Date and time: <code>31/12 18:30</code>\n"
            "• A time today: <code>21:00</code>\n"
            "• A duration: <code>10m</code> · <code>2h30m</code> · <code>3d</code> · <code>45s</code>\n\n"
            "<b>2. Add your message</b> before or after it (optional)\n"
            "<code>New Year 🎆 31/12</code>\n\n"
            "<b>Where you can use it</b>\n"
            "• <b>Here:</b> just send it to me.\n"
            "• <b>Any chat:</b> type <code>@{bot} 31/12 New Year</code> and tap the result.\n"
            "• <b>Groups:</b> add me, then an admin sends <code>/set 31/12 New Year</code>.\n\n"
            "<b>Stopping</b>\n"
            "Tap ⏹ under the countdown, or send /stop in the chat.\n\n"
            "🕒 Times are in {tz}."
        ),
        "set_usage": (
            "⏳ <b>Start a countdown</b>\n\n"
            "<code>/set 31/12 New Year 🎆</code>\n"
            "<code>/set 10m Break is over</code>\n\n"
            "See /help for all the formats."
        ),
        "bad_format": (
            "🤔 I couldn't understand the time.\n\n"
            "Try <code>31/12/2026 New Year</code> or <code>10m Break</code>.\n"
            "See /help for all the formats."
        ),
        "past": "⌛ That time has already passed. Pick a time in the future.",
        "range": "📏 A countdown can be from 5 seconds up to 10 years.",
        "limit": "✋ You already have {max} countdowns running. Stop one first.",
        "admins_only": "👮 Only group admins can do this here.",
        "stopped_n": "⏹ Stopped {n} countdown(s).",
        "none_running": "There are no countdowns running in this chat.",
        "not_yours": "Only the person who started this countdown or a group admin can stop it.",
        "already_over": "This countdown is already over.",
        "lang_set": "✅ Language set to English",
        "unit_d": "days",
        "unit_h": "hrs",
        "unit_m": "min",
        "unit_s": "sec",
        "done": "🎉 <b>Time's up!</b>",
        "done_notify": "⏰ <b>Time's up!</b>",
        "stopped": "⏹ <i>Countdown stopped</i>",
        "inline_how": "📖 How to use",
        "inline_bad": "🤔 Type a date, e.g. 31/12 New Year",
        "inline_untitled": "⏳ Countdown",
        "inline_desc": "Ends {date} · tap to send",
        "btn_inline": "⏳ Countdown in any chat",
        "btn_group": "➕ Add me to a group",
        "btn_help": "❓ Help",
        "btn_lang": "🌐 Language",
        "btn_channel": "📣 Channel",
        "btn_dev": "👨‍💻 Developer",
        "btn_back": "⬅️ Back",
        "btn_stop": "⏹ Stop",
        "cmd_start": "Main menu",
        "cmd_help": "How to use countdowns",
        "cmd_lang": "Change your language",
        "cmd_set": "Start a countdown",
        "cmd_stop": "Stop countdowns in this chat",
        "bot_about": "Live countdowns to your events, in any chat. By @{channel}",
        "bot_description": (
            "⏳ Live countdowns for your important events.\n\n"
            "Send a date and a message, and I'll keep the countdown ticking right in your chat, "
            "group or channel.\n\n"
            "📣 News: @{channel}\n"
            "👨‍💻 Developer: @{developer}"
        ),
    },
    "ar": {
        "welcome": (
            "👋 أهلاً <b>{name}</b>!\n\n"
            "أنا <b>بوت العد التنازلي</b> ⏳\n"
            "أصنع لك عدّاداً حيّاً يتحدّث تلقائياً داخل محادثاتك.\n\n"
            "<b>طريقة الاستخدام:</b>\n"
            "أرسل لي تاريخاً ورسالة، مثل:\n"
            "<code>31/12/2026 رأس السنة 🎆</code>\n"
            "<code>2h30m تبدأ المباراة ⚽</code>\n\n"
            "أو استخدمني في <b>أي محادثة</b> بكتابة:\n"
            "<code>@{bot} 31/12 حفلة 🎉</code>\n\n"
            "وفي المجموعات يستطيع المشرفون استخدام /set\n\n"
            "📣 الأخبار: @{channel}\n"
            "👨‍💻 المطوّر: @{developer}"
        ),
        "help": (
            "ℹ️ <b>المساعدة</b>\n\n"
            "<b>1. اختر موعد الانتهاء</b>\n"
            "• تاريخ: <code>31/12/2026</code> · <code>2026/12/31</code> · <code>31/12</code>\n"
            "• تاريخ ووقت: <code>31/12 18:30</code>\n"
            "• وقت اليوم: <code>21:00</code>\n"
            "• مدة: <code>10د</code> · <code>2س30د</code> · <code>3ي</code> · <code>45ث</code>\n"
            "  (أو بالإنجليزية: <code>10m</code> · <code>2h30m</code> · <code>3d</code> · <code>45s</code>)\n\n"
            "<b>2. اكتب رسالتك</b> قبله أو بعده (اختياري)\n"
            "<code>رأس السنة 🎆 31/12</code>\n\n"
            "<b>أين تستخدمه</b>\n"
            "• <b>هنا:</b> أرسله لي مباشرة.\n"
            "• <b>أي محادثة:</b> اكتب <code>@{bot} 31/12 رأس السنة</code> ثم اضغط على النتيجة.\n"
            "• <b>المجموعات:</b> أضفني، ثم يرسل أحد المشرفين <code>/set 31/12 رأس السنة</code>\n\n"
            "<b>الإيقاف</b>\n"
            "اضغط ⏹ تحت العدّاد، أو أرسل /stop في المحادثة.\n\n"
            "🕒 الأوقات بتوقيت {tz}."
        ),
        "set_usage": (
            "⏳ <b>ابدأ عدّاً تنازلياً</b>\n\n"
            "<code>/set 31/12 رأس السنة 🎆</code>\n"
            "<code>/set 10د انتهت الاستراحة</code>\n\n"
            "أرسل /help لمعرفة كل الصيغ."
        ),
        "bad_format": (
            "🤔 لم أفهم الوقت.\n\n"
            "جرّب <code>31/12/2026 رأس السنة</code> أو <code>10د استراحة</code>\n"
            "أرسل /help لمعرفة كل الصيغ."
        ),
        "past": "⌛ هذا الوقت مضى بالفعل. اختر وقتاً في المستقبل.",
        "range": "📏 مدة العد التنازلي من 5 ثوانٍ إلى 10 سنوات.",
        "limit": "✋ لديك {max} عدّادات تعمل حالياً. أوقف أحدها أولاً.",
        "admins_only": "👮 هذا الأمر للمشرفين فقط هنا.",
        "stopped_n": "⏹ تم إيقاف {n} عدّاد.",
        "none_running": "لا توجد عدّادات تعمل في هذه المحادثة.",
        "not_yours": "فقط من بدأ هذا العدّاد أو مشرف المجموعة يستطيع إيقافه.",
        "already_over": "هذا العدّاد انتهى بالفعل.",
        "lang_set": "✅ تم اختيار اللغة العربية",
        "unit_d": "يوم",
        "unit_h": "ساعة",
        "unit_m": "دقيقة",
        "unit_s": "ثانية",
        "done": "🎉 <b>انتهى الوقت!</b>",
        "done_notify": "⏰ <b>انتهى الوقت!</b>",
        "stopped": "⏹ <i>تم إيقاف العدّاد</i>",
        "inline_how": "📖 طريقة الاستخدام",
        "inline_bad": "🤔 اكتب تاريخاً، مثل 31/12 رأس السنة",
        "inline_untitled": "⏳ عدّ تنازلي",
        "inline_desc": "ينتهي {date} · اضغط للإرسال",
        "btn_inline": "⏳ عدّاد في أي محادثة",
        "btn_group": "➕ أضفني إلى مجموعة",
        "btn_help": "❓ المساعدة",
        "btn_lang": "🌐 اللغة",
        "btn_channel": "📣 القناة",
        "btn_dev": "👨‍💻 المطوّر",
        "btn_back": "⬅️ رجوع",
        "btn_stop": "⏹ إيقاف",
        "cmd_start": "القائمة الرئيسية",
        "cmd_help": "طريقة استخدام العدّاد",
        "cmd_lang": "تغيير اللغة",
        "cmd_set": "ابدأ عدّاً تنازلياً",
        "cmd_stop": "أوقف العدّادات في هذه المحادثة",
        "bot_about": "عدّ تنازلي حيّ لمناسباتك في أي محادثة. من @{channel}",
        "bot_description": (
            "⏳ عدّ تنازلي حيّ لمناسباتك المهمة.\n\n"
            "أرسل تاريخاً ورسالة، وسأبقي العدّاد يتحدّث داخل محادثتك أو مجموعتك أو قناتك.\n\n"
            "📣 الأخبار: @{channel}\n"
            "👨‍💻 المطوّر: @{developer}"
        ),
    },
}


def t(lang, key, **values):
    text = TEXTS.get(lang, TEXTS["en"])[key]
    return text.format(**values) if values else text
