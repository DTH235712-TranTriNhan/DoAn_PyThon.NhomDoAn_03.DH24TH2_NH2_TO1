import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import os

from App.Views.ProductCard import ProductCard
from Database.dbOrders import createOrder, format_currency
from Database.dbProducts import getProductsForPOS
# Giả định ProductCard, dbProducts, dbOrders, format_currency được import và hoạt động đúng

# Import từ ProductCard để đảm bảo đường dẫn ảnh đúng
ROOT_DIR = os.getcwd()
BASE_IMAGE_DIR = os.path.normpath(os.path.join(ROOT_DIR, 'App', 'Images'))

# --- THÔNG SỐ CỐ ĐỊNH CHIỀU CAO CHO ẢNH TRONG MODAL ---
MODAL_IMAGE_SIZE = (200, 200) 
# --------------------------------------------------------

class POSPage(tk.Frame):
    """Giao diện Điểm Bán Hàng (Point of Sale) chính."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFF8F0")
        self.controller = controller

        # Dữ liệu
        self.current_user = None
        self.cart_items = {}
        self.products = []
        self.display_index = 0 # để phân trang sản phẩm (6 sp / lần)
        self.photo_modal = None # Lưu trữ ImageTk.PhotoImage cho modal
        # Cập nhật trạng thái Toast
        self.current_toast = None # FIX 1: Lưu trữ tham chiếu đến toast hiện tại
        self.toast_id = None # ID để hủy hiệu ứng after (hẹn giờ)

        # Layout chính
        self.create_header()
        
        # THAY ĐỔI: Tạo Toast Manager riêng
        self.create_toast_manager() 
        
        self.create_product_grid() 
        self.create_footer()
        self.load_products_list()

    # --- FIX 2: PROPERTY KIỂM TRA ĐĂNG NHẬP ---
    @property
    def is_logged_in(self):
        """Kiểm tra xem người dùng hiện tại có hợp lệ không."""
        return self.current_user and 'id' in self.current_user

    # ------------------ HEADER ------------------
    def create_header(self):
        header = tk.Frame(self, bg="#8B0000", height=60)
        header.pack(fill="x")

        tk.Label(
            header, text="🍇 RubyOak POS",
            bg="#8B0000", fg="white",
            font=("Times New Roman", 20, "bold")
        ).pack(side="left", padx=20)

        self.login_button = tk.Button(
            header, text="Đăng nhập", bg="#E53935", fg="white",
            font=("Times New Roman", 12, "bold"),
            relief="flat", command=self.show_login_dialog
        )
        self.login_button.pack(side="right", padx=10, pady=10)

        self.user_label = tk.Label(header, text="Chưa đăng nhập", bg="#8B0000", fg="#FFCDD2")
        self.user_label.pack(side="right", padx=10)
        
        self.user_label.bind("<Button-1>", lambda e: self.show_user_info_dialog())
        self.user_label.config(cursor="hand2")

        self.cart_btn = tk.Button(
            header, text="🛒 Giỏ hàng (0)", bg="#A52A2A", fg="white",
            font=("Times New Roman", 12, "bold"),
            relief="flat", command=self.show_cart_window
        )
        self.cart_btn.pack(side="right", padx=10, pady=10)
    
    # ------------------ KHU VỰC TOAST RIÊNG ------------------
    def create_toast_manager(self):
        """Tạo/chuẩn bị 1 Toplevel nhỏ để hiển thị toast (reusable)."""
        # Nếu đã tạo thì bỏ qua
        if getattr(self, "toast_win", None) and self.toast_win.winfo_exists():
            return

        # Toplevel không viền, luôn topmost, ẩn ban đầu
        self.toast_win = tk.Toplevel(self)
        self.toast_win.overrideredirect(True)
        self.toast_win.attributes("-topmost", True)
        # Không cho tương tác chuột (tùy OS — nếu gây lỗi thì comment dòng dưới)
        try:
            self.toast_win.attributes("-transparentcolor", "pink")  # optional visual tweak on some systems
        except Exception:
            pass

        # Nội dung: label nhỏ, margin, rounded-ish via border
        self.toast_label = tk.Label(
            self.toast_win,
            text="",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12, pady=6,
            bd=0, relief="flat",
            wraplength=400, justify="center"
        )
        self.toast_label.pack()

        # Ẩn window ban đầu
        self.toast_win.withdraw()
        self.current_toast = None
        self.toast_id = None

    # ------------------ GRID SẢN PHẨM ------------------
    def create_product_grid(self):
        # Frame chứa Canvas và Scrollbar
        product_area = tk.Frame(self, bg="#FFF8F0", height=400) 
        product_area.pack(fill="both", expand=True, padx=20, pady=0) 

        # 1. Scrollbar và Canvas
        self.canvas = tk.Canvas(product_area, bg="#FFF8F0", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True) 

        self.v_scroll = ttk.Scrollbar(product_area, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side="right", fill="y") # Mặc định hiển thị, sau đó hàm update sẽ ẩn nếu cần
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        # 2. self.grid_frame (Frame sẽ chứa các ProductCard, đặt bên trong Canvas)
        self.grid_frame = tk.Frame(self.canvas, bg="#FFF8F0")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw") 

        # 3. Label thông báo "Không có sản phẩm" (Tạo nhưng chưa pack)
        self.no_products_label = tk.Label(
            self.grid_frame, text="Không có sản phẩm nào để hiển thị.", 
            bg="#FFF8F0", fg="#5C2E0C", font=("Times New Roman", 14)
        )

        # Ràng buộc sự kiện để cập nhật kích thước 
        self.canvas.bind('<Configure>', self.on_canvas_resize) 
        self.grid_frame.bind('<Configure>', self._update_scroll_region)
        self.canvas.bind('<Configure>', self._update_scroll_region, add='+')

        # Nút Xem thêm (Đặt bên ngoài Canvas)
        self.more_btn = tk.Button(
            self, text="Xem thêm sản phẩm",
            bg="#A52A2A", fg="white",
            font=("Times New Roman", 12, "bold"),
            command=self.load_more_products
        )

        self.canvas.bind_all("<MouseWheel>", self._on_canvas_mousewheel)    # Windows, Mac
        self.canvas.bind_all("<Button-4>", self._on_canvas_mousewheel)      # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_canvas_mousewheel)

    def on_canvas_resize(self, event):
        """Đảm bảo self.grid_frame (nội dung) luôn rộng bằng Canvas."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def load_products_list(self):
        """Tải và làm mới danh sách sản phẩm."""
        try:
            # SỬ DỤNG MOCK DATA NẾU KHÔNG CÓ DB ĐỂ TRÁNH LỖI IMPORT
            try:
                self.products = getProductsForPOS() or [] 
            except NameError:
                print("Warning: Using Mock Data. Ensure Database imports are correct.")
                self.products = [
                    {"sku": "SKU001", "name": "Vang Đỏ Cabernet", "price": 500000.0, "price_str": "500.000 đ", "stock": 10, "imagePath": "wine1.jpg"},
                    {"sku": "SKU002", "name": "Vang Trắng Chardonnay", "price": 450000.0, "price_str": "450.000 đ", "stock": 5, "imagePath": "wine2.jpg"},
                    {"sku": "SKU003", "name": "Vang Nổ Sparkling", "price": 600000.0, "price_str": "600.000 đ", "stock": 0, "imagePath": "wine3.jpg"},
                    {"sku": "SKU004", "name": "Rượu Sake Nhật", "price": 800000.0, "price_str": "800.000 đ", "stock": 15, "imagePath": "wine4.jpg"},
                ]
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể tải sản phẩm: {e}")
            self.products = []
            
        self.display_index = 0
        
        # 1. Xóa tất cả các card cũ
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        # 2. Ẩn nút "Xem thêm" và thông báo trước
        self.more_btn.pack_forget() 
            
        self.show_next_products()
        # Đặt lại vị trí Scrollbar về đầu
        if hasattr(self, 'canvas'):
            self.canvas.yview_moveto(0)


    def show_next_products(self):
        """Hiển thị 6 sản phẩm mỗi lần, nối tiếp sản phẩm đã có."""
        start = self.display_index
        end = start + 6
        display_items = self.products[start:end]
        cols = 3

        # Trường hợp 1: Danh sách sản phẩm TỔNG THỂ trống.
        if not self.products:
            self.more_btn.pack_forget() 
            self.no_products_label.pack(pady=50) 
            return

        # Ẩn thông báo "Không có sản phẩm" nếu đã có sản phẩm
        self.no_products_label.pack_forget()

        # Tính toán row offset (hàng bắt đầu) để sản phẩm mới nối tiếp sản phẩm cũ
        row_offset = start // cols 

        for i, prod_data in enumerate(display_items):
            # CẬP NHẬT: Dùng Mock ProductCard nếu cần
            try:
                card = ProductCard(self.grid_frame, prod_data, self.open_product_detail)
            except NameError:
                # Fallback: Dùng Label đơn giản nếu ProductCard không import được
                card = tk.Label(self.grid_frame, text=f"{prod_data.get('name')}\n{prod_data.get('price_str')}", bd=1, relief="solid", padx=10, pady=10)
                card.bind("<Button-1>", lambda e, p=prod_data: self.open_product_detail(p))
            
            r, c = divmod(i, cols) 
            card.grid(row=r + row_offset, column=c, padx=5, pady=5, sticky="nsew") 
            
            if start == 0:
                self.grid_frame.grid_columnconfigure(c, weight=1) 

        # Cần ràng buộc lại scrollregion sau khi thêm widget
        self.grid_frame.update_idletasks()
        self.canvas.config(scrollregion = self.canvas.bbox("all"))

        # --- ĐIỀU CHỈNH HIỂN THỊ NÚT "XEM THÊM" ---
        if end < len(self.products):
            self.more_btn.config(state=tk.NORMAL, text="Xem thêm sản phẩm")
            self.more_btn.pack(pady=(0, 10))
        else:
            self.more_btn.pack_forget() 


    def load_more_products(self):
        self.display_index += 6
        self.show_next_products()
        
    # ------------------ CỬA SỔ CHI TIẾT SẢN PHẨM ------------------
    def open_product_detail(self, product):
        """Modal chi tiết: canvas scrollable ở trên + fixed bottom button bar.
        Layout uses grid on `win` so bottom bar stays visible and content scrolls when needed.
        """
        win = tk.Toplevel(self)
        win.title(product.get("name", "Chi tiết sản phẩm"))
        win.geometry("700x480")
        win.minsize(520, 360)
        win.resizable(True, True)
        win.grab_set()

        # Lấy ảnh
        image_path = self._get_absolute_image_path(product)
        photo_modal_local = self._load_image_for_modal(image_path)

        # --- Grid config on window: row0 = content (expandable), row1 = ctrl (fixed) ---
        win.grid_rowconfigure(0, weight=1) # content expands
        win.grid_rowconfigure(1, weight=0) # ctrl fixed
        win.grid_columnconfigure(0, weight=1)

        # --- CONTENT FRAME (holds canvas + scrollbar) ---
        content_frame = tk.Frame(win, bg="#FFF8F0")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)

        # Canvas + vertical scrollbar (canvas will take the available space of content_frame)
        canvas = tk.Canvas(content_frame, bg="#FFF8F0", highlightthickness=0)
        v_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Frame inside canvas which will hold the actual two-column content
        scrollable = tk.Frame(canvas, bg="#FFF8F0")
        # create window inside canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")

        # keep canvas scrollregion updated
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable.bind("<Configure>", _on_frame_configure)

        # Also ensure canvas width follows content_frame width (responsive)
        def _on_canvas_configure(event):
            # set inner frame width to canvas width so columns wrap properly
            canvas.itemconfigure(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # === 2 CỘT CHÍNH trong scrollable ===
        scrollable.grid_columnconfigure(0, weight=1, uniform="col")
        scrollable.grid_columnconfigure(1, weight=1, uniform="col")

        # LEFT COLUMN (image + basic info)
        left = tk.Frame(scrollable, bg="#FFF8F0")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=10)

        if photo_modal_local:
            img_lbl = tk.Label(left, image=photo_modal_local, bg="#FFF8F0")
            img_lbl.image = photo_modal_local
            img_lbl.pack(pady=8)
        else:
            tk.Label(left, text="(Không có ảnh)", bg="#F5F5F5", width=20, height=8).pack(pady=8)

        tk.Label(left, text=product.get("name", "Tên sản phẩm"), font=("Times New Roman", 16, "bold"),
                    fg="#8B0000", bg="#FFF8F0", wraplength=320, justify="left").pack(anchor="w", pady=(6, 4))
        tk.Label(left, text=f"Giá: {product.get('price_str', '0 đ')}", font=("Times New Roman", 14, "bold"),
                    fg="red", bg="#FFF8F0").pack(anchor="w", pady=(0, 6))

        stock = product.get("stock", 0)
        stock_color = "green" if stock > 0 else "red"
        tk.Label(left, text=f"Tồn kho: {stock}", font=("Times New Roman", 12, "italic"),
                    fg=stock_color, bg="#FFF8F0").pack(anchor="w", pady=(0, 8))

        # RIGHT COLUMN (description area)
        right = tk.Frame(scrollable, bg="#FFF8F0")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=10)

        tk.Label(right, text="Mô tả sản phẩm", font=("Times New Roman", 12, "bold"), bg="#FFF8F0").pack(anchor="w", pady=(0, 6))

        full_desc = product.get("description", "") or "Không có mô tả cho sản phẩm này."

        desc_frame = tk.Frame(right, bg="#FFF8F0")
        desc_frame.pack(fill="both", expand=True)

        # Text read-only + scrollbar: give it a sensible min height, but it will scroll inside canvas if needed
        txt = tk.Text(desc_frame, wrap="word", font=("Times New Roman", 11), bd=1, relief="solid", height=12)
        txt.insert("1.0", full_desc)
        txt.config(state="disabled")
        txt.pack(side="left", fill="both", expand=True)

        txt_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=txt.yview)
        txt_scroll.pack(side="right", fill="y")
        txt.config(yscrollcommand=txt_scroll.set)
        
        # ----------------------------------------------------
        # --- CẬP NHẬT: CHỈ CUỘN TRONG KHU VỰC MÔ TẢ (txt) ---
        # ----------------------------------------------------
        
        def _on_text_mousewheel(event):
            """Xử lý cuộn chuột cho Text widget và ngăn chặn lan truyền."""
            # Dùng yview_scroll để cuộn nội dung trong Text widget
            if event.num == 5 or event.delta < 0:
                txt.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                txt.yview_scroll(-1, "units")
                
            # Quan trọng: Trả về 'break' để ngăn sự kiện lan truyền lên các widget cha (Canvas)
            return "break" 

        # Ràng buộc cuộn chuột chỉ vào widget Text (txt)
        txt.bind("<MouseWheel>", _on_text_mousewheel)    # Windows, Mac
        txt.bind("<Button-4>", _on_text_mousewheel)      # Linux scroll up
        txt.bind("<Button-5>", _on_text_mousewheel)      # Linux scroll down

        # --- FIXED BOTTOM BUTTON BAR (always visible) ---
        ctrl = tk.Frame(win, bg="#FFF8F0")
        ctrl.grid(row=1, column=0, sticky="ew", padx=12, pady=(6, 12))
        ctrl.grid_columnconfigure(0, weight=1)
        ctrl.grid_columnconfigure(1, weight=1)

        buy_now_btn = tk.Button(ctrl, text="💰 Mua ngay (Thanh toán)", bg="#4CAF50", fg="white",
                                font=("Times New Roman", 12, "bold"),
                                command=lambda: self.process_buy_now(product, win))
        buy_now_btn.grid(row=0, column=0, padx=8, sticky="ew")

        add_to_cart_btn = tk.Button(ctrl, text="🛒 Thêm vào giỏ hàng", bg="#A52A2A", fg="white",
                                    font=("Times New Roman", 12, "bold"),
                                    command=lambda: self._add_to_cart_from_detail(product, win))
        add_to_cart_btn.grid(row=0, column=1, padx=8, sticky="ew")

        if stock <= 0:
            buy_now_btn.config(state=tk.DISABLED, text="Hết hàng")
            add_to_cart_btn.config(state=tk.DISABLED)


    def _get_absolute_image_path(self, product):
        """Hàm hỗ trợ lấy đường dẫn ảnh cho modal."""
        image_filename = product.get("imagePath", "") 
        if image_filename:
            base_filename = os.path.basename(image_filename)
            abs_path = os.path.normpath(os.path.join(BASE_IMAGE_DIR, base_filename))
            if os.path.exists(abs_path):
                return abs_path

        abs_default_path = os.path.join(BASE_IMAGE_DIR, "default.jpg")
        if os.path.exists(abs_default_path):
            return abs_default_path
            
        return None
        
    def _load_image_for_modal(self, abs_path):
        """Tải và trả về ImageTk.PhotoImage cho modal."""
        if abs_path is None:
            return None
        try:
            img = Image.open(abs_path)
            img.thumbnail(MODAL_IMAGE_SIZE) 
            self.photo_modal = ImageTk.PhotoImage(img) 
            return self.photo_modal
        except Exception as e:
            print(f"LỖI LOAD ẢNH cho modal: {e}") 
            return None


    def _add_to_cart_from_detail(self, product, win):
        try:
            self.add_to_cart(product)
        except Exception as e:
            print(f"Error in _add_to_cart_from_detail: {e}")
        finally:
            if win and win.winfo_exists():
                win.destroy()


    def process_buy_now(self, product, win):
        """Thực hiện thanh toán ngay lập tức cho 1 sản phẩm."""
        win.destroy() # Đóng modal
        
        # KIỂM TRA ĐĂNG NHẬP
        if not self.is_logged_in: # Sử dụng property is_logged_in
            self.show_error_toast("Bạn cần đăng nhập để thanh toán.")
            # Loại bỏ self.show_login_dialog() theo yêu cầu người dùng
            return
            
        # Kiểm tra tồn kho lần cuối
        if product.get("stock", 0) <= 0:
            messagebox.showerror("Lỗi", f"Sản phẩm '{product.get('name')}' đã hết hàng.")
            self.load_products_list()
            return
            
        # Chuẩn bị dữ liệu đơn hàng (chỉ 1 sản phẩm)
        user_id = self.current_user['id']
        name = product.get("name")
        price = float(product.get("price", 0))
        total = price
        
        items_to_checkout = [{
            "sku": product.get("sku"), 
            "name": name, 
            "quantity": 1, 
            "unitPrice": price
        }]
        
        try:
            # SỬ DỤNG MOCK FUNCTION NẾU KHÔNG CÓ DB
            success, result = createOrder(user_id, items_to_checkout) 
        except NameError:
            success, result = True, "MOCK-12345" # Giả lập thành công
            print("Warning: Using Mock createOrder function.")
        
        if success:
            try:
                formatted_total = format_currency(total)
            except NameError:
                formatted_total = f"{total:,}"
            # Hiển thị toast thay vì messagebox
            toast_msg = f"Thanh toán thành công!\nTổng: {formatted_total} VNĐ"
            # Nếu muốn chỉ 1 dòng: toast_msg = f"Thanh toán thành công — Mã: {result} — {formatted_total} VNĐ"
            self.show_toast(toast_msg)
            # Cập nhật view / dữ liệu
            self.load_products_list()
        else:
            messagebox.showerror("Lỗi", f"Thanh toán thất bại: {result}")
            

    # --- FIX 3: ĐỊNH NGHĨA HÀM DỌN DẸP TOAST ---
    def _clear_current_toast(self):
        """Hủy toast hiện tại: huỷ after và ẩn toast_win."""
        # Cancel timer
        if getattr(self, "toast_id", None):
            try:
                self.after_cancel(self.toast_id)
            except Exception:
                pass
            self.toast_id = None

        # Ẩn Toplevel nếu còn hiện
        if getattr(self, "toast_win", None) and self.toast_win.winfo_exists():
            try:
                self.toast_win.withdraw()
            except Exception:
                pass

        self.current_toast = None
            
    # ------------------ THÊM VÀO GIỎ + TOAST ------------------
    def add_to_cart(self, product):
        """Thêm sản phẩm vào giỏ hàng (Được gọi từ _add_to_cart_from_detail hoặc mua ngay)."""
        
        # KIỂM TRA ĐĂNG NHẬP (Sử dụng property is_logged_in)
        if not self.is_logged_in: 
            self.show_error_toast("Bạn cần đăng nhập để thêm sản phẩm vào giỏ.")
            # Loại bỏ self.show_login_dialog() theo yêu cầu người dùng
            return

        # Hàm này nhận 'product' là dictionary từ ProductCard
        sku = product.get("sku")
        name = product.get("name")
        price = float(product.get("price", 0))
        stock = product.get("stock", 0)

        # Kiểm tra tồn kho
        if stock <= 0:
            self.show_error_toast(f"Sản phẩm '{name}' đã hết hàng.")
            return
            
        # Kiểm tra nếu thêm vượt quá tồn kho
        current_qty = self.cart_items[sku]["quantity"] if sku in self.cart_items else 0
        if current_qty + 1 > stock:
            self.show_error_toast(f"Không thể thêm. Tồn kho chỉ còn {stock} sản phẩm.")
            return

        if sku in self.cart_items:
            self.cart_items[sku]["quantity"] += 1
        else:
            self.cart_items[sku] = {
                "sku": sku, "name": name, "quantity": 1, "unitPrice": price, "stock": stock
            }

        self.update_cart_badge()
        self.show_toast(f"Đã thêm '{name}' vào giỏ hàng")


    def run_toast_animation(self, message, is_error=False):
        """Hiển thị toast in-place using self.toast_win and auto-hide after delay."""
        if not getattr(self, "toast_win", None) or not self.toast_win.winfo_exists():
            # đảm bảo đã tạo manager
            self.create_toast_manager()

        # Style tùy theo error hay success
        bg = "#F44336" if is_error else "#4CAF50"
        self.toast_label.config(text=message, bg=bg)

        # Position toast_win near top center of the application window
        # Calculate root window absolute position and width
        try:
            # self.winfo_toplevel() là cửa sổ chính
            root = self.winfo_toplevel()
            root.update_idletasks()
            rx = root.winfo_rootx()
            ry = root.winfo_rooty()
            rwidth = root.winfo_width()
            # width/height của toast (after packing)
            self.toast_win.update_idletasks()
            tw = self.toast_win.winfo_reqwidth()
            th = self.toast_win.winfo_reqheight()
            # đặt ở top center, cách top của root khoảng 10px (hoặc dưới header nếu bạn muốn)
            x = rx + max(10, (rwidth - tw) // 2)
            y = ry + 10  # 10 px từ cạnh trên cửa sổ chính
            self.toast_win.geometry(f"{tw}x{th}+{x}+{y}")
        except Exception:
            # Fallback: center on screen
            self.toast_win.geometry("+200+50")

        # Show and cancel any previous timer
        try:
            self.toast_win.deiconify()
            self.toast_win.lift()
        except Exception:
            pass

        if self.toast_id:
            try:
                self.after_cancel(self.toast_id)
            except Exception:
                pass
            self.toast_id = None

        # Auto-hide sau 2000-3000ms
        self.toast_id = self.after(2500, self._clear_current_toast)
        self.current_toast = message


    def show_error_toast(self, message):
        """Hiện toast lỗi (màu đỏ). Nếu cùng message đang hiện thì reset thời gian."""
        # Nếu cùng message đang hiện -> reset timer
        if getattr(self, "current_toast", None) == message and getattr(self, "toast_win", None) and self.toast_win.winfo_ismapped():
            if self.toast_id:
                try:
                    self.after_cancel(self.toast_id)
                except Exception:
                    pass
            self.toast_id = self.after(2500, self._clear_current_toast)
            return

        self._clear_current_toast()
        self.run_toast_animation(message, is_error=True)

    def show_toast(self, message):
        """Hiện toast thành công. Nếu cùng message đang hiện thì reset thời gian."""
        # Nếu cùng message đang hiện -> reset timer
        if getattr(self, "current_toast", None) == message and getattr(self, "toast_win", None) and self.toast_win.winfo_ismapped():
            if self.toast_id:
                try:
                    self.after_cancel(self.toast_id)
                except Exception:
                    pass
            self.toast_id = self.after(2500, self._clear_current_toast)
            return

        # Ngược lại: show mới
        self._clear_current_toast()
        self.run_toast_animation(message, is_error=False)

    def update_cart_badge(self):
        total_qty = sum(item["quantity"] for item in self.cart_items.values())
        self.cart_btn.config(text=f"🛒 Giỏ hàng ({total_qty})")

    # ------------------ GIỎ HÀNG (THÊM CHỨC NĂNG XÓA) ------------------
    def show_cart_window(self):
        if not self.cart_items:
            messagebox.showinfo("Giỏ hàng", "Giỏ hàng trống.")
            return

        win = tk.Toplevel(self)
        win.title("Giỏ hàng")
        win.geometry("550x450") # Tăng chiều rộng để thêm cột Xóa
        win.grab_set()
        
        # Frame chứa Treeview và Nút Xóa
        tree_frame = tk.Frame(win, padx=10, pady=10)
        tree_frame.pack(fill="both", expand=True)

        # 1. Treeview
        cart_tree = ttk.Treeview(
            tree_frame, columns=("Tên", "SL", "Đơn giá", "Tổng", "Xóa"), show="headings"
        )
        for col in ("Tên", "SL", "Đơn giá", "Tổng", "Xóa"):
            cart_tree.heading(col, text=col)
        
        cart_tree.column("Tên", width=180, anchor="w")
        cart_tree.column("SL", width=40, anchor="center")
        cart_tree.column("Đơn giá", width=90, anchor="e")
        cart_tree.column("Tổng", width=90, anchor="e")
        cart_tree.column("Xóa", width=40, anchor="center") # Cột cho nút xóa
        
        cart_tree.pack(side="left", fill="both", expand=True)
        
        # Thêm Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=cart_tree.yview)
        vsb.pack(side="right", fill="y")
        cart_tree.configure(yscrollcommand=vsb.set)

        total = self.populate_cart_tree(cart_tree)

        # Binding sự kiện click cho nút xóa (trong Treeview)
        cart_tree.bind('<ButtonRelease-1>', lambda e: self.handle_cart_click(e, cart_tree, win))


        # Frame cho tổng tiền và nút Thanh toán
        control_frame = tk.Frame(win, padx=10, pady=10)
        control_frame.pack(fill="x", side="bottom")
        
        try:
            # SỬ DỤNG MOCK FORMATTER NẾU KHÔNG CÓ DB
            formatted_total = format_currency(total)
        except NameError:
            formatted_total = f"{total:,}"

        self.total_label = tk.Label(
            control_frame, text=f"Tổng cộng: {formatted_total} VNĐ",
            fg="red", font=("Times New Roman", 14, "bold")
        )
        self.total_label.pack(side="left", padx=10)

        tk.Button(
            control_frame, text="Thanh toán", bg="#4CAF50", fg="white",
            font=("Times New Roman", 12, "bold"),
            command=lambda: self.process_checkout(win, total)
        ).pack(side="right", padx=10)
        
        self.win = win # Lưu tham chiếu để có thể đóng từ hàm remove_from_cart
        self.cart_tree = cart_tree # Lưu tham chiếu để có thể cập nhật

    def populate_cart_tree(self, cart_tree):
        """Đổ dữ liệu giỏ hàng vào Treeview và tính tổng cộng."""
        total = 0
        cart_tree.delete(*cart_tree.get_children()) # Xóa dữ liệu cũ
        
        for sku, item in self.cart_items.items():
            subtotal = item["quantity"] * item["unitPrice"]
            total += subtotal
            
            try:
                # SỬ DỤNG MOCK FORMATTER NẾU KHÔNG CÓ DB
                formatted_unit_price = format_currency(item["unitPrice"])
                formatted_subtotal = format_currency(subtotal)
            except NameError:
                formatted_unit_price = f"{item['unitPrice']:,}"
                formatted_subtotal = f"{subtotal:,}"
                
            cart_tree.insert(
                "", tk.END,
                iid=sku, # Dùng SKU làm ID của item trong Treeview
                values=(item["name"], item["quantity"],
                        formatted_unit_price,
                        formatted_subtotal,
                        '🗑️ Xóa') # Nút xóa
            )
        return total

    def handle_cart_click(self, event, cart_tree, win):
        """Xử lý sự kiện click trong Treeview, đặc biệt cho cột 'Xóa'."""
        item = cart_tree.identify_row(event.y)
        column = cart_tree.identify_column(event.x)
        
        # Kiểm tra xem có phải click vào cột 'Xóa' không (cột #5)
        if column == '#5' and item:
            sku = item # item id chính là SKU
            self.remove_from_cart(sku, win)
            
    def remove_from_cart(self, sku, win):
        """Xóa sản phẩm khỏi giỏ hàng, cập nhật Treeview và tổng tiền."""
        if sku in self.cart_items:
            product_name = self.cart_items[sku]["name"]
            del self.cart_items[sku]
            self.update_cart_badge()
            self.show_toast(f"Đã xóa '{product_name}' khỏi giỏ hàng.")

            # Cập nhật Treeview và Tổng tiền
            total = self.populate_cart_tree(self.cart_tree)
            try:
                formatted_total = format_currency(total)
            except NameError:
                formatted_total = f"{total:,}"
                
            self.total_label.config(text=f"Tổng cộng: {formatted_total} VNĐ")

            # Nếu giỏ hàng trống, đóng cửa sổ
            if not self.cart_items:
                win.destroy()
                self.show_toast("Giỏ hàng trống.")
                
            self.load_products_list() # Tải lại sản phẩm để cập nhật tồn kho (nếu có)


    def process_checkout(self, win, total):
        win.destroy()
        if not self.is_logged_in:
            messagebox.showerror("Lỗi", "Bạn phải đăng nhập để thanh toán.")
            # Loại bỏ self.show_login_dialog() theo yêu cầu người dùng
            return
            
        user_id = self.current_user['id']
        
        # Chuẩn bị danh sách items cho CSDL (bỏ "stock")
        items_to_checkout = [{k: v for k, v in item.items() if k != 'stock'} 
                             for item in self.cart_items.values()]
                             
        try:
            # SỬ DỤNG MOCK FUNCTION NẾU KHÔNG CÓ DB
            success, result = createOrder(user_id, items_to_checkout) 
        except NameError:
            success, result = True, "MOCK-12345" # Giả lập thành công
            print("Warning: Using Mock createOrder function.")
        
        if success:
            try:
                formatted_total = format_currency(total)
            except NameError:
                formatted_total = f"{total:,}"
            # Hiển thị toast thay vì messagebox
            toast_msg = f"Thanh toán thành công!\nTổng: {formatted_total} VNĐ"
            self.show_toast(toast_msg)
            # Reset giỏ hàng và cập nhật giao diện
            self.cart_items.clear()
            self.update_cart_badge()
            self.load_products_list()  # Tải lại sản phẩm để cập nhật tồn kho
        else:
            messagebox.showerror("Lỗi", f"Thanh toán thất bại: {result}")

    # ------------------ FOOTER ------------------
    def create_footer(self):
        footer = tk.Frame(self, bg="#FFF0E6", height=60)
        footer.pack(fill="x", side="bottom")
        tk.Label(
            footer,
            text="🍷 RubyOak — Hương vị rượu vang hảo hạng từ thiên nhiên.\nTrải nghiệm đẳng cấp trong từng giọt rượu.",
            bg="#FFF0E6", fg="#5C2E0C", font=("Times New Roman", 11, "italic")
        ).pack(pady=10)

    # ------------------ XỬ LÝ TÀI KHOẢN & ĐĂNG NHẬP ------------------
    def show_login_dialog(self):
        """Chuyển đến trang Đăng nhập hoặc Đăng xuất."""
        if self.current_user:
            self.logout()
            return
        # Giả định controller có phương thức show_frame
        try:
            self.controller.show_frame("LoginPage")
        except AttributeError:
            messagebox.showinfo("Thông báo", "Chức năng đăng nhập/đăng xuất chưa được liên kết.")

    def show_user_info_dialog(self):
        """Hiển thị thông tin người dùng hiện tại (khi click vào nhãn username)."""
        if not self.current_user:
            self.show_error_toast("Bạn chưa đăng nhập.")
            return

        win = tk.Toplevel(self)
        win.title("Thông tin tài khoản")
        win.geometry("300x150")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="👤 THÔNG TIN TÀI KHOẢN", font=("Times New Roman", 14, "bold"), fg="#8B0000").pack(pady=10)
        tk.Label(win, text=f"Tên đăng nhập: {self.current_user.get('username', 'N/A')}", font=("Times New Roman", 12)).pack(anchor='w', padx=20)
        tk.Label(win, text=f"ID người dùng: {self.current_user.get('id', 'N/A')}", font=("Times New Roman", 12)).pack(anchor='w', padx=20)
        tk.Label(win, text=f"Vai trò: {self.current_user.get('role', 'N/A')}", font=("Times New Roman", 12)).pack(anchor='w', padx=20)

    def logout(self):
        """Xóa user, reset giỏ hàng, và cập nhật giao diện."""
        self.current_user = None
        self.user_label.config(text="Chưa đăng nhập", fg="#FFCDD2", cursor="") 
        self.login_button.config(text="Đăng nhập")
        self.cart_items = {}
        self.update_cart_badge()
        self.show_toast("Đã đăng xuất thành công.")
    
    def update_user_status(self, user_id, username, role):
        """Cập nhật trạng thái user sau khi đăng nhập."""
        self.current_user = {'id': user_id, 'username': username, 'role': role}

        self.user_label.config(text=f"Xin chào: {username}", fg="white", cursor="hand2")
        self.login_button.config(text="Đăng xuất")
        
        # Phân quyền & Điều hướng
        if role == 'Admin':
            # Giả định controller có phương thức show_frame
            try:
                self.controller.show_frame("AdminPage")
            except AttributeError:
                print("Lỗi: Không tìm thấy AdminPage.")
            
    # ------------------ XỬ LÝ DỮ LIỆU & VIEW ------------------
    def on_show(self):
        """Phương thức được Controller gọi khi Frame này được hiển thị (tkraise)."""
        self.load_products_list()

    def _on_canvas_mousewheel(self, event):
        """
        Xử lý cuộn chuột trên Canvas. 
        Chỉ cho phép cuộn khi nội dung vượt quá chiều cao Canvas.
        """
        # Cần update_idletasks để bbox() trả về kích thước mới nhất của self.grid_frame
        self.canvas.update_idletasks()
        
        # 1. Lấy kích thước nội dung (self.grid_frame)
        bbox = self.canvas.bbox("all")
        # Nếu chưa có nội dung, mặc định là 0
        content_height = bbox[3] if bbox else 0 
        
        # 2. Lấy chiều cao của Canvas (vùng nhìn thấy)
        canvas_height = self.canvas.winfo_height()
        if content_height > canvas_height:
            if event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            return "break"
        else:
            return "break"
        
    def _update_scroll_region(self, event=None):
        """Tính toán scrollregion và điều chỉnh scrollbar."""
        self.canvas.update_idletasks()
        scroll_bbox = self.canvas.bbox("all")
        
        # 1. Đặt scrollregion mặc định theo nội dung
        self.canvas.config(scrollregion=scroll_bbox)
        
        # 2. Điều chỉnh trạng thái của Scrollbar
        if scroll_bbox and scroll_bbox[3] <= self.canvas.winfo_height():
            # Nếu nội dung nhỏ hơn hoặc bằng Canvas, vô hiệu hóa scrollbar
            self.v_scroll.pack_forget() # Ẩn hẳn scrollbar
        else:
            # Ngược lại, hiển thị scrollbar
            self.v_scroll.pack(side="right", fill="y")
            # Cần đảm bảo canvas và scrollbar được bố trí đúng trong container cha
            # (Giả định bạn đã dùng grid/pack cho self.canvas và self.v_scroll trong create_product_grid)