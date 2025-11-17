import os
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont


class ImageUtilsMixin:

    PREVIEW_MAX_W = 81
    PREVIEW_MAX_H = 144

    def get_target_image_dir(self):
        """Trả về thư mục App/Images."""
        target_dir = os.path.join(os.getcwd(), 'App', 'Images')
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def browseImage(self):
        """Chỉ chọn ảnh bên trong App/Images và lưu path tương đối."""
        start_dir = self.get_target_image_dir()

        filepath_absolute = filedialog.askopenfilename(
            title="Chọn ảnh sản phẩm (Đã có sẵn trong App/Images)",
            initialdir=start_dir,
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*"))
        )

        if filepath_absolute:
            normalized_start = os.path.normpath(start_dir)
            normalized_file = os.path.normpath(filepath_absolute)

            # Chỉ cho phép chọn file trong App/Images
            if not normalized_file.startswith(normalized_start + os.sep):
                messagebox.showwarning("Cảnh báo", "Ảnh phải nằm trong thư mục App/Images.")
                return

            filename = os.path.basename(filepath_absolute)
            relative_path = os.path.join('App', 'Images', filename)

            self.entries['imagePath'].delete(0, 'end')
            self.entries['imagePath'].insert(0, relative_path)
            messagebox.showinfo("Đã chọn", f"Đã chọn ảnh: {relative_path}")

            self.load_image_preview(relative_path)

    def _create_error_canvas(self, message):
        """Tạo một ảnh canvas cố định 81x144 với thông báo lỗi được viết lên đó."""
        FRAME_W = self.PREVIEW_MAX_W
        FRAME_H = self.PREVIEW_MAX_H
        
        # 1. Tạo canvas trắng (kích thước cố định)
        canvas = Image.new('RGB', (FRAME_W, FRAME_H), '#F0F0F0') # Màu xám nhạt làm nền lỗi
        draw = ImageDraw.Draw(canvas)
        
        # 2. Định nghĩa font
        try:
            # Thử dùng font Arial 10pt (thường có sẵn)
            font = ImageFont.truetype("arial.ttf", 10) 
        except IOError:
            # Fallback về Default font
            font = ImageFont.load_default()

        # Chia message để viết lên canvas
        lines = []
        words = message.split(' ')
        current_line = ""
        
        # Logic đơn giản để chia dòng, giới hạn khoảng 10-12 ký tự/dòng
        for word in words:
            if len(current_line + word) < 12: 
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())

        # Tính toán vị trí text để căn giữa
        line_height = 12
        text_height = len(lines) * line_height
        y_text = (FRAME_H - text_height) // 2
        
        # 4. Vẽ từng dòng
        for line in lines:
            try:
                # Dùng textlength nếu có ImageFont
                textwidth = draw.textlength(line, font=font)
            except AttributeError:
                # Fallback cho ImageFont.load_default()
                textwidth = len(line) * 6 

            x_text = (FRAME_W - textwidth) // 2
            
            # Nếu là thông báo lỗi (Lỗi tải ảnh/Không tìm thấy file) dùng màu đỏ, 
            # nếu là placeholder (Ảnh Xem trước) dùng màu đen/xám
            text_color = 'red' if 'Lỗi' in message or 'tìm thấy' in message else '#555555' 
            draw.text((x_text, y_text), line, font=font, fill=text_color)
            y_text += line_height
            
        return ImageTk.PhotoImage(canvas)


    def load_image_preview(self, imagePath):
        """
        Tải và hiển thị ảnh xem trước trong khung cố định (81x144),
        giữ nguyên tỷ lệ khung hình (aspect ratio) bằng cách thêm khoảng trắng (canvas).
        """
        FRAME_W = self.PREVIEW_MAX_W
        FRAME_H = self.PREVIEW_MAX_H

        # LUÔN ĐẶT KÍCH THƯỚC CỐ ĐỊNH TRƯỚC KHI XỬ LÝ (để xóa mọi ảnh/text cũ)
        self.image_preview_label.config(
            image='', 
            text="", # Xóa văn bản cũ
            width=FRAME_W, 
            height=FRAME_H 
        )
        self.photo_admin = None
        
        if not imagePath:
            # SỬA LỖI: Khi không có đường dẫn (initial load/placeholder), tạo placeholder image
            self.photo_admin = self._create_error_canvas("Ảnh Xem trước")
            self.image_preview_label.config(
                image=self.photo_admin, # Luôn hiển thị ảnh
                width=FRAME_W, 
                height=FRAME_H
            )
            return

        absolute_path = os.path.normpath(os.path.join(os.getcwd(), imagePath))

        if not os.path.exists(absolute_path):
            # KHẮC PHỤC LỖI: Dùng canvas lỗi 
            self.photo_admin = self._create_error_canvas("Không tìm thấy file")
            self.image_preview_label.config(
                image=self.photo_admin, # Luôn hiển thị ảnh
                text="", 
                width=FRAME_W, 
                height=FRAME_H
            )
            return

        try:
            img = Image.open(absolute_path)
            
            # --- XỬ LÝ ẢNH (Thu nhỏ và Tạo Canvas) ---
            
            # Thu nhỏ ảnh gốc để giữ tỷ lệ (không méo)
            img.thumbnail((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
            
            img_w, img_h = img.size
            
            # Tạo ảnh nền trắng (canvas) có kích thước cố định
            canvas = Image.new('RGB', (FRAME_W, FRAME_H), 'white') 
            
            # Tính toán vị trí chèn (căn giữa)
            x_offset = (FRAME_W - img_w) // 2
            y_offset = (FRAME_H - img_h) // 2
            
            # Chèn ảnh đã thu nhỏ vào ảnh nền
            canvas.paste(img, (x_offset, y_offset))
            
            # 3. Chuyển đổi và hiển thị ảnh canvas cố định
            self.photo_admin = ImageTk.PhotoImage(canvas)

            self.image_preview_label.config(
                image=self.photo_admin, 
                text="", 
                width=FRAME_W, # Kích thước cố định
                height=FRAME_H # Kích thước cố định
            )
            
        except Exception as e:
            print("Lỗi tải ảnh:", e)
            # KHẮC PHỤC LỖI: Dùng canvas lỗi
            self.photo_admin = self._create_error_canvas("Lỗi tải ảnh")
            self.image_preview_label.config(
                image=self.photo_admin, # Luôn hiển thị ảnh
                text="",
                width=FRAME_W, 
                height=FRAME_H
            )
            self.photo_admin = None
