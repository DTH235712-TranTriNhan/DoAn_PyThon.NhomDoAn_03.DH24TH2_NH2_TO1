import tkinter as tk

def create_toast_manager_ui(self):
    if getattr(self, "toast_win", None) and self.toast_win.winfo_exists():
        return

    self.toast_win = tk.Toplevel(self)
    self.toast_win.overrideredirect(True)
    self.toast_win.attributes("-topmost", True)

    try:
        self.toast_win.attributes("-transparentcolor", "pink")
    except Exception:
        pass

    self.toast_label = tk.Label(
        self.toast_win,
        text="",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=12, pady=6,
        bd=0, relief="flat",
        wraplength=400, justify="center"
    )
    self.toast_label.pack()

    self.toast_win.withdraw()
    self.current_toast = None
    self.toast_id = None
