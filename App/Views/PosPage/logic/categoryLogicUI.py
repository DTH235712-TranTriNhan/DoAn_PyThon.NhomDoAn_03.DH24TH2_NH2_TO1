from tkinter import messagebox
from Database.dbProducts import getProductsByCategoryForPOS

def load_products_by_category_ui(self, category_name):
    """Tải và hiển thị sản phẩm theo danh mục."""
    try:
        if hasattr(self, 'search_entry'):
            try:
                self.search_entry.delete(0, 'end')
            except Exception:
                pass

        try:
            self.products = getProductsByCategoryForPOS(category_name) or []
        except Exception as e:
            # if DB function not available, fallback to mock
            print("Warning: getProductsByCategoryForPOS error:", e)
            self.products = []
    except Exception as e:
        messagebox.showerror("Lỗi Tải Sản Phẩm", f"Không thể tải sản phẩm cho danh mục '{category_name}': {e}")
        self.products = []

    self._display_product_list()


def set_active_category_button_ui(self, active_button=None):
    """Đặt/reset màu cho các nút danh mục, highlight nút đang active."""
    if active_button:
        self.active_category_button = active_button

    ACTIVE_BG = "#A52A2A"
    ACTIVE_FG = "white"
    NORMAL_BG = "#FFF0E6"
    NORMAL_FG = "black"

    for button in getattr(self, 'category_buttons', []):
        try:
            button.config(bg=NORMAL_BG, fg=NORMAL_FG)
        except Exception:
            pass

    if hasattr(self, 'active_category_button') and self.active_category_button in getattr(self, 'category_buttons', []):
        try:
            self.active_category_button.config(bg=ACTIVE_BG, fg=ACTIVE_FG)
        except Exception:
            pass
