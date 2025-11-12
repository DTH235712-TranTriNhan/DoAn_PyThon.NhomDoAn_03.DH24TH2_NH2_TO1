import tkinter as tk
from PIL import Image, ImageTk
import os

ROOT_DIR = os.getcwd()
BASE_IMAGE_DIR = os.path.normpath(os.path.join(ROOT_DIR, 'App', 'Images'))

# --- THAY ĐỔI CÁC HẰNG SỐ NÀY ---
# Kích thước cố định của khung/box chứa ảnh (ví dụ 150x150)
IMAGE_CONTAINER_SIZE = 150 
# Kích thước tối đa của ảnh thumbnail bên trong khung (ví dụ 120x120 để chừa padding)
IMAGE_THUMBNAIL_SIZE = (120, 120) 
# Xóa IMAGE_AREA_HEIGHT không cần thiết
# --------------------------------

class ProductCard(tk.Frame):
    """
    Thẻ hiển thị từng sản phẩm trong POS.
    Hiện: ảnh, tên, giá, tồn kho. Không hiển thị SKU/description.
    """
    def __init__(self, parent, product, open_detail_callback, **kwargs):
        super().__init__(parent, **kwargs)

        self.product = product
        self.open_detail_callback = open_detail_callback

        self.config(
            relief="raised",
            bd=1,
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc"
        )

        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

        # Ảnh
        self.image_label = tk.Label(self, bg="white", compound='center')
        
        # SỬA: Cố định kích thước của Label để nó hoạt động như một 'box'
        self.image_label.config(
            width=IMAGE_CONTAINER_SIZE, 
            height=IMAGE_CONTAINER_SIZE
        )
        self.image_label.pack_propagate(False) # Rất quan trọng: Ngăn nội dung co/giãn box

        self.image_label.pack(padx=10, pady=8)
        self.photo = None
        self.load_image()

        # Tên
        name = product.get("name", "Sản phẩm không tên")
        self.name_label = tk.Label(
            self,
            text=name,
            font=("Times New Roman", 12, "bold"),
            bg="white",
            wraplength=160,
            justify="center"
        )
        self.name_label.pack(padx=5, pady=(0, 6))

        # Giá
        price_str = product.get("price_str", "0 đ")
        self.price_label = tk.Label(
            self,
            text=price_str,
            font=("Times New Roman", 12),
            fg="red",
            bg="white"
        )
        self.price_label.pack(pady=(0, 6))

        # Tồn kho
        stock_qty = self.product.get("stock", "N/A")
        stock_text = f"Tồn kho: {stock_qty}"
        self.stock_label = tk.Label(
            self,
            text=stock_text,
            font=("Times New Roman", 10),
            fg="#444",
            bg="white"
        )
        self.stock_label.pack(pady=(0, 8))

        # Binding click cho toàn bộ card
        widgets = [self, self.image_label, self.name_label, self.price_label, self.stock_label]
        for w in widgets:
            w.bind("<Button-1>", self.on_card_click)

    def load_image(self):
        abs_path = self.get_absolute_image_path()

        if abs_path is None:
            self.image_label.config(
                image='',
                text="(Không có ảnh)",
                compound='center',
                # Kích thước cố định được giữ nguyên từ __init__
            )
            self.photo = None
            return

        try:
            img = Image.open(abs_path)
            # Ảnh được thu nhỏ về kích thước tối đa của thumbnail (120x120)
            img.thumbnail(IMAGE_THUMBNAIL_SIZE, Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            self.image_label.config(
                image=self.photo,
                text="",
                compound='center', # Quan trọng: Căn giữa ảnh nhỏ bên trong Label cố định
                # XÓA: Loại bỏ các lệnh cấu hình width/height động
            )
            self.image_label.image = self.photo
            
            # XÓA: Loại bỏ các lệnh pack/propagate không cần thiết hoặc sai vị trí
            # self.image_label.pack_forget() 
            # self.image_label.pack(expand=True)
            # self.image_label.configure(anchor="center") 

        except Exception as e:
            print(f"LỖI LOAD ẢNH '{abs_path}': {e}")
            self.image_label.config(
                image='',
                text="(Ảnh lỗi)",
                compound='center',
                # Kích thước cố định được giữ nguyên từ __init__
            )
            self.photo = None

    def get_absolute_image_path(self):
        # ... (giữ nguyên) ...
        image_filename = self.product.get("imagePath", "")
        if image_filename:
            base_filename = os.path.basename(image_filename)
            abs_path = os.path.normpath(os.path.join(BASE_IMAGE_DIR, base_filename))
            if os.path.exists(abs_path):
                return abs_path
        abs_default_path = os.path.join(BASE_IMAGE_DIR, "default.jpg")
        if os.path.exists(abs_default_path):
            return abs_default_path
        return None

    def on_hover(self, event):
        self.config(highlightbackground="#8B0000", bg="#FFF5F5")

    def on_leave(self, event):
        self.config(highlightbackground="#ccc", bg="white")

    def on_card_click(self, event):
        try:
            event.widget.focus_set()
        except Exception:
            pass
        self.open_detail_callback(self.product)