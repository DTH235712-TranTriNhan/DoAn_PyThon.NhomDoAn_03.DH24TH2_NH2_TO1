import tkinter as tk
from tkinter import messagebox
from Database.dbProducts import (
    addProduct, updateProduct, discontinueProduct,
    searchProducts, removeProductPermanently, resumeProduct,
    getAllProductsForAdmin
)


class ProductActionsMixin:

    def clear_entries(self):
        for key in self.entries:
            self.entries[key].delete(0, tk.END)

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = getAllProductsForAdmin()

        for product in products:
            self.tree.insert('', tk.END, values=(
                product['SKU'],
                product['name'],
                product['category'],
                product['price'],
                product['stock'],
                product['imagePath'],
                product['description'],
                product['status_text']
            ), tags=(product['status_text'].replace(" ", ""),))

        self.clear_entries()

    def select_item(self, event):
        self.clear_entries()
        selected_item = self.tree.focus()

        if not selected_item:
            return

        keys = ["sku", "name", "category", "price", "stock", "imagePath", "description"]

        values = self.tree.item(selected_item, 'values')
        for key, val in zip(keys, values[:7]):
            if key == "category":
                self.entries[key].set(val)
            else:
                self.entries[key].insert(0, val)

        if hasattr(self, "load_image_preview"):
            self.load_image_preview(values[5])

    def get_input_data(self):
        data = {k: self.entries[k].get().strip() for k in self.entries}

        if not data['sku'] or not data['name']:
            messagebox.showerror("Lỗi Dữ liệu", "Mã sản phẩm và Tên sản phẩm không được để trống.")
            return None

        try:
            data['price'] = float(data['price'].replace('.', '').replace(',', ''))
            data['stock'] = int(data['stock'])
            data['imagePath'] = data['imagePath'] or None
            data['description'] = data['description'] or None
            return data
        except:
            messagebox.showerror("Lỗi Dữ liệu", "Giá và tồn kho phải là số hợp lệ.")
            return None

    def search_product_action(self):
        keyword = self.search_entry.get().strip()

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not keyword:
            messagebox.showwarning("Tìm kiếm", "Không có từ khóa. Đang tải lại toàn bộ.")
            self.load_products()
            return

        results = searchProducts(keyword)

        if results:
            for product in results:
                self.tree.insert('', tk.END, values=product)
        else:
            messagebox.showinfo("Kết quả", f"Không tìm thấy '{keyword}'.")

    def add_product_action(self):
        data = self.get_input_data()
        if not data:
            return

        success, msg = addProduct(
            data['sku'], data['name'], data['category'],
            data['price'], data['stock'], data['imagePath'], data['description']
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            self.load_products()
            self.clear_entries()
        else:
            messagebox.showerror("Lỗi", msg)

    def update_product_action(self):
        data = self.get_input_data()
        if not data:
            return

        success, msg = updateProduct(
            data['sku'], data['name'], data['category'],
            data['price'], data['stock'],
            data['imagePath'], data['description']
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            self.load_products()
            self.clear_entries()
        else:
            messagebox.showerror("Lỗi", msg)

    def remove_product_action(self):
        sku = self.entries["sku"].get().strip()

        if not sku:
            messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm để xóa.")
            return

        if messagebox.askyesno("Xác nhận", f"Xóa vĩnh viễn sản phẩm {sku}?"):
            success, msg = removeProductPermanently(sku)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_products()
                self.clear_entries()
            else:
                messagebox.showerror("Lỗi", msg)

    def resume_product_action(self):
        sku = self.entries["sku"].get().strip()
        if not sku:
            messagebox.showerror("Lỗi", "Chọn sản phẩm.")
            return

        if messagebox.askyesno("Xác nhận", f"Kinh doanh lại sản phẩm {sku}?"):
            success, msg = resumeProduct(sku)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_products()
                self.clear_entries()
            else:
                messagebox.showerror("Lỗi", msg)

    def discontinue_product_action(self):
        sku = self.entries["sku"].get().strip()
        if not sku:
            messagebox.showerror("Lỗi", "Chọn sản phẩm.")
            return

        if messagebox.askyesno("Xác nhận", f"Ngừng kinh doanh sản phẩm {sku}?"):
            success, msg = discontinueProduct(sku)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_products()
                self.clear_entries()
            else:
                messagebox.showerror("Lỗi", msg)

    def refresh_page(self):
        try:
            self.clear_entries()
            self.load_products()
            self.load_orders_admin()
        except Exception as e:
            print("Refresh error:", e)
