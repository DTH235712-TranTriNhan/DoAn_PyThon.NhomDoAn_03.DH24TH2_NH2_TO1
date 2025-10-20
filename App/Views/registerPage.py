import tkinter as tk
from tkinter import messagebox
# Chỉ cần registerUser và checkUserNameExists
from Database.dbUsers import registerUser, checkUserNameExists 
import uuid

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 24)).pack(pady=20)
        
        # Khung nhập liệu
        fields_frame = tk.Frame(self)
        fields_frame.pack(pady=10)

        self.fields = {}
        # Đã loại bỏ "Mã Nhân viên" khỏi labels
        labels = ["Tên đăng nhập", "Mật khẩu", "Họ và tên", "Điện thoại", "Địa chỉ"]
        # Đã loại bỏ "user_id" khỏi keys
        keys = ["username", "password", "fullname", "phone", "address"]

        for i, (label_text, key) in enumerate(zip(labels, keys)):
            tk.Label(fields_frame, text=f"{label_text}:", font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            
            # Xóa logic cho user_id đã ẩn
            if key == "password":
                entry = tk.Entry(fields_frame, width=30, show="*")
            else:
                entry = tk.Entry(fields_frame, width=30)
                
            # GẮN SỰ KIỆN: Kiểm tra duy nhất theo thời gian thực (chỉ cho username)
            if key == "username":
                entry.bind("<KeyRelease>", self.check_unique_input)
                
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.fields[key] = entry
            
        # Nút Đăng ký
        tk.Button(self, text="Đăng ký", font=("Arial", 12), command=self.register_action, width=20).pack(pady=20)
        
        # Nút Quay lại
        tk.Button(self, text="Quay lại Đăng nhập", command=lambda: controller.show_frame("LoginPage")).pack()

    # --- HÀM KIỂM TRA DUY NHẤT REAL-TIME (CHỈ CHO USERNAME) ---
    def check_unique_input(self, event):
        """Kiểm tra tính duy nhất của Tên đăng nhập ngay khi gõ."""
        widget = event.widget
        input_value = widget.get()
        
        # Bỏ qua nếu trường rỗng
        if not input_value:
            widget.config(bg='white')
            return

        is_duplicate = False
        
        # CHỈ CẦN KIỂM TRA USERNAME
        if checkUserNameExists(input_value):
            is_duplicate = True
        
        if is_duplicate:
            widget.config(bg='lightcoral') 
        else:
            widget.config(bg='white')

    # --- HÀM XỬ LÝ ĐĂNG KÝ (FIXED) ---
    def register_action(self):
        # Lấy dữ liệu từ các trường
        data = {k: e.get() for k, e in self.fields.items()}
        
        if not all(data.values()):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        # KIỂM TRA CUỐI CÙNG TRƯỚC KHI GỌI CSDL (Chỉ kiểm tra username)
        if self.fields['username'].cget('bg') == 'lightcoral':
           messagebox.showerror("Lỗi", "Tên đăng nhập đã bị trùng. Vui lòng sửa lại.")
           return

        # Gọi hàm registerUser và truyền None cho user_id (để hàm CSDL tự tạo)
        success, message = registerUser(
            None, # <--- TRUYỀN NONE: BÁO CHO HÀM CSDL TỰ TẠO USER_ID
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
            # HIỂN THỊ THÔNG BÁO LỖI CỤ THỂ
            messagebox.showerror("Lỗi", message)