import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from App.Views.PosPage.views.searchBarUI import create_search_bar_ui
from App.Views.ProductCard.ProductCard import ProductCard
from Database.dbProducts import getProductsForPOS


def create_product_grid_ui(self):
    self.main_content_area = tk.Frame(self, bg="#FFF8F0")
    self.main_content_area.pack(fill="both", expand=True, padx=0, pady=0)

    self.create_category_sidebar(self.main_content_area)

    right_content_frame = tk.Frame(self.main_content_area, bg="#FFF8F0")
    right_content_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

    create_search_bar_ui(self, right_content_frame)

    # --- VÙNG CUỘN ---
    canvas_scroll_frame = tk.Frame(right_content_frame, bg="#FFF8F0")
    canvas_scroll_frame.pack(fill="both", expand=True)

    self.canvas = tk.Canvas(canvas_scroll_frame, bg="#FFF8F0", highlightthickness=0)
    self.canvas.pack(side="left", fill="both", expand=True)

    self.v_scroll = ttk.Scrollbar(canvas_scroll_frame, orient="vertical", command=self.canvas.yview)
    self.v_scroll.pack(side="right", fill="y")

    self.canvas.configure(yscrollcommand=self.v_scroll.set)

    # Body Frame
    self.body_frame = tk.Frame(self.canvas, bg="#FFF8F0")
    self.canvas_window = self.canvas.create_window((0, 0), window=self.body_frame, anchor="nw")

    # Grid Frame
    self.grid_frame = tk.Frame(self.body_frame, bg="#FFF8F0")
    self.grid_frame.pack(fill="x", expand=True, padx=10)

    self.no_products_label = tk.Label(
        self.grid_frame, text="Không có sản phẩm nào để hiển thị.",
        bg="#FFF8F0", fg="#5C2E0C", font=("Times New Roman", 14)
    )

    self.more_btn = tk.Button(
        self.body_frame,
        text="Xem thêm sản phẩm ▼",      # Thêm mũi tên
        bg="#A52A2A", fg="white",
        font=("Times New Roman", 12, "bold"),
        relief="flat",                   # Làm phẳng nút
        cursor="hand2",                  # Hiện bàn tay khi di chuột
        pady=8,                          # Tăng chiều cao nút
        command=self.load_more_products
    )
    
    # Label thông báo hết hàng (ẩn mặc định)
    self.end_label = tk.Label(
        self.body_frame, 
        text="--- Đã hiển thị hết sản phẩm ---",
        bg="#FFF8F0", fg="#888888",
        font=("Times New Roman", 11, "italic")
    )

    self.canvas.bind('<Configure>', lambda event: on_canvas_resize_ui(self, event))
    self.body_frame.bind('<Configure>', self._update_scroll_region)

    self.canvas.bind_all("<MouseWheel>", self._on_canvas_mousewheel)
    self.canvas.bind_all("<Button-4>", self._on_canvas_mousewheel)
    self.canvas.bind_all("<Button-5>", self._on_canvas_mousewheel)


def on_canvas_resize_ui(self, event):
    self.canvas.itemconfig(self.canvas_window, width=event.width)
    self._update_scroll_region()


def load_products_list_ui(self):
    try:
        self.products = getProductsForPOS() or []
    except Exception as e:
        messagebox.showerror("Lỗi CSDL", f"Không thể tải sản phẩm: {e}")
        self.products = []

    self._display_product_list()


def show_next_products_ui(self):
    start = self.display_index

    end = start + 12 
    
    display_items = self.products[start:end]
    total_products = len(self.products)
    
    if total_products == 1: cols = 1 
    elif total_products == 2: cols = 2 
    else: cols = 3 

    label_exists = hasattr(self, 'no_products_label') and self.no_products_label.winfo_exists()

    # Ẩn label hết hàng trước khi load
    if hasattr(self, 'end_label'):
        self.end_label.pack_forget()

    if not self.products:
        self.more_btn.pack_forget()
        if label_exists:
            self.no_products_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.body_frame.update_idletasks()
        self._update_scroll_region()
        return

    if label_exists:
        self.no_products_label.place_forget()

    if start == 0:
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        for i in range(5): self.grid_frame.grid_columnconfigure(i, weight=0)
        for i in range(cols): self.grid_frame.grid_columnconfigure(i, weight=1)

    row_offset = start // cols

    for i, prod_data in enumerate(display_items):
        try:
            card = ProductCard(self.grid_frame, prod_data, self.open_product_detail)
        except Exception:
            card = tk.Label(self.grid_frame, text=prod_data.get("name"), bd=1, relief="solid")

        r, c = divmod(i, cols)
        card.grid(row=r + row_offset, column=c, padx=5, pady=5, sticky="nsew")
        self._bind_children_mousewheel(card)
        if start == 0: self.grid_frame.grid_columnconfigure(c, weight=1)

    # --- XỬ LÝ HIỂN THỊ NÚT ---
    if end < len(self.products):
        self.more_btn.config(state=tk.NORMAL, text="Xem thêm sản phẩm ▼")
        self.more_btn.pack(pady=(20, 30), side="bottom", fill="x", padx=250)
    else:
        self.more_btn.pack_forget()
        self.end_label.pack(pady=(10, 30), side="bottom")

    self.body_frame.update_idletasks()
    self.canvas.config(scrollregion=self.canvas.bbox("all"))
    self._update_scroll_region()
