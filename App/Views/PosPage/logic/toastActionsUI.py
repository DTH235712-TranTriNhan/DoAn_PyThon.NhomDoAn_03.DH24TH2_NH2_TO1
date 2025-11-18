def run_toast_animation_ui(self, message, is_error=False):
    if not getattr(self, "toast_win", None) or not self.toast_win.winfo_exists():
        self.create_toast_manager()

    bg = "#F44336" if is_error else "#4CAF50"
    self.toast_label.config(text=message, bg=bg)

    try:
        root = self.winfo_toplevel()
        root.update_idletasks()
        rx = root.winfo_rootx()
        ry = root.winfo_rooty()
        rwidth = root.winfo_width()

        self.toast_win.update_idletasks()
        tw = self.toast_win.winfo_reqwidth()
        th = self.toast_win.winfo_reqheight()

        x = rx + max(10, (rwidth - tw) // 2)
        y = ry + 10
        self.toast_win.geometry(f"{tw}x{th}+{x}+{y}")
    except Exception:
        self.toast_win.geometry("+200+50")

    try:
        self.toast_win.deiconify()
        self.toast_win.lift()
    except Exception:
        pass

    if self.toast_id:
        try:
            self.after_cancel(self.toast_id)
        except Exception:
            pass
        self.toast_id = None

    self.toast_id = self.after(2500, self._clear_current_toast)
    self.current_toast = message


def show_error_toast_ui(self, message):
    if getattr(self, "current_toast", None) == message and getattr(self, "toast_win", None) and self.toast_win.winfo_ismapped():
        if self.toast_id:
            try:
                self.after_cancel(self.toast_id)
            except Exception:
                pass
        self.toast_id = self.after(2500, self._clear_current_toast)
        return

    self._clear_current_toast()
    run_toast_animation_ui(self, message, is_error=True)


def show_toast_ui(self, message):
    if getattr(self, "current_toast", None) == message and getattr(self, "toast_win", None) and self.toast_win.winfo_ismapped():
        if self.toast_id:
            try:
                self.after_cancel(self.toast_id)
            except Exception:
                pass
        self.toast_id = self.after(2500, self._clear_current_toast)
        return

    self._clear_current_toast()
    run_toast_animation_ui(self, message, is_error=False)


def update_cart_badge_ui(self):
    total_qty = sum(item["quantity"] for item in self.cart_items.values())
    self.cart_btn.config(text=f"🛒 Giỏ hàng ({total_qty})")
