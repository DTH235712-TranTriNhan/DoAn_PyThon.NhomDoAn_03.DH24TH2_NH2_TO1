import tkinter as tk
from tkinter import Toplevel, messagebox, filedialog 
import tkinter.ttk as ttk
import os 
from Database.dbProducts import addProduct, deleteProduct, getAllProducts, updateProduct, searchProducts, removeProductPermanently
from PIL import Image, ImageTk
from Database.dbOrders import getAllOrdersForAdmin, getAllOrders, getOrderDetails

class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- BIẾN ĐỂ GIỮ THAM CHIẾU ẢNH ---
        self.photo_admin = None # Biến giữ tham chiếu ảnh PIL/ImageTk
        self.categories = ["Điện tử", "Phụ kiện", "Đồ gia dụng", "Thời trang", "Khác"]
        self.entries = {}
        
        # === Notebook (2 tab) ===
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        product_tab = tk.Frame(notebook)
        order_tab = tk.Frame(notebook)
        notebook.add(product_tab, text="Quản lý sản phẩm")
        notebook.add(order_tab, text="Quản lý đơn hàng")

        # ---------------------- TAB 1: QUẢN LÝ SẢN PHẨM ----------------------
        header_frame = tk.Frame(product_tab)
        header_frame.pack(fill='x', pady=10)

        tk.Label(header_frame, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, text="Đăng xuất", command=lambda: controller.show_frame("LoginPage")).pack(side=tk.RIGHT, padx=10)

        input_frame = tk.LabelFrame(product_tab, text="Thông tin Sản phẩm", padx=10, pady=10)
        input_frame.pack(fill='x', padx=10)

        labels = ["Mã SP", "Tên SP", "Danh mục", "Giá", "Tồn kho", "Đường dẫn Ảnh", "Mô tả"]
        keys = ["sku", "name", "category", "price", "stock", "imagePath", "description"]
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)

        base_fields = ["sku", "name", "category", "price", "stock"]
        for i, key in enumerate(base_fields):
            label_text = labels[keys.index(key)]
            r = i // 3
            c = (i % 3) * 2
            tk.Label(input_frame, text=label_text + ":", anchor='w').grid(row=r, column=c, padx=5, pady=5, sticky='w')

            if key == "category":
                entry = ttk.Combobox(input_frame, width=20, values=self.categories)
                entry.set(self.categories[0])
            else:
                entry = tk.Entry(input_frame, width=20)

            entry.grid(row=r, column=c + 1, padx=5, pady=5, sticky='ew')
            self.entries[key] = entry

        key = "imagePath"
        label_text = labels[keys.index(key)]
        tk.Label(input_frame, text=label_text + ":", anchor='w').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        entry = tk.Entry(input_frame, width=60)
        entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky='ew')
        self.entries[key] = entry
        tk.Button(input_frame, text="Chọn ảnh...", command=self.browseImage, width=10).grid(row=2, column=4, padx=5, pady=5, sticky='w')

        self.image_preview_label = tk.Label(input_frame, text="Ảnh Xem trước",
                                            width=20, height=10, relief="sunken", bg="lightgray")
        self.image_preview_label.grid(row=2, column=5, rowspan=2, padx=10, pady=5, sticky='nsew')

        key = "description"
        label_text = labels[keys.index(key)]
        tk.Label(input_frame, text=label_text + ":", anchor='w').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        entry = tk.Entry(input_frame, width=80)
        entry.grid(row=3, column=1, padx=5, pady=5, columnspan=4, sticky='ew')
        self.entries[key] = entry

        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=5, pady=10)
        tk.Button(button_frame, text="Thêm", command=self.add_product_action, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Sửa", command=self.update_product_action, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Xóa", command=self.delete_product_action, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Xóa vĩnh viễn", command=self.remove_product_action, width=15, bg="#d9534f", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Làm mới", command=self.load_products, width=10).pack(side=tk.LEFT, padx=10)

        search_frame = tk.Frame(product_tab, padx=10, pady=5)
        search_frame.pack(fill='x')
        tk.Label(search_frame, text="Tìm kiếm (SKU/Tên):", width=15).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        tk.Button(search_frame, text="Tìm kiếm", command=self.search_product_action, width=10).pack(side=tk.LEFT)

        columns = ("Mã SP", "Tên SP", "Danh mục", "Giá", "Tồn kho", "Đường dẫn Ảnh", "Mô tả")
        self.tree = ttk.Treeview(product_tab, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        self.tree.column("Tên SP", width=150)
        self.tree.column("Đường dẫn Ảnh", width=120)
        self.tree.column("Mô tả", width=150)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.select_item)
        self.load_products()

        # ---------------------- TAB 2: QUẢN LÝ ĐƠN HÀNG ----------------------
        order_frame = tk.LabelFrame(order_tab, text="Danh sách đơn hàng", padx=10, pady=10)
        order_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("Mã ĐH", "Người mua", "Tên đăng nhập", "Ngày đặt", "Sản phẩm", "Số lượng", "Đơn giá", "Tổng tiền", "Trạng thái")
        self.order_tree = ttk.Treeview(order_frame, columns=columns, show="headings")

        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, anchor=tk.CENTER, width=110)

        self.order_tree.pack(fill='both', expand=True)
        tk.Button(order_frame, text="Tải lại danh sách", command=self.load_orders_admin).pack(pady=5)
        self.order_tree.bind("<Double-1>", self.show_order_details)

