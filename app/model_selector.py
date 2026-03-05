from __future__ import annotations

import customtkinter as ctk

MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-thinking",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


class ModelSelector(ctk.CTkFrame):
    def __init__(self, master, current_model: str, on_change):
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change
        self.opt = ctk.CTkOptionMenu(self, values=MODELS, command=self.on_change)
        self.opt.set(current_model)
        self.opt.pack(fill="x")
