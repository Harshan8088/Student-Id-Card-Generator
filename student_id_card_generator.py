import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    Image = ImageDraw = ImageFont = ImageTk = None


APP_BG = "#edf2f7"
NAVY = "#102a43"
BLUE = "#2474d1"
PALE_BLUE = "#e7f0fb"
TEXT = "#243b53"
MUTED = "#627d98"
WHITE = "#ffffff"
BORDER = "#d9e2ec"
TEAL = "#159a9c"


class StudentIDCardGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Student ID Card Generator")
        self.root.geometry("1180x760")
        self.root.minsize(980, 660)
        self.root.configure(bg=APP_BG)

        self.photo_path = None
        self.photo_image = None
        self.preview_photo = None
        self.status_var = tk.StringVar(value="Ready to create a student ID card")

        self.fields = {
            "student_name": tk.StringVar(value="Alex Johnson"),
            "student_id": tk.StringVar(value="STU-2026-0148"),
            "course": tk.StringVar(value="Computer Science"),
            "year": tk.StringVar(value="Year 2"),
            "valid_until": tk.StringVar(value="June 2027"),
            "institution": tk.StringVar(value="Northbridge University"),
        }

        self._configure_styles()
        self._build_header()
        self._build_content()
        self._bind_updates()
        self.update_preview()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TEntry", fieldbackground=WHITE, background=WHITE,
                        foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER,
                        darkcolor=BORDER, padding=9)
        style.configure("TCombobox", fieldbackground=WHITE, background=WHITE,
                        foreground=TEXT, bordercolor=BORDER, padding=8)
        style.configure("Primary.TButton", background=BLUE, foreground=WHITE,
                        borderwidth=0, padding=(16, 10), font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", background=[("active", "#1d5fae")])
        style.configure("Secondary.TButton", background=WHITE, foreground=TEXT,
                        borderwidth=1, relief="solid", padding=(14, 9),
                        font=("Segoe UI", 10, "bold"))
        style.map("Secondary.TButton", background=[("active", PALE_BLUE)])

    def _build_header(self):
        header = tk.Frame(self.root, bg=NAVY, height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=NAVY)
        brand.pack(side="left", padx=30, pady=16)
        tk.Label(brand, text="NB", bg=TEAL, fg=WHITE, width=4, height=2,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 12))
        title_box = tk.Frame(brand, bg=NAVY)
        title_box.pack(side="left")
        tk.Label(title_box, text="Student ID Card Generator", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(title_box, text="Create a polished campus card in seconds", bg=NAVY,
                 fg="#b9d3e9", font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        tk.Label(header, text="ID CARD STUDIO", bg=NAVY, fg="#8fb7d5",
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=30)

    def _build_content(self):
        content = tk.Frame(self.root, bg=APP_BG)
        content.pack(fill="both", expand=True, padx=28, pady=26)
        content.grid_columnconfigure(0, weight=0, minsize=370)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self._build_form_panel(content)
        self._build_preview_panel(content)

    def _build_form_panel(self, parent):
        panel = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        tk.Label(panel, text="Card details", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=25, pady=(24, 2))
        tk.Label(panel, text="Fill in the information shown on the card.", bg=WHITE,
                 fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=25, pady=(0, 20))

        form = tk.Frame(panel, bg=WHITE)
        form.pack(fill="x", padx=25)
        self._add_field(form, "Student name", "student_name", 0)
        self._add_field(form, "Student ID", "student_id", 1)
        self._add_field(form, "Course / major", "course", 2)
        self._add_field(form, "Year", "year", 3)
        self._add_field(form, "Valid until", "valid_until", 4)
        self._add_field(form, "Institution", "institution", 5)

        tk.Label(form, text="Student photo", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky="w", pady=(18, 6))
        photo_row = tk.Frame(form, bg=WHITE)
        photo_row.grid(row=7, column=0, sticky="ew")
        photo_row.grid_columnconfigure(0, weight=1)
        self.photo_label = tk.Label(photo_row, text="No photo selected", anchor="w", bg="#f7f9fc",
                                    fg=MUTED, padx=10, font=("Segoe UI", 9))
        self.photo_label.grid(row=0, column=0, sticky="ew", ipady=6)
        ttk.Button(photo_row, text="Browse", style="Secondary.TButton",
                   command=self.choose_photo).grid(row=0, column=1, padx=(8, 0))

        ttk.Button(panel, text="Export card as PNG", style="Primary.TButton",
                   command=self.export_card).pack(fill="x", padx=25, pady=(25, 10))
        ttk.Button(panel, text="Reset form", style="Secondary.TButton",
                   command=self.reset_form).pack(fill="x", padx=25)

        tk.Label(panel, textvariable=self.status_var, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8), wraplength=300, justify="left").pack(anchor="w", padx=25, pady=(18, 22))

    def _add_field(self, parent, label, key, row):
        tk.Label(parent, text=label, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).grid(row=row * 2, column=0, sticky="w", pady=(0, 5 if row == 0 else 4))
        entry = ttk.Entry(parent, textvariable=self.fields[key])
        entry.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 10))
        parent.grid_columnconfigure(0, weight=1)

    def _build_preview_panel(self, parent):
        panel = tk.Frame(parent, bg=APP_BG)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        heading = tk.Frame(panel, bg=APP_BG)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        tk.Label(heading, text="Live preview", bg=APP_BG, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        tk.Label(heading, text="FRONT SIDE", bg=APP_BG, fg=BLUE,
                 font=("Segoe UI", 9, "bold")).pack(side="right", pady=4)

        canvas_frame = tk.Frame(panel, bg="#dce6f0")
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        self.canvas = tk.Canvas(canvas_frame, bg="#dce6f0", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda event: self.update_preview())

    def _bind_updates(self):
        for variable in self.fields.values():
            variable.trace_add("write", lambda *_: self.update_preview())

    def initials(self):
        words = self.fields["student_name"].get().strip().split()
        if not words:
            return "??"
        return "".join(word[0] for word in words[:2]).upper()

    def choose_photo(self):
        path = filedialog.askopenfilename(
            title="Choose student photo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")],
        )
        if not path:
            return
        if Image is None:
            messagebox.showwarning("Pillow required", "Install Pillow to use custom photos: pip install pillow")
            return
        try:
            image = Image.open(path).convert("RGB")
            self.photo_image = image
            self.photo_path = path
            self.photo_label.configure(text=os.path.basename(path), fg=TEXT)
            self.status_var.set("Photo loaded. Your card preview is updated.")
            self.update_preview()
        except Exception as error:
            messagebox.showerror("Could not load photo", str(error))

    def reset_form(self):
        defaults = ["Alex Johnson", "STU-2026-0148", "Computer Science", "Year 2", "June 2027", "Northbridge University"]
        for key, value in zip(self.fields, defaults):
            self.fields[key].set(value)
        self.photo_path = None
        self.photo_image = None
        self.photo_label.configure(text="No photo selected", fg=MUTED)
        self.status_var.set("Form reset to the sample student")
        self.update_preview()

    def update_preview(self):
        if not hasattr(self, "canvas"):
            return
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 400)
        self.canvas.delete("all")

        card_width = min(680, width - 90)
        card_height = card_width * 0.625
        if card_height > height - 70:
            card_height = height - 70
            card_width = card_height / 0.625
        left = (width - card_width) / 2
        top = (height - card_height) / 2
        right = left + card_width
        bottom = top + card_height

        self.canvas.create_rectangle(left + 7, top + 9, right + 7, bottom + 9,
                                     fill="#b4c4d3", outline="")
        self.canvas.create_rectangle(left, top, right, bottom, fill=WHITE, outline="")
        self.canvas.create_rectangle(left, top, right, top + card_height * 0.28,
                                     fill=NAVY, outline="")
        self.canvas.create_polygon(left, top + card_height * 0.28, right, top + card_height * 0.28,
                                   right, top + card_height * 0.34, left, top + card_height * 0.45,
                                   fill=TEAL, outline="")

        scale = card_width / 680
        self.canvas.create_text(left + 28 * scale, top + 28 * scale, text="NB",
                                fill=WHITE, font=("Segoe UI", max(10, int(19 * scale)), "bold"), anchor="w")
        self.canvas.create_text(left + 28 * scale, top + 53 * scale,
                                text=self.fields["institution"].get().upper() or "INSTITUTION",
                                fill="#b9d3e9", font=("Segoe UI", max(7, int(10 * scale)), "bold"), anchor="w")
        self.canvas.create_text(right - 28 * scale, top + 36 * scale, text="STUDENT ID",
                                fill=WHITE, font=("Segoe UI", max(8, int(11 * scale)), "bold"), anchor="e")
        self.canvas.create_text(right - 28 * scale, top + 56 * scale, text="2026 / 27",
                                fill="#b9d3e9", font=("Segoe UI", max(7, int(9 * scale))), anchor="e")

        photo_size = 142 * scale
        photo_left = left + 34 * scale
        photo_top = top + 112 * scale
        self._draw_photo(photo_left, photo_top, photo_size, scale)

        text_x = left + 205 * scale
        self.canvas.create_text(text_x, top + 124 * scale, text=self.fields["student_name"].get() or "Student Name",
                                fill=NAVY, font=("Segoe UI", max(12, int(24 * scale)), "bold"), anchor="w")
        self.canvas.create_text(text_x, top + 161 * scale, text=self.fields["course"].get() or "Course / Major",
                                fill=TEAL, font=("Segoe UI", max(9, int(13 * scale)), "bold"), anchor="w")
        self.canvas.create_text(text_x, top + 207 * scale, text="STUDENT ID", fill=MUTED,
                                font=("Segoe UI", max(7, int(9 * scale)), "bold"), anchor="w")
        self.canvas.create_text(text_x, top + 226 * scale, text=self.fields["student_id"].get() or "ID number",
                                fill=TEXT, font=("Segoe UI", max(9, int(14 * scale)), "bold"), anchor="w")
        self.canvas.create_text(text_x, top + 261 * scale, text=f"{self.fields['year'].get()}  •  Valid until {self.fields['valid_until'].get()}",
                                fill=MUTED, font=("Segoe UI", max(7, int(10 * scale))), anchor="w")

        self.canvas.create_line(left + 34 * scale, bottom - 48 * scale, right - 34 * scale,
                                bottom - 48 * scale, fill=BORDER, width=1)
        self.canvas.create_text(left + 34 * scale, bottom - 25 * scale, text="PROPERTY OF NORTHBRIDGE UNIVERSITY",
                                fill=MUTED, font=("Segoe UI", max(6, int(8 * scale)), "bold"), anchor="w")
        self.canvas.create_text(right - 34 * scale, bottom - 25 * scale, text="www.northbridge.edu",
                                fill=BLUE, font=("Segoe UI", max(6, int(8 * scale))), anchor="e")

    def _draw_photo(self, x, y, size, scale):
        self.canvas.create_rectangle(x, y, x + size, y + size, fill=PALE_BLUE, outline="#c4d8ed", width=1)
        if self.photo_image is not None and ImageTk is not None:
            image = self.photo_image.copy()
            image.thumbnail((max(1, int(size)), max(1, int(size))))
            self.preview_photo = ImageTk.PhotoImage(image)
            image_x = x + (size - image.width()) / 2
            image_y = y + (size - image.height()) / 2
            self.canvas.create_image(image_x, image_y, image=self.preview_photo, anchor="nw")
            return
        self.canvas.create_oval(x + size * 0.31, y + size * 0.18, x + size * 0.69,
                                y + size * 0.56, fill="#8fb7d5", outline="")
        self.canvas.create_oval(x + size * 0.15, y + size * 0.47, x + size * 0.85,
                                y + size * 1.12, fill="#5b8db7", outline="")
        self.canvas.create_text(x + size / 2, y + size * 0.84, text=self.initials(),
                                fill=WHITE, font=("Segoe UI", max(10, int(18 * scale)), "bold"))

    def export_card(self):
        if Image is None:
            messagebox.showwarning("Pillow required", "Install Pillow to export PNG files: pip install pillow")
            return
        output_path = filedialog.asksaveasfilename(
            title="Save student ID card",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile=f"{self.fields['student_id'].get() or 'student_id_card'}.png",
        )
        if not output_path:
            return
        try:
            image = self._render_export_image()
            image.save(output_path, "PNG")
            self.status_var.set(f"Saved card to {os.path.basename(output_path)}")
            messagebox.showinfo("Card exported", "Your student ID card was exported successfully.")
        except Exception as error:
            messagebox.showerror("Export failed", str(error))

    def _render_export_image(self):
        width, height = 1360, 850
        image = Image.new("RGB", (width, height), WHITE)
        draw = ImageDraw.Draw(image)
        navy, blue, teal = NAVY, BLUE, TEAL

        draw.rectangle((0, 0, width, 235), fill=navy)
        draw.polygon((0, 235, width, 235, width, 285, 0, 385), fill=teal)
        draw.text((56, 58), "NB", fill=WHITE, font=self._font(38, True))
        draw.text((56, 112), self.fields["institution"].get().upper() or "INSTITUTION", fill="#b9d3e9", font=self._font(20, True))
        draw.text((width - 56, 82), "STUDENT ID", fill=WHITE, font=self._font(22, True), anchor="ra")
        draw.text((width - 56, 125), "2026 / 27", fill="#b9d3e9", font=self._font(18), anchor="ra")

        photo_size = 284
        photo_x, photo_y = 68, 372
        draw.rectangle((photo_x, photo_y, photo_x + photo_size, photo_y + photo_size), fill=PALE_BLUE, outline="#c4d8ed", width=2)
        if self.photo_image is not None:
            photo = self.photo_image.copy()
            photo.thumbnail((photo_size, photo_size))
            image.paste(photo, (photo_x + (photo_size - photo.width) // 2, photo_y + (photo_size - photo.height) // 2))
        else:
            draw.ellipse((photo_x + 88, photo_y + 48, photo_x + 196, photo_y + 156), fill="#8fb7d5")
            draw.ellipse((photo_x + 42, photo_y + 138, photo_x + 242, photo_y + 330), fill="#5b8db7")
            draw.text((photo_x + photo_size // 2, photo_y + 240), self.initials(), fill=WHITE, font=self._font(34, True), anchor="mm")

        text_x = 410
        draw.text((text_x, 390), self.fields["student_name"].get() or "Student Name", fill=navy, font=self._font(48, True))
        draw.text((text_x, 474), self.fields["course"].get() or "Course / Major", fill=teal, font=self._font(26, True))
        draw.text((text_x, 565), "STUDENT ID", fill=MUTED, font=self._font(18, True))
        draw.text((text_x, 600), self.fields["student_id"].get() or "ID number", fill=TEXT, font=self._font(28, True))
        draw.text((text_x, 670), f"{self.fields['year'].get()}  |  Valid until {self.fields['valid_until'].get()}", fill=MUTED, font=self._font(20))
        draw.line((68, 777, width - 68, 777), fill=BORDER, width=2)
        draw.text((68, 800), "PROPERTY OF NORTHBRIDGE UNIVERSITY", fill=MUTED, font=self._font(15, True))
        draw.text((width - 68, 800), "www.northbridge.edu", fill=blue, font=self._font(15), anchor="ra")
        return image.resize((680, 425), Image.Resampling.LANCZOS)

    @staticmethod
    def _font(size, bold=False):
        if ImageFont is None:
            return None
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()


def main():
    root = tk.Tk()
    StudentIDCardGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
