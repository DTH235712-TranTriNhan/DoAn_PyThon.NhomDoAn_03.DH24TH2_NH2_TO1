import tkinter as tk
from tkinter import messagebox
from Database.dbUsers import checkLogin 

def handle_login(controller, username, password, username_entry, password_entry):
    """
    Xử lý logic đăng nhập: gọi CSDL, kiểm tra, và điều hướng.
    Tham số:
    - controller: Tham chiếu đến main controller để điều hướng frame.
    - username, password: Chuỗi tên đăng nhập và mật khẩu.
    - username_entry, password_entry: Tham chiếu đến Entry widget để xóa input và set focus.
    """

    # 2. Kiểm tra rỗng
    if not username:
        messagebox.showwarning("Lỗi", "Vui lòng nhập tên đăng nhập.")
        username_entry.focus_set()
        return

    if not password:
        messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu.")
        password_entry.focus_set()
        return
        
    # 3. GỌI HÀM KIỂM TRA CSDL
    try:
        user_id, role = checkLogin(username, password) 
    except Exception as e:
        messagebox.showerror("Lỗi CSDL", f"Không thể kết nối CSDL: {e}")
        return
    
    if role:
        # Lấy instance của trang POS và cập nhật trạng thái user
        try:
            pos_page_instance = controller.frames["POSPage"]
            pos_page_instance.update_user_status(user_id, username, role)
        except Exception as e:
            print(f"Lưu ý: Không thể cập nhật trạng thái POSPage: {e}")

        # Xóa trường nhập liệu sau khi thành công
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        
        # Đăng nhập thành công và Điều hướng
        if role.lower() == 'admin':
            try:
                admin_page_instance = controller.frames["AdminPage"]
                admin_page_instance.refresh_page() 
            except Exception as e:
                print(f"Lỗi khi làm mới AdminPage: {e}")
            controller.show_frame("AdminPage") 
        else:
            controller.show_frame("POSPage")
    else:
        # Đăng nhập thất bại
        messagebox.showerror("Lỗi Đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")
        
        # Xóa mật khẩu sau khi thất bại
        password_entry.delete(0, tk.END)
        password_entry.focus_set()