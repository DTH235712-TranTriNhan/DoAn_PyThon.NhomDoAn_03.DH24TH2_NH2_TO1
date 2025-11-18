def display_product_list_ui(self):
    """
    (Hàm trợ giúp) Xóa grid cũ và hiển thị danh sách self.products hiện tại.
    Hàm này được gọi bởi load_products_list, perform_search, và load_products_by_category.
    """
    self.display_index = 0

    # Xóa tất cả các card cũ
    try:
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
    except Exception:
        pass

    # Ẩn nút "Xem thêm"
    try:
        self.more_btn.pack_forget()
    except Exception:
        pass

    # Hiển thị sản phẩm (hàm show_next_products sẽ xử lý khi danh sách rỗng)
    self.show_next_products()

    # Đặt lại vị trí Scrollbar về đầu
    try:
        if hasattr(self, 'canvas'):
            self.canvas.yview_moveto(0)
    except Exception:
        pass
