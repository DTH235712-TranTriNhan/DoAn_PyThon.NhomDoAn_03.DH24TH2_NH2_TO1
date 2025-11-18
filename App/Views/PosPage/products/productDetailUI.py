import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


def open_product_detail_ui(self, product):
    win = tk.Toplevel(self)
    win.title(product.get("name", "Chi tiết sản phẩm"))
    win.geometry("700x480")
    win.minsize(520, 360)
    win.resizable(True, True)
    win.grab_set()

    image_path = self._get_absolute_image_path(product)
    photo_modal_local = self._load_image_for_modal(image_path)

    win.grid_rowconfigure(0, weight=1)
    win.grid_rowconfigure(1, weight=0)
    win.grid_columnconfigure(0, weight=1)

    content_frame = tk.Frame(win, bg="#FFF8F0")
    content_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)

    canvas = tk.Canvas(content_frame, bg="#FFF8F0", highlightthickness=0)
    v_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=v_scroll.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    v_scroll.grid(row=0, column=1, sticky="ns")

    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    scrollable = tk.Frame(canvas, bg="#FFF8F0")
    canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")

    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable.bind("<Configure>", _on_frame_configure)

    def _on_canvas_configure(event):
        canvas.itemconfigure(canvas_window, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    scrollable.grid_columnconfigure(0, weight=1, uniform="col")
    scrollable.grid_columnconfigure(1, weight=1, uniform="col")

    left = tk.Frame(scrollable, bg="#FFF8F0")
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=10)

    if photo_modal_local:
        img_lbl = tk.Label(left, image=photo_modal_local, bg="#FFF8F0")
        img_lbl.image = photo_modal_local
        img_lbl.pack(pady=8)
    else:
        tk.Label(left, text="(Không có ảnh)", bg="#F5F5F5", width=20, height=8).pack(pady=8)

    tk.Label(left, text=product.get("name", "Tên sản phẩm"),
             font=("Times New Roman", 16, "bold"),
             fg="#8B0000", bg="#FFF8F0",
             wraplength=320, justify="left").pack(anchor="w", pady=(6, 4))

    tk.Label(left, text=f"Giá: {product.get('price_str', '0 đ')}",
             font=("Times New Roman", 14, "bold"), fg="red",
             bg="#FFF8F0").pack(anchor="w", pady=(0, 6))

    stock = product.get("stock", 0)
    stock_color = "green" if stock > 0 else "red"
    tk.Label(left, text=f"Tồn kho: {stock}",
             font=("Times New Roman", 12, "italic"),
             fg=stock_color, bg="#FFF8F0").pack(anchor="w", pady=(0, 8))

    # RIGHT COLUMN
    right = tk.Frame(scrollable, bg="#FFF8F0")
    right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=10)

    tk.Label(right, text="Mô tả sản phẩm",
             font=("Times New Roman", 12, "bold"), bg="#FFF8F0").pack(anchor="w", pady=(0, 6))

    desc_frame = tk.Frame(right, bg="#FFF8F0")
    desc_frame.pack(fill="both", expand=True)

    full_desc = product.get("description", "") or "Không có mô tả cho sản phẩm này."

    txt = tk.Text(desc_frame, wrap="word",
                  font=("Times New Roman", 11),
                  bd=1, relief="solid", height=12)
    txt.insert("1.0", full_desc)
    txt.config(state="disabled")
    txt.pack(side="left", fill="both", expand=True)

    txt_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=txt.yview)
    txt_scroll.pack(side="right", fill="y")
    txt.config(yscrollcommand=txt_scroll.set)

    def _on_text_mousewheel(event):
        if event.num == 5 or event.delta < 0:
            txt.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            txt.yview_scroll(-1, "units")
        return "break"

    txt.bind("<MouseWheel>", _on_text_mousewheel)
    txt.bind("<Button-4>", _on_text_mousewheel)
    txt.bind("<Button-5>", _on_text_mousewheel)

    # BOTTOM BAR
    ctrl = tk.Frame(win, bg="#FFF8F0")
    ctrl.grid(row=1, column=0, sticky="ew", padx=12, pady=(6, 12))
    ctrl.grid_columnconfigure(0, weight=1)
    ctrl.grid_columnconfigure(1, weight=1)

    tk.Button(
        ctrl, text="💰 Mua ngay (Thanh toán)", bg="#4CAF50", fg="white",
        font=("Times New Roman", 12, "bold"),
        command=lambda: self.process_buy_now(product, win)
    ).grid(row=0, column=0, padx=8, sticky="ew")

    add_btn = tk.Button(
        ctrl, text="🛒 Thêm vào giỏ hàng",
        bg="#A52A2A", fg="white",
        font=("Times New Roman", 12, "bold"),
        command=lambda: self._add_to_cart_from_detail(product, win)
    )
    add_btn.grid(row=0, column=1, padx=8, sticky="ew")

    if stock <= 0:
        add_btn.config(state=tk.DISABLED)
