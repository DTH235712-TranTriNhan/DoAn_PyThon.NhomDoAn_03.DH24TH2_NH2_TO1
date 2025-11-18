import tkinter as tk

def create_footer_ui(self):
    footer = tk.Frame(self, bg="#FFF0E6", height=60)
    footer.pack(fill="x", side="bottom")
    tk.Label(
        footer,
        text=(
            "🍷 RubyOak — Hương vị rượu vang hảo hạng từ thiên nhiên.\n"
            "Trải nghiệm đẳng cấp trong từng giọt rượu."
        ),
        bg="#FFF0E6", fg="#5C2E0C", font=("Times New Roman", 11, "italic")
    ).pack(pady=10)
