from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog


class InputBar(ctk.CTkFrame):
    def __init__(self, master, on_send, on_cancel):
        super().__init__(master)
        self.on_send = on_send
        self.on_cancel = on_cancel

        self.grid_columnconfigure(1, weight=1)
        self.attach_btn = ctk.CTkButton(self, text="📎", width=40, command=self.attach_file)
        self.attach_btn.grid(row=0, column=0, padx=8, pady=8)

        self.input_box = ctk.CTkTextbox(self, height=90)
        self.input_box.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        self.input_box.bind("<Return>", self._on_return)

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, padx=8, pady=8)
        self.counter = ctk.CTkLabel(right, text="0 chars • ~0 tokens")
        self.counter.pack(pady=(0, 6))
        self.send_btn = ctk.CTkButton(right, text="Send", command=self.send)
        self.send_btn.pack(fill="x")
        self.cancel_btn = ctk.CTkButton(right, text="Stop", command=self.on_cancel)
        self.cancel_btn.pack(fill="x", pady=(6, 0))

        self.input_box.bind("<KeyRelease>", lambda _: self.update_counter())

    def _on_return(self, event):
        if event.state & 0x1:
            return
        self.send()
        return "break"

    def update_counter(self):
        text = self.input_box.get("1.0", "end").strip()
        self.counter.configure(text=f"{len(text)} chars • ~{max(1, len(text)//4)} tokens")

    def send(self):
        text = self.input_box.get("1.0", "end").strip()
        if not text:
            return
        self.on_send(text)
        self.input_box.delete("1.0", "end")
        self.update_counter()

    def attach_file(self):
        file = filedialog.askopenfilename(filetypes=[("Supported", "*.txt *.pdf *.py *.js *.md")])
        if not file:
            return
        path = Path(file)
        if path.suffix.lower() == ".pdf":
            blob = f"[Attached PDF file: {path.name}]\n"
        else:
            blob = path.read_text(encoding="utf-8", errors="ignore")
        self.input_box.insert("end", f"\n\n[Attached file: {path.name}]\n{blob}")
        self.update_counter()
