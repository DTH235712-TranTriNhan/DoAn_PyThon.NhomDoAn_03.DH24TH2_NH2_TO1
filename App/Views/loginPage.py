import tkinter as tk
from tkinter import messagebox
from Database.dbUsers import checkLogin

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        tk.Label(self, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 24)).pack(pady=50)
        
        tk.Label(self, text="Tên đăng nhập:", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack()

        tk.Label(self, text="Mật khẩu:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Đăng nhập", font=("Arial", 12), command=self.loginAction, width=20).pack(pady=20)
        
        tk.Button(self, text="Đăng ký tài khoản mới", command=lambda: controller.show_frame("RegisterPage")).pack()

    def loginAction(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        role = checkLogin(username, password)
        
        if role:
            messagebox.showinfo("Thành công", f"Đăng nhập thành công!")
            
            if role == 'admin':
                self.controller.show_frame("AdminPage")
            else:
                self.controller.show_frame("POSPage")
        else:
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")