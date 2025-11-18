import tkinter as tk

def create_header_ui(self):
    header = tk.Frame(self, bg="#8B0000", height=60)
    header.pack(fill="x")

    tk.Label(
        header, text="🍇 RubyOak POS",
        bg="#8B0000", fg="white",
        font=("Times New Roman", 20, "bold")
    ).pack(side="left", padx=20)

    self.login_button = tk.Button(
        header, text="Đăng nhập", bg="#E53935", fg="white",
        font=("Times New Roman", 12, "bold"),
        relief="flat", command=self.show_login_dialog
    )
    self.login_button.pack(side="right", padx=10, pady=10)

    self.user_label = tk.Label(header, text="Chưa đăng nhập",
                               bg="#8B0000", fg="#FFCDD2")
    self.user_label.pack(side="right", padx=10)
    self.user_label.bind("<Button-1>", lambda e: self.show_user_info_dialog())
    self.user_label.config(cursor="hand2")

    self.cart_btn = tk.Button(
        header, text="🛒 Giỏ hàng (0)", bg="#A52A2A", fg="white",
        font=("Times New Roman", 12, "bold"),
        relief="flat", command=self.show_cart_window
    )
    self.cart_btn.pack(side="right", padx=10, pady=10)
