import tkinter as tk
from tkinter import messagebox

def show_login_dialog_ui(self):
    """Chuyển đến trang Đăng nhập hoặc Đăng xuất."""
    if self.current_user:
        self.logout()
        return
    try:
        self.controller.show_frame("LoginPage")
    except AttributeError:
        self.show_error_toast("Chức năng đăng nhập/đăng xuất chưa được liên kết.")

def show_user_info_dialog_ui(self):
    """Hiển thị thông tin người dùng hiện tại (khi click vào nhãn username)."""
    if not self.current_user:
        self.show_error_toast("Bạn chưa đăng nhập.")
        return

    win = tk.Toplevel(self)
    win.title("Thông tin tài khoản")
    win.geometry("300x150")
    win.resizable(False, False)
    win.grab_set()

    tk.Label(win, text="👤 THÔNG TIN TÀI KHOẢN", font=("Times New Roman", 14, "bold"), fg="#8B0000").pack(pady=10)
    tk.Label(win, text=f"Tên đăng nhập: {self.current_user.get('username', 'N/A')}", font=("Times New Roman", 12)).pack(anchor='w', padx=20)
    tk.Label(win, text=f"ID người dùng: {self.current_user.get('id', 'N/A')}", font=("Times New Roman", 12)).pack(anchor='w', padx=20)
    tk.Label(win, text=f"Vai trò: {self.current_user.get('role', 'N/A')}", font=("Times New Roman", 12)).pack(anchor='w', padx=20)

def logout_ui(self):
    """Xóa user, reset giỏ hàng, và cập nhật giao diện."""
    self.current_user = None
    try:
        self.user_label.config(text="Chưa đăng nhập", fg="#FFCDD2", cursor="")
        self.login_button.config(text="Đăng nhập")
    except Exception:
        pass
    self.cart_items = {}
    try:
        self.update_cart_badge()
    except Exception:
        pass
    self.show_toast("Đã đăng xuất thành công.")

def update_user_status_ui(self, user_id, username, role):
    """Cập nhật trạng thái user sau khi đăng nhập."""
    self.current_user = {'id': user_id, 'username': username, 'role': role}
    try:
        self.user_label.config(text=f"Xin chào: {username}", fg="white", cursor="hand2")
        self.login_button.config(text="Đăng xuất")
    except Exception:
        pass

    if role == 'Admin':
        try:
            self.controller.show_frame("AdminPage")
        except Exception:
            print("Lỗi: Không tìm thấy AdminPage.")
