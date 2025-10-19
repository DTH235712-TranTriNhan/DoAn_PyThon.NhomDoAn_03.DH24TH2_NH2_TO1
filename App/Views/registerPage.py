import tkinter as tk
from tkinter import messagebox
from Database.dbUsers import registerUser, checkUserIDExists, checkUserNameExists # Cần thêm 2 hàm check mới
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
        labels = ["Mã Nhân viên", "Tên đăng nhập", "Mật khẩu", "Họ và tên", "Điện thoại", "Địa chỉ"]
        keys = ["user_id", "username", "password", "fullname", "phone", "address"]

        for i, (label_text, key) in enumerate(zip(labels, keys)):
            tk.Label(fields_frame, text=f"{label_text}:", font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            
            # Ẩn mật khẩu
            if key == "password":
                entry = tk.Entry(fields_frame, width=30, show="*")
            # Gợi ý tạo mã tự động cho user_id
            elif key == "user_id":
                entry = tk.Entry(fields_frame, width=30)
                entry.insert(0, str(uuid.uuid4())[:8].upper())
            else:
                entry = tk.Entry(fields_frame, width=30)
                
            # GẮN SỰ KIỆN: Kiểm tra duy nhất theo thời gian thực
            if key in ["user_id", "username"]:
                entry.bind("<KeyRelease>", self.check_unique_input)
                
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.fields[key] = entry
            
        # Nút Đăng ký
        tk.Button(self, text="Đăng ký", font=("Arial", 12), command=self.register_action, width=20).pack(pady=20)
        
        # Nút Quay lại
        tk.Button(self, text="Quay lại Đăng nhập", command=lambda: controller.show_frame("LoginPage")).pack()

    # --- HÀM KIỂM TRA DUY NHẤT REAL-TIME ---
    def check_unique_input(self, event):
        """Kiểm tra tính duy nhất của Mã Nhân viên và Tên đăng nhập ngay khi gõ."""
        widget = event.widget
        input_value = widget.get()
        
        # Bỏ qua nếu trường rỗng
        if not input_value:
            widget.config(bg='white')
            return

        is_duplicate = False
        message = ""
        
        if widget == self.fields['user_id']:
            if checkUserIDExists(input_value):
                is_duplicate = True
                message = "Mã Nhân viên này đã tồn tại!"
        
        elif widget == self.fields['username']:
            if checkUserNameExists(input_value):
                is_duplicate = True
                message = "Tên đăng nhập này đã tồn tại!"
                
        if is_duplicate:
            widget.config(bg='lightcoral') 
            # Không cần messagebox.showwarning liên tục, chỉ cần đổi màu
            # messagebox.showwarning("Cảnh báo Trùng lặp", message) 
        else:
            widget.config(bg='white')

    # --- HÀM XỬ LÝ ĐĂNG KÝ (FIXED) ---
    def register_action(self):
        # Lấy dữ liệu từ các trường
        data = {k: e.get() for k, e in self.fields.items()}
        
        if not all(data.values()):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        # KIỂM TRA CUỐI CÙNG TRƯỚC KHI GỌI CSDL (Dựa vào màu nền để kiểm tra trực quan)
        if self.fields['user_id'].cget('bg') == 'lightcoral' or \
           self.fields['username'].cget('bg') == 'lightcoral':
            messagebox.showerror("Lỗi", "Mã Nhân viên hoặc Tên đăng nhập bị trùng. Vui lòng sửa lại.")
            return

        # SỬA: PHẢI NHẬN CẢ 'success' VÀ 'message'
        success, message = registerUser(
            data['user_id'], 
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
            # HIỂN THỊ THÔNG BÁO LỖI CỤ THỂ TỪ HÀM CSDL (Nếu có lỗi khác)
            messagebox.showerror("Lỗi", message)