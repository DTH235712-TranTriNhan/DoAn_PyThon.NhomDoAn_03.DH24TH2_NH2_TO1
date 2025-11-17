import tkinter as tk
from App.Views.PosPage.posPage import POSPage

class PosTabUI:
    def build_pos_tab(self, parent, controller):
        """Tạo giao diện Tab xem sản phẩm POS."""
        self.pos_view = POSPage(parent=parent, controller=controller)
        self.pos_view.pack(fill="both", expand=True)
