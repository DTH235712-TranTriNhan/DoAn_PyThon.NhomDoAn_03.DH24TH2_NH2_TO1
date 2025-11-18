import tkinter as tk
from Database.dbProducts import getAllCategories

def create_category_sidebar_ui(self, parent_frame):
    """Tạo khung sidebar cơ bản và container chứa nút."""
    
    # 1. Tạo khung chính Sidebar
    self.sidebar_frame = tk.Frame(parent_frame, bg="#FFF0E6", width=160, bd=1, relief="solid")
    self.sidebar_frame.pack(side="left", fill="y", padx=(20, 10))
    self.sidebar_frame.pack_propagate(False)

    # 2. Tạo Tiêu đề (Sẽ KHÔNG bị xóa khi refresh)
    tk.Label(
        self.sidebar_frame, text="🍷 Danh Mục",
        font=("Times New Roman", 14, "bold"),
        bg="#8B0000", fg="white"
    ).pack(fill="x", pady=(0, 5), ipady=5)

    # 3. Tạo Frame chứa các nút (Container)
    # Đây là nơi các nút sẽ được thêm vào/xóa đi
    self.sidebar_content_frame = tk.Frame(self.sidebar_frame, bg="#FFF0E6")
    self.sidebar_content_frame.pack(fill="both", expand=True)

    # 4. Gọi hàm refresh lần đầu để vẽ nút
    refresh_category_sidebar_ui(self)


def refresh_category_sidebar_ui(pos_page):
    """Hàm xóa nút cũ và tải lại danh mục mới nhất từ Database"""
    
    # 1. Kiểm tra xem khung chứa nút có tồn tại không
    if not hasattr(pos_page, 'sidebar_content_frame'):
        return

    # 2. Xóa các nút cũ bên trong container
    for widget in pos_page.sidebar_content_frame.winfo_children():
        widget.destroy()
    
    # 3. Reset danh sách quản lý nút
    pos_page.category_buttons = []

    # 4. Vẽ nút "Tất cả sản phẩm"
    btn_all = tk.Button(
        pos_page.sidebar_content_frame, text="Tất cả sản phẩm", # Gắn vào sidebar_content_frame
        font=("Times New Roman", 11, "bold"),
        relief="flat", bg="#FFF0E6", fg="black"
    )
    # Lưu ý: Dùng pos_page thay vì self
    btn_all.config(command=lambda b=btn_all: (pos_page._set_active_category_button(b), pos_page.load_products_list()))
    btn_all.pack(fill="x", padx=5, pady=(5, 2))
    
    # Sự kiện hover
    btn_all.bind("<Enter>", lambda e: e.widget.config(bg="#E0D4CC"))
    btn_all.bind("<Leave>", lambda e: pos_page._set_active_category_button()) # Reset về trạng thái active
    
    pos_page.category_buttons.append(btn_all)

    # 5. Vẽ các nút danh mục từ Database
    try:
        categories = getAllCategories() # Lấy danh sách mới nhất
        
        for cat_name in categories:
            btn_cat = tk.Button(
                pos_page.sidebar_content_frame, text=cat_name,
                font=("Times New Roman", 11),
                relief="flat", bg="#FFF0E6", fg="black"
            )
            # Lưu ý: Dùng pos_page.load_products_by_category
            btn_cat.config(command=lambda b=btn_cat, c=cat_name: (pos_page._set_active_category_button(b), pos_page.load_products_by_category(c)))
            btn_cat.pack(fill="x", padx=5, pady=1)
            
            # Sự kiện hover
            btn_cat.bind("<Enter>", lambda e: e.widget.config(bg="#E0D4CC"))
            btn_cat.bind("<Leave>", lambda e: pos_page._set_active_category_button())

            pos_page.category_buttons.append(btn_cat)

    except Exception as e:
        print(f"Không thể tải danh mục: {e}")
        tk.Label(pos_page.sidebar_content_frame, text="(Lỗi tải danh mục)", bg="#FFF0E6").pack()

    # 6. Mặc định chọn nút "Tất cả" sau khi refresh
    pos_page._set_active_category_button(btn_all)