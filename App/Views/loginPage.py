import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from Database.dbUsers import checkLogin 

class LoginPage(tk.Frame):
    """Giao diện Đăng nhập với thiết kế hiện đại và chức năng Placeholder."""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- 1. THIẾT LẬP STYLE VÀ MÀU SẮC ---
        self.COLOR_BG = "white"
        self.COLOR_PRIMARY = "#E50019" # Đỏ tươi
        self.COLOR_TEXT = "#333333"
        self.COLOR_HINT = "#AAAAAA"
        
        self.config(bg=self.COLOR_BG) 
        self._configure_styles() # Gọi hàm cấu hình Style

        # --- 2. KHUNG CHỨA TRUNG TÂM (CENTER FRAME) ---
        main_frame = tk.Frame(self, bg=self.COLOR_BG)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(main_frame, text="Đăng nhập Hệ Thống", style="Modern.Title.TLabel").pack(pady=30) 

        # --- 3. TRƯỜNG NHẬP LIỆU ---
        input_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        input_frame.pack(padx=20, pady=10)

        # Tên đăng nhập
        ttk.Label(input_frame, text="Tên đăng nhập:", style="Modern.TLabel").pack(anchor='w', pady=(10, 2))
        self.username_container = self._create_custom_entry(input_frame, "Nhập tên đăng nhập của bạn")
        self.username_container.pack(fill='x', ipady=5)

        # Mật khẩu
        ttk.Label(input_frame, text="Mật khẩu:", style="Modern.TLabel").pack(anchor='w', pady=(15, 2))
        self.password_container = self._create_custom_entry(input_frame, "Nhập mật khẩu của bạn", show="•")
        self.password_container.pack(fill='x', ipady=5)

        # 4. NÚT ĐĂNG NHẬP
        ttk.Button(main_frame, text="Đăng nhập", command=self._login_action, 
                   style="Primary.TButton").pack(fill='x', padx=20, pady=25)

        # 5. NÚT ĐĂNG KÝ
        ttk.Button(main_frame, text="Đăng ký tài khoản mới", 
                   command=lambda: controller.show_frame("RegisterPage"), 
                   style="Secondary.TButton").pack(pady=5)

    # ----------------------------------------------------------------------
    # --- PHẦN HÀM THIẾT LẬP STYLE & ENTRY (Được đặt tên với _ để chỉ hàm nội bộ) ---
    # ----------------------------------------------------------------------

    def _configure_styles(self):
        """Cấu hình các style hiện đại cho ttk widgets."""
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Styles cho Label
        style.configure("Modern.Title.TLabel", font=("Helvetica", 24, "bold"), foreground=self.COLOR_PRIMARY, background=self.COLOR_BG)
        style.configure("Modern.TLabel", font=("Helvetica", 12), foreground=self.COLOR_TEXT, background=self.COLOR_BG)
        
        # Styles cho Entry
        style.configure("Modern.TEntry", font=("Helvetica", 12), padding=10, fieldbackground="white", selectbackground=self.COLOR_PRIMARY)
        style.map("Modern.TEntry", fieldbackground=[('focus', 'white')])
        
        # Styles cho Button
        style.configure("Primary.TButton", font=("Helvetica", 14, "bold"), background=self.COLOR_PRIMARY, foreground="white", padding=10, relief="flat", focuscolor=self.COLOR_PRIMARY)
        style.map("Primary.TButton", background=[('active', '#CC0016')])
        style.configure("Secondary.TButton", font=("Helvetica", 11), background=self.COLOR_BG, foreground="#007bff", relief="flat")
        style.map("Secondary.TButton", foreground=[('active', self.COLOR_PRIMARY)], background=[('active', self.COLOR_BG)])

    def _get_entry_widget(self, container):
        """Trả về widget Entry thực tế nằm trong Canvas container."""
        for widget in container.winfo_children():
            if isinstance(widget, ttk.Entry):
                return widget
        return None

    def _create_custom_entry(self, parent, placeholder, show=""):
        """Tạo Entry với Placeholder và viền tùy chỉnh (dùng Canvas)."""
        container = tk.Canvas(parent, highlightthickness=1, highlightbackground=self.COLOR_HINT, 
                              bg="white", relief="flat", bd=0, width=300, height=40)
        container.pack_propagate(False)
        
        entry = ttk.Entry(container, style="Modern.TEntry", show=show)
        entry.pack(fill='both', expand=True, padx=2, pady=2)
        
        entry.insert(0, placeholder)
        entry.config(foreground=self.COLOR_HINT)
        
        # Bind sự kiện Focus
        entry.bind("<FocusIn>", lambda e: self._on_focus_in(entry, placeholder, show))
        entry.bind("<FocusOut>", lambda e: self._on_focus_out(entry, placeholder))
        
        return container

    def _on_focus_in(self, entry, placeholder, show):
        """Xử lý khi focus: Xóa Placeholder và đặt thuộc tính show."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(show=show)
            entry.config(foreground=self.COLOR_TEXT)
        entry.master.config(highlightbackground=self.COLOR_PRIMARY)

    def _on_focus_out(self, entry, placeholder):
        """Xử lý khi mất focus: Hiện lại Placeholder nếu rỗng."""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(show="")
            entry.config(foreground=self.COLOR_HINT)
        entry.master.config(highlightbackground=self.COLOR_HINT)
            
    # ----------------------------------------------------------------------
    # --- LOGIC ĐĂNG NHẬP ---
    # ----------------------------------------------------------------------
    
    def _login_action(self):
        """Xử lý logic đăng nhập: Lấy data, kiểm tra rỗng, gọi CSDL và điều hướng."""
        # 1. Lấy Entry widgets
        username_entry_widget = self._get_entry_widget(self.username_container)
        password_entry_widget = self._get_entry_widget(self.password_container)

        # 2. Lấy giá trị (Đã xử lý Placeholder bằng FocusOut/FocusIn)
        username = username_entry_widget.get()
        password = password_entry_widget.get()
        
        placeholder_u = "Nhập tên đăng nhập của bạn"
        placeholder_p = "Nhập mật khẩu của bạn"

        # 3. Kiểm tra rỗng (Bao gồm cả trường hợp Placeholder còn tồn tại)
        if username == placeholder_u or not username:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên đăng nhập.")
            return

        if password == placeholder_p or not password:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu.")
            return
            
        # 4. GỌI HÀM KIỂM TRA CSDL
        user_id, role = checkLogin(username, password)
        
        if role:
            # Lấy instance của trang POS và cập nhật trạng thái user
            pos_page_instance = self.controller.frames["POSPage"]
            pos_page_instance.update_user_status(user_id, username, role)

            # Xóa trường nhập liệu sau khi thành công (Đặt lại Placeholder)
            username_entry_widget.delete(0, tk.END)
            password_entry_widget.delete(0, tk.END)
            self._on_focus_out(username_entry_widget, placeholder_u)
            self._on_focus_out(password_entry_widget, placeholder_p)
            
            # Đăng nhập thành công
            if role.lower() == 'admin':
                admin_page_instance = self.controller.frames["AdminPage"]
                admin_page_instance.refresh_page()  # Làm mới dữ liệu thật sự của frame đang dùng
                self.controller.show_frame("AdminPage") 
            else:
                self.controller.show_frame("POSPage")
        else:
            # Đăng nhập thất bại
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
            
            # Xóa mật khẩu sau khi thất bại
            password_entry_widget.delete(0, tk.END)
            self._on_focus_out(password_entry_widget, placeholder_p)