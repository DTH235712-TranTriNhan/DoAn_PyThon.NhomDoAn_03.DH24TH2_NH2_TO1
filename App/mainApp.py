import tkinter as tk
import tkinter.ttk as ttk
from App.Views.LoginPage.loginPage import LoginPage 
from App.Views.RegisterPage.registerPage import RegisterPage
from App.Views.AdminPage.adminPage import AdminPage
from App.Views.PosPage.posPage import POSPage

class SalesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Quản lý Bán hàng")
        self.geometry("800x600")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Thêm các Form vào ứng dụng (sử dụng các lớp đã import)
        for F in (LoginPage, RegisterPage, AdminPage, POSPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("POSPage") # Khởi đầu bằng trang Đăng nhập

    def show_frame(self, page_name):
        '''Hiển thị frame được chỉ định'''
        frame = self.frames[page_name]
        if hasattr(frame, "on_show_frame"):
            frame.on_show_frame() # Nếu có, hãy gọi nó để cập nhật kích thước
    # ---------------------
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

if __name__ == "__main__":
    app = SalesApp()
    app.mainloop()

    