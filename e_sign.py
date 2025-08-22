import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io
import os


class LivePDFESign:
    def __init__(self, root):
        self.root = root
        self.root.title("Live PDF E-Sign")
        self.root.geometry("1000x700")

        self.pdf_doc = None
        self.current_page = 0
        self.signature_text = ""
        self.signature_id = None
        self.signature_pos = (100, 100)

        # Toolbar
        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        open_btn = tk.Button(toolbar, text="Open PDF", command=self.open_pdf)
        open_btn.pack(side=tk.LEFT, padx=5, pady=5)

        sign_btn = tk.Button(toolbar, text="Add Signature", command=self.add_signature)
        sign_btn.pack(side=tk.LEFT, padx=5, pady=5)

        save_btn = tk.Button(toolbar, text="Save PDF", command=self.save_pdf)
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Canvas
        self.canvas = tk.Canvas(root, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_doc = fitz.open(file_path)
            self.current_page = 0
            self.display_page()

    def display_page(self):
        if not self.pdf_doc:
            return
        page = self.pdf_doc[self.current_page]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("ppm")
        self.img = Image.open(io.BytesIO(img_data))
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        if self.signature_text:
            self.signature_id = self.canvas.create_text(
                self.signature_pos[0],
                self.signature_pos[1],
                text=self.signature_text,
                fill="blue",
                font=("Arial", 20, "bold"),
                tags="signature",
            )

    def add_signature(self):
        sig = tk.simpledialog.askstring("Signature", "Enter your signature text:")
        if sig:
            self.signature_text = sig
            self.signature_pos = (150, 150)
            self.display_page()

    def start_drag(self, event):
        if self.signature_id and self.canvas.type(self.signature_id) == "text":
            bbox = self.canvas.bbox(self.signature_id)
            if bbox and (bbox[0] <= event.x <= bbox[2]) and (bbox[1] <= event.y <= bbox[3]):
                self.drag_data = (event.x, event.y)

    def do_drag(self, event):
        if hasattr(self, "drag_data") and self.signature_id:
            dx = event.x - self.drag_data[0]
            dy = event.y - self.drag_data[1]
            self.canvas.move(self.signature_id, dx, dy)
            self.drag_data = (event.x, event.y)
            coords = self.canvas.coords(self.signature_id)
            self.signature_pos = (coords[0], coords[1])

    def save_pdf(self):
        if not self.pdf_doc or not self.signature_text:
            messagebox.showerror("Error", "No PDF or signature to save!")
            return

        page = self.pdf_doc[self.current_page]
        page.insert_text(
            self.signature_pos,
            self.signature_text,
            fontsize=20,
            fontname="helv",
            fill=(0, 0, 255),
        )

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            self.pdf_doc.save(save_path)
            messagebox.showinfo("Success", f"PDF saved as {os.path.basename(save_path)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LivePDFESign(root)
    root.mainloop()
