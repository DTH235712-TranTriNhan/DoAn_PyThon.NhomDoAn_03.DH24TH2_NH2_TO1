import tkinter as tk
# Bỏ 'import tkinter.ttk as ttk' vì chúng ta chỉ dùng tk cơ bản cho giao diện này
from tkinter import messagebox
from Database.dbUsers import checkLogin 

class LoginPage(tk.Frame):
    """Giao diện Đăng nhập với thiết kế cổ điển (theo yêu cầu)."""
    
    import tkinter as tk
# Bỏ 'import tkinter.ttk as ttk' vì chúng ta chỉ dùng tk cơ bản cho giao diện này
from tkinter import messagebox
from Database.dbUsers import checkLogin 

class LoginPage(tk.Frame):
    """Giao diện Đăng nhập với thiết kế đồng bộ RubyOak."""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- 1. THIẾT KẾ GIAO DIỆN (ĐỒNG BỘ VỚI POSPAGE) ---
        
        # Đặt màu nền cho Frame chính
        self.config(bg="#FFF8F0") # Nền be/kem

        # Khung chứa trung tâm để mọi thứ căn giữa
        main_frame = tk.Frame(self, bg="#FFF8F0") # Nền đồng bộ
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(
            main_frame, text="🍇 ĐĂNG NHẬP HỆ THỐNG", 
            font=("Times New Roman", 24, "bold"), 
            fg="#8B0000", # Màu đỏ rượu (header)
            bg="#FFF8F0"  # Nền đồng bộ
        ).pack(pady=(0, 50)) # Thêm padding dưới
        
        # Tên đăng nhập
        tk.Label(
            main_frame, text="Tên đăng nhập:", 
            font=("Times New Roman", 15),
            fg="#5C2E0C", # Màu chữ nâu
            bg="#FFF8F0"
        ).pack(pady=5)
        
        self.username_entry = tk.Entry(
            main_frame, width=30, 
            font=("Times New Roman", 12),
            relief="solid", bd=1 # Viền rõ ràng
        )
        self.username_entry.pack(ipady=4) # Thêm padding bên trong cho cao hơn

        # Mật khẩu
        tk.Label(
            main_frame, text="Mật khẩu:", 
            font=("Times New Roman", 15),
            fg="#5C2E0C",
            bg="#FFF8F0"
        ).pack(pady=5)
        
        self.password_entry = tk.Entry(
            main_frame, width=30, show="*", 
            font=("Times New Roman", 12),
            relief="solid", bd=1 # Viền rõ ràng
        )
        self.password_entry.pack(ipady=4) # Thêm padding bên trong cho cao hơn

        # Nút Đăng nhập
        tk.Button(
            main_frame, 
            text="Đăng nhập", 
            font=("Times New Roman", 12, "bold"), 
            command=self._login_action, # Giữ tên hàm logic gốc
            width=20, 
            bg="#A52A2A", # Màu nút nâu đỏ
            fg="white",
            relief="flat", # Đồng bộ
            pady=5
        ).pack(pady=20)
        
        # Nút Đăng ký (Style như link)
        tk.Button(
            main_frame, text="Đăng ký tài khoản mới", 
            font=("Times New Roman", 11, "underline"), # Thêm gạch chân
            command=lambda: controller.show_frame("RegisterPage"),
            fg="#5C2E0C", # Màu chữ nâu
            bg="#FFF8F0",
            relief="flat", 
            borderwidth=0,
            cursor="hand2" # Đổi con trỏ
        ).pack()
        
        # Bind phím Enter để đăng nhập
        self.username_entry.bind("<Return>", self._login_on_enter)
        self.password_entry.bind("<Return>", self._login_on_enter)


    # ----------------------------------------------------------------------
    # --- LOGIC ĐĂNG NHẬP (KHÔNG THAY ĐỔI) ---
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
        try:
            user_id, role = checkLogin(username, password) 
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể kết nối CSDL: {e}")
            return
        
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
                try:
                    admin_page_instance = self.controller.frames["AdminPage"]
                    admin_page_instance.refresh_page() # Làm mới dữ liệu
                except Exception as e:
                    print(f"Lỗi khi làm mới AdminPage: {e}")
                self.controller.show_frame("AdminPage") 
            else:
                self.controller.show_frame("POSPage")
        else:
            # Đăng nhập thất bại
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
            
            # Xóa mật khẩu sau khi thất bại
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
        
        
    def on_show_frame(self):
        """Hàm này sẽ được controller gọi khi trang này được hiển thị."""
        # Cập nhật: Đổi sang 'zoomed' để đồng bộ với các trang khác
        self.controller.state("zoomed")
        # Tự động focus vào trường username
        self.username_entry.focus_set()


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
                admin_page_instance = self.controller.frames["AdminPage"]
                admin_page_instance.refresh_page()  # Làm mới dữ liệu thật sự của frame đang dùng
                self.controller.show_frame("AdminPage") 
            else:
                self.controller.show_frame("POSPage")
        else:
            # Đăng nhập thất bại
            messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
            
            # Xóa mật khẩu sau khi thất bại
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
        
        # ... (bên trong class LoginPage) ...
    #### autozoom 

    def on_show_frame(self):
        """Hàm này sẽ được controller gọi khi trang này được hiển thị."""
        # Đặt kích thước cửa sổ mong muốn (Rộng x Cao)
        # Bạn có thể thử nghiệm các giá trị này, ví dụ: 450x550 hoặc 400x500
        self.controller.geometry("550x550")
        


