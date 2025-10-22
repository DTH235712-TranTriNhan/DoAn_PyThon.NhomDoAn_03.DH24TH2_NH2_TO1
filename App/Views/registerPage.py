import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import uuid

# ====================================================================
# --- MOCK DATABASE (GIẢ LẬP CƠ SỞ DỮ LIỆU) ---
# Dữ liệu mẫu: admin/123456 (admin) và user/654321 (pos)
# ====================================================================

MOCK_USERS = {
    "admin": {"password": "123456", "role": "admin", "fullname": "Quản Trị Viên"},
    "user": {"password": "654321", "role": "pos", "fullname": "Nhân Viên Bán Hàng"},
}

def checkLogin(username, password):
    """Kiểm tra tên đăng nhập và mật khẩu (Mock)."""
    user_data = MOCK_USERS.get(username)
    if user_data and user_data["password"] == password:
        return user_data["role"]
    return None

def checkUserNameExists(username):
    """Kiểm tra tên đăng nhập đã tồn tại chưa (Mock)."""
    return username in MOCK_USERS

def registerUser(id, username, password, fullname, phone, address):
    """Đăng ký người dùng mới (Mock)."""
    if checkUserNameExists(username):
        return False, "Tên đăng nhập đã tồn tại."
    
    # Giả lập tạo ID
    new_user_id = str(uuid.uuid4()) 
    MOCK_USERS[username] = {
        "password": password,
        "role": "pos", # Mặc định người dùng đăng ký là POS (nhân viên)
        "fullname": fullname,
        "phone": phone,
        "address": address
    }
    print(f"User registered: {username}, Role: pos, ID: {new_user_id}")
    return True, f"Đăng ký tài khoản '{username}' thành công! (ID: {new_user_id})"

