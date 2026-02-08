#!/usr/bin/env python3
"""
Simple barcode sequence label generator (Code 128) with Avery templates.

Dependencies: python-barcode, pillow, reportlab

Run: python barcode_creator.py
"""
import io
import math
import os
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, filedialog
from tkinter import ttk

from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


TEMPLATES = {
    "Avery 5160 (30 labels)": {
        "cols": 3,
        "rows": 10,
        "label_w": 2.625 * inch,
        "label_h": 1.0 * inch,
        "margin_left": 0.1875 * inch,
        "margin_top": 0.5 * inch,
        "h_space": 0.0 * inch,
        "v_space": 0.0 * inch,
    },
    "Avery 6576 (20 labels)": {
        "cols": 2,
        "rows": 10,
        "label_w": 4.0 * inch,
        "label_h": 1.0 * inch,
        "margin_left": 0.25 * inch,
        "margin_top": 0.5 * inch,
        "h_space": 0.0 * inch,
        "v_space": 0.0 * inch,
    },
    "Custom (one per page)": {
        "cols": 1,
        "rows": 1,
        "label_w": 6.0 * inch,
        "label_h": 1.5 * inch,
        "margin_left": 0.5 * inch,
        "margin_top": 0.5 * inch,
        "h_space": 0.0 * inch,
        "v_space": 0.0 * inch,
    },
}


def generate_barcode_image(data: str, scale: float = 1.0) -> Image.Image:
    writer = ImageWriter()
    rv = io.BytesIO()
    barcode_obj = Code128(data, writer=writer)
    options = {
        "module_width": 0.2 * scale,
        "module_height": 15 * scale,
        "font_size": 10,
        "quiet_zone": 2.0,
    }
    barcode_obj.write(rv, options)
    rv.seek(0)
    img = Image.open(rv).convert("RGB")
    return img


def create_pdf(start: int, end: int, template_name: str, output_path: str, header_text: str = ""):
    tpl = TEMPLATES.get(template_name)
    if not tpl:
        raise ValueError("Unknown template")

    c = canvas.Canvas(output_path, pagesize=(8.5 * inch, 11 * inch))

    cols = tpl["cols"]
    rows = tpl["rows"]
    label_w = tpl["label_w"]
    label_h = tpl["label_h"]
    mx = tpl["margin_left"]
    my = tpl["margin_top"]
    h_space = tpl["h_space"]
    v_space = tpl["v_space"]

    x_positions = [mx + i * (label_w + h_space) for i in range(cols)]
    y_positions = [11 * inch - my - (r + 1) * label_h - r * v_space for r in range(rows)]

    numbers = list(range(start, end + 1))
    total = len(numbers)
    per_page = cols * rows
    pages = math.ceil(total / per_page)

    idx = 0
    for p in range(pages):
        for r in range(rows):
            for cidx in range(cols):
                if idx >= total:
                    break
                num = numbers[idx]
                text = str(num)
                img = generate_barcode_image(text, scale=1.0)

                # Fit barcode into label area (work in points). Render at high DPI
                # to keep barcode bars sharp when placed into PDF.
                max_img_w_pt = float(label_w - 10)  # leave a small horizontal padding (points)
                max_img_h_pt = float(label_h - 18)  # leave a small vertical padding (points)

                target_dpi = 300.0
                # Convert target size in points to pixels for high-res raster
                target_px_w = max(1, int(math.ceil(max_img_w_pt * (target_dpi / 72.0))))
                target_px_h = max(1, int(math.ceil(max_img_h_pt * (target_dpi / 72.0))))

                # Resize using NEAREST to preserve sharp barcode edges
                img = img.resize((target_px_w, target_px_h), resample=Image.NEAREST)

                buf = io.BytesIO()
                img.save(buf, format="PNG", dpi=(int(target_dpi), int(target_dpi)))
                buf.seek(0)

                x = x_positions[cidx]
                y = y_positions[r]

                # Draw header text if provided
                if header_text:
                    c.setFont("Helvetica", 9)
                    c.drawCentredString(x + label_w / 2, y + label_h - 10, header_text)

                # Center horizontally and vertically a bit
                draw_x = x + (label_w - max_img_w_pt) / 2
                draw_y = y + (label_h - max_img_h_pt) / 2 - 8 if header_text else y + (label_h - max_img_h_pt) / 2 + 6

                # Draw at point sizes (PDF units). ReportLab will use the provided
                # width/height in points; since we rendered the PNG at `target_dpi`,
                # the image will look crisp.
                c.drawImage(ImageReader(buf), draw_x, draw_y, width=max_img_w_pt, height=max_img_h_pt)

                # small text below barcode
                c.setFont("Helvetica", 8)
                c.drawCentredString(x + label_w / 2, y + 4, text)

                idx += 1
            if idx >= total:
                break
        c.showPage()

    c.save()


class App:
    def __init__(self, root):
        self.root = root
        root.title("Barcode Sequence to Avery Labels")

        Label(root, text="Start number:").grid(row=0, column=0, sticky="e")
        self.start_var = StringVar(value="1")
        Entry(root, textvariable=self.start_var).grid(row=0, column=1)

        Label(root, text="End number:").grid(row=1, column=0, sticky="e")
        self.end_var = StringVar(value="30")
        Entry(root, textvariable=self.end_var).grid(row=1, column=1)

        Label(root, text="Header text (optional):").grid(row=2, column=0, sticky="e")
        self.header_var = StringVar(value="")
        Entry(root, textvariable=self.header_var).grid(row=2, column=1)

        Label(root, text="Avery template:").grid(row=3, column=0, sticky="e")
        self.template_var = StringVar()
        cb = ttk.Combobox(root, textvariable=self.template_var, values=list(TEMPLATES.keys()), state="readonly")
        cb.grid(row=3, column=1)
        cb.current(0)

        Button(root, text="Choose output PDF...", command=self.choose_output).grid(row=4, column=0)
        self.out_label = Label(root, text="Not chosen")
        self.out_label.grid(row=4, column=1)

        Button(root, text="Generate PDF", command=self.generate).grid(row=5, column=0, columnspan=2, pady=10)

        self.output_path = None

    def choose_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.output_path = path
            self.out_label.config(text=os.path.basename(path))

    def generate(self):
        try:
            start = int(self.start_var.get())
            end = int(self.end_var.get())
        except ValueError:
            messagebox.showerror("Error", "Start and End must be integers")
            return

        if start > end:
            messagebox.showerror("Error", "Start must be <= End")
            return

        if not self.output_path:
            messagebox.showerror("Error", "Please choose an output PDF file")
            return

        try:
            header_text = self.header_var.get().strip()
            create_pdf(start, end, self.template_var.get(), self.output_path, header_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")
            return

        messagebox.showinfo("Done", f"Saved labels to {self.output_path}")


def main():
    root = Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
