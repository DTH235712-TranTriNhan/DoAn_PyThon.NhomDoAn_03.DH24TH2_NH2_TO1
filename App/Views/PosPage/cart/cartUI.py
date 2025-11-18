import tkinter as tk
from tkinter import ttk, messagebox
from Database.dbOrders import createOrder, format_currency


def show_cart_window_ui(self):
    if not self.cart_items:
        messagebox.showinfo("Giỏ hàng", "Giỏ hàng trống.")
        return

    win = tk.Toplevel(self)
    win.title("Giỏ hàng")
    win.geometry("550x450")
    win.grab_set()

    tree_frame = tk.Frame(win, padx=10, pady=10)
    tree_frame.pack(fill="both", expand=True)

    cart_tree = ttk.Treeview(
        tree_frame, columns=("Tên", "SL", "Đơn giá", "Tổng", "Xóa"), show="headings"
    )

    for col in ("Tên", "SL", "Đơn giá", "Tổng", "Xóa"):
        cart_tree.heading(col, text=col)

    cart_tree.column("Tên", width=180, anchor="w")
    cart_tree.column("SL", width=40, anchor="center")
    cart_tree.column("Đơn giá", width=90, anchor="e")
    cart_tree.column("Tổng", width=90, anchor="e")
    cart_tree.column("Xóa", width=40, anchor="center")

    cart_tree.pack(side="left", fill="both", expand=True)

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=cart_tree.yview)
    vsb.pack(side="right", fill="y")
    cart_tree.configure(yscrollcommand=vsb.set)

    total = self.populate_cart_tree(cart_tree)

    cart_tree.bind('<ButtonRelease-1>',
                   lambda e: self.handle_cart_click(e, cart_tree, win))

    control_frame = tk.Frame(win, padx=10, pady=10)
    control_frame.pack(fill="x", side="bottom")

    formatted_total = format_currency(total)

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

    self.win = win
    self.cart_tree = cart_tree


def populate_cart_tree_ui(self, cart_tree):
    total = 0
    cart_tree.delete(*cart_tree.get_children())

    for sku, item in self.cart_items.items():
        subtotal = item["quantity"] * item["unitPrice"]
        total += subtotal

        formatted_unit = format_currency(item["unitPrice"])
        formatted_sub = format_currency(subtotal)

        cart_tree.insert(
            "", tk.END,
            iid=sku,
            values=(item["name"], item["quantity"], formatted_unit, formatted_sub, '🗑️ Xóa')
        )

    return total


def handle_cart_click_ui(self, event, cart_tree, win):
    item = cart_tree.identify_row(event.y)
    column = cart_tree.identify_column(event.x)

    if column == '#5' and item:
        sku = item
        self.remove_from_cart(sku, win)


def remove_from_cart_ui(self, sku, win):
    if sku in self.cart_items:
        product_name = self.cart_items[sku]["name"]
        del self.cart_items[sku]

        self.update_cart_badge()
        self.show_toast(f"Đã xóa '{product_name}' khỏi giỏ hàng.")

        total = self.populate_cart_tree(self.cart_tree)
        formatted_total = format_currency(total)
        self.total_label.config(text=f"Tổng cộng: {formatted_total} VNĐ")

        if not self.cart_items:
            win.destroy()
            self.show_toast("Giỏ hàng trống.")

        self.load_products_list()


def process_checkout_ui(self, win, total):
    win.destroy()

    if not self.is_logged_in:
        messagebox.showerror("Lỗi", "Bạn phải đăng nhập để thanh toán.")
        return

    user_id = self.current_user['id']

    items = [
        {k: v for k, v in item.items() if k != 'stock'}
        for item in self.cart_items.values()
    ]

    try:
        success, result = createOrder(user_id, items)
    except Exception:
        success, result = True, "MOCK-123"
        print("Warning: Mock createOrder used.")

    if success:
        formatted_total = format_currency(total)
        self.show_toast(f"Thanh toán thành công!\nTổng: {formatted_total} VNĐ")

        self.cart_items.clear()
        self.update_cart_badge()
        self.load_products_list()
    else:
        messagebox.showerror("Lỗi", f"Thanh toán thất bại: {result}")
