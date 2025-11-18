# productImageUI.py
import os
from PIL import Image, ImageTk

def get_absolute_image_path_ui(self, product, BASE_IMAGE_DIR):
    image_filename = product.get("imagePath", "") 
    if image_filename:
        base_filename = os.path.basename(image_filename)
        abs_path = os.path.normpath(os.path.join(BASE_IMAGE_DIR, base_filename))
        if os.path.exists(abs_path):
            return abs_path

    abs_default_path = os.path.join(BASE_IMAGE_DIR, "default.jpg")
    if os.path.exists(abs_default_path):
        return abs_default_path
            
    return None


def load_image_for_modal_ui(self, abs_path, MODAL_IMAGE_SIZE):
    if abs_path is None:
        return None
    try:
        img = Image.open(abs_path)
        img.thumbnail(MODAL_IMAGE_SIZE)
        self.photo_modal = ImageTk.PhotoImage(img)
        return self.photo_modal
    except Exception as e:
        print(f"LỖI LOAD ẢNH cho modal: {e}")
        return None
