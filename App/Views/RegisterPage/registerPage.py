import tkinter as tk
from tkinter import messagebox
from .registerLogic import check_unique_input, register_action


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        # 1. --- THIẾT LẬP NỀN CHÍNH ---
        tk.Frame.__init__(self, parent, bg="#FFF8F0") 
        self.controller = controller
        
        # 2. --- TIÊU ĐỀ ĐỒNG BỘ ---
        tk.Label(
            self, text="🍇 ĐĂNG KÝ TÀI KHOẢN", 
            font=("Times New Roman", 24, "bold"), 
            fg="#8B0000",
            bg="#FFF8F0"
        ).pack(pady=20)
        
        # Khung nhập liệu (container chính cho các Label/Entry)
        fields_frame = tk.Frame(self, bg="#FFF8F0")
        fields_frame.pack(pady=10, padx=20) 

        self.fields = {}
        
        # Danh sách dữ liệu
        labels = ["Tên đăng nhập", "Mật khẩu", "Nhập lại Mật khẩu", "Họ và tên", "Điện thoại", "Địa chỉ"]
        keys = ["username", "password", "confirm_password", "fullname", "phone", "address"]
        
        # --- LOGIC CHIA THÀNH 2 CỘT (Giữ nguyên) ---
        num_fields = len(keys) 
        
        for i, (label_text, key) in enumerate(zip(labels, keys)):
            
            # Xác định vị trí (Row và Column)
            if i < num_fields / 2: # 3 trường đầu
                current_row = i
                label_column = 0
                entry_column = 1
            else: # 3 trường sau
                current_row = i - int(num_fields / 2)
                label_column = 2
                entry_column = 3

            # 3. --- LABEL ĐỒNG BỘ ---
            tk.Label(
                fields_frame, text=f"{label_text}:", 
                font=("Times New Roman", 15),
                fg="#5C2E0C",
                bg="#FFF8F0"
            ).grid(
                row=current_row, column=label_column, sticky="w", padx=(30, 5), pady=10
            )
            
            # 4. --- ENTRY ĐỒNG BỘ ---
            entry_width = 30
            entry_font = ("Times New Roman", 11)
            
            if key in ["password", "confirm_password"]:
                entry = tk.Entry(
                    fields_frame, width=entry_width, show="*",
                    font=entry_font, relief="solid", bd=1
                )
            else:
                entry = tk.Entry(
                    fields_frame, width=entry_width,
                    font=entry_font, relief="solid", bd=1
                )
                
            # GẮN SỰ KIỆN: Kiểm tra duy nhất (Chuyển sang hàm mới)
            if key == "username":
                entry.bind("<KeyRelease>", self._check_unique_wrapper) # Gọi hàm wrapper
                
            entry.grid(row=current_row, column=entry_column, padx=(5, 30), pady=10)
            self.fields[key] = entry
            
        # Khung chứa nút
        buttons_frame = tk.Frame(self, bg="#FFF8F0")
        buttons_frame.pack(pady=20)

        # 5. --- NÚT ĐĂNG KÝ ĐỒNG BỘ ---
        tk.Button(
            buttons_frame, 
            text="Đăng ký", 
            font=("Times New Roman", 15, "bold"),
            command=self._register_wrapper, # Gọi hàm wrapper
            width=20,
            bg="#A52A2A",
            fg="white",
            relief="flat"
        ).pack(pady=30)
        
        # 6. --- NÚT QUAY LẠI ĐỒNG BỘ (Style link) ---
        tk.Button(
            buttons_frame, 
            text="Quay lại Đăng nhập", 
            font=("Times New Roman", 13, "underline"),
            command=lambda: controller.show_frame("LoginPage"),
            fg="#5C2E0C",
            bg="#FFF8F0",
            relief="flat", 
            borderwidth=0,
            cursor="hand2"
        ).pack(pady=10)


    # ----------------------------------------------------------------------
    # --- WRAPPER VÀ EVENT HANDLER (GỌI HÀM LOGIC) ---
    # ----------------------------------------------------------------------

    def _check_unique_wrapper(self, event):
        """Wrapper gọi hàm check_unique_input từ file logic."""
        widget = event.widget
        input_value = widget.get()
        # 💡 GỌI HÀM LOGIC ĐÃ TÁCH
        check_unique_input(input_value, widget)

    def _register_wrapper(self):
        """Wrapper gọi hàm register_action từ file logic."""
        # 💡 GỌI HÀM LOGIC ĐÃ TÁCH
        register_action(self.controller, self.fields)
        
    def on_show_frame(self):
        """Hàm này sẽ được controller gọi khi trang này được hiển thị."""
        # Đặt kích thước cửa sổ mong muốn (Rộng x Cao)
        self.controller.state('zoomed')
        # Focus vào trường username
        self.fields['username'].focus_set()