# ====================================================================
# --- LỚP ỨNG DỤNG CHÍNH (MAIN APPLICATION) ---
# ====================================================================

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Ứng dụng Quản lý Bán hàng Tkinter")
        self.geometry("1000x750")
        self.minsize(600, 400)

        # Container chứa tất cả các frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}    
        
        # Danh sách các trang
        for F in (LoginPage, RegisterPage, AdminPage, POSPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        """Hiển thị một frame cụ thể"""
        frame = self.frames[page_name]
        frame.tkraise()

# ====================================================================
# --- KHU VỰC TRANG CHỨC NĂNG (MOCK) ---
# ====================================================================

class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(self, bg="white")
        content_frame.grid(row=0, column=0)
        
        tk.Label(content_frame, text="TRANG QUẢN TRỊ (ADMIN)", font=("Helvetica", 36, "bold"), fg="#E50019", bg="white").pack(pady=50)
        ttk.Button(content_frame, text="Đăng xuất", command=lambda: controller.show_frame("LoginPage")).pack(pady=20)

class POSPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(self, bg="white")
        content_frame.grid(row=0, column=0)
        
        tk.Label(content_frame, text="TRANG BÁN HÀNG (POS)", font=("Helvetica", 36, "bold"), fg="#007bff", bg="white").pack(pady=50)
        ttk.Button(content_frame, text="Đăng xuất", command=lambda: controller.show_frame("LoginPage")).pack(pady=20)
        
# ====================================================================
# --- 1. LỚP ĐĂNG NHẬP (ĐÃ SỬA DỤNG GRID CHO CĂN GIỮA) ---
# ====================================================================

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- CẤU HÌNH STYLE HIỆN ĐẠI & MÀU SẮC ---
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # MÀU SẮC 
        self.COLOR_BG = "white"
        self.COLOR_PRIMARY = "#E50019" # Màu Đỏ tươi mạnh mẽ
        self.COLOR_TEXT = "#333333"
        self.COLOR_HINT = "#AAAAAA"
        
        self.config(bg=self.COLOR_BG) 

        # Cấu hình Styles (Unchanged)
        style.configure("Modern.Title.TLabel", font=("Helvetica", 24, "bold"), foreground=self.COLOR_PRIMARY, background=self.COLOR_BG)
        style.configure("Modern.TLabel", font=("Helvetica", 12), foreground=self.COLOR_TEXT, background=self.COLOR_BG)
        style.configure("Modern.TEntry", font=("Helvetica", 12), padding=[5, 8], fieldbackground="white", selectbackground=self.COLOR_PRIMARY, relief="flat")
        style.map("Modern.TEntry", fieldbackground=[('focus', 'white')])
        
        style.configure("Primary.TButton", font=("Helvetica", 14, "bold"), background=self.COLOR_PRIMARY, foreground="white", padding=10, relief="flat", focuscolor=self.COLOR_PRIMARY)
        style.map("Primary.TButton", background=[('active', '#CC0016')])
        style.configure("Secondary.TButton", font=("Helvetica", 11), background=self.COLOR_BG, foreground="#007bff", relief="flat")
        style.map("Secondary.TButton", foreground=[('active', self.COLOR_PRIMARY)], background=[('active', self.COLOR_BG)])

        # --- NEW CENTERING AND EXPANSION SETUP ---
        # Cấu hình frame cha (LoginPage) để mở rộng
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- KHUNG CHỨA TRUNG TÂM ---
        main_frame = tk.Frame(self, bg=self.COLOR_BG)
        # Thay thế place bằng grid để căn giữa. Sticky="" giữ kích thước frame,
        # trong khi weight=1 trên self cho phép vùng trống xung quanh mở rộng.
        main_frame.grid(row=0, column=0, padx=20, pady=20) 
        
        # Đảm bảo nội dung bên trong main_frame có thể mở rộng (để fill='x' hoạt động)
        main_frame.grid_columnconfigure(0, weight=1) 

        # 1. TIÊU ĐỀ
        ttk.Label(main_frame, text="Đăng nhập Hệ Thống", style="Modern.Title.TLabel").pack(pady=30) 

        # 2. TRƯỜNG NHẬP LIỆU
        input_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        input_frame.pack(padx=2, pady=10, fill='x') # Fill='x' để input_frame lấp đầy main_frame
        input_frame.grid_columnconfigure(0, weight=1)

        # Tên đăng nhập (Canvas container)
        ttk.Label(input_frame, text="Tên đăng nhập:", style="Modern.TLabel").pack(anchor='w', pady=(10, 2))
        # FIX: Pass '•' for password mask
        self.username_container = self.create_custom_entry(input_frame, "Nhập tên đăng nhập của bạn")
        self.username_container.pack(fill='x') 

        # Mật khẩu (Canvas container)
        ttk.Label(input_frame, text="Mật khẩu:", style="Modern.TLabel").pack(anchor='w', pady=(15, 2))
        # FIX: Pass '•' for password mask
        self.password_container = self.create_custom_entry(input_frame, "Nhập mật khẩu của bạn", show_char="•")
        self.password_container.pack(fill='x')

        # 3. NÚT CHÍNH (Đăng nhập)
        ttk.Button(main_frame, text="Đăng nhập", command=self.loginAction, 
                    style="Primary.TButton").pack(fill='x', padx=20, pady=(25, 5))

        # 4. NÚT PHỤ
        ttk.Button(main_frame, text="Đăng ký tài khoản mới", 
                    command=lambda: controller.show_frame("RegisterPage"), 
                    style="Secondary.TButton").pack(pady=5)
    
    # --- HÀM TẠO CUSTOM ENTRY (SỬA LỖI SHOW) ---
    def get_entry_widget(self, container):
        """Tìm và trả về widget Entry NẰM TRONG Canvas container."""
        for widget in container.winfo_children():
            if isinstance(widget, ttk.Entry):
                return widget
        return None

    # SỬ DỤNG show_char ĐỂ PASS KÝ TỰ CHE MẬT KHẨU
    def create_custom_entry(self, parent, placeholder, show_char=""):
        """Tạo Entry với Placeholder và viền mỏng (sử dụng Canvas) VÀ CỐ ĐỊNH KÍCH THƯỚC."""
        # Canvas là Container tạo viền
        container = tk.Canvas(parent, highlightthickness=1, highlightbackground=self.COLOR_HINT, 
                              bg="white", relief="flat", bd=0, height=40) 
        container.pack_propagate(False)
        
        # SỬ DỤNG show_char THAY VÌ HARDCODE show=25 HOẶC show="show"
        entry = ttk.Entry(container, style="Modern.TEntry", show=show_char)
        entry.pack(fill='both', expand=True, padx=2, pady=2)
        
        entry.insert(0, placeholder)
        entry.config(foreground=self.COLOR_HINT)
        # Truyền show_char vào hàm xử lý focus
        entry.bind("<FocusIn>", lambda e: self.on_focus_in(entry, placeholder, show_char))
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(entry, placeholder, show_char))
        
        return container

    def on_focus_in(self, entry, placeholder, show_char):
        """Xóa Placeholder khi click vào."""
        # Kiểm tra nếu đang là Placeholder
        if entry.get() == placeholder and entry.cget('show') == "":
            entry.delete(0, tk.END)
            # Thiết lập ký tự che mật khẩu nếu có (ví dụ: '•')
            entry.config(show=show_char) 
            entry.config(foreground=self.COLOR_TEXT)
        # Highlight viền Canvas
        entry.master.config(highlightbackground=self.COLOR_PRIMARY)

    def on_focus_out(self, entry, placeholder, show_char):
        """Hiện lại Placeholder khi không focus."""
        if not entry.get():
            entry.insert(0, placeholder)
            # Thiết lập show="" (không che) khi hiển thị placeholder
            entry.config(show="") 
            entry.config(foreground=self.COLOR_HINT)
        # Bỏ Highlight viền Canvas
        entry.master.config(highlightbackground=self.COLOR_HINT)
            
    # --- LOGIC ĐĂNG NHẬP (loginAction) ---
    def loginAction(self):
        # 1. Lấy Entry widget thực tế từ Canvas container
        username_entry_widget = self.get_entry_widget(self.username_container)
        password_entry_widget = self.get_entry_widget(self.password_container)

        # 2. Lấy dữ liệu
        username = username_entry_widget.get().strip()
        password = password_entry_widget.get()
        
        placeholder_u = "Nhập tên đăng nhập của bạn"
        placeholder_p = "Nhập mật khẩu của bạn"

        # 3. Kiểm tra Placeholder/rỗng
        if username == placeholder_u.strip() or not username:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên đăng nhập.")
            return

        # Kiểm tra nếu mật khẩu đang hiển thị placeholder (show="") hoặc rỗng
        is_password_placeholder = (password_entry_widget.cget('show') == "" and password == placeholder_p)
        if is_password_placeholder or not password.strip():
            messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu.")
            return
            
        # 4. GỌI HÀM KIỂM TRA CSDL
        role = checkLogin(username, password)
        
        if role:
            # Đăng nhập thành công
            if role.lower() == 'admin':
                messagebox.showinfo("Thành công", f"Đăng nhập thành công! Vai trò: {role}")
                self.controller.show_frame("AdminPage") 
            else:
                messagebox.showinfo("Thành công", f"Đăng nhập thành công! Vai trò: {role}")
                self.controller.show_frame("POSPage")
                
            # Xóa sạch Entry sau khi đăng nhập thành công
            username_entry_widget.delete(0, tk.END)
            password_entry_widget.delete(0, tk.END)
            self.on_focus_out(username_entry_widget, placeholder_u, "")
            self.on_focus_out(password_entry_widget, placeholder_p, "•")

        else:
            # Đăng nhập thất bại
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
            # Xóa mật khẩu sau khi thất bại
            password_entry_widget.delete(0, tk.END)
            # Quan trọng: Đảm bảo hiển thị lại placeholder sau khi xóa nội dung thất bại
            self.on_focus_out(password_entry_widget, placeholder_p, show_char="•")


