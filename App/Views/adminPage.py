import tkinter as tk
from tkinter import messagebox, filedialog 
import tkinter.ttk as ttk
import os 
from Database.dbProducts import addProduct, deleteProduct, getAllProducts, updateProduct, searchProducts
from PIL import Image, ImageTk

class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- PHẦN TRÊN: TIÊU ĐỀ VÀ NÚT ĐĂNG XUẤT ---
        header_frame = tk.Frame(self)
        header_frame.pack(fill='x', pady=10)
        
        tk.Label(header_frame, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, text="Đăng xuất", command=lambda: controller.show_frame("LoginPage")).pack(side=tk.RIGHT, padx=10)

        # --- PHẦN GIỮA: FORM NHẬP LIỆU (CRUD) ---
        input_frame = tk.LabelFrame(self, text="Thông tin Sản phẩm", padx=10, pady=10)
        input_frame.pack(fill='x', padx=10)

        labels = ["Mã SP", "Tên SP", "Danh mục", "Giá", "Tồn kho", "Đường dẫn Ảnh", "Mô tả"]
        keys = ["sku", "name", "category", "price", "stock", "imagePath", "description"]
        self.entries = {}
        self.categories = ["Điện tử", "Phụ kiện", "Đồ gia dụng", "Thời trang", "Khác"]
        
        # Thiết lập cột mở rộng cho input_frame
        input_frame.grid_columnconfigure(1, weight=1) 
        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(5, weight=0)
        
        # ---------------- HÀNG 0 VÀ HÀNG 1 (5 TRƯỜNG CƠ BẢN) ----------------
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
            
        # ---------------- HÀNG 2 (Đường dẫn Ảnh) ----------------
        key = "imagePath"
        label_text = labels[keys.index(key)]
        
        tk.Label(input_frame, text=label_text + ":", anchor='w').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        entry = tk.Entry(input_frame, width=60) 
        entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky='ew') # Kéo dài qua 3 cột
        self.entries[key] = entry
        
        # Nút Chọn ảnh (Đặt ở cột 4)
        tk.Button(input_frame, text="Chọn ảnh...", command=self.browseImage, width=10).grid(row=2, column=4, padx=5, pady=5, sticky='w')
        
        # --- THÊM: Khung Ảnh Xem Trước (Cột 5, Hàng 2-3) ---
        self.image_preview_label = tk.Label(input_frame, text="Ảnh Xem trước", 
                                            width=20, height=10, relief="sunken", 
                                            bg="lightgray")
        # Đặt ở cột 5 và kéo dài qua 2 hàng (2 và 3)
        self.image_preview_label.grid(row=2, column=5, rowspan=2, padx=10, pady=5, sticky='nsew')
        self.photo_admin = None # Biến giữ tham chiếu ảnh PIL

        # ---------------- HÀNG 3 (Mô tả) ----------------
        key = "description"
        label_text = labels[keys.index(key)]
        
        tk.Label(input_frame, text=label_text + ":", anchor='w').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        entry = tk.Entry(input_frame, width=80) 
        entry.grid(row=3, column=1, padx=5, pady=5, columnspan=4, sticky='ew') # Kéo dài qua 4 cột
        self.entries[key] = entry
        
        # Cột cuối cùng (5) không cần weight vì đã dùng columnspan

        # ---------------- HÀNG 4 (Các nút chức năng CRUD) ----------------
        button_frame = tk.Frame(input_frame)
        # Chiếm hết chiều rộng (từ cột 0 đến 4)
        button_frame.grid(row=4, column=0, columnspan=5, pady=10) 
        
        tk.Button(button_frame, text="Thêm", command=self.add_product_action, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Sửa", command=self.update_product_action, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Xóa", command=self.delete_product_action, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Làm mới", command=self.load_products, width=10).pack(side=tk.LEFT, padx=10)
        
        
        # --- KHUNG TÌM KIẾM (MỚI) ---
        search_frame = tk.Frame(self, padx=10, pady=5)
        search_frame.pack(fill='x')
        
        tk.Label(search_frame, text="Tìm kiếm (SKU/Tên):", width=15).pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        
        tk.Button(search_frame, text="Tìm kiếm", command=self.search_product_action, width=10).pack(side=tk.LEFT)


        # --- PHẦN DƯỚI: DANH SÁCH SẢN PHẨM (Treeview) ---
        columns = ("Mã SP", "Tên SP", "Danh mục", "Giá", "Tồn kho", "Đường dẫn Ảnh", "Mô tả") 
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER) 
            
        self.tree.column("Tên SP", width=150)
        self.tree.column("Đường dẫn Ảnh", width=120)
        self.tree.column("Mô tả", width=150)
            
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tree.bind("<<TreeviewSelect>>", self.select_item)
        self.load_products()

    # ... (Các hàm browseImage, clear_entries, load_products, select_item, get_input_data, 
    #      add_product_action, update_product_action, delete_product_action giữ nguyên) ...

    # --- HÀM TÌM KIẾM SẢN PHẨM (MỚI) ---
    def search_product_action(self):
        """Xử lý hành động tìm kiếm và hiển thị kết quả."""
        keyword = self.search_entry.get().strip()
        
        if not keyword:
            messagebox.showwarning("Tìm kiếm", "Vui lòng nhập từ khóa tìm kiếm.")
            self.load_products() # Tải lại toàn bộ nếu không có từ khóa
            return

        # Gọi hàm tìm kiếm từ CSDL
        results = searchProducts(keyword) 
        
        # Xóa dữ liệu cũ trên Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if results:
            for product in results:
                self.tree.insert('', tk.END, values=product)
        else:
            messagebox.showinfo("Kết quả", f"Không tìm thấy sản phẩm nào khớp với '{keyword}'.")

    # Lưu ý: Các hàm logic cũ (browseImage, clear_entries, load_products, select_item, 
    # get_input_data, add_product_action, update_product_action, delete_product_action)
    # cần được giữ nguyên như bạn đã gửi ở câu hỏi trước.
    
    # ... (Bạn cần chép lại các hàm logic cũ vào đây, hoặc đảm bảo chúng đã có sẵn 
    #       trong file adminPage.py của bạn) ...

    def get_target_image_dir(self):
        """Trả về đường dẫn tuyệt đối đến thư mục chứa ảnh (App/Images)."""
        # os.getcwd() là thư mục gốc dự án (vì bạn chạy python -m App.mainApp)
        target_dir = os.path.join(os.getcwd(), 'App', 'Images')
        # Đảm bảo thư mục tồn tại (nếu chưa có)
        os.makedirs(target_dir, exist_ok=True) 
        return target_dir
    
    def browseImage(self):
        """Mở hộp thoại chọn file ảnh CHỈ TỪ FOLDER App/Images VÀ LƯU PATH TƯƠNG ĐỐI."""
        
        start_dir = self.get_target_image_dir()
        
        # Mở hộp thoại CHỈ TẠI FOLDER DỰ ÁN
        filepath_absolute = filedialog.askopenfilename(
            title="Chọn ảnh sản phẩm (Đã có sẵn trong App/Images)",
            initialdir=start_dir, 
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*"))
        )
        
        if filepath_absolute:
            
            # --- PHẦN SỬA LỖI QUAN TRỌNG: CHUẨN HÓA VÀ KIỂM TRA ---
            
            # 1. Chuẩn hóa đường dẫn để xử lý sự khác biệt giữa / và \ (Windows)
            normalized_start_dir = os.path.normpath(start_dir)
            normalized_filepath = os.path.normpath(filepath_absolute)
            
            # 2. Kiểm tra an toàn: Đảm bảo file được chọn nằm trong thư mục App/Images
            # Thêm dấu 'os.sep' (dấu phân cách thư mục) để kiểm tra chính xác thư mục con
            if not normalized_filepath.startswith(normalized_start_dir + os.sep) and normalized_filepath != normalized_start_dir:
                messagebox.showwarning("Cảnh báo", "Vui lòng chỉ chọn ảnh đã được copy vào thư mục App/Images.")
                return 

            # --- Logic lưu đường dẫn tương đối (đã hoạt động đúng) ---
            
            # Lấy tên file: Tu_Lanh.webp
            filename = os.path.basename(filepath_absolute)
            
            # Tạo đường dẫn tương đối: App\Images\Tu_Lanh.webp
            relative_path_for_db = os.path.join('App', 'Images', filename)
            
            # 3. Cập nhật Entry
            self.entries['imagePath'].delete(0, tk.END)
            self.entries['imagePath'].insert(0, relative_path_for_db)
            messagebox.showinfo("Đã chọn", f"Đã chọn ảnh: {relative_path_for_db}")

            self.load_image_preview(relative_path_for_db)
            
        else:
            pass

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
    
    # KHỞI TẠO TẤT CẢ BIẾN CẦN THIẾT
        image_path_value = None 
        keys = ["sku", "name", "category", "price", "stock", "imagePath", "description"] 
    
        if selected_item:
        # BIẾN values CHỈ ĐƯỢC TẠO RA KHI CÓ selected_item
            values = self.tree.item(selected_item, 'values')
        
        # CHUYỂN VÒNG LẶP FOR VÀO BÊN TRONG KHỐI IF
        # (Chỉ chạy khi values đã được định nghĩa)
            for i, (key, value) in enumerate(zip(keys, values)):
                display_value = "" if value is None else value
            
            # Xử lý trường Category (Combobox)
                if key == "category":
                # Đảm bảo bạn xóa nội dung entry trước khi set (clear_entries đã làm)
                    self.entries[key].set(display_value) 
                else:
                    self.entries[key].insert(0, display_value)
            
            # Lấy đường dẫn ảnh để tải
                if key == "imagePath":
                    image_path_value = display_value
        self.load_image_preview(image_path_value)
                        
    def get_input_data(self):
        """Lấy dữ liệu từ các trường nhập liệu, chuẩn hóa giá/tồn kho."""
        data = {k: self.entries[k].get() for k in self.entries}
        
        # Kiểm tra SKU và Tên SP không rỗng 
        if not data['sku'] or not data['name']:
              messagebox.showerror("Lỗi Dữ liệu", "Mã SP và Tên SP không được để trống.")
              return None
            
        try:
            # Chuyển đổi giá và tồn kho sang định dạng số
            data['price'] = float(data['price'].replace(',', '')) 
            data['stock'] = int(data['stock'])
            
            # Xử lý các trường có thể là NULL: Gửi None nếu chuỗi rỗng
            data['imagePath'] = data.get('imagePath', '').strip() or None
            data['description'] = data.get('description', '').strip() or None
            
            return data
        except ValueError:
            messagebox.showerror("Lỗi Dữ liệu", "Giá và Tồn kho phải là số hợp lệ.")
            return None

    def add_product_action(self):
        data = self.get_input_data()
        if data:
            # Truyền thêm imagePath và description
            success, message = addProduct(data['sku'], data['name'], data['category'], data['price'], data['stock'], data['imagePath'], data['description']) 
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_products()
            else:
                messagebox.showerror("Lỗi", message)

    def update_product_action(self):
        data = self.get_input_data()
        
        if data:
            # Dữ liệu đã hợp lệ và có SKU
            sku_to_update = data['sku']
            
            # Đảm bảo bạn gọi hàm updateProduct với 7 tham số
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
            else:
                messagebox.showerror("Lỗi", message)
        else:
            # Lỗi sẽ được xử lý bởi get_input_data (thiếu SKU/Tên hoặc lỗi số)
            pass

    def delete_product_action(self):
        sku_to_delete = self.entries['sku'].get() 
        if sku_to_delete:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn 'xóa' (set tồn kho về 0) sản phẩm Mã SP {sku_to_delete}?"):
                if deleteProduct(sku_to_delete):
                    messagebox.showinfo("Thành công", "Đã 'xóa' sản phẩm (Tồn kho = 0).")
                    self.load_products()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa sản phẩm.")
        else:
            messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm để xóa.")

    def add_product_action(self):
        data = self.get_input_data()
        if data:
            # Truyền đúng 7 tham số
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
            else:
                messagebox.showerror("Lỗi", message)

    def load_image_preview(self, imagePath):
        """Tải và hiển thị ảnh xem trước từ đường dẫn tương đối."""
        w, h = 81, 144 
        
        # 1. Đặt lại Label ban đầu
        self.image_preview_label.config(image='', text="Ảnh Xem trước", width=20, height=10) 
        self.photo_admin = None
        
        if imagePath:
            # 1. Chuyển đổi sang đường dẫn tuyệt đối
            # Dùng os.path.normpath để xử lý dấu '/' hay '\' trên các hệ điều hành khác nhau
            absolute_path = os.path.normpath(os.path.join(os.getcwd(), imagePath)) 
            
            # KIỂM TRA ĐƯỜNG DẪN TUYỆT ĐỐI
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
                # <-- Kết quả: "Không tìm thấy file"
                self.image_preview_label.config(image='', text="Không tìm thấy file", width=20, height=10)
        else:
            # Đường dẫn rỗng
            pass # Giữ nguyên text "Ảnh Xem trước"