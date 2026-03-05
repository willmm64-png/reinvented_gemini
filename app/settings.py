from __future__ import annotations

import customtkinter as ctk


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, config: dict, on_save, on_export, on_clear, on_api_key):
        super().__init__(master)
        self.title("Settings")
        self.geometry("480x520")
        self.on_save = on_save
        self.on_export = on_export
        self.on_clear = on_clear
        self.on_api_key = on_api_key

        self.temp = ctk.CTkSlider(self, from_=0.0, to=2.0)
        self.temp.set(config["temperature"])
        ctk.CTkLabel(self, text="Temperature").pack(anchor="w", padx=16, pady=(16, 4))
        self.temp.pack(fill="x", padx=16)

        self.max_tokens = ctk.CTkEntry(self)
        self.max_tokens.insert(0, str(config["max_output_tokens"]))
        ctk.CTkLabel(self, text="Max output tokens").pack(anchor="w", padx=16, pady=(12, 4))
        self.max_tokens.pack(fill="x", padx=16)

        self.top_p = ctk.CTkSlider(self, from_=0.0, to=1.0)
        self.top_p.set(config["top_p"])
        ctk.CTkLabel(self, text="Top-P").pack(anchor="w", padx=16, pady=(12, 4))
        self.top_p.pack(fill="x", padx=16)

        self.top_k = ctk.CTkSlider(self, from_=1, to=100)
        self.top_k.set(config["top_k"])
        ctk.CTkLabel(self, text="Top-K").pack(anchor="w", padx=16, pady=(12, 4))
        self.top_k.pack(fill="x", padx=16)

        self.theme = ctk.CTkOptionMenu(self, values=["dark", "light", "system"])
        self.theme.set(config["theme"])
        ctk.CTkLabel(self, text="Theme").pack(anchor="w", padx=16, pady=(12, 4))
        self.theme.pack(fill="x", padx=16)

        self.font_size = ctk.CTkOptionMenu(self, values=["small", "medium", "large"])
        self.font_size.set(config["font_size"])
        ctk.CTkLabel(self, text="Font size").pack(anchor="w", padx=16, pady=(12, 4))
        self.font_size.pack(fill="x", padx=16)

        ctk.CTkButton(self, text="Update API Key", command=self.on_api_key).pack(fill="x", padx=16, pady=(16, 6))
        ctk.CTkButton(self, text="Export All Data", command=self.on_export).pack(fill="x", padx=16, pady=6)
        ctk.CTkButton(self, text="Clear All Data", fg_color="#f87171", command=self.on_clear).pack(fill="x", padx=16, pady=6)
        ctk.CTkButton(self, text="Save", command=self.save).pack(fill="x", padx=16, pady=(24, 16))

    def save(self):
        self.on_save(
            {
                "temperature": float(self.temp.get()),
                "max_output_tokens": int(self.max_tokens.get() or 8192),
                "top_p": float(self.top_p.get()),
                "top_k": int(self.top_k.get()),
                "theme": self.theme.get(),
                "font_size": self.font_size.get(),
            }
        )
        self.destroy()
