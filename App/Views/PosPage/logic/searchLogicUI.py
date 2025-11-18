from Database.dbProducts import searchProductsForPOS


def load_more_products_ui(self):
    self.display_index += 6
    self.show_next_products()


def perform_search_ui(self, event=None):
    keyword = self.search_entry.get().strip()
    if not keyword:
        self.show_error_toast("Vui lòng nhập tên hoặc SKU để tìm.")
        return

    self._set_active_category_button(None)

    try:
        self.products = searchProductsForPOS(keyword) or []
    except Exception:
        self.products = []

    self._display_product_list()


def bind_children_mousewheel_ui(self, widget):
    widget.bind("<MouseWheel>", self._on_canvas_mousewheel)
    widget.bind("<Button-4>", self._on_canvas_mousewheel)
    widget.bind("<Button-5>", self._on_canvas_mousewheel)

    for child in widget.winfo_children():
        bind_children_mousewheel_ui(self, child)
