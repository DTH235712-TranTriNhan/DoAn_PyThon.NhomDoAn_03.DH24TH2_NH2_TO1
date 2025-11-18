# mouseWheelUI.py

def on_canvas_mousewheel_ui(self, event):
    if event.delta:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    else:
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    return "break"
