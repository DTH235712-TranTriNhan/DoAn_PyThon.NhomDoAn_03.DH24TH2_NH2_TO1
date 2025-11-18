import tkinter as tk
from tkinter import messagebox
from Database.dbUsers import registerUser, checkUserNameExists 

def check_unique_input(input_value, username_entry):
    """
    Kiểm tra tính duy nhất của Tên đăng nhập và cập nhật màu nền của Entry.
    Trả về True nếu trùng, False nếu không.
    """
    if not input_value:
        username_entry.config(bg='white')
        return False

    # 3. KIỂM TRA TÊN ĐĂNG NHẬP TRÙNG LẶP
    if checkUserNameExists(input_value):
        username_entry.config(bg='lightcoral') 
        return True
    else:
        username_entry.config(bg='white')
        return False

def register_action(controller, fields):
    """
    Xử lý logic đăng ký: kiểm tra dữ liệu, gọi CSDL và điều hướng.
    
    Tham số:
    - controller: Tham chiếu đến main controller để điều hướng frame.
    - fields: Dictionary chứa các Entry widget {key: widget}
    """
    # Lấy giá trị từ các widget
    data = {k: e.get() for k, e in fields.items()}
    
    # 1. KIỂM TRA ĐẦY ĐỦ THÔNG TIN
    if not all(data.values()):
        messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ tất cả các trường.")
        return

    # 2. KIỂM TRA MẬT KHẨU KHỚP NHAU
    if data['password'] != data['confirm_password']:
        messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp. Vui lòng kiểm tra lại.")
        # Xóa trường nhập liệu
        fields['password'].delete(0, tk.END)
        fields['confirm_password'].delete(0, tk.END)
        return

    # 3. KIỂM TRA TÊN ĐĂNG NHẬP TRÙNG LẶP
    if fields['username'].cget('bg') == 'lightcoral':
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
        # Xóa hết các trường sau khi đăng ký thành công
        for entry in fields.values():
            entry.delete(0, tk.END)
        # Điều hướng về trang đăng nhập
        controller.show_frame("LoginPage")
    else:
        messagebox.showerror("Lỗi", message)