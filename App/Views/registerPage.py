import tkinter as tk
from tkinter import messagebox
# Chỉ cần registerUser và checkUserNameExists
from Database.dbUsers import registerUser, checkUserNameExists 
import uuid

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        # 1. --- THIẾT LẬP NỀN CHÍNH ---
        tk.Frame.__init__(self, parent, bg="#FFF8F0") 
        self.controller = controller
        
        # 2. --- TIÊU ĐỀ ĐỒNG BỘ ---
        tk.Label(
            self, text="🍇 ĐĂNG KÝ TÀI KHOẢN", 
            font=("Times New Roman", 24, "bold"), 
            fg="#8B0000", # Màu đỏ rượu
            bg="#FFF8F0"
        ).pack(pady=20)
        
        # Khung nhập liệu (container chính cho các Label/Entry)
        fields_frame = tk.Frame(self, bg="#FFF8F0") # Nền đồng bộ
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
                current_row = i - int(num_fields / 2) # Row 0, 1, 2
                label_column = 2
                entry_column = 3

            # 3. --- LABEL ĐỒNG BỘ ---
            tk.Label(
                fields_frame, text=f"{label_text}:", 
                font=("Times New Roman", 15),
                fg="#5C2E0C", # Màu chữ nâu
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
                
            # GẮN SỰ KIỆN: Kiểm tra duy nhất (Giữ nguyên)
            if key == "username":
                entry.bind("<KeyRelease>", self.check_unique_input)
                
            entry.grid(row=current_row, column=entry_column, padx=(5, 30), pady=10)
            self.fields[key] = entry
            
        # Khung chứa nút
        buttons_frame = tk.Frame(self, bg="#FFF8F0") # Nền đồng bộ
        buttons_frame.pack(pady=20)

        # 5. --- NÚT ĐĂNG KÝ ĐỒNG BỘ ---
        tk.Button(
            buttons_frame, 
            text="Đăng ký", 
            font=("Times New Roman", 15, "bold"), # Thêm bold
            command=self.register_action, 
            width=20,
            bg="#A52A2A", # Màu nút nâu đỏ
            fg="white",
            relief="flat" # Đồng bộ
        ).pack(pady=30)
        
        # 6. --- NÚT QUAY LẠI ĐỒNG BỘ (Style link) ---
        tk.Button(
            buttons_frame, 
            text="Quay lại Đăng nhập", 
            font=("Times New Roman", 13, "underline"), # Thêm gạch chân
            command=lambda: controller.show_frame("LoginPage"),
            fg="#5C2E0C", # Màu chữ nâu
            bg="#FFF8F0",
            relief="flat", 
            borderwidth=0,
            cursor="hand2" # Đổi con trỏ
        ).pack(pady=10)



#  LOGIC XỬ LÝ Ở DƯỚI ĐÂY  #

        

    # --- HÀM KIỂM TRA DUY NHẤT REAL-TIME (CHỈ CHO USERNAME) ---
    def check_unique_input(self, event):
        """Kiểm tra tính duy nhất của Tên đăng nhập ngay khi gõ."""
        widget = event.widget
        input_value = widget.get()
        
        if not input_value:
            widget.config(bg='white')
            return

        is_duplicate = False
        
        if checkUserNameExists(input_value):
            is_duplicate = True
        
        if is_duplicate:
            widget.config(bg='lightcoral') 
        else:
            widget.config(bg='white')

    # --- HÀM XỬ LÝ ĐĂNG KÝ (FIXED) ---
    def register_action(self):
        data = {k: e.get() for k, e in self.fields.items()}
        
        # 1. KIỂM TRA ĐẦY ĐỦ THÔNG TIN
        if not all(data.values()):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        # 2. KIỂM TRA MẬT KHẨU KHỚP NHAU
        if data['password'] != data['confirm_password']:
            messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp. Vui lòng kiểm tra lại.")
            self.fields['password'].delete(0, tk.END)
            self.fields['confirm_password'].delete(0, tk.END)
            return

        # 3. KIỂM TRA TÊN ĐĂNG NHẬP TRÙNG LẶP (Kiểm tra cuối cùng)
        if self.fields['username'].cget('bg') == 'lightcoral':
           messagebox.showerror("Lỗi", "Tên đăng nhập đã bị trùng. Vui lòng sửa lại.")
           return

        # 4. GỌI HÀM ĐĂNG KÝ
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
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror("Lỗi", message)

    def on_show_frame(self):
        """Hàm này sẽ được controller gọi khi trang này được hiển thị."""
        # Đặt kích thước cửa sổ mong muốn (Rộng x Cao)
        # Bạn có thể thử nghiệm các giá trị này, ví dụ: 450x550 hoặc 400x500
        self.controller.geometry("800x500")