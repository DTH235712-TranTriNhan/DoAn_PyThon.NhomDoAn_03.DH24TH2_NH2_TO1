import tkinter as tk
from PIL import Image, ImageTk
import os

ROOT_DIR = os.getcwd()
# Giả định cấu trúc thư mục của bạn
BASE_IMAGE_DIR = os.path.normpath(os.path.join(ROOT_DIR, 'App', 'Images')) 

# --- HẰNG SỐ CẤU HÌNH ---
# Kích thước cố định của khung/box chứa ảnh (ví dụ 150x150 pixels)
IMAGE_CONTAINER_SIZE = 150 
# Kích thước tối đa của ảnh thumbnail bên trong khung (ví dụ 120x120 để chừa padding)
IMAGE_THUMBNAIL_SIZE = (120, 120) 
# ------------------------

class ProductCard(tk.Frame):
    """
    Thẻ hiển thị từng sản phẩm trong hệ thống POS.
    Hiển thị: ảnh, tên, giá, tồn kho.
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

        # ==========================================================
        # KHU VỰC ẢNH: Sử dụng Frame cố định để ngăn ngừa lỗi bố cục
        # ==========================================================
        
        # 1. Tạo Frame cố định kích thước (Container)
        self.image_container = tk.Frame(
            self, 
            width=IMAGE_CONTAINER_SIZE, 
            height=IMAGE_CONTAINER_SIZE, 
            bg="white"
        )
        # RẤT QUAN TRỌNG: Buộc Frame giữ kích thước cố định đã đặt
        self.image_container.pack_propagate(False) 
        self.image_container.pack(padx=10, pady=8) 

        # 2. Tạo Label chứa ảnh/text lỗi bên trong Frame Container
        self.image_label = tk.Label(
            self.image_container, 
            bg="white", 
            compound='center'
        )
        # Sử dụng PLACE để Label chiếm 100% diện tích của Frame cố định
        self.image_label.place(relwidth=1, relheight=1)

        self.photo = None
        self.load_image()

        # ==========================================================
        
        # Tên Sản phẩm
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

        # Gắn sự kiện click cho tất cả các widget liên quan (bao gồm Frame mới)
        widgets = [self, self.image_container, self.image_label, self.name_label, self.price_label, self.stock_label]
        for w in widgets:
            w.bind("<Button-1>", self.on_card_click)

    def load_image(self):
        abs_path = self.get_absolute_image_path()

        if abs_path is None:
            # Xử lý: Không tìm thấy đường dẫn ảnh
            self.image_label.config(
                image='',
                text="(Không có ảnh)",
                compound='center',
            )
            self.photo = None
            return

        try:
            img = Image.open(abs_path)
            # Thay đổi kích thước ảnh về kích thước thumbnail
            img.thumbnail(IMAGE_THUMBNAIL_SIZE, Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            # Cấu hình Label để hiển thị ảnh
            self.image_label.config(
                image=self.photo,
                text="",
                compound='center',
            )
            self.image_label.image = self.photo

        except Exception as e:
            print(f"LỖI LOAD ẢNH '{abs_path}': {e}")
            # Xử lý: Tải ảnh thất bại (hiển thị text lỗi)
            self.image_label.config(
                image='',
                text="(Ảnh lỗi)",
                compound='center',
            )
            self.photo = None

    def get_absolute_image_path(self):
        # Logic tìm đường dẫn tuyệt đối của ảnh sản phẩm hoặc ảnh mặc định
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