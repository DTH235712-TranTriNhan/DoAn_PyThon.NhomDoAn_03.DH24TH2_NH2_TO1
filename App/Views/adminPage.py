import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from Database.dbProducts import addProduct, deleteProduct, getAllProducts, updateProduct

class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- PHẦN TRÊN: TIÊU ĐỀ VÀ NÚT ---
        header_frame = tk.Frame(self)
        header_frame.pack(fill='x', pady=10)
        
        tk.Label(header_frame, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, text="Đăng xuất", command=lambda: controller.show_frame("LoginPage")).pack(side=tk.RIGHT, padx=10)

        # --- PHẦN GIỮA: FORM NHẬP LIỆU (CRUD) ---
        input_frame = tk.Frame(self, padx=10, pady=10, bd=2, relief=tk.GROOVE)
        input_frame.pack(fill='x', padx=10)

        # Các trường nhập liệu (THAY ĐỔI: ID -> SKU)
        labels = ["Mã SP (SKU)", "Tên SP", "Danh mục", "Giá", "Tồn kho"]
        keys = ["sku", "name", "category", "price", "stock"]
        self.entries = {}
        
        # Danh mục cho Combobox
        self.categories = ["Điện tử", "Phụ kiện", "Đồ gia dụng", "Thời trang", "Khác"]
        
        for i, (label_text, key) in enumerate(zip(labels, keys)):
            tk.Label(input_frame, text=label_text + ":").grid(row=0, column=i, padx=5, pady=5)
            
            if key == "category":
                # THAY ĐỔI: SỬ DỤNG COMBOBOX CHO DANH MỤC
                entry = ttk.Combobox(input_frame, width=10, values=self.categories)
                entry.set(self.categories[0]) # Đặt giá trị mặc định
            else:
                entry = tk.Entry(input_frame, width=12)
                
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[key] = entry
            
        # KHÔNG VÔ HIỆU HÓA TRƯỜNG SKU (Trường SKU là tự nhập)

        # Các nút chức năng
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=5, pady=10)
        
        tk.Button(button_frame, text="Thêm", command=self.add_product_action).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Sửa", command=self.update_product_action).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Xóa", command=self.delete_product_action).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Làm mới", command=self.load_products).pack(side=tk.LEFT, padx=10)
        
        # --- PHẦN DƯỚI: DANH SÁCH SẢN PHẨM (Treeview) ---
        
        # Tạo Treeview (THAY ĐỔI: ID -> Mã SP)
        columns = ("Mã SP", "Tên SP", "Danh mục", "Giá", "Tồn kho")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
            
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Gắn sự kiện khi chọn một dòng
        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        # Tải dữ liệu khi khởi tạo
        self.load_products()

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
        for product in products:
            # product là một tuple: (sku, name, category, price, stockQuantity)
            self.tree.insert('', tk.END, values=product)

        self.clear_entries()

    def select_item(self, event):
        """Đổ dữ liệu từ dòng được chọn vào các trường nhập liệu."""
        self.clear_entries()
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            keys = ["sku", "name", "category", "price", "stock"] # THAY ĐỔI: 'id' -> 'sku'
            
            for key, value in zip(keys, values):
                self.entries[key].insert(0, value)
                    
    def get_input_data(self):
        """Lấy dữ liệu từ các trường nhập liệu, chuẩn hóa giá/tồn kho."""
        data = {k: self.entries[k].get() for k in self.entries}
        
        # Kiểm tra SKU và Tên SP không rỗng (bắt buộc phải có cho mọi hành động)
        if not data['sku'] or not data['name']:
             messagebox.showerror("Lỗi Dữ liệu", "Mã SP (SKU) và Tên SP không được để trống.")
             return None
             
        try:
            # Chuyển đổi giá và tồn kho sang định dạng số
            # Loại bỏ dấu phẩy từ giá trước khi chuyển đổi
            data['price'] = float(data['price'].replace(',', '')) 
            data['stock'] = int(data['stock'])
            return data
        except ValueError:
            messagebox.showerror("Lỗi Dữ liệu", "Giá và Tồn kho phải là số hợp lệ.")
            return None

    def add_product_action(self):
        data = self.get_input_data()
        if data:
            # THAY ĐỔI: Thêm tham số SKU vào hàm addProduct
            success, message = addProduct(data['sku'], data['name'], data['category'], data['price'], data['stock'])
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_products()
            else:
                messagebox.showerror("Lỗi", message)

    def update_product_action(self):
        data = self.get_input_data()
        sku_to_update = self.entries['sku'].get() # THAY ĐỔI: Lấy SKU
        
        if data and sku_to_update:
            # THAY ĐỔI: Dùng SKU thay cho product_id
            success, message = updateProduct(sku_to_update, data['name'], data['category'], data['price'], data['stock'])
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_products()
            else:
                messagebox.showerror("Lỗi", message)
        else:
             messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm cần sửa.")

    def delete_product_action(self):
        sku_to_delete = self.entries['sku'].get() # THAY ĐỔI: Lấy SKU
        if sku_to_delete:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn 'xóa' (set tồn kho về 0) sản phẩm Mã SP {sku_to_delete}?"):
                # THAY ĐỔI: Dùng SKU và hàm deleteProduct đã được sửa để set tồn kho = 0
                if deleteProduct(sku_to_delete):
                    messagebox.showinfo("Thành công", "Đã 'xóa' sản phẩm (Tồn kho = 0).")
                    self.load_products()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa sản phẩm.")
        else:
            messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm để xóa.")