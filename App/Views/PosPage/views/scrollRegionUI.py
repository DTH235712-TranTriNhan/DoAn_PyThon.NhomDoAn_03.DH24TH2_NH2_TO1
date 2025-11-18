def update_scroll_region_ui(self, event=None):
    self.canvas.update_idletasks()  
    bbox = self.canvas.bbox("all")

    if bbox is None:
        self.canvas.config(scrollregion=(0, 0, 0, 0))
        self.v_scroll.pack_forget()
        return

    self.canvas.config(scrollregion=bbox)

    canvas_height = self.canvas.winfo_height()
    content_height = bbox[3]

    SCROLL_THRESHOLD = 1

    if content_height <= canvas_height + SCROLL_THRESHOLD:
        self.v_scroll.pack_forget()
        self.canvas.yview_moveto(0)
    else:
        self.v_scroll.pack(side="right", fill="y")
