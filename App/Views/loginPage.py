import tkinter as tk
# Bỏ 'import tkinter.ttk as ttk' vì chúng ta chỉ dùng tk cơ bản cho giao diện này
from tkinter import messagebox
from Database.dbUsers import checkLogin 

class LoginPage(tk.Frame):
    """Giao diện Đăng nhập với thiết kế cổ điển (theo yêu cầu)."""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- 1. THIẾT KẾ GIAO DIỆN (THEO MẪU THỨ 2) ---
        
        # Đặt màu nền cho Frame chính
        # Bạn có thể đổi "SystemButtonFace" thành "white" nếu muốn
        self.config(bg="SystemButtonFace") 

        # Khung chứa trung tâm để mọi thứ căn giữa
        main_frame = tk.Frame(self) 
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(main_frame, text="ĐĂNG NHẬP HỆ THỐNG", 
                 font=("Times New Roman", 24), 
                 fg="red").pack(pady=(0, 50)) # Thêm padding dưới
        
        # Tên đăng nhập
        tk.Label(main_frame, text="Tên đăng nhập:", 
                 font=("Times New Roman", 15)).pack(pady=5)
        self.username_entry = tk.Entry(main_frame, width=30, 
                                       font=("Times New Roman", 12))
        self.username_entry.pack(ipady=4) # Thêm padding bên trong cho cao hơn

        # Mật khẩu
        tk.Label(main_frame, text="Mật khẩu:", 
                 font=("Times New Roman", 15)).pack(pady=5)
        self.password_entry = tk.Entry(main_frame, width=30, show="*", 
                                       font=("Times New Roman", 12))
        self.password_entry.pack(ipady=4) # Thêm padding bên trong cho cao hơn

        # Nút Đăng nhập
        tk.Button(main_frame, 
                  text="Đăng nhập", 
                  font=("Times New Roman", 12, "bold"), 
                  command=self._login_action, # Giữ tên hàm logic gốc
                  width=20, 
                  bg="red", 
                  fg="white",
                   pady=5).pack(pady=20)
        
        
        
         
        
        # Nút Đăng ký
        tk.Button(main_frame, text="Đăng ký tài khoản mới", 
                  font=("Times New Roman", 11),
                  command=lambda: controller.show_frame("RegisterPage"),
                  relief="flat", borderwidth=0).pack()
        
        

        # Bind phím Enter để đăng nhập
        self.username_entry.bind("<Return>", self._login_on_enter)
        self.password_entry.bind("<Return>", self._login_on_enter)


    # ----------------------------------------------------------------------
    # --- LOGIC ĐĂNG NHẬP (GIỮ TỪ CODE GỐC CỦA BẠN) ---
    # ----------------------------------------------------------------------

    def _login_on_enter(self, event=None):
        """Hàm hỗ trợ gọi đăng nhập khi nhấn Enter."""
        self._login_action()

    def _login_action(self):
        """Xử lý logic đăng nhập: Lấy data, kiểm tra rỗng, gọi CSDL và điều hướng."""
        
        # 1. Lấy giá trị trực tiếp từ tk.Entry
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # 2. Kiểm tra rỗng (đơn giản hơn vì không có placeholder)
        if not username:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên đăng nhập.")
            self.username_entry.focus_set()
            return

        if not password:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu.")
            self.password_entry.focus_set()
            return
            
        # 3. GỌI HÀM KIỂM TRA CSDL (Giữ nguyên logic gốc của bạn)
        # Giả định checkLogin trả về (user_id, role)
        user_id, role = checkLogin(username, password) 
        
        if role:
            # Lấy instance của trang POS và cập nhật trạng thái user
            # (Giữ nguyên logic gốc của bạn)
            try:
                pos_page_instance = self.controller.frames["POSPage"]
                pos_page_instance.update_user_status(user_id, username, role)
            except KeyError:
                print("Lưu ý: Không tìm thấy 'POSPage'. Bỏ qua việc cập nhật trạng thái.")
            except AttributeError:
                 print("Lưu ý: 'POSPage' không có hàm 'update_user_status'. Bỏ qua.")

            # Xóa trường nhập liệu sau khi thành công
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            
            # Đăng nhập thành công
            if role.lower() == 'admin':
                self.controller.show_frame("AdminPage") 
            else:
                self.controller.show_frame("POSPage")
        else:
            # Đăng nhập thất bại
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
            
            # Xóa mật khẩu sau khi thất bại
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
