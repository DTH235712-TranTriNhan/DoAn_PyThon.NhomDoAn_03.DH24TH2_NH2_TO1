import tkinter as tk
from tkinter import messagebox
from Database.dbUsers import checkLogin

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        tk.Label(self, text="ĐĂNG NHẬP HỆ THỐNG", font=("Times New Roman", 24), fg="red" ).pack(pady=50)
        
        tk.Label(self, text="Tên đăng nhập:", font=("Times New Roman", 15)).pack(pady=5)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack()

        tk.Label(self, text="Mật khẩu:", font=("Times New Roman", 15)).pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Đăng nhập", font=("Times New Roman", 12), command=self.loginAction, width=20, bg="red",fg="white").pack(pady=20)
        
        tk.Button(self, text="Đăng ký tài khoản mới", command=lambda: controller.show_frame("RegisterPage")).pack()

    def loginAction(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        role = checkLogin(username, password)
        
        if role:
            if role == 'admin':
                self.controller.show_frame("AdminPage")
            else:
                self.controller.show_frame("POSPage")
        else:
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")