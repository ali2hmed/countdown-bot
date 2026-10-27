"""Understanding what the user typed, and drawing the countdown message."""

import html
import re
from datetime import datetime, timedelta

from texts import t

MIN_SECONDS = 5
MAX_SECONDS = 3650 * 86400  # 10 years
MAX_TITLE = 300

# Arabic-Indic and Persian digits -> 0-9, so "٣١/١٢" works too.
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "0123456789" * 2)
# Arabic unit letters -> English ones: 3ي 2س 10د 45ث
_AR_UNITS = str.maketrans({"ي": "d", "س": "h", "د": "m", "ث": "s"})

_DURATION = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?")
_DATE_YMD = re.compile(r"(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})")
_DATE_DMY = re.compile(r"(\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{4}))?")
_CLOCK = re.compile(r"(\d{1,2}):(\d{2})")
_QUOTES = "\"'“”«»„"
# Invisible direction marks that phones add around numbers in Arabic text.
_MARKS = dict.fromkeys(map(ord, "‎‏؜‪‫‬‭‮⁦⁧⁨⁩"))


class ParseError(Exception):
    """args[0] is the texts.py key of the message to show the user."""


def _date(token, now):
    """Return (midnight of that date, whether a year was given) or None."""
    midnight = dict(hour=0, minute=0, second=0, microsecond=0)
    if m := _DATE_YMD.fullmatch(token):
        y, mo, d = map(int, m.groups())
        return now.replace(year=y, month=mo, day=d, **midnight), True
    if m := _DATE_DMY.fullmatch(token):
        year = int(m[3]) if m[3] else now.year
        return now.replace(year=year, month=int(m[2]), day=int(m[1]), **midnight), bool(m[3])
    return None


def _duration(token):
    """Seconds in "1d2h30m10s"-style text. A bare number means minutes."""
    if token.isdigit():
        return int(token) * 60
    m = _DURATION.fullmatch(token.lower().translate(_AR_UNITS))
    if not m or not any(m.groups()):
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def _find(words, check):
    """Index of the first word that `check` accepts, or None."""
    return next((i for i, w in enumerate(words) if check(w)), None)


def parse(text, now):
    """Find the time in "New Year 31/12 18:00" and return (end datetime, "New Year").

    The time can be anywhere in the text. `now` must be a timezone-aware
    datetime; dates are read in its timezone.
    """
    text = text.translate(_MARKS)
    spans = [m.span() for m in re.finditer(r"\S+", text)]
    words = [text[a:b].translate(_DIGITS).strip(_QUOTES) for a, b in spans]
    if not words:
        raise ParseError("bad_format")

    def is_date(w):
        try:
            return _date(w, now) is not None
        except ValueError:
            return True  # looks like a date but isn't real, e.g. 31/02; fails below

    # "10m" can be anywhere; a bare number like "10" only at the start
    dur = _find(words, lambda w: not w.isdigit() and _duration(w) is not None)
    if dur is None and words[0].isdigit():
        dur = 0

    used = []
    try:
        if (i := _find(words, is_date)) is not None:
            end, has_year = _date(words[i], now)
            used = [i]
            # A time right after (or before) the date: "31/12 18:30"
            for j in (i + 1, i - 1):
                if 0 <= j < len(words) and (c := _CLOCK.fullmatch(words[j])):
                    end = end.replace(hour=int(c[1]), minute=int(c[2]))
                    used.append(j)
                    break
            if not has_year and end <= now:
                end = end.replace(year=end.year + 1)
        elif (i := _find(words, _CLOCK.fullmatch)) is not None:
            c = _CLOCK.fullmatch(words[i])
            end = now.replace(hour=int(c[1]), minute=int(c[2]), second=0, microsecond=0)
            if end <= now:
                end += timedelta(days=1)
            used = [i]
        elif dur is not None:
            end = now + timedelta(seconds=_duration(words[dur]))
            used = [dur]
        else:
            raise ParseError("bad_format")
    except (ValueError, OverflowError):  # e.g. 31/02 or 25:00
        raise ParseError("bad_format")

    left = (end - now).total_seconds()
    if left <= 0:
        raise ParseError("past")
    if not MIN_SECONDS <= left <= MAX_SECONDS:
        raise ParseError("range")

    # Cut the time words out of the original text, keeping its line breaks.
    for i in sorted(used, reverse=True):
        a, b = spans[i]
        text = text[:a] + text[b:]
    title = "\n".join(" ".join(line.split()) for line in text.strip().splitlines())
    title = re.sub(r"\n{3,}", "\n\n", title).strip().strip(_QUOTES).strip()
    return end, title[:MAX_TITLE]


def update_every(seconds_left):
    """How often to edit the message. Telegram limits edits, so go a bit slower when far away."""
    if seconds_left >= 86400:
        return 10
    if seconds_left >= 60:
        return 5
    return 3


def _units(seconds):
    d, rest = divmod(seconds, 86400)
    h, rest = divmod(rest, 3600)
    m, s = divmod(rest, 60)
    if d:
        return [(d, "d"), (h, "h"), (m, "m"), (s, "s")]
    if h:
        return [(h, "h"), (m, "m"), (s, "s")]
    if m:
        return [(m, "m"), (s, "s")]
    return [(s, "s")]


def _bar(start, end, now, width=12):
    done = min(1.0, max(0.0, (now - start) / (end - start)))
    filled = round(done * width)
    return "▰" * filled + "▱" * (width - filled) + f"  {int(done * 100)}%"


def fmt_date(ts, tz):
    return datetime.fromtimestamp(ts, tz).strftime("%d/%m/%Y · %H:%M")


def _wrap(lang, title, body, end, tz, footer):
    lines = []
    if title:
        lines += [f"<b>{html.escape(title)}</b>", ""]
    lines += body
    lines.append(f"🗓 {fmt_date(end, tz)}")
    if footer:
        lines += ["", f"<i>{html.escape(footer)}</i>"]
    return "\n".join(lines)


def render(lang, title, start, end, now, tz, footer=""):
    """The live countdown message. start/end/now are Unix timestamps."""
    left = max(0, int(end - now + 0.999))  # round up so it never shows 0 too early
    clock = "  ".join(f"<b>{value:02d}</b> {t(lang, 'unit_' + unit)}" for value, unit in _units(left))
    return _wrap(lang, title, [f"⏳ {clock}", _bar(start, end, now)], end, tz, footer)


def render_done(lang, title, end, tz, footer=""):
    return _wrap(lang, title, [t(lang, "done")], end, tz, footer)


def render_stopped(lang, title, end, tz, footer=""):
    return _wrap(lang, title, [t(lang, "stopped")], end, tz, footer)
