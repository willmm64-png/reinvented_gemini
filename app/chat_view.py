from __future__ import annotations

import datetime as dt

import customtkinter as ctk


class ChatView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.message_widgets: list[ctk.CTkFrame] = []

    def clear(self):
        for w in self.scroll.winfo_children():
            w.destroy()

    def append_message(self, role: str, content: str) -> ctk.CTkTextbox:
        wrap = ctk.CTkFrame(self.scroll, fg_color="transparent")
        wrap.pack(fill="x", padx=4, pady=6)
        is_user = role == "user"
        bubble = ctk.CTkFrame(wrap, fg_color="#1e1e24" if not is_user else "#4f8ef7")
        bubble.pack(anchor="e" if is_user else "w", padx=4)
        meta = ctk.CTkLabel(
            bubble,
            text=f"{'You' if is_user else 'Gemini'} • {dt.datetime.now().strftime('%H:%M')}",
            text_color="#8888a0",
            font=ctk.CTkFont(size=11),
        )
        meta.pack(anchor="w", padx=8, pady=(6, 2))
        txt = ctk.CTkTextbox(bubble, width=680, height=20, activate_scrollbars=False, wrap="word")
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        copy_btn = ctk.CTkButton(bubble, text="Copy", width=60, command=lambda t=content: self.clipboard_copy(t))
        copy_btn.pack(anchor="e", padx=8, pady=(0, 8))
        self.after(50, lambda: self.scroll._parent_canvas.yview_moveto(1.0))
        return txt

    def update_streaming_text(self, textbox: ctk.CTkTextbox, content: str) -> None:
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")
        self.after(10, lambda: self.scroll._parent_canvas.yview_moveto(1.0))

    def clipboard_copy(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
