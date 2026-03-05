from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Gemini Desktop"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DATA_DIR / "conversations.db"
CONFIG_PATH = APP_DATA_DIR / "config.json"


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    model TEXT NOT NULL,
    system_prompt TEXT DEFAULT '',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('user', 'model', 'error')),
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
ON messages(conversation_id, created_at);
"""


class Database:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def create_conversation(self, title: str, model: str, system_prompt: str = "") -> str:
        now = int(time.time())
        conv_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO conversations(id, title, model, system_prompt, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, title, model, system_prompt, now, now),
        )
        self.conn.commit()
        return conv_id

    def list_conversations(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, title, model, system_prompt, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def rename_conversation(self, conversation_id: str, title: str) -> None:
        self.conn.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", (title, int(time.time()), conversation_id))
        self.conn.commit()

    def update_conversation_settings(self, conversation_id: str, model: str, system_prompt: str) -> None:
        self.conn.execute(
            "UPDATE conversations SET model = ?, system_prompt = ?, updated_at = ? WHERE id = ?",
            (model, system_prompt, int(time.time()), conversation_id),
        )
        self.conn.commit()

    def delete_conversation(self, conversation_id: str) -> None:
        self.conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        self.conn.commit()

    def add_message(self, conversation_id: str, role: str, content: str) -> str:
        msg_id = str(uuid.uuid4())
        now = int(time.time())
        self.conn.execute(
            "INSERT INTO messages(id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (msg_id, conversation_id, role, content, now),
        )
        self.conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
        self.conn.commit()
        return msg_id

    def get_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def export_all_json(self) -> str:
        payload = {
            "conversations": self.list_conversations(),
            "messages": [
                dict(r)
                for r in self.conn.execute(
                    "SELECT id, conversation_id, role, content, created_at FROM messages ORDER BY created_at ASC"
                ).fetchall()
            ],
        }
        return json.dumps(payload, indent=2)

    def clear_all(self) -> None:
        self.conn.executescript("DELETE FROM messages; DELETE FROM conversations;")
        self.conn.commit()


def load_config() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "temperature": 1.0,
        "max_output_tokens": 8192,
        "top_p": 0.95,
        "top_k": 40,
        "theme": "system",
        "font_size": "medium",
        "model": "gemini-2.0-flash",
        "system_prompt": "",
        "personas": {},
    }
    if not CONFIG_PATH.exists():
        save_config(defaults)
        return defaults
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    defaults.update(data)
    return defaults


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
