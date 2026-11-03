"""A small SQLite file (bot.db) so languages and running countdowns survive restarts."""

import sqlite3
import time
from dataclasses import dataclass, field


@dataclass
class Countdown:
    id: str
    owner_id: int
    lang: str
    title: str
    start: float  # Unix timestamps
    end: float
    chat_id: int | None = None  # set for messages the bot sent itself...
    message_id: int | None = None
    inline_id: str | None = None  # ...or this, for messages sent with @bot in other chats
    # Not saved, only used while running:
    next_edit: float = field(default=0, compare=False)
    last_text: str = field(default="", compare=False)
    fails: int = field(default=0, compare=False)


class DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self._upgrade_users()
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                lang TEXT,  -- empty until they pick a language
                first_seen INTEGER NOT NULL DEFAULT 0,  -- Unix time; 0 = before stats were added
                last_seen INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS chats (  -- groups and channels the bot has been used in
                id INTEGER PRIMARY KEY,
                type TEXT, title TEXT,
                first_seen INTEGER NOT NULL, last_seen INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (  -- one row per download / countdown, for /stats
                time INTEGER NOT NULL, user_id INTEGER, kind TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS events_time ON events (time);
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS countdowns (
                id TEXT PRIMARY KEY,
                owner_id INTEGER, lang TEXT, title TEXT,
                starts_at REAL, ends_at REAL,
                chat_id INTEGER, message_id INTEGER, inline_id TEXT
            );
        """)
        with self.conn:
            if self.conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'users_old'").fetchone():
                self.conn.execute("INSERT OR IGNORE INTO users (id, lang) SELECT id, lang FROM users_old")
                self.conn.execute("DROP TABLE users_old")
            self.conn.execute("INSERT OR IGNORE INTO meta VALUES ('stats_since', ?)", (str(int(time.time())),))
        self._seen = {}  # id -> when we last wrote last_seen

    def get_lang(self, user_id):
        row = self.conn.execute("SELECT lang FROM users WHERE id = ?", (user_id,)).fetchone()
        return row[0] if row else None

    def set_lang(self, user_id, lang):
        now = int(time.time())
        with self.conn:
            self.conn.execute(
                "INSERT INTO users (id, lang, first_seen, last_seen) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET lang = excluded.lang",
                (user_id, lang, now, now),
            )

    # ---------- stats ----------

    def _upgrade_users(self):
        """bot.db files from before /stats had users(id, lang NOT NULL) only.
        Move them aside here; they're copied into the new table right after it's created."""
        columns = [row[1] for row in self.conn.execute("PRAGMA table_info(users)")]
        if columns and "first_seen" not in columns:
            with self.conn:
                self.conn.execute("ALTER TABLE users RENAME TO users_old")

    def _recently_seen(self, key, now):
        # Write at most once a minute per person or chat, not on every message.
        if now - self._seen.get(key, 0) < 60:
            return True
        self._seen[key] = now
        return False

    def seen_user(self, user_id):
        now = int(time.time())
        if self._recently_seen(user_id, now):
            return
        with self.conn:
            self.conn.execute(
                "INSERT INTO users (id, first_seen, last_seen) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET last_seen = excluded.last_seen",
                (user_id, now, now),
            )

    def seen_chat(self, chat_id, kind, title):
        now = int(time.time())
        if self._recently_seen(chat_id, now):
            return
        with self.conn:
            self.conn.execute(
                "INSERT INTO chats VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE "
                "SET type = excluded.type, title = excluded.title, last_seen = excluded.last_seen",
                (chat_id, kind, title, now, now),
            )

    def add_event(self, user_id, kind):
        with self.conn:
            self.conn.execute("INSERT INTO events VALUES (?, ?, ?)", (int(time.time()), user_id, kind))

    def stats(self):
        now = int(time.time())
        day, week = now - 86400, now - 7 * 86400

        def count(sql, *args):
            return self.conn.execute(sql, args).fetchone()[0]

        events = {}
        for kind, total, today, this_week in self.conn.execute(
            "SELECT kind, COUNT(*), SUM(time >= ?), SUM(time >= ?) FROM events GROUP BY kind", (day, week)
        ):
            events[kind] = (total, today, this_week)
        return {
            "users": count("SELECT COUNT(*) FROM users"),
            "new_day": count("SELECT COUNT(*) FROM users WHERE first_seen >= ?", day),
            "new_week": count("SELECT COUNT(*) FROM users WHERE first_seen >= ?", week),
            "active_day": count("SELECT COUNT(*) FROM users WHERE last_seen >= ?", day),
            "active_week": count("SELECT COUNT(*) FROM users WHERE last_seen >= ?", week),
            "ar": count("SELECT COUNT(*) FROM users WHERE lang = 'ar'"),
            "en": count("SELECT COUNT(*) FROM users WHERE lang = 'en'"),
            "groups": count("SELECT COUNT(*) FROM chats WHERE type IN ('group', 'supergroup')"),
            "channels": count("SELECT COUNT(*) FROM chats WHERE type = 'channel'"),
            "since": int(self.conn.execute("SELECT value FROM meta WHERE key = 'stats_since'").fetchone()[0]),
            "events": events,
        }

    def add(self, cd):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO countdowns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (cd.id, cd.owner_id, cd.lang, cd.title, cd.start, cd.end,
                 cd.chat_id, cd.message_id, cd.inline_id),
            )

    def remove(self, cd_id):
        with self.conn:
            self.conn.execute("DELETE FROM countdowns WHERE id = ?", (cd_id,))

    def load(self):
        rows = self.conn.execute(
            "SELECT id, owner_id, lang, title, starts_at, ends_at, chat_id, message_id, inline_id FROM countdowns"
        )
        return [Countdown(*row) for row in rows]
