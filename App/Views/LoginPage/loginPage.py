import tkinter as tk
from tkinter import messagebox
from .loginLogic import handle_login 

class LoginPage(tk.Frame):
    """Giao diện Đăng nhập với thiết kế đồng bộ RubyOak."""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- 1. THIẾT KẾ GIAO DIỆN ---
        # Đặt màu nền cho Frame chính
        self.config(bg="#FFF8F0")

        # Khung chứa trung tâm để mọi thứ căn giữa
        main_frame = tk.Frame(self, bg="#FFF8F0")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(
            main_frame, text="🍇 ĐĂNG NHẬP HỆ THỐNG", 
            font=("Times New Roman", 24, "bold"), 
            fg="#8B0000",
            bg="#FFF8F0"
        ).pack(pady=(0, 50))
        
        # Tên đăng nhập
        tk.Label(
            main_frame, text="Tên đăng nhập:", 
            font=("Times New Roman", 15),
            fg="#5C2E0C", 
            bg="#FFF8F0"
        ).pack(pady=5)
        
        self.username_entry = tk.Entry(
            main_frame, width=30, 
            font=("Times New Roman", 12),
            relief="solid", bd=1 
        )
        self.username_entry.pack(ipady=4)

        # Mật khẩu
        tk.Label(
            main_frame, text="Mật khẩu:", 
            font=("Times New Roman", 15),
            fg="#5C2E0C",
            bg="#FFF8F0"
        ).pack(pady=5)
        
        self.password_entry = tk.Entry(
            main_frame, width=30, show="*", 
            font=("Times New Roman", 12),
            relief="solid", bd=1
        )
        self.password_entry.pack(ipady=4)

        # Nút Đăng nhập
        tk.Button(
            main_frame, 
            text="Đăng nhập", 
            font=("Times New Roman", 12, "bold"), 
            command=self._login_action,
            width=20, 
            bg="#A52A2A",
            fg="white",
            relief="flat",
            pady=5
        ).pack(pady=20)
        
        # Nút Đăng ký
        tk.Button(
            main_frame, text="Đăng ký tài khoản mới", 
            font=("Times New Roman", 11, "underline"),
            command=lambda: controller.show_frame("RegisterPage"),
            fg="#5C2E0C",
            bg="#FFF8F0",
            relief="flat", 
            borderwidth=0,
            cursor="hand2"
        ).pack()
        
        # Bind phím Enter để đăng nhập
        self.username_entry.bind("<Return>", self._login_on_enter)
        self.password_entry.bind("<Return>", self._login_on_enter)

    def _login_on_enter(self, event=None):
        """Hàm hỗ trợ gọi đăng nhập khi nhấn Enter."""
        self._login_action()

    def _login_action(self):
        """Lấy data và ủy thác việc xử lý logic cho file loginLogic.py."""
        
        username = self.username_entry.get()
        password = self.password_entry.get()

        handle_login(
            self.controller, 
            username, 
            password, 
            self.username_entry, 
            self.password_entry 
        )
        
    def on_show_frame(self):
        """Hàm này sẽ được controller gọi khi trang này được hiển thị."""
        # Đặt kích thước cửa sổ mong muốn (Rộng x Cao)
        self.controller.state('zoomed')
        # Tự động focus vào trường username
        self.username_entry.focus_set()