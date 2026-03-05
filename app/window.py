from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from tkinter import simpledialog, messagebox

from app.chat_view import ChatView
from app.input_bar import InputBar
from app.model_selector import ModelSelector
from app.settings import SettingsWindow
from app.sidebar import Sidebar
from app.system_prompt import SystemPromptPanel
from core.database import Database, load_config, save_config
from core.gemini_client import GeminiClient
from core.keystore import delete_api_key, get_api_key, set_api_key


class GeminiDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gemini Desktop")
        self.geometry("1300x820")
        self.minsize(980, 640)

        self.db = Database()
        self.config_data = load_config()
        ctk.set_appearance_mode(self.config_data.get("theme", "system"))

        self.active_conversation_id: str | None = None
        self.abort_stream = False
        self.client: GeminiClient | None = None

        self._ensure_api_key()
        self._build_ui()
        self.refresh_sidebar()
        self.new_chat()

        self.bind("<Control-n>", lambda _: self.new_chat())
        self.bind("<Escape>", lambda _: self.stop_generation())
        self.bind("<Control-comma>", lambda _: self.open_settings())

    def _ensure_api_key(self):
        key = get_api_key()
        while not key:
            key = simpledialog.askstring("Gemini API Key", "Enter your Gemini API key:", show="*")
            if key:
                try:
                    client = GeminiClient(key)
                    client.validate_key()
                    set_api_key(key)
                except Exception as exc:
                    messagebox.showerror("Invalid API key", str(exc))
                    key = None
            else:
                if messagebox.askyesno("Exit", "API key is required. Exit app?"):
                    self.destroy()
                    raise SystemExit(0)
        self.client = GeminiClient(key)

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        titlebar = ctk.CTkFrame(self, height=48)
        titlebar.grid(row=0, column=0, columnspan=2, sticky="ew")
        titlebar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(titlebar, text="Gemini Desktop", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=12, pady=8
        )
        self.model_selector = ModelSelector(titlebar, self.config_data["model"], self.on_model_change)
        self.model_selector.grid(row=0, column=1, padx=8, pady=8, sticky="e")
        ctk.CTkButton(titlebar, text="⚙", width=36, command=self.open_settings).grid(row=0, column=2, padx=12)

        self.sidebar = Sidebar(self, self.new_chat, self.load_conversation, self.delete_conversation)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        content = ctk.CTkFrame(self)
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self.system_prompt_panel = SystemPromptPanel(content, self.config_data.get("system_prompt", ""), self.save_persona)
        self.system_prompt_panel.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        self.chat_view = ChatView(content)
        self.chat_view.grid(row=1, column=0, sticky="nsew")

        self.input_bar = InputBar(content, self.send_message, self.stop_generation)
        self.input_bar.grid(row=2, column=0, sticky="ew", padx=8, pady=8)

    def refresh_sidebar(self):
        self.sidebar.refresh(self.db.list_conversations(), self.active_conversation_id)

    def new_chat(self):
        conv_id = self.db.create_conversation(
            title="New Chat",
            model=self.config_data["model"],
            system_prompt=self.system_prompt_panel.get_text() if hasattr(self, "system_prompt_panel") else "",
        )
        self.active_conversation_id = conv_id
        self.chat_view.clear()
        self.refresh_sidebar()

    def load_conversation(self, conversation_id: str):
        self.active_conversation_id = conversation_id
        self.chat_view.clear()
        for msg in self.db.get_messages(conversation_id):
            self.chat_view.append_message(msg["role"], msg["content"])
        self.refresh_sidebar()

    def delete_conversation(self, conversation_id: str):
        if messagebox.askyesno("Delete", "Delete this conversation?"):
            self.db.delete_conversation(conversation_id)
            if self.active_conversation_id == conversation_id:
                self.active_conversation_id = None
                self.chat_view.clear()
            self.refresh_sidebar()

    def on_model_change(self, model: str):
        self.config_data["model"] = model
        save_config(self.config_data)

    def save_persona(self, prompt: str):
        name = simpledialog.askstring("Save Persona", "Persona name:")
        if name:
            self.config_data.setdefault("personas", {})[name] = prompt
            self.config_data["system_prompt"] = prompt
            save_config(self.config_data)

    def stop_generation(self):
        self.abort_stream = True

    def send_message(self, text: str):
        if not self.active_conversation_id:
            self.new_chat()
        assert self.active_conversation_id

        if self.db.list_conversations()[0]["title"] == "New Chat":
            self.db.rename_conversation(self.active_conversation_id, text[:48])

        self.db.add_message(self.active_conversation_id, "user", text)
        self.chat_view.append_message("user", text)

        assistant_box = self.chat_view.append_message("model", "")
        self.abort_stream = False

        threading.Thread(target=self._run_stream, args=(assistant_box,), daemon=True).start()
        self.refresh_sidebar()

    def _run_stream(self, assistant_box):
        assert self.client and self.active_conversation_id
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in self.db.get_messages(self.active_conversation_id)
            if m["role"] in {"user", "model"}
        ]
        full = ""
        try:
            for chunk in self.client.stream_response(
                model_name=self.config_data["model"],
                messages=messages,
                system_prompt=self.system_prompt_panel.get_text(),
                temperature=self.config_data["temperature"],
                max_tokens=self.config_data["max_output_tokens"],
                top_p=self.config_data["top_p"],
                top_k=self.config_data["top_k"],
            ):
                if self.abort_stream:
                    break
                full += chunk
                self.after(0, lambda c=full: self.chat_view.update_streaming_text(assistant_box, c))
                time.sleep(0.01)
            if not full:
                full = "No response was generated. Try rephrasing."
            self.db.add_message(self.active_conversation_id, "model", full)
        except Exception as exc:
            err = f"API Error: {exc}"
            self.after(0, lambda: self.chat_view.update_streaming_text(assistant_box, err))
            self.db.add_message(self.active_conversation_id, "error", err)
        finally:
            self.after(0, self.refresh_sidebar)

    def open_settings(self):
        SettingsWindow(
            self,
            self.config_data,
            self.on_save_settings,
            self.export_all,
            self.clear_all,
            self.update_api_key,
        )

    def on_save_settings(self, updates: dict):
        self.config_data.update(updates)
        ctk.set_appearance_mode(self.config_data["theme"])
        save_config(self.config_data)

    def update_api_key(self):
        key = simpledialog.askstring("Update API Key", "Enter new API key:", show="*")
        if key:
            set_api_key(key)
            self.client = GeminiClient(key)
        elif messagebox.askyesno("Delete key", "Delete API key?"):
            delete_api_key()

    def export_all(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            Path(path).write_text(self.db.export_all_json(), encoding="utf-8")

    def clear_all(self):
        if messagebox.askyesno("Clear all", "Delete all conversations and settings?"):
            self.db.clear_all()
            self.config_data["personas"] = {}
            save_config(self.config_data)
            self.chat_view.clear()
            self.refresh_sidebar()
