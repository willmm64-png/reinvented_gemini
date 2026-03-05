from __future__ import annotations

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_new_chat, on_select_chat, on_delete_chat):
        super().__init__(master, corner_radius=0, width=260)
        self.on_new_chat = on_new_chat
        self.on_select_chat = on_select_chat
        self.on_delete_chat = on_delete_chat

        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text="Conversations", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(12, 4), sticky="w"
        )
        ctk.CTkButton(self, text="+ New Chat", command=self.on_new_chat).grid(row=1, column=0, padx=12, pady=8, sticky="ew")

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.chat_buttons: dict[str, ctk.CTkFrame] = {}

    def refresh(self, conversations, active_id: str | None):
        for child in self.scroll.winfo_children():
            child.destroy()
        for conv in conversations:
            row = ctk.CTkFrame(self.scroll)
            row.pack(fill="x", padx=4, pady=4)
            title_btn = ctk.CTkButton(
                row,
                text=conv["title"][:32],
                fg_color="#4f8ef7" if conv["id"] == active_id else "transparent",
                command=lambda c=conv["id"]: self.on_select_chat(c),
                anchor="w",
            )
            title_btn.pack(side="left", fill="x", expand=True, padx=(4, 2), pady=4)
            del_btn = ctk.CTkButton(row, text="✕", width=28, command=lambda c=conv["id"]: self.on_delete_chat(c))
            del_btn.pack(side="right", padx=(2, 4), pady=4)
