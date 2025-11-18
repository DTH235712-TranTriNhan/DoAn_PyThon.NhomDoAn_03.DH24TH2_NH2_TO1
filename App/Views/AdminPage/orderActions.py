import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from Database.dbOrders import getOrderDetails, getAllOrders, getAllOrdersForAdmin


class OrderActionsMixin:

    def load_orders_admin(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        orders = getAllOrdersForAdmin()
        if not orders:
            return

        for order in orders:
            total = order['quantity'] * order['unitPrice']
            self.order_tree.insert('', tk.END, values=(
                order['orderID'],
                order['fullName'],
                order['userName'],
                order['orderDate'],
                order['productName'],
                order['quantity'],
                f"{order['unitPrice']:,}".replace(",", "."),
                f"{total:,}".replace(",", "."),
                order['status']
            ))

    def load_orders(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        orders = getAllOrders()
        for order in orders:
            if isinstance(order['orderDate'], str):
                order_date = order['orderDate']
            else:
                order_date = order['orderDate'].strftime("%d/%m/%Y %H:%M")

            total_amount = f"{order['totalAmount']:,}".replace(",", ".") + " ₫"

            self.order_tree.insert("", "end", values=(
                order['orderID'],
                order_date,
                order['userName'],
                order['fullName'],
                total_amount,
                order['status']
            ))

    def show_order_details(self, event):
        selected = self.order_tree.focus()
        if not selected:
            return

        orderID = self.order_tree.item(selected)["values"][0]
        details = getOrderDetails(orderID)

        if not details:
            messagebox.showinfo("Chi tiết đơn hàng", "Không có sản phẩm trong đơn hàng này.")
            return

        popup = Toplevel(self)
        popup.title(f"Chi tiết đơn hàng #{orderID}")
        popup.geometry("600x300")

        cols = ("SKU", "Tên sản phẩm", "Số lượng", "Đơn giá", "Thành tiền")
        tree = ttk.Treeview(popup, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)

        tree.pack(fill="both", expand=True)

        for item in details:
            unit_price = f"{item['unitPrice']:,}".replace(",", ".") + " ₫"
            total_price = f"{item['totalPrice']:,}".replace(",", ".") + " ₫"
            tree.insert("", "end", values=(
                item["SKU"],
                item["productName"],
                item["quantity"],
                unit_price,
                total_price
            ))
