import tkinter as tk
from tkinter import messagebox

class POSPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="TRANG BÁN HÀNG (POS)", font=("Arial", 30)).pack(pady=50)
        tk.Label(self, text="Nơi thực hiện các giao dịch bán hàng").pack()
        tk.Button(self, text="Đăng xuất", command=lambda: controller.show_frame("LoginPage")).pack(pady=20)