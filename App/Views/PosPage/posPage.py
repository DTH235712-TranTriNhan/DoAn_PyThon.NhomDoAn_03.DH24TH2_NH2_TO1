import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

from App.Views.ProductCard.ProductCard import ProductCard
from Database.dbOrders import createOrder, format_currency
from Database.dbProducts import (
    getProductsForPOS, searchProductsForPOS,
    getAllCategories, getProductsByCategoryForPOS
)

# Import UI đã tách
from App.Views.PosPage.views.headerUI import create_header_ui
from App.Views.PosPage.views.searchBarUI import create_search_bar_ui
from App.Views.PosPage.views.toastUI import create_toast_manager_ui
from App.Views.PosPage.products.productGridUI import (
    create_product_grid_ui,
    on_canvas_resize_ui,
    load_products_list_ui,
    show_next_products_ui
)
from App.Views.PosPage.logic.searchLogicUI import load_more_products_ui, perform_search_ui, bind_children_mousewheel_ui
from App.Views.PosPage.products.productDetailUI import open_product_detail_ui
from App.Views.PosPage.cart.buyCartManagerUI import add_to_cart_from_detail_ui, process_buy_now_ui, clear_current_toast_ui

from App.Views.PosPage.cart.addToCartUI import add_to_cart_ui
from App.Views.PosPage.logic.toastActionsUI import (
    run_toast_animation_ui, show_error_toast_ui,
    show_toast_ui, update_cart_badge_ui
)
from App.Views.PosPage.cart.cartUI import (
    show_cart_window_ui, populate_cart_tree_ui,
    handle_cart_click_ui, remove_from_cart_ui,
    process_checkout_ui
)

from App.Views.PosPage.views.footerUI import create_footer_ui
from App.Views.PosPage.logic.accountUI import (
    show_login_dialog_ui, show_user_info_dialog_ui,
    logout_ui, update_user_status_ui
)
from App.Views.PosPage.views.sidebarUI import create_category_sidebar_ui
from App.Views.PosPage.logic.categoryLogicUI import (
    load_products_by_category_ui, set_active_category_button_ui
)
from App.Views.PosPage.products.productDisplayUI import display_product_list_ui
from App.Views.PosPage.views.scrollRegionUI import update_scroll_region_ui
from .utils.mouseWheelUI import on_canvas_mousewheel_ui
from .products.productImageUI import (
    get_absolute_image_path_ui,
    load_image_for_modal_ui
)


ROOT_DIR = os.getcwd()
BASE_IMAGE_DIR = os.path.normpath(os.path.join(ROOT_DIR, 'App', 'Images'))
MODAL_IMAGE_SIZE = (200, 200)


class POSPage(tk.Frame):
    """Giao diện Điểm Bán Hàng (POS) chính."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFF8F0")
        self.controller = controller

        # BIẾN TRẠNG THÁI
        self.current_user = None
        self.cart_items = {}
        self.products = []
        self.display_index = 0
        self.photo_modal = None
        self.current_toast = None
        self.toast_id = None
        self.category_buttons = []

        # Gọi UI đã tách
        create_header_ui(self)
        create_toast_manager_ui(self)
        create_product_grid_ui(self)

        # Tải sản phẩm ban đầu
        load_products_list_ui(self)

    # ===========================================================
    # PROPERTY
    @property
    def is_logged_in(self):
        return self.current_user and 'id' in self.current_user

    # ===========================================================
    # RÀNG BUỘC HÀM UI

    def on_canvas_resize(self, event): on_canvas_resize_ui(self, event)
    def load_products_list(self): load_products_list_ui(self)
    def show_next_products(self): show_next_products_ui(self)

    def load_more_products(self): load_more_products_ui(self)
    def perform_search(self, event=None): perform_search_ui(self, event)
    def _bind_children_mousewheel(self, widget): bind_children_mousewheel_ui(self, widget)

    def open_product_detail(self, product): open_product_detail_ui(self, product)

    def _add_to_cart_from_detail(self, product, win): add_to_cart_from_detail_ui(self, product, win)
    def process_buy_now(self, product, win): process_buy_now_ui(self, product, win)
    def _clear_current_toast(self): clear_current_toast_ui(self)

    def add_to_cart(self, product): return add_to_cart_ui(self, product)

    def run_toast_animation(self, m, e=False): return run_toast_animation_ui(self, m, e)
    def show_error_toast(self, m): return show_error_toast_ui(self, m)
    def show_toast(self, m): return show_toast_ui(self, m)
    def update_cart_badge(self): return update_cart_badge_ui(self)

    def show_cart_window(self): return show_cart_window_ui(self)
    def populate_cart_tree(self, t): return populate_cart_tree_ui(self, t)
    def handle_cart_click(self, e, t, w): return handle_cart_click_ui(self, e, t, w)
    def remove_from_cart(self, sku, w): return remove_from_cart_ui(self, sku, w)
    def process_checkout(self, win, total): return process_checkout_ui(self, win, total)

    def create_footer(self): return create_footer_ui(self)
    def show_login_dialog(self): return show_login_dialog_ui(self)
    def show_user_info_dialog(self): return show_user_info_dialog_ui(self)
    def logout(self): return logout_ui(self)
    def update_user_status(self, *args): return update_user_status_ui(self, *args)

    def create_category_sidebar(self, parent): return create_category_sidebar_ui(self, parent)
    def load_products_by_category(self, c): return load_products_by_category_ui(self, c)
    def _set_active_category_button(self, b=None): return set_active_category_button_ui(self, b)

    def _display_product_list(self): return display_product_list_ui(self)
    def create_search_bar(self, parent): return create_search_bar_ui(self, parent)
    def _update_scroll_region(self, event=None): return update_scroll_region_ui(self, event)
    def _on_canvas_mousewheel(self, event): return on_canvas_mousewheel_ui(self, event)

    def _get_absolute_image_path(self, product): return get_absolute_image_path_ui(self, product, BASE_IMAGE_DIR)
    def _load_image_for_modal(self, abs_path): return load_image_for_modal_ui(self, abs_path, MODAL_IMAGE_SIZE)

    def on_show_frame(self):
        try:
            self.controller.state("zoomed")
        except:
            pass

        try:
            self.load_products()
            self.load_orders_admin()
        except:
            pass