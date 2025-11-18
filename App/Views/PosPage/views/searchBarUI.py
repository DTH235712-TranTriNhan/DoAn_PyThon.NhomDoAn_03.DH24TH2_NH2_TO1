import tkinter as tk
from tkinter import ttk

def create_search_bar_ui(self, parent):
    search_frame = tk.Frame(parent, bg="#FFF8F0", pady=5)
    search_frame.pack(fill="x")

    reset_btn = tk.Button(
        search_frame, text="♻️ Đặt lại",
        bg="#B0BEC5", fg="#263238",
        font=("Times New Roman", 11, "bold"),
        relief="flat", cursor="hand2",
        command=lambda: (
            self._set_active_category_button(self.category_buttons[0] if self.category_buttons else None),
            self.load_products_list()
        )
    )
    reset_btn.pack(side="right", padx=(0, 5))

    search_btn = tk.Button(
        search_frame, text="🔍 Tìm",
        bg="#A52A2A", fg="white",
        font=("Times New Roman", 11, "bold"),
        relief="flat", cursor="hand2",
        command=self.perform_search
    )
    search_btn.pack(side="right", padx=5)

    self.search_entry = ttk.Entry(
        search_frame,
        font=("Times New Roman", 12),
        width=34
    )
    self.search_entry.pack(
        side="right",
        padx=(0, 5),
        ipady=2
    )
    self.search_entry.bind("<Return>", self.perform_search)
