import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
# Đảm bảo đường dẫn import này là chính xác
from Database.dbUsers import checkLogin 

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- CẤU HÌNH STYLE HIỆN ĐẠI & MÀU SẮC ---
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # MÀU SẮC (Sử dụng self. để truy cập trong các hàm)
        self.COLOR_BG = "white"
        self.COLOR_PRIMARY = "#E50019" # Màu Đỏ tươi mạnh mẽ
        self.COLOR_TEXT = "#333333"
        self.COLOR_HINT = "#AAAAAA"
        
        self.config(bg=self.COLOR_BG) 

        # Cấu hình Styles
        style.configure("Modern.Title.TLabel", font=("Helvetica", 24, "bold"), foreground=self.COLOR_PRIMARY, background=self.COLOR_BG)
        style.configure("Modern.TLabel", font=("Helvetica", 12), foreground=self.COLOR_TEXT, background=self.COLOR_BG)
        style.configure("Modern.TEntry", font=("Helvetica", 12), padding=10, fieldbackground="white", selectbackground=self.COLOR_PRIMARY)
        style.map("Modern.TEntry", fieldbackground=[('focus', 'white')])
        style.configure("Primary.TButton", font=("Helvetica", 14, "bold"), background=self.COLOR_PRIMARY, foreground="white", padding=10, relief="flat", focuscolor=self.COLOR_PRIMARY)
        style.map("Primary.TButton", background=[('active', '#CC0016')])
        style.configure("Secondary.TButton", font=("Helvetica", 11), background=self.COLOR_BG, foreground="#007bff", relief="flat")
        style.map("Secondary.TButton", foreground=[('active', self.COLOR_PRIMARY)], background=[('active', self.COLOR_BG)])

        # --- KHUNG CHỨA TRUNG TÂM ---
        main_frame = tk.Frame(self, bg=self.COLOR_BG)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 1. TIÊU ĐỀ
        ttk.Label(main_frame, text="Đăng nhập Hệ Thống", style="Modern.Title.TLabel").pack(pady=30) 

        # 2. TRƯỜNG NHẬP LIỆU
        input_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        input_frame.pack(padx=20, pady=10)

        # Tên đăng nhập (Lưu trữ Canvas container)
        ttk.Label(input_frame, text="Tên đăng nhập:", style="Modern.TLabel").pack(anchor='w', pady=(10, 2))
        # Đổi tên biến thành self.username_container để dễ phân biệt là Canvas
        self.username_container = self.create_custom_entry(input_frame, "Nhập tên đăng nhập của bạn")
        self.username_container.pack(fill='x', ipady=5)

        # Mật khẩu (Lưu trữ Canvas container)
        ttk.Label(input_frame, text="Mật khẩu:", style="Modern.TLabel").pack(anchor='w', pady=(15, 2))
        # Đổi tên biến thành self.password_container để dễ phân biệt là Canvas
        self.password_container = self.create_custom_entry(input_frame, "Nhập mật khẩu của bạn", show="•")
        self.password_container.pack(fill='x', ipady=5)

        # 3. NÚT CHÍNH (Đăng nhập)
        ttk.Button(main_frame, text="Đăng nhập", command=self.loginAction, 
                   style="Primary.TButton").pack(fill='x', padx=20, pady=25)

        # 4. NÚT PHỤ
        ttk.Button(main_frame, text="Đăng ký tài khoản mới", 
                   command=lambda: controller.show_frame("RegisterPage"), 
                   style="Secondary.TButton").pack(pady=5)
        
        # ttk.Button(main_frame, text="Quên mật khẩu?", 
        #            command=self.forgot_password, 
        #            style="Secondary.TButton").pack(pady=5)
    
    # --- HÀM TRỢ GIÚP ---
    def get_entry_widget(self, container):
        """Tìm và trả về widget Entry NẰM TRONG Canvas container."""
        for widget in container.winfo_children():
            if isinstance(widget, ttk.Entry):
                return widget
        return None

    def create_custom_entry(self, parent, placeholder, show=""):
        """Tạo Entry với Placeholder và viền mỏng (sử dụng Canvas)."""
        container = tk.Canvas(parent, highlightthickness=1, highlightbackground=self.COLOR_HINT, 
                              bg="white", relief="flat", bd=0, width=300, height=40)
        container.pack_propagate(False)
        
        entry = ttk.Entry(container, style="Modern.TEntry", show=show)
        entry.pack(fill='both', expand=True, padx=2, pady=2)
        
        entry.insert(0, placeholder)
        entry.config(foreground=self.COLOR_HINT)
        entry.bind("<FocusIn>", lambda e: self.on_focus_in(entry, placeholder, show))
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(entry, placeholder, show))
        
        return container

    def on_focus_in(self, entry, placeholder, show):
        """Xóa Placeholder khi click vào."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(show=show)
            entry.config(foreground=self.COLOR_TEXT)
        entry.master.config(highlightbackground=self.COLOR_PRIMARY)

    def on_focus_out(self, entry, placeholder, show):
        """Hiện lại Placeholder khi không focus."""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(show="")
            entry.config(foreground=self.COLOR_HINT)
        entry.master.config(highlightbackground=self.COLOR_HINT)
            
    # --- LOGIC ĐĂNG NHẬP (loginAction) ---
    def loginAction(self):
        # 1. Lấy Entry widget thực tế từ Canvas container
        username_entry_widget = self.get_entry_widget(self.username_container)
        password_entry_widget = self.get_entry_widget(self.password_container)

        # 2. Lấy dữ liệu
        username = username_entry_widget.get()
        password = password_entry_widget.get()
        
        placeholder_u = "Nhập tên đăng nhập của bạn"
        placeholder_p = "Nhập mật khẩu của bạn"

        # 3. Kiểm tra Placeholder/rỗng
        if username == placeholder_u or not username:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên đăng nhập.")
            return

        # Khi người dùng focus vào, mật khẩu sẽ có show="•", nên placeholder_p không cần thiết
        if password == placeholder_p or not password:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu.")
            return
            
        # 4. GỌI HÀM KIỂM TRA CSDL
        role = checkLogin(username, password)
        
        if role:
            pos_page_instance = self.controller.frames["POSPage"]
            pos_page_instance.update_user_status(username, role)

            # Xóa trường nhập liệu sau khi thành công
            username_entry_widget.delete(0, tk.END)
            password_entry_widget.delete(0, tk.END)

            # Đăng nhập thành công
            if role.lower() == 'admin':
                # Chuyển đến trang Quản trị              
                self.controller.show_frame("AdminPage") 
            else:
                # Chuyển đến trang Bán hàng (POS)
                self.controller.show_frame("POSPage")
        else:
            # Đăng nhập thất bại
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
            # Xóa mật khẩu sau khi thất bại
            password_entry_widget.delete(0, tk.END)


    # def forgot_password(self):
    #     messagebox.showinfo("Hỗ trợ", "Chức năng quên mật khẩu hiện chưa được triển khai.")
