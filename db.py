"""A small SQLite file (bot.db) so languages and running countdowns survive restarts."""

import sqlite3
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
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS countdowns (
                id TEXT PRIMARY KEY,
                owner_id INTEGER, lang TEXT, title TEXT,
                starts_at REAL, ends_at REAL,
                chat_id INTEGER, message_id INTEGER, inline_id TEXT
            );
        """)

    def get_lang(self, user_id):
        row = self.conn.execute("SELECT lang FROM users WHERE id = ?", (user_id,)).fetchone()
        return row[0] if row else None

    def set_lang(self, user_id, lang):
        with self.conn:
            self.conn.execute(
                "INSERT INTO users VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET lang = excluded.lang",
                (user_id, lang),
            )

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
