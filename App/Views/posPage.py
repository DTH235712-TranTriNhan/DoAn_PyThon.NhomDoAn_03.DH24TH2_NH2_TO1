import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk # <-- CẦN THÊM PIL
import os
from Database.dbProducts import getAllProducts, getProductDetailBySku 

class POSPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Khung này sẽ được PACK đầu tiên, nên nó sẽ nằm ở trên cùng
        status_frame = tk.Frame(self, relief=tk.RAISED, bd=1) 
        status_frame.pack(fill='x', padx=10, pady=5)

        # Khởi tạo trạng thái ban đầu
        self.current_user = None 

        self.user_label = tk.Label(status_frame, text="Chưa đăng nhập", fg="red")
        self.user_label.pack(side=tk.LEFT, padx=10)

        self.login_button = tk.Button(status_frame, text="Đăng nhập", command=self.show_login_dialog)
        self.login_button.pack(side=tk.RIGHT, padx=10)
        
        # --- TIÊU ĐỀ ---
        tk.Label(self, text="TRANG BÁN HÀNG (POS)", font=("Arial", 20, "bold")).pack(pady=10)
        
        # --- Khung Chính: Chia thành 2 cột ---
        main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # --- Cột 1: Danh sách Sản phẩm (Treeview) ---
        list_frame = tk.LabelFrame(main_paned_window, text="Danh sách Sản phẩm")
        main_paned_window.add(list_frame, weight=1)
        
        # Tạo Treeview
        columns = ("Mã SP", "Tên SP", "Giá") 
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("Mã SP", text="Mã SP")
        self.tree.heading("Tên SP", text="Tên SP")
        self.tree.heading("Giá", text="Giá")
        
        # Định nghĩa kích thước cột
        self.tree.column("Mã SP", width=80, anchor=tk.CENTER)
        self.tree.column("Tên SP", width=200)
        self.tree.column("Giá", width=100, anchor=tk.E)
        
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # LIÊN KẾT SỰ KIỆN KHI CHỌN DÒNG
        self.tree.bind("<<TreeviewSelect>>", self.display_product_detail)
        
        # --- Cột 2: Chi tiết Sản phẩm (MỚI) ---
        self.detail_frame = tk.LabelFrame(main_paned_window, text="Chi tiết Sản phẩm", padx=10, pady=10)
        main_paned_window.add(self.detail_frame, weight=1)
        
        # Khung Ảnh (Sử dụng Label để chứa ảnh)
        self.image_label = tk.Label(self.detail_frame, text="Ảnh Sản phẩm", width=30, height=15, relief="groove")
        self.image_label.pack(pady=10)
        self.photo = None # Biến để giữ tham chiếu ảnh PIL
        
        # Tên Sản phẩm
        tk.Label(self.detail_frame, text="Tên SP:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.name_label = tk.Label(self.detail_frame, text="...", anchor='w', font=("Arial", 14))
        self.name_label.pack(fill='x')
        
        # Giá
        tk.Label(self.detail_frame, text="Giá Bán:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        self.price_label = tk.Label(self.detail_frame, text="...", fg="red", font=("Arial", 18, "bold"), anchor='w')
        self.price_label.pack(fill='x')

        # Mô tả
        tk.Label(self.detail_frame, text="Mô tả:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        # Sử dụng Text Widget cho mô tả dài, có thanh cuộn (Scrollbar)
        scrollbar = ttk.Scrollbar(self.detail_frame)
        self.description_text = tk.Text(self.detail_frame, height=5, wrap='word', yscrollcommand=scrollbar.set) 
        scrollbar.config(command=self.description_text.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.pack(fill='x', expand=True)

        # Ban đầu, load danh sách
        self.load_products_list()


    def load_products_list(self):
        """Tải dữ liệu danh sách rút gọn vào Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        products = getAllProducts()
        
        for product in products:
            # Lấy 3 trường cần thiết: sku, name, price_str
            sku, name, _, price_str, *_ = product 
            # Dùng sku làm iid (ID của item trong treeview)
            self.tree.insert('', tk.END, values=(sku, name, price_str), iid=sku) 


    def display_product_detail(self, event):
        """Xử lý sự kiện khi chọn sản phẩm, tải chi tiết và hiển thị."""
        # Lấy iid (chính là SKU) của dòng được chọn
        selected_sku = self.tree.focus() 
        
        if selected_sku:
            product_data = getProductDetailBySku(selected_sku)
            
            if product_data:
                # 1. Hiển thị Tên & Giá
                self.name_label.config(text=product_data['name'])
                self.price_label.config(text=product_data['price_str'])
                
                # 2. Hiển thị Mô tả
                self.description_text.delete('1.0', tk.END) # Xóa nội dung cũ
                self.description_text.insert('1.0', product_data['description'])
                self.description_text.config(state=tk.DISABLED) # Cho phép cuộn nhưng không cho sửa
                
                # 3. Hiển thị Ảnh
                self.load_image(product_data['imagePath'])
            else:
                self.clear_detail_view() # Xóa nếu không tìm thấy dữ liệu

    
    def load_image(self, imagePath):
        """Tải và hiển thị ảnh bằng Pillow. (Kích thước ảnh mặc định là 200x200)"""
        self.clear_image() # Xóa ảnh cũ
        
        # 1. CHUYỂN ĐỔI SANG ĐƯỜNG DẪN TUYỆT ĐỐI AN TOÀN
        if imagePath:
            # Đường dẫn tuyệt đối dựa trên thư mục chạy chính (os.getcwd())
            absolute_path = os.path.join(os.getcwd(), imagePath)
        else:
            absolute_path = None
            print(f"DEBUG: Đang cố tải ảnh từ: {absolute_path}") # Kiểm tra Debug
        
        if absolute_path and os.path.exists(absolute_path):
            try:
                # 2. Mở ảnh
                img = Image.open(absolute_path) # SỬ DỤNG ĐƯỜNG DẪN TUYỆT ĐỐI
                
                # 3. Thay đổi kích thước (Resize) và hiển thị
                w, h = 141, 250 
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img) 
                self.image_label.config(image=self.photo, text="", width=w, height=h)
                
            except Exception as e:
                print(f"Lỗi tải ảnh (PIL): {e}")
                self.image_label.config(image='', text="Không tải được ảnh")
                
        else:
            # Debug: Đường dẫn không tồn tại
            self.image_label.config(image='', text="Không có ảnh/Ảnh lỗi")
            
    def clear_detail_view(self):
        """Xóa nội dung khung chi tiết."""
        self.name_label.config(text="...")
        self.price_label.config(text="...")
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete('1.0', tk.END)
        self.clear_image()
        
    def clear_image(self):
        """Xóa ảnh và giải phóng tham chiếu."""
        self.image_label.config(image='', 
                                text="Ảnh Sản phẩm",
                                width=30,
                                height=15)
        self.photo = None


    def show_login_dialog(self):
        """Mở cửa sổ đăng nhập/đăng ký."""
    
    # Nếu đang hiển thị Đăng xuất, thì thực hiện Logout
        if self.current_user:
            self.logout()
            return

        self.controller.show_frame("LoginPage")

    def logout(self):
        """Xóa thông tin người dùng và chuyển về trạng thái chưa đăng nhập."""
        self.current_user = None
        self.user_label.config(text="Chưa đăng nhập", fg="red")
        self.login_button.config(text="Đăng nhập")
    # Đảm bảo trở lại trang POS (nếu Admin đã nhảy sang trang Quản lý)
        self.controller.show_frame("POSPage")
    
    def update_user_status(self, username, role):
        """Cập nhật trạng thái người dùng sau khi đăng nhập thành công."""
        self.current_user = {'username': username, 'role': role}
        self.user_label.config(text=f"Xin chào: {username} ({role})", fg="green")
        self.login_button.config(text="Đăng xuất")
    
    # ⭐️ BƯỚC 4: PHÂN QUYỀN VÀ ĐIỀU HƯỚNG
        if role == 'Admin':
            self.controller.show_frame("AdminPage")
        elif role == 'User':
        # Giữ nguyên trên trang POS
            pass

