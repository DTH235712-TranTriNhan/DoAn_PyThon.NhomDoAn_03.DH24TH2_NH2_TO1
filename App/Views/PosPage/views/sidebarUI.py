import tkinter as tk
from Database.dbProducts import getAllCategories

def create_category_sidebar_ui(self, parent_frame):
    """Tạo sidebar danh mục bên trong parent_frame."""
    self.sidebar_frame = tk.Frame(parent_frame, bg="#FFF0E6", width=160, bd=1, relief="solid")
    self.sidebar_frame.pack(side="left", fill="y", padx=(20, 10))
    self.sidebar_frame.pack_propagate(False)

    tk.Label(
        self.sidebar_frame, text="🍷 Danh Mục",
        font=("Times New Roman", 14, "bold"),
        bg="#8B0000", fg="white"
    ).pack(fill="x", pady=(0, 5), ipady=5)

    self.category_buttons.clear()

    btn_all = tk.Button(
        self.sidebar_frame, text="Tất cả sản phẩm",
        font=("Times New Roman", 11, "bold"),
        relief="flat", bg="#FFF0E6", fg="black"
    )
    btn_all.config(command=lambda b=btn_all: (self._set_active_category_button(b), self.load_products_list()))
    btn_all.pack(fill="x", padx=5, pady=(5, 2))
    self.category_buttons.append(btn_all)

    try:
        categories = getAllCategories()
        for cat_name in categories:
            btn_cat = tk.Button(
                self.sidebar_frame, text=cat_name,
                font=("Times New Roman", 11),
                relief="flat", bg="#FFF0E6", fg="black"
            )
            btn_cat.config(command=lambda b=btn_cat, c=cat_name: (self._set_active_category_button(b), self.load_products_by_category(c)))
            btn_cat.pack(fill="x", padx=5, pady=1)
            self.category_buttons.append(btn_cat)

            btn_cat.bind("<Enter>", lambda e: e.widget.config(bg="#E0D4CC"))
            btn_cat.bind("<Leave>", lambda e: self._set_active_category_button())
    except Exception as e:
        print(f"Không thể tải danh mục: {e}")
        tk.Label(self.sidebar_frame, text="(Lỗi tải danh mục)", bg="#FFF0E6").pack()

    btn_all.bind("<Enter>", lambda e: e.widget.config(bg="#E0D4CC"))
    btn_all.bind("<Leave>", lambda e: self._set_active_category_button())

    self._set_active_category_button(btn_all)
