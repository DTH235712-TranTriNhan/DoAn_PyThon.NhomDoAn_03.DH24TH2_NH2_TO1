def add_to_cart_ui(self, product):
    """Thêm sản phẩm vào giỏ hàng (giữ nguyên logic gốc)."""

    if not self.is_logged_in:
        self.show_error_toast("Bạn cần đăng nhập để thêm sản phẩm vào giỏ.")
        return

    sku = product.get("sku")
    name = product.get("name")
    price = float(product.get("price", 0))
    stock = product.get("stock", 0)

    if stock <= 0:
        self.show_error_toast(f"Sản phẩm '{name}' đã hết hàng.")
        return

    current_qty = self.cart_items[sku]["quantity"] if sku in self.cart_items else 0
    if current_qty + 1 > stock:
        self.show_error_toast(f"Không thể thêm. Tồn kho chỉ còn {stock} sản phẩm.")
        return

    if sku in self.cart_items:
        self.cart_items[sku]["quantity"] += 1
    else:
        self.cart_items[sku] = {
            "sku": sku,
            "name": name,
            "quantity": 1,
            "unitPrice": price,
            "stock": stock
        }

    self.update_cart_badge()
    self.show_toast(f"Đã thêm '{name}' vào giỏ hàng")
