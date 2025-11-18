import tkinter as tk
import tkinter.ttk as ttk

# ---- Import các module đã tách ----
from .productActions import ProductActionsMixin
from .orderActions import OrderActionsMixin
from .imageUtils import ImageUtilsMixin
from .orderTabUI import OrderTabUI
from .productTabUI import ProductTabUI
from .posTabUI import PosTabUI

from App.Views.PosPage.views.sidebarUI import refresh_category_sidebar_ui

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
        self.categories = ["Rượu Whisky", "Rượu Brandy",
                            "Rượu Vodka", "Rượu Gin", "Rượu Rum", "Rượu Tequila",
                            "Rượu Vang", "Rượu Mùi",  "Khác"]

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

        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        return notebook
    
    # ----------------------------------------------------------------------
    # HÀM XỬ LÝ SỰ KIỆN CHUYỂN TAB
    # ----------------------------------------------------------------------
    def on_tab_changed(self, event):
        notebook = event.widget
        # Lấy index tab hiện tại (0: Product, 1: Order, 2: POS)
        current_tab_index = notebook.index("current")

        # Nếu là Tab số 2 (Tab POS)
        if current_tab_index == 2:
            # Kiểm tra xem self.pos_view đã được tạo chưa (tên biến trong PosTabUI)
            if hasattr(self, 'pos_view'):
                try:
                    # 1. Tải lại danh sách sản phẩm
                    self.pos_view.load_products_list()
                    
                    # 2. Tải lại sidebar danh mục
                    refresh_category_sidebar_ui(self.pos_view)
                    
                except Exception as e:
                    print(f"Lỗi làm mới POS trong Admin: {e}")
    # ----------------------------------------------------------------------
    # Khi trang được hiển thị
    # ----------------------------------------------------------------------
    def on_show_frame(self):
        try:
            self.controller.state("zoomed")
        except:
            pass

        # Tải lại dữ liệu khi hiển thị trang Admin
        try:
            self.load_products()      # Refresh bảng Admin
            self.load_orders_admin()  # Refresh đơn hàng Admin
        except:
            pass