# ======================================================================
# --- HÀM LOGIC ---
# ======================================================================

    def load_orders_admin(self):
        """Tải danh sách đơn hàng từ CSDL để admin xem."""
        # Xóa dữ liệu cũ
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        orders = getAllOrdersForAdmin()
        if not orders:
            messagebox.showinfo("Thông báo", "Hiện chưa có đơn hàng nào.")
            return

        for order in orders:
            total = order['quantity'] * order['unitPrice']
            self.order_tree.insert('', tk.END, values=(
                order['orderID'],
                order['fullName'],
                order['userName'],
                order['orderDate'],
                order['productName'],
                order['quantity'],
                f"{order['unitPrice']:,}".replace(",", "."),
                f"{total:,}".replace(",", "."),
                order['status']
            ))

    def get_target_image_dir(self):
        """Trả về đường dẫn tuyệt đối đến thư mục chứa ảnh (App/Images)."""
        # os.getcwd() là thư mục gốc dự án
        target_dir = os.path.join(os.getcwd(), 'App', 'Images')
        os.makedirs(target_dir, exist_ok=True) 
        return target_dir
    
    def browseImage(self):
        """Mở hộp thoại chọn file ảnh CHỈ TỪ FOLDER App/Images VÀ LƯU PATH TƯƠNG ĐỐI."""
        
        start_dir = self.get_target_image_dir()
        
        filepath_absolute = filedialog.askopenfilename(
            title="Chọn ảnh sản phẩm (Đã có sẵn trong App/Images)",
            initialdir=start_dir, 
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*"))
        )
        
        if filepath_absolute:
            
            # --- CHUẨN HÓA VÀ KIỂM TRA AN TOÀN ---
            normalized_start_dir = os.path.normpath(start_dir)
            normalized_filepath = os.path.normpath(filepath_absolute)
            
            # Kiểm tra: Đảm bảo file được chọn nằm trong thư mục App/Images
            if not normalized_filepath.startswith(normalized_start_dir + os.sep) and normalized_filepath != normalized_start_dir:
                messagebox.showwarning("Cảnh báo", "Vui lòng chỉ chọn ảnh đã được copy vào thư mục App/Images.")
                return 

            # --- Logic lưu đường dẫn tương đối ---
            filename = os.path.basename(filepath_absolute)
            relative_path_for_db = os.path.join('App', 'Images', filename)
            
            # 3. Cập nhật Entry và Xem trước ảnh
            self.entries['imagePath'].delete(0, tk.END)
            self.entries['imagePath'].insert(0, relative_path_for_db)
            messagebox.showinfo("Đã chọn", f"Đã chọn ảnh: {relative_path_for_db}")

            self.load_image_preview(relative_path_for_db)
            
    def clear_entries(self):
        """Xóa nội dung tất cả các trường nhập liệu."""
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
            
    def load_products(self):
        """Tải dữ liệu sản phẩm từ CSDL và đổ vào Treeview."""
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        products = getAllProducts()
        
        # product là tuple 7 phần tử: (sku, name, category, price_str, stockQuantity, imagePath, description)
        for product in products:
            self.tree.insert('', tk.END, values=product)

        self.clear_entries()

    def select_item(self, event):
        """Đổ dữ liệu từ dòng được chọn vào các trường nhập liệu và hiển thị ảnh."""
        self.clear_entries()
        selected_item = self.tree.focus()
    
        image_path_value = None 
        keys = ["sku", "name", "category", "price", "stock", "imagePath", "description"] 
    
        if selected_item:
            values = self.tree.item(selected_item, 'values')
        
            for i, (key, value) in enumerate(zip(keys, values)):
                display_value = "" if value is None else value
            
                if key == "category":
                    self.entries[key].set(display_value) 
                else:
                    self.entries[key].insert(0, display_value)
            
                if key == "imagePath":
                    image_path_value = display_value
                    
            self.load_image_preview(image_path_value)
                    
    def get_input_data(self):
        """Lấy dữ liệu từ các trường nhập liệu, chuẩn hóa giá/tồn kho."""
        data = {k: self.entries[k].get().strip() for k in self.entries}
        
        # Kiểm tra SKU và Tên SP không rỗng 
        if not data['sku'] or not data['name']:
             messagebox.showerror("Lỗi Dữ liệu", "Mã SP và Tên SP không được để trống.")
             return None
            
        try:
            # Chuyển đổi giá và tồn kho sang định dạng số
            # Giá được lưu trong Treeview có dấu chấm (1.000.000), cần loại bỏ trước khi chuyển float
            price_str_clean = data['price'].replace('.', '').replace(',', '')
            data['price'] = float(price_str_clean)
            data['stock'] = int(data['stock'])
            
            # Xử lý các trường có thể là NULL: Gửi None nếu chuỗi rỗng
            data['imagePath'] = data['imagePath'] or None
            data['description'] = data['description'] or None
            
            return data
        except ValueError:
            messagebox.showerror("Lỗi Dữ liệu", "Giá và Tồn kho phải là số hợp lệ.")
            return None

    def update_product_action(self):
        data = self.get_input_data()
        
        if data:
            sku_to_update = data['sku']
            
            success, message = updateProduct(sku_to_update, 
                                             data['name'], 
                                             data['category'], 
                                             data['price'], 
                                             data['stock'], 
                                             data['imagePath'], 
                                             data['description']) 
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_products()
                # Tải lại danh sách sản phẩm cho trang POS (nếu POSPage đã tồn tại)
                if "POSPage" in self.controller.frames:
                    self.controller.frames["POSPage"].load_products_list()
            else:
                messagebox.showerror("Lỗi", message)

    def delete_product_action(self):
        sku_to_delete = self.entries['sku'].get().strip()
        if sku_to_delete:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn 'xóa' (set tồn kho về 0) sản phẩm Mã SP {sku_to_delete}?"):
                if deleteProduct(sku_to_delete):
                    messagebox.showinfo("Thành công", "Đã 'xóa' sản phẩm (Tồn kho = 0).")
                    self.load_products()
                    # Tải lại danh sách sản phẩm cho trang POS
                    if "POSPage" in self.controller.frames:
                        self.controller.frames["POSPage"].load_products_list()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa sản phẩm.")
        else:
            messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm để xóa.")
    
    def remove_product_action(self):
        sku_to_delete = self.entries['sku'].get().strip()
        if not sku_to_delete:
            messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm để xóa vĩnh viễn.")
            return

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn XÓA VĨNH VIỄN sản phẩm Mã SP {sku_to_delete}? (Không thể khôi phục)"):
           success, message = removeProductPermanently(sku_to_delete)
           if success:
               messagebox.showinfo("Thành công", message)
               self.load_products()
               # Làm mới POSPage nếu có
               if "POSPage" in self.controller.frames:
                   self.controller.frames["POSPage"].load_products_list()
           else:
               messagebox.showerror("Lỗi", message)

    def add_product_action(self):
        data = self.get_input_data()
        if data:
            success, message = addProduct(data['sku'], 
                                          data['name'], 
                                          data['category'], 
                                          data['price'], 
                                          data['stock'], 
                                          data['imagePath'], 
                                          data['description']) 
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_products()
                # Tải lại danh sách sản phẩm cho trang POS
                if "POSPage" in self.controller.frames:
                    self.controller.frames["POSPage"].load_products_list()
            else:
                messagebox.showerror("Lỗi", message)

    def search_product_action(self):
        """Xử lý hành động tìm kiếm và hiển thị kết quả."""
        keyword = self.search_entry.get().strip()
        
        # Xóa dữ liệu cũ trên Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not keyword:
            messagebox.showwarning("Tìm kiếm", "Không có từ khóa. Đang tải lại toàn bộ sản phẩm.")
            self.load_products() # Tải lại toàn bộ nếu không có từ khóa
            return

        results = searchProducts(keyword) 
            
        if results:
            for product in results:
                self.tree.insert('', tk.END, values=product)
        else:
            messagebox.showinfo("Kết quả", f"Không tìm thấy sản phẩm nào khớp với '{keyword}'.")

    def load_image_preview(self, imagePath):
        """Tải và hiển thị ảnh xem trước từ đường dẫn tương đối."""
        w, h = 81, 144 
        
        # 1. Đặt lại Label ban đầu
        self.image_preview_label.config(image='', text="Ảnh Xem trước", width=20, height=10) 
        self.photo_admin = None
        
        if imagePath:
            # 1. Chuyển đổi sang đường dẫn tuyệt đối
            absolute_path = os.path.normpath(os.path.join(os.getcwd(), imagePath)) 
            
            if os.path.exists(absolute_path):
                try:
                    # 2. Mở ảnh và Resize
                    img = Image.open(absolute_path)
                    img = img.resize((w, h), Image.Resampling.LANCZOS)
                    self.photo_admin = ImageTk.PhotoImage(img)
                    
                    # 3. Hiển thị ảnh và ép kích thước Label theo pixel
                    self.image_preview_label.config(image=self.photo_admin, text="", width=w, height=h)
                    
                except Exception as e:
                    print(f"Lỗi tải ảnh xem trước (Admin): {e}")
                    self.image_preview_label.config(image='', text="Lỗi tải ảnh", width=20, height=10)
            else:
                self.image_preview_label.config(image='', text="Không tìm thấy file", width=20, height=10)
        else:
            # Đường dẫn rỗng
            pass
    
    def load_orders(self):
        """Tải danh sách đơn hàng từ CSDL"""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        orders = getAllOrders()
        for order in orders:
            # orderDate có thể là chuỗi hoặc datetime → chuẩn hóa
            if isinstance(order['orderDate'], str):
               order_date = order['orderDate']
            else:
                order_date = order['orderDate'].strftime("%d/%m/%Y %H:%M")
            total_amount = f"{order['totalAmount']:,}".replace(",", ".")
            self.order_tree.insert("", "end", values=(
                order['orderID'],
                order_date,
                order['userName'],
                order['fullName'],
                total_amount + " ₫",
                order['status']
            ))

    def show_order_details(self, event):
        """Mở popup hiển thị chi tiết đơn hàng"""
        selected = self.order_tree.focus()
        if not selected:
            return
        order_data = self.order_tree.item(selected)["values"]
        orderID = order_data[0]

        details = getOrderDetails(orderID)
        if not details:
            messagebox.showinfo("Chi tiết đơn hàng", "Không có sản phẩm trong đơn hàng này.")
            return

        popup = Toplevel(self)
        popup.title(f"Chi tiết đơn hàng #{orderID}")
        popup.geometry("600x300")

        cols = ("SKU", "Tên sản phẩm", "Số lượng", "Đơn giá", "Thành tiền")
        tree = ttk.Treeview(popup, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill="both", expand=True)

        for item in details:
            unit_price = f"{item['unitPrice']:,}".replace(",", ".")
            total_price = f"{item['totalPrice']:,}".replace(",", ".")
            tree.insert("", "end", values=(
                item["SKU"],
                item["productName"],
                item["quantity"],
                unit_price + " ₫",
                total_price + " ₫"
        ))
            
    def refresh_page(self):
        """Làm mới toàn bộ dữ liệu trên trang Admin."""
        try:
            self.clear_entries()         # Xóa input nếu có
            self.load_products()         # Tải lại danh sách sản phẩm
            self.load_orders_admin()     # Tải lại danh sách đơn hàng
        except Exception as e:
            print(f"Lỗi khi làm mới AdminPage: {e}")