from __future__ import annotations

import customtkinter as ctk


class SystemPromptPanel(ctk.CTkFrame):
    def __init__(self, master, initial_text: str, on_save_persona):
        super().__init__(master)
        self.on_save_persona = on_save_persona
        self.collapsed = True

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=6, pady=4)
        self.toggle_btn = ctk.CTkButton(top, text="System Prompt ▼", command=self.toggle)
        self.toggle_btn.pack(side="left")
        self.save_btn = ctk.CTkButton(top, text="Save Persona", command=self.save_persona)
        self.save_btn.pack(side="right")

        self.box = ctk.CTkTextbox(self, height=80)
        self.box.insert("1.0", initial_text)
        self.box.pack(fill="x", padx=6, pady=(0, 6))
        self.box.pack_forget()

    def toggle(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.box.pack_forget()
            self.toggle_btn.configure(text="System Prompt ▼")
        else:
            self.box.pack(fill="x", padx=6, pady=(0, 6))
            self.toggle_btn.configure(text="System Prompt ▲")

    def get_text(self) -> str:
        return self.box.get("1.0", "end").strip()

    def save_persona(self):
        self.on_save_persona(self.get_text())
