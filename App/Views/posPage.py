import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import os
# Import các hàm CSDL cần thiết
from Database.dbProducts import getProductDetailBySku, getProductsForPOS
from Database.dbOrders import createOrder, format_currency

class POSPage(tk.Frame):
    """Giao diện Điểm Bán Hàng (Point of Sale) chính."""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- DỮ LIỆU VÀ TRẠNG THÁI ---
        self.current_user = None         # Thông tin user đã đăng nhập: {'id', 'username', 'role'}
        self.cart_items = {}             # Giỏ hàng: {sku: {sku, name, quantity, unitPrice}}
        self.current_sku = None          # SKU đang được chọn trên Treeview
        self.selected_product_is_available = False # Cờ kiểm tra tồn kho

        # --- KHUNG TRẠNG THÁI USER & ĐĂNG NHẬP/ĐĂNG XUẤT ---
        self.create_user_status_frame()
        
        # --- TIÊU ĐỀ CHÍNH ---
        tk.Label(self, text="TRANG BÁN HÀNG (POS)", font=("Arial", 20, "bold")).pack(pady=10)
        
        # --- KHUNG CHÍNH (Chia 2 cột) ---
        main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Khung 1: Danh sách Sản phẩm (Treeview)
        self.create_product_list_frame(main_paned_window)
        
        # Khung 2: Chi tiết Sản phẩm & Thao tác
        self.create_product_detail_frame(main_paned_window)

        # Tải dữ liệu khi khởi tạo
        self.load_products_list()

    # ----------------------------------------------------------------------
    # --- PHẦN KHỞI TẠO GIAO DIỆN CON ---
    # ----------------------------------------------------------------------

    def create_user_status_frame(self):
        """Khởi tạo khung trạng thái người dùng (Đăng nhập/Đăng xuất)."""
        status_frame = tk.Frame(self, relief=tk.RAISED, bd=1) 
        status_frame.pack(fill='x', padx=10, pady=5)

        self.user_label = tk.Label(status_frame, text="Chưa đăng nhập", fg="red")
        self.user_label.pack(side=tk.LEFT, padx=10)

        self.login_button = tk.Button(status_frame, text="Đăng nhập", command=self.show_login_dialog)
        self.login_button.pack(side=tk.RIGHT, padx=10)

    def create_product_list_frame(self, parent_window):
        """Khởi tạo Treeview hiển thị danh sách sản phẩm."""
        list_frame = tk.LabelFrame(parent_window, text="Danh sách Sản phẩm")
        parent_window.add(list_frame, weight=1)
        
        columns = ("Mã SP", "Tên SP", "Giá") 
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("Mã SP", text="Mã SP")
        self.tree.heading("Tên SP", text="Tên SP")
        self.tree.heading("Giá", text="Giá")
        
        self.tree.column("Mã SP", width=80, anchor=tk.CENTER)
        self.tree.column("Tên SP", width=200)
        self.tree.column("Giá", width=100, anchor=tk.E)
        
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.display_product_detail)

    def create_product_detail_frame(self, parent_window):
        """Khởi tạo khung hiển thị chi tiết sản phẩm, nút Thêm vào giỏ & Thanh toán."""
        self.detail_frame = tk.LabelFrame(parent_window, text="Chi tiết Sản phẩm", padx=10, pady=10)
        parent_window.add(self.detail_frame, weight=1)
        
        # 1. Ảnh
        self.image_label = tk.Label(self.detail_frame, text="Ảnh Sản phẩm", width=30, height=15, relief="groove")
        self.image_label.pack(pady=10)
        self.photo = None 
        
        # 2. Tên Sản phẩm
        tk.Label(self.detail_frame, text="Tên SP:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.name_label = tk.Label(self.detail_frame, text="...", anchor='w', font=("Arial", 14))
        self.name_label.pack(fill='x')
        
        # 3. Giá
        tk.Label(self.detail_frame, text="Giá Bán:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        self.price_label = tk.Label(self.detail_frame, text="...", fg="red", font=("Arial", 18, "bold"), anchor='w')
        self.price_label.pack(fill='x')

        # 4. Mô tả
        tk.Label(self.detail_frame, text="Mô tả:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        scrollbar = ttk.Scrollbar(self.detail_frame)
        self.description_text = tk.Text(self.detail_frame, height=5, wrap='word', yscrollcommand=scrollbar.set) 
        scrollbar.config(command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.pack(fill='x', expand=True)

        # 5. Nút Thao tác
        button_frame = tk.Frame(self.detail_frame)
        button_frame.pack(fill='x', pady=15)
        
        self.add_to_cart_button = tk.Button(button_frame, text="➕ Thêm vào Giỏ", 
                                            command=self.add_to_cart, 
                                            bg="#2196F3", fg="white", font=("Arial", 12, "bold"))
        self.add_to_cart_button.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        
        self.checkout_button = tk.Button(button_frame, text="🛒 Thanh toán", 
                                            command=self.show_checkout_dialog, 
                                            bg="#FF9800", fg="white", font=("Arial", 12, "bold"), state=tk.DISABLED) 
        self.checkout_button.pack(side=tk.RIGHT, fill='x', expand=True, padx=(5, 0))

    # ----------------------------------------------------------------------
    # --- XỬ LÝ DỮ LIỆU & VIEW ---
    # ----------------------------------------------------------------------

    def load_products_list(self):
        """Tải dữ liệu rút gọn vào Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        products = getProductsForPOS()
        for product in products:
            sku, name, _, price_str, *_ = product 
            self.tree.insert('', tk.END, values=(sku, name, price_str), iid=sku) 

    def display_product_detail(self, event):
        """Lấy và hiển thị chi tiết sản phẩm khi chọn trên Treeview."""
        selected_sku = self.tree.focus()
        self.current_sku = selected_sku
        self.selected_product_is_available = False
        
        if selected_sku:
            product_data = getProductDetailBySku(selected_sku)
            
            if product_data:
                quantity = product_data.get('quantity', 0) 
                original_name = product_data['name']
                
                # Cập nhật trạng thái tồn kho
                if quantity <= 0:
                    display_name = f"{original_name} (HẾT HÀNG)"
                    self.name_label.config(text=display_name, fg="red") 
                    self.selected_product_is_available = False
                else:
                    display_name = original_name
                    self.name_label.config(text=display_name, fg="black") 
                    self.selected_product_is_available = True
                
                # Hiển thị Chi tiết
                self.price_label.config(text=product_data['price_str'])
                self.description_text.config(state=tk.NORMAL)
                self.description_text.delete('1.0', tk.END) 
                self.description_text.insert('1.0', product_data['description'])
                self.description_text.config(state=tk.DISABLED) 
                
                # Hiển thị Ảnh
                self.load_image(product_data['imagePath'])
            else:
                self.clear_detail_view()
                self.selected_product_is_available = False
        
    def load_image(self, imagePath):
        """Tải và hiển thị ảnh (Resize 141x250)."""
        self.clear_image()
        
        if imagePath:
            absolute_path = os.path.join(os.getcwd(), imagePath)
        else:
            absolute_path = None
        
        if absolute_path and os.path.exists(absolute_path):
            try:
                img = Image.open(absolute_path)
                w, h = 141, 250 
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img) 
                self.image_label.config(image=self.photo, text="", width=w, height=h)
            except Exception as e:
                print(f"Lỗi tải ảnh (PIL): {e}")
                self.image_label.config(image='', text="Không tải được ảnh")
        else:
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
        self.image_label.config(image='', text="Ảnh Sản phẩm", width=30, height=15)
        self.photo = None


    # ----------------------------------------------------------------------
    # --- XỬ LÝ TÀI KHOẢN & ĐĂNG NHẬP ---
    # ----------------------------------------------------------------------
    
    def show_login_dialog(self):
        """Chuyển đến trang Đăng nhập hoặc Đăng xuất."""
        if self.current_user:
            self.logout()
            return
        self.controller.show_frame("LoginPage")

    def logout(self):
        """Xóa user, reset giỏ hàng, và cập nhật giao diện."""
        self.current_user = None
        self.user_label.config(text="Chưa đăng nhập", fg="red")
        self.login_button.config(text="Đăng nhập")
        self.cart_items = {}
        self.checkout_button.config(state=tk.DISABLED)
        self.controller.show_frame("POSPage")
    
    def update_user_status(self, user_id, username, role):
        """Cập nhật trạng thái user sau khi đăng nhập."""
        self.current_user = {'id': user_id, 'username': username, 'role': role}
        self.user_label.config(text=f"Xin chào: {username} ({role})", fg="green")
        self.login_button.config(text="Đăng xuất")
        
        # Phân quyền & Điều hướng
        if role == 'Admin':
            self.controller.show_frame("AdminPage")
        # 'User' hoặc 'Guest' giữ nguyên trên trang POS

    # ----------------------------------------------------------------------
    # --- XỬ LÝ GIỎ HÀNG & THANH TOÁN ---
    # ----------------------------------------------------------------------

    def add_to_cart(self):
        """Thêm sản phẩm đang chọn vào giỏ hàng."""
        if not self.current_user:
            messagebox.showwarning("Cảnh báo", "Vui lòng đăng nhập để thực hiện giao dịch.")
            return

        selected_sku = self.current_sku or self.tree.focus()
        if not selected_sku:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sản phẩm trước.")
            return

        if not self.selected_product_is_available:
            messagebox.showerror("Lỗi Tồn kho", "Sản phẩm này đã hết hàng.")
            return
            
        product_data = getProductDetailBySku(selected_sku)
        if not product_data:
            messagebox.showerror("Lỗi", "Không tìm thấy chi tiết sản phẩm.")
            return

        name = product_data['name']
        price = product_data['price'] # Giá trị số
        
        if selected_sku in self.cart_items:
            # Tăng số lượng & kiểm tra giới hạn tồn kho
            current_available_stock = product_data['quantity']
            if self.cart_items[selected_sku]['quantity'] >= current_available_stock:
                 messagebox.showwarning("Lỗi tồn kho", f"Đã đạt giới hạn tồn kho ({current_available_stock}).")
                 return
                 
            self.cart_items[selected_sku]['quantity'] += 1
            message = f"Đã tăng SL '{name}' lên {self.cart_items[selected_sku]['quantity']}."
        else:
            # Thêm mới (SL = 1)
            self.cart_items[selected_sku] = {
                'sku': selected_sku,
                'name': name,
                'quantity': 1,
                'unitPrice': price
            }
            message = f"Đã thêm '{name}' vào giỏ hàng (SL: 1)."
            
        messagebox.showinfo("Thành công", message)
        self.checkout_button.config(state=tk.NORMAL if self.cart_items else tk.DISABLED)


    def show_checkout_dialog(self):
        """Hiển thị pop-up xác nhận thanh toán với chi tiết giỏ hàng."""
        if not self.cart_items:
            messagebox.showwarning("Cảnh báo", "Giỏ hàng trống.")
            return
        
        checkout_window = tk.Toplevel(self)
        checkout_window.title("Xác nhận Thanh toán")
        checkout_window.grab_set()

        cart_frame = tk.LabelFrame(checkout_window, text="Chi tiết Giỏ hàng", padx=10, pady=10)
        cart_frame.pack(padx=20, pady=10, fill='both', expand=True)

        # Treeview
        cart_tree = ttk.Treeview(cart_frame, columns=("Tên SP", "SL", "Đơn giá", "Tổng"), show="headings")
        cart_tree.heading("Tên SP", text="Tên SP")
        cart_tree.heading("SL", text="SL", anchor=tk.CENTER)
        cart_tree.heading("Đơn giá", text="Đơn giá", anchor=tk.E)
        cart_tree.heading("Tổng", text="Tổng", anchor=tk.E)
        cart_tree.column("SL", width=50, anchor=tk.CENTER)
        cart_tree.column("Đơn giá", width=100, anchor=tk.E)
        cart_tree.column("Tổng", width=100, anchor=tk.E)
        cart_tree.pack(fill='both', expand=True)
        
        total_amount = 0

        # Điền dữ liệu
        for item in self.cart_items.values():
            # Sử dụng float cho tính toán rồi dùng format_currency cho hiển thị
            item_total = item['quantity'] * float(item['unitPrice']) 
            total_amount += item_total
            cart_tree.insert('', tk.END, values=(
                item['name'], 
                item['quantity'], 
                format_currency(item['unitPrice']),
                format_currency(item_total)
            ))

        # Khung tổng tiền
        total_frame = tk.Frame(checkout_window)
        total_frame.pack(fill='x', padx=20, pady=(0, 10))
        tk.Label(total_frame, text="TỔNG THANH TOÁN:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(total_frame, 
                 text=f"{format_currency(total_amount)} VNĐ", 
                 fg="red", 
                 font=("Arial", 16, "bold")).pack(side=tk.RIGHT)
        
        # Nút xác nhận
        confirm_button = tk.Button(checkout_window, text="XÁC NHẬN THANH TOÁN", 
                                   command=lambda: self.process_order(checkout_window, total_amount),
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        confirm_button.pack(fill='x', padx=20, pady=(0, 15))


    def process_order(self, checkout_window, total_amount):
        """Thực hiện gọi hàm tạo đơn hàng (createOrder) và xử lý kết quả."""
        
        # 1. Chuẩn bị dữ liệu
        items_for_db = list(self.cart_items.values())
        if not self.current_user or 'id' not in self.current_user or self.current_user['id'] is None:
            checkout_window.destroy()
            messagebox.showerror("Lỗi", "Thông tin người dùng không hợp lệ. Vui lòng đăng nhập lại.")
            return
        user_id = self.current_user['id']
        
        # Đóng cửa sổ pop-up ngay trước khi gọi CSDL
        checkout_window.destroy()

        # 2. Gọi hàm tạo đơn hàng
        success, result = createOrder(user_id, items_for_db)

        # 3. Xử lý kết quả
        if success:
            order_id = result # result là orderID
            messagebox.showinfo("Thành công", f"Thanh toán thành công!\nTổng tiền: {format_currency(total_amount)} VNĐ\nMã Đơn hàng: {order_id}")
            
            # Reset giao diện
            self.cart_items = {}
            self.checkout_button.config(state=tk.DISABLED)
            self.load_products_list()
            self.clear_detail_view()
        else:
            # result là error_message
            messagebox.showerror("Lỗi Thanh toán", f"Thất bại khi tạo đơn hàng/trừ tồn kho: \n{result}")