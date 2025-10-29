import tkinter as tk
from tkinter import messagebox
# Chỉ cần registerUser và checkUserNameExists
from Database.dbUsers import registerUser, checkUserNameExists 
import uuid

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Thiết lập kích thước tối thiểu cho cửa sổ để chứa giao diện 2 cột
        # Bạn có thể điều chỉnh 600x400 cho phù hợp với ứng dụng tổng thể
        # Lưu ý: Lệnh này thường đặt ở cửa sổ root, nhưng có thể dùng để gợi ý kích thước
        # Tạm thời bỏ qua việc đặt kích thước cố định ở đây nếu bạn sử dụng controller
        # để quản lý cửa sổ root, nhưng giao diện sẽ rộng ra.

        tk.Label(self, text="ĐĂNG KÝ TÀI KHOẢN", font=("Times New Roman", 24), fg="red").pack(pady=20)
        
        # Khung nhập liệu (container chính cho các Label/Entry)
        fields_frame = tk.Frame(self)
        fields_frame.pack(pady=10, padx=20) # Thêm padx để có lề hai bên

        self.fields = {}
        
        # Danh sách dữ liệu
        labels = ["Tên đăng nhập", "Mật khẩu", "Nhập lại Mật khẩu", "Họ và tên", "Điện thoại", "Địa chỉ"]
        keys = ["username", "password", "confirm_password", "fullname", "phone", "address"]
        
        # --- LOGIC CHIA THÀNH 2 CỘT ---
        # 3 trường đầu (0, 1, 2) sẽ ở Cột 0 (Label: 0, Entry: 1)
        # 3 trường sau (3, 4, 5) sẽ ở Cột 2 (Label: 2, Entry: 3)

        num_fields = len(keys) # 6 trường
        
        for i, (label_text, key) in enumerate(zip(labels, keys)):
            
            # Xác định vị trí (Row và Column)
            if i < num_fields / 2: # 3 trường đầu (i = 0, 1, 2)
                current_row = i
                label_column = 0
                entry_column = 1
            else: # 3 trường sau (i = 3, 4, 5)
                current_row = i - int(num_fields / 2) # Row 0, 1, 2
                label_column = 2
                entry_column = 3

            # 1. Tạo Label
            tk.Label(fields_frame, text=f"{label_text}:", font=("Times New Roman", 15)).grid(
                row=current_row, column=label_column, sticky="w", padx=(30, 5), pady=10
            )
            
            # 2. Tạo Entry
            # Giữ nguyên width để cả hai cột trông đồng đều.
            entry_width = 30
            if key in ["password", "confirm_password"]:
                entry = tk.Entry(fields_frame, width=entry_width, show="*")
            else:
                entry = tk.Entry(fields_frame, width=entry_width)
                
            # GẮN SỰ KIỆN: Kiểm tra duy nhất theo thời gian thực (chỉ cho username)
            if key == "username":
                entry.bind("<KeyRelease>", self.check_unique_input)
                
            entry.grid(row=current_row, column=entry_column, padx=(5, 30), pady=10)
            self.fields[key] = entry
            
        # Nút Đăng ký và Quay lại giờ sẽ ở dưới, căn giữa khung nhập liệu (columnspan=4)
        
        # Khung chứa nút để căn giữa dễ dàng hơn
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=20)

        # Nút Đăng ký
        tk.Button(buttons_frame, 
                  text="Đăng ký", 
                  font=("Times New Roman", 15), 
                  command=self.register_action, 
                  width=20,
                  bg="red",
                  fg="white"
        ).pack(pady=30)
        
        # Nút Quay lại
        tk.Button(buttons_frame, 
                  text="Quay lại Đăng nhập", 
                  font=("Times New Roman", 13),
                  width=17,

                  command=lambda: controller.show_frame("LoginPage"),
                  relief="flat", borderwidth=0

        ).pack(pady=10)



        

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