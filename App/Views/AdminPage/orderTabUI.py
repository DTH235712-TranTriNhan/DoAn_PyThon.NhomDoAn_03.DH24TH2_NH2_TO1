import tkinter as tk
from tkinter import ttk

class OrderTabUI:
    def build_order_tab(self, parent):
        """Tạo giao diện Tab Quản lý đơn hàng."""

        order_frame = tk.LabelFrame(
            parent, text="Danh sách đơn hàng",
            padx=10, pady=10,
            bg="#FFF8F0", fg="#5C2E0C",
            font=("Times New Roman", 12, "bold"),
            relief="solid", bd=1
        )
        order_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = (
            "Mã ĐH", "Người mua", "Tên đăng nhập", "Ngày đặt",
            "Sản phẩm", "Số lượng", "Đơn giá", "Tổng tiền", "Trạng thái"
        )

        self.order_tree = ttk.Treeview(
            order_frame, columns=columns, show="headings",
            style="Admin.Treeview"
        )

        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=110, anchor=tk.CENTER)

        self.order_tree.column("Người mua", anchor='w')
        self.order_tree.column("Sản phẩm", anchor='w')
        self.order_tree.column("Đơn giá", anchor='e')
        self.order_tree.column("Tổng tiền", anchor='e')

        # Scrollbar
        scroll_y = ttk.Scrollbar(order_frame, orient="vertical", command=self.order_tree.yview)
        scroll_x = ttk.Scrollbar(order_frame, orient="horizontal", command=self.order_tree.xview)

        self.order_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        self.order_tree.pack(fill='both', expand=True)
        scroll_x.pack(side="bottom", fill="x")

        # Nút tải lại
        tk.Button(
            order_frame, text="Tải lại danh sách",
            command=self.load_orders_admin,
            bg="#A52A2A", fg="white",
            font=("Times New Roman", 12, "bold"),
            relief="flat"
        ).pack(pady=10)

        # Double click để xem chi tiết
        self.order_tree.bind("<Double-1>", self.show_order_details)
