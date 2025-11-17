import tkinter as tk
import tkinter.ttk as ttk


class ProductTabUI:

    def build_product_tab(self, product_tab):
        """Tạo giao diện tab Quản Lý Sản Phẩm."""

        # --- HEADER ---
        header_frame = tk.Frame(product_tab, bg="#FFF8F0")
        header_frame.pack(fill='x', pady=10)

        tk.Label(
            header_frame, text="🍇 QUẢN LÝ SẢN PHẨM",
            font=("Times New Roman", 20, "bold"),
            fg="#8B0000", bg="#FFF8F0"
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            header_frame, text="Đăng xuất",
            bg="#E53935", fg="white",
            font=("Times New Roman", 12, "bold"),
            relief="flat",
            command=lambda: self.controller.show_frame("LoginPage")
        ).pack(side=tk.RIGHT, padx=10, pady=5)

        # --- FORM INPUT ---
        input_frame = tk.LabelFrame(
            product_tab, text="Thông tin Sản phẩm",
            padx=10, pady=10, bg="#FFF8F0", fg="#5C2E0C",
            font=("Times New Roman", 12, "bold"),
            relief="solid", bd=1
        )
        input_frame.pack(fill="x", padx=10)

        labels = ["Mã Sản Phẩm ", "Tên Sản Phẩm", "Danh mục", "Giá", "Tồn kho", "Đường dẫn Ảnh", "Mô tả"]
        keys = ["sku", "name", "category", "price", "stock", "imagePath", "description"]

        base_fields = ["sku", "name", "category", "price", "stock"]

        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)

        for i, key in enumerate(base_fields):
            label = labels[keys.index(key)]
            r = i // 3
            c = (i % 3) * 2

            tk.Label(
                input_frame, text=label + ":", anchor="w",
                bg="#FFF8F0", fg="#5C2E0C",
                font=("Times New Roman", 11)
            ).grid(row=r, column=c, padx=5, pady=5, sticky="w")

            if key == "category":
                entry = ttk.Combobox(
                    input_frame, width=20,
                    values=self.categories,
                    font=("Times New Roman", 11)
                )
                entry.set(self.categories[0])
            else:
                entry = tk.Entry(
                    input_frame, width=20,
                    font=("Times New Roman", 11),
                    relief="solid", bd=1
                )

            entry.grid(row=r, column=c+1, padx=5, pady=5, sticky="ew")
            self.entries[key] = entry

        # Image Path
        tk.Label(
            input_frame, text="Đường dẫn Ảnh:",
            bg="#FFF8F0", fg="#5C2E0C",
            font=("Times New Roman", 11)
        ).grid(row=2, column=0, padx=5, pady=5, sticky="w")

        entry = tk.Entry(input_frame, width=60,
                         font=("Times New Roman", 11),
                         relief="solid", bd=1)
        entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.entries["imagePath"] = entry

        tk.Button(
            input_frame, text="Chọn ảnh...",
            command=self.browseImage, width=10,
            bg="#A52A2A", fg="white",
            font=("Times New Roman", 10, "bold"),
            relief="flat"
        ).grid(row=2, column=4, padx=5, pady=5, sticky='w')

        # Image Preview
        self.image_preview_label = tk.Label(
            input_frame, text="Ảnh Xem trước",
            relief="solid", bg="#FFF0E6", bd=1
        )
        self.image_preview_label.grid(row=2, column=5, rowspan=2,
                                      padx=10, pady=5)
        self.load_image_preview("")

        # Description
        tk.Label(
            input_frame, text="Mô tả:",
            bg="#FFF8F0", fg="#5C2E0C",
            font=("Times New Roman", 11)
        ).grid(row=3, column=0, padx=5, pady=5, sticky="w")

        entry = tk.Entry(input_frame, width=80,
                         font=("Times New Roman", 11),
                         relief="solid", bd=1)
        entry.grid(row=3, column=1, columnspan=4,
                   padx=5, pady=5, sticky="ew")
        self.entries["description"] = entry

        # Buttons
        button_frame = tk.Frame(input_frame, bg="#FFF8F0")
        button_frame.grid(row=4, column=0, columnspan=5, pady=10)

        btn = ("Times New Roman", 12, "bold")

        tk.Button(button_frame, text="Thêm", bg="#A52A2A",
                  fg="white", font=btn, relief="flat",
                  width=10, command=self.add_product_action
                  ).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Sửa", bg="#A52A2A",
                  fg="white", font=btn, width=10,
                  relief="flat", command=self.update_product_action
                  ).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Ngừng Kinh Doanh",
                  bg="#f0ad4e", fg="white", width=15,
                  font=btn, relief="flat",
                  command=self.discontinue_product_action
                  ).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Kinh doanh lại",
                  bg="#4CAF50", fg="white", width=15,
                  font=btn, relief="flat",
                  command=self.resume_product_action
                  ).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Xóa vĩnh viễn",
                  bg="#E53935", fg="white", width=15,
                  font=btn, relief="flat",
                  command=self.remove_product_action
                  ).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Làm mới",
                  font=btn, width=10, relief="flat",
                  command=self.load_products
                  ).pack(side=tk.LEFT, padx=10)

        # Search Bar
        search_frame = tk.Frame(product_tab, padx=10,
                                pady=5, bg="#FFF8F0")
        search_frame.pack(fill="x")

        tk.Label(
            search_frame, text="Tìm kiếm:",
            width=10, anchor="w",
            bg="#FFF8F0", fg="#5C2E0C",
            font=("Times New Roman", 11)
        ).pack(side=tk.LEFT)

        self.search_entry = tk.Entry(
            search_frame, font=("Times New Roman", 11),
            relief="solid", bd=1
        )
        self.search_entry.pack(side=tk.LEFT, fill="x",
                               expand=True, padx=5)

        tk.Button(
            search_frame, text="Tìm kiếm",
            command=self.search_product_action, width=10,
            bg="#8B0000", fg="white",
            font=("Times New Roman", 11, "bold"),
            relief="flat"
        ).pack(side=tk.LEFT)

        # TreeView
        columns = (
            "Mã Sản Phẩm", "Tên Sản Phẩm", "Danh mục", "Giá",
            "Tồn kho", "Đường dẫn Ảnh", "Mô tả", "Trạng thái"
        )

        self.tree = ttk.Treeview(
            product_tab, columns=columns,
            show="headings", style="Admin.Treeview"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.column("Tên Sản Phẩm", width=150, anchor='w')
        self.tree.column("Mô tả", width=150, anchor='w')

        scroll_y = ttk.Scrollbar(
            product_tab, orient="vertical",
            command=self.tree.yview
        )
        scroll_x = ttk.Scrollbar(
            product_tab, orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10)
        scroll_x.pack(side="bottom", fill="x", padx=10, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)
