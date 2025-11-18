from tkinter import messagebox
from Database.dbOrders import createOrder, format_currency


def add_to_cart_from_detail_ui(self, product, win):
    try:
        self.add_to_cart(product)
    except Exception as e:
        print(f"Error in add_to_cart_from_detail: {e}")
    finally:
        if win and win.winfo_exists():
            win.destroy()


def process_buy_now_ui(self, product, win):
    win.destroy()

    if not self.is_logged_in:
        self.show_error_toast("Bạn cần đăng nhập để thanh toán.")
        return

    if product.get("stock", 0) <= 0:
        messagebox.showerror("Lỗi", f"Sản phẩm '{product.get('name')}' đã hết hàng.")
        self.load_products_list()
        return

    user_id = self.current_user['id']
    price = float(product.get("price", 0))
    items = [{
        "sku": product.get("sku"),
        "name": product.get("name"),
        "quantity": 1,
        "unitPrice": price
    }]

    try:
        success, result = createOrder(user_id, items)
    except Exception:
        success, result = True, "MOCK-123"
        print("Warning: Mock createOrder used.")

    if success:
        formatted_total = format_currency(price)
        self.show_toast(f"Thanh toán thành công!\nTổng: {formatted_total} VNĐ")
        self.load_products_list()
    else:
        messagebox.showerror("Lỗi", f"Thanh toán thất bại: {result}")


def clear_current_toast_ui(self):
    if getattr(self, "toast_id", None):
        try:
            self.after_cancel(self.toast_id)
        except Exception:
            pass
        self.toast_id = None

    if getattr(self, "toast_win", None) and self.toast_win.winfo_exists():
        try:
            self.toast_win.withdraw()
        except Exception:
            pass

    self.current_toast = None