# ====================================================================
# --- 2. LỚP ĐĂNG KÝ (ĐÃ SỬA LỖI SIZE) ---
# ====================================================================

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- CẤU HÌNH MÀU & STYLE ---
        style = ttk.Style(self)
        style.theme_use("clam")

        self.COLOR_BG = "white"
        self.COLOR_PRIMARY = "#E50019"
        self.COLOR_TEXT = "#333333"
        self.COLOR_HINT = "#AAAAAA"
        self.COLOR_SECONDARY = "#007BFF"
        self.ERROR_BG = '#F0D4D4'
        self.SUCCESS_BG = 'white'

        self.config(bg=self.COLOR_BG)

        # --- STYLE CHUNG (Đảm bảo đồng bộ) ---
        style.configure("Modern.Title.TLabel", font=("Helvetica", 24, "bold"), foreground=self.COLOR_PRIMARY, background=self.COLOR_BG)
        style.configure("Modern.TLabel", font=("Helvetica", 12), foreground=self.COLOR_TEXT, background=self.COLOR_BG)
        style.configure("Modern.TEntry", font=("Helvetica", 12), padding=[5, 8], fieldbackground="white", selectbackground=self.COLOR_PRIMARY, relief="flat")
        style.map("Modern.TEntry", fieldbackground=[('focus', 'white')])

        style.configure("Primary.TButton", font=("Helvetica", 14, "bold"), background=self.COLOR_PRIMARY, foreground="white", padding=[20, 10], relief="flat")
        style.map("Primary.TButton", background=[('active', '#CC0016')])
        style.configure("Secondary.TButton", font=("Helvetica", 11, "underline"), background=self.COLOR_BG, foreground=self.COLOR_SECONDARY, relief="flat")
        style.map("Secondary.TButton", foreground=[('active', self.COLOR_PRIMARY)], background=[('active', self.COLOR_BG)])
        
        # --- NEW CENTERING AND EXPANSION SETUP ---
        # Cấu hình frame cha (RegisterPage) để mở rộng
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- KHUNG CHÍNH ---
        main_frame = tk.Frame(self, bg=self.COLOR_BG)
        # Thay thế place bằng grid để căn giữa và cho phép form mở rộng
        main_frame.grid(row=0, column=0, padx=20, pady=20) 
        main_frame.grid_columnconfigure(0, weight=1) # Đảm bảo nội dung bên trong có thể mở rộng
        
        ttk.Label(main_frame, text="ĐĂNG KÝ TÀI KHOẢN", style="Modern.Title.TLabel").pack(pady=20)

        # --- KHUNG NHẬP LIỆU ---
        fields_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        fields_frame.pack(pady=10, padx=20, fill='x', expand=True)
        # Giữ nguyên grid layout bên trong fields_frame
        fields_frame.grid_columnconfigure(0, weight=1)

        fields_pairs = [
            # Sửa placeholder cho rõ ràng hơn, đặc biệt là username
            [("Tên đăng nhập (duy nhất)", "username", False, "Tên đăng nhập (ít nhất 6 ký tự)"),
             ("Địa chỉ", "address", False, "Nhập địa chỉ hiện tại")],

            [("Mật khẩu", "password", True, "Mật khẩu của bạn"),
             ("Họ và tên", "fullname", False, "Nhập đầy đủ họ và tên")],

            [("Nhập lại mật khẩu", "re_password", True, "Nhập lại mật khẩu"),
             ("Điện thoại", "phone", False, "Nhập số điện thoại")]
        ]

        self.fields = {}
        row_counter = 0

        for pair in fields_pairs:
            pair_frame = tk.Frame(fields_frame, bg=self.COLOR_BG)
            pair_frame.grid(row=row_counter, column=0, pady=5, sticky="ew")
            # Cấu hình column weights để 2 cột chia đôi chiều rộng của fields_frame
            pair_frame.grid_columnconfigure(0, weight=1)
            pair_frame.grid_columnconfigure(1, weight=1)

            col_counter = 0
            for label_text, key, is_password, placeholder in pair:
                field_container = tk.Frame(pair_frame, bg=self.COLOR_BG)
                field_container.grid(row=0, column=col_counter, padx=15, pady=10, sticky="ew") # Giảm padx để tăng không gian
                field_container.grid_columnconfigure(0, weight=1)

                ttk.Label(field_container, text=f"{label_text}:", style="Modern.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 2))
                
                show_char = "•" if is_password else ""
                
                # SỬ DỤNG HÀM TẠO CUSTOM ENTRY MỚI (Canvas Wrapper)
                entry_container = self.create_custom_entry(field_container, placeholder, show_char)
                
                # Dùng sticky="ew" để lấp đầy chiều rộng của field_container (field_container đã có weight=1)
                entry_container.grid(row=1, column=0, sticky="ew") 
                
                self.fields[key] = entry_container
                
                entry_widget = self.get_entry_widget(entry_container)

                if key == "username":
                    entry_widget.bind("<KeyRelease>", self.check_unique_input)
                elif key == "re_password":
                    entry_widget.bind("<KeyRelease>", self.check_password_match)
                    # Bind KeyRelease cho cả trường mật khẩu
                    self.get_entry_widget(self.fields["password"]).bind("<KeyRelease>", self.check_password_match)
                    
                col_counter += 1

            row_counter += 1

        # --- NÚT ĐĂNG KÝ ---
        ttk.Button(main_frame, text="Đăng ký", command=self.register_action,
                   style="Primary.TButton").pack(pady=(30, 5), padx=40, fill='x')

        # --- NÚT QUAY LẠI ---
        ttk.Button(main_frame, text="Quay lại Đăng nhập",
                   command=lambda: controller.show_frame("LoginPage"),
                   style="Secondary.TButton").pack(pady=5)
                   
    # ------------------- HÀM HELPER (ĐÃ ĐỒNG BỘ VÀ FIX KÍCH THƯỚC) -------------------
    
    def get_entry_widget(self, container):
        """Tìm và trả về widget Entry NẰM TRONG Canvas container."""
        for widget in container.winfo_children():
            if isinstance(widget, ttk.Entry):
                return widget
        return None

    def create_custom_entry(self, parent, placeholder, show_char=""):
        """Tạo Entry với Placeholder và viền mỏng (sử dụng Canvas) VÀ CỐ ĐỊNH KÍCH THƯỚC."""
        container = tk.Canvas(parent, highlightthickness=1, highlightbackground=self.COLOR_HINT, 
                              bg="white", relief="flat", bd=0, height=40)
        container.pack_propagate(False) # Ngăn Canvas thay đổi kích thước theo Entry
        
        # SỬ DỤNG show_char ĐỂ PASS KÝ TỰ CHE MẬT KHẨU
        entry = ttk.Entry(container, style="Modern.TEntry", show=show_char)
        entry.pack(fill='both', expand=True, padx=2, pady=2)
        
        entry.insert(0, placeholder)
        entry.config(foreground=self.COLOR_HINT)
        entry.bind("<FocusIn>", lambda e: self.on_focus_in(entry, placeholder, show_char))
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(entry, placeholder, show_char))
        
        return container

    def on_focus_in(self, entry, placeholder, show_char):
        """Xóa Placeholder khi click vào."""
        if entry.get() == placeholder and entry.cget('show') == "":
            entry.delete(0, tk.END)
            entry.config(show=show_char)
            entry.config(foreground=self.COLOR_TEXT)
        entry.master.config(highlightbackground=self.COLOR_PRIMARY)

    def on_focus_out(self, entry, placeholder, show_char):
        """Hiện lại Placeholder khi không focus."""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(show="") # Thiết lập show="" (không che) khi hiển thị placeholder
            entry.config(foreground=self.COLOR_HINT)
        entry.master.config(highlightbackground=self.COLOR_HINT)
    
    # ------------------- KIỂM TRA MẬT KHẨU -------------------
    def check_password_match(self, event=None):
        widget_p = self.get_entry_widget(self.fields['password'])
        widget_rp = self.get_entry_widget(self.fields['re_password'])
        
        password = widget_p.get()
        re_password = widget_rp.get()

        is_p_placeholder = (widget_p.cget('show') == "" and password == "Mật khẩu của bạn")
        is_rp_placeholder = (widget_rp.cget('show') == "" and re_password == "Nhập lại mật khẩu")

        # Bỏ qua kiểm tra nếu đang là placeholder
        if is_p_placeholder and is_rp_placeholder:
            widget_p.config(fieldbackground=self.SUCCESS_BG)
            widget_rp.config(fieldbackground=self.SUCCESS_BG)
            return

        if password == re_password and len(password) > 0:
            widget_p.config(fieldbackground=self.SUCCESS_BG)
            widget_rp.config(fieldbackground=self.SUCCESS_BG)
        else:
            widget_p.config(fieldbackground=self.ERROR_BG)
            widget_rp.config(fieldbackground=self.ERROR_BG)

    # ------------------- KIỂM TRA TÊN DUY NHẤT -------------------
    def check_unique_input(self, event):
        widget = event.widget 
        input_value = widget.get().strip()
        
        placeholder = "Tên đăng nhập (ít nhất 6 ký tự)"

        # Kiểm tra nếu đang là placeholder hoặc rỗng
        is_placeholder = (widget.cget('show') == "" and input_value == placeholder) or not input_value.strip()

        if is_placeholder:
            widget.config(fieldbackground=self.SUCCESS_BG)
            return

        is_duplicate = checkUserNameExists(input_value)
        if is_duplicate:
            widget.config(fieldbackground=self.ERROR_BG)
        else:
            widget.config(fieldbackground=self.SUCCESS_BG)
            
    # ------------------- ĐĂNG KÝ NGƯỜI DÙNG -------------------
    def register_action(self):
        data = {}
        re_password_value = ""
        
        placeholders = {
            'username': "Tên đăng nhập (ít nhất 6 ký tự)",
            'address': "Nhập địa chỉ hiện tại",
            'password': "Mật khẩu của bạn",
            'fullname': "Nhập đầy đủ họ và tên",
            're_password': "Nhập lại mật khẩu",
            'phone': "Nhập số điện thoại"
        }

        # 1. Lấy và làm sạch dữ liệu
        for k, container in self.fields.items():
            entry_widget = self.get_entry_widget(container)
            value = entry_widget.get().strip()
            placeholder = placeholders[k]
            
            # Kiểm tra nếu giá trị là placeholder hoặc rỗng
            is_empty_or_placeholder = (entry_widget.cget('show') == "" and value == placeholder) or not value
            
            if k == 're_password':
                re_password_value = "" if is_empty_or_placeholder else value
                continue
            
            data[k] = "" if is_empty_or_placeholder else value

        # 2. Kiểm tra dữ liệu trống
        if not all(data.values()) or not re_password_value:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        # 3. Kiểm tra tên trùng
        if checkUserNameExists(data['username']):
            messagebox.showerror("Lỗi", "Tên đăng nhập đã bị trùng. Vui lòng sửa lại.")
            self.get_entry_widget(self.fields['username']).config(fieldbackground=self.ERROR_BG)
            return

        # 4. Kiểm tra mật khẩu khớp
        if data['password'] != re_password_value:
            messagebox.showerror("Lỗi", "Mật khẩu và Nhập lại mật khẩu không khớp.")
            self.check_password_match() # Highlight lỗi
            return
            
        # 5. Kiểm tra độ dài mật khẩu tối thiểu (nên có)
        if len(data['password']) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự.")
            self.get_entry_widget(self.fields['password']).config(fieldbackground=self.ERROR_BG)
            return

        # 6. Gọi hàm đăng ký
        success, message = registerUser(
            None,
            data['username'],
            data['password'],
            data['fullname'],
            data['phone'],
            data['address']
        )

        if success:
            messagebox.showinfo("Thành công", message)
            
            # Xóa các trường sau khi đăng ký thành công
            for k, container in self.fields.items():
                entry_widget = self.get_entry_widget(container)
                entry_widget.delete(0, tk.END)
                # Đảm bảo placeholder và show status được reset
                placeholder_text = placeholders[k]
                show_char = "•" if k in ['password', 're_password'] else ""
                self.on_focus_out(entry_widget, placeholder_text, show_char) 
            
            # Chuyển về trang Đăng nhập
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror("Lỗi", message)


if __name__ == "__main__":
    app = App()
    app.mainloop()

