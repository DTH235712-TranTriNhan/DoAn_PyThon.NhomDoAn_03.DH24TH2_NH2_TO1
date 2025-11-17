import tkinter as tk
import tkinter.ttk as ttk

# ---- Import các module đã tách ----
from .productActions import ProductActionsMixin
from .orderActions import OrderActionsMixin
from .imageUtils import ImageUtilsMixin
from .orderTabUI import OrderTabUI
from .productTabUI import ProductTabUI
from .posTabUI import PosTabUI


class AdminPage(
    tk.Frame,
    ProductActionsMixin,
    OrderActionsMixin,
    ImageUtilsMixin,
    ProductTabUI,
    OrderTabUI,
    PosTabUI
):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFF8F0")
        self.controller = controller
        self.entries = {}
        self.photo_admin = None
        self.categories = ["Điện tử", "Phụ kiện", "Đồ gia dụng", "Thời trang", "Khác"]

        # Tạo Style chung
        self.setup_styles()

        # Tạo Notebook Tabs
        self.build_tabs()

    # ----------------------------------------------------------------------
    # STYLE GLOBAL
    # ----------------------------------------------------------------------
    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('default')

        # Notebook
        self.style.configure("Admin.TNotebook", background="#FFF8F0")
        self.style.configure(
            "Admin.TNotebook.Tab",
            background="#A52A2A",
            foreground="white",
            font=("Times New Roman", 11, "bold"),
            padding=[10, 5],
            relief="flat"
        )
        self.style.map(
            "Admin.TNotebook.Tab",
            background=[("selected", "#8B0000")],
            foreground=[("selected", "white")]
        )

        # Treeview
        self.style.configure(
            "Admin.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#5C2E0C",
            font=("Times New Roman", 10),
            rowheight=25
        )
        self.style.configure(
            "Admin.Treeview.Heading",
            background="#8B0000",
            foreground="white",
            font=("Times New Roman", 11, "bold"),
            relief="flat"
        )

    # ----------------------------------------------------------------------
    # BUILD ALL TABS
    # ----------------------------------------------------------------------
    def build_tabs(self):
        notebook = ttk.Notebook(self, style="Admin.TNotebook")
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tabs
        product_tab = tk.Frame(notebook, bg="#FFF8F0")
        order_tab = tk.Frame(notebook, bg="#FFF8F0")
        pos_view_tab = tk.Frame(notebook, bg="#FFF8F0")

        notebook.add(product_tab, text="Quản lý sản phẩm")
        notebook.add(order_tab, text="Quản lý đơn hàng")
        notebook.add(pos_view_tab, text="Xem sản phẩm POS")

        # Build UI for each Tab
        self.build_product_tab(product_tab)
        self.build_order_tab(order_tab)
        self.build_pos_tab(pos_view_tab, self.controller)

        return notebook

    # ----------------------------------------------------------------------
    # Khi trang được hiển thị
    # ----------------------------------------------------------------------
    def on_show_frame(self):
        try:
            self.controller.state("zoomed")
        except:
            pass

        # Tải lại dữ liệu khi hiển thị
        try:
            self.load_products()
            self.load_orders_admin()
        except:
            pass
