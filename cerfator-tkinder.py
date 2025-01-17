import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


class PDFSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cerfator")
        self.root.geometry("400x600")

        # Signature file selection
        tk.Label(root, text="Selectioner une signature:").pack(pady=5)
        self.signature_path = tk.StringVar()
        tk.Entry(root, textvariable=self.signature_path, width=40).pack(pady=5)
        tk.Button(root, text="Browse", command=self.select_signature_file).pack(pady=5)

        # PDF folder selection
        tk.Label(root, text="Select un dossier:").pack(pady=5)
        self.pdf_folder_path = tk.StringVar()
        tk.Entry(root, textvariable=self.pdf_folder_path, width=40).pack(pady=5)
        tk.Button(root, text="Browse", command=self.select_pdf_folder).pack(pady=5)

        # X and Y position inputs with default values
        tk.Label(root, text="X Position (default: 380):").pack(pady=5)
        self.x_position = tk.Entry(root)
        self.x_position.insert(0, "380")  # Default value
        self.x_position.pack(pady=5)

        tk.Label(root, text="Y Position (default: 180):").pack(pady=5)
        self.y_position = tk.Entry(root)
        self.y_position.insert(0, "180")  # Default value
        self.y_position.pack(pady=5)

        # Scale factor input with default value
        tk.Label(root, text="Scale Factor (default: 0.45):").pack(pady=5)
        self.scale_factor = tk.Entry(root)
        self.scale_factor.insert(0, "0.45")  # Default value
        self.scale_factor.pack(pady=5)

        # Page input
        tk.Label(root, text="Page(s) (e.g., '1', '1-3', '1,3,5')").pack(pady=5)
        self.page_input = tk.Entry(root)
        self.page_input.insert(0,"2") # Default value
        self.page_input.pack(pady=5)

        # Process button
        tk.Button(root, text="Ajouter la signature aux PDFs", command=self.process_pdfs).pack(pady=10)

    def select_signature_file(self):
        file_path = filedialog.askopenfilename(
            # filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
        )
        if file_path:
            self.signature_path.set(file_path)

    def select_pdf_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.pdf_folder_path.set(folder_path)

    def process_pdfs(self):
        signature_path = self.signature_path.get()
        pdf_folder = self.pdf_folder_path.get()

        try:
            x_position = int(self.x_position.get())
            y_position = int(self.y_position.get())
            scale_factor = float(self.scale_factor.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid position or scale factor input.")
            return

        if not signature_path or not pdf_folder:
            messagebox.showerror("Error", "Please select a signature file and a PDF folder.")
            return

        # Parse the page input
        pages = self.parse_pages(self.page_input.get())
        if pages is None:
            messagebox.showerror("Error", "Invalid page input format.")
            return

        for file_name in os.listdir(pdf_folder):
            if file_name.endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, file_name)
                output_path = os.path.join(pdf_folder, f"signed_{file_name}")
                self.add_signature_to_pdf(
                    pdf_path, signature_path, output_path, x_position, y_position, scale_factor, pages
                )

        messagebox.showinfo("Success", "Signature ajoutée à tous les PDFs du dossier.")

    def parse_pages(self, page_input):
        """Parse the page input into a set of page numbers."""
        pages = set()
        if not page_input.strip():
            return None

        try:
            ranges = page_input.split(",")
            for r in ranges:
                if "-" in r:
                    start, end = map(int, r.split("-"))
                    pages.update(range(start, end + 1))
                else:
                    pages.add(int(r))
            return pages
        except ValueError:
            return None

    def add_signature_to_pdf(self, pdf_path, signature_path, output_path, x, y, scale, pages):
        # Create a temporary PDF with the signature
        temp_pdf = "temp_signature.pdf"
        c = canvas.Canvas(temp_pdf, pagesize=letter)
        signature = ImageReader(signature_path)

        # Adjust dimensions based on scale factor
        sig_width, sig_height = signature.getSize()
        sig_width *= scale
        sig_height *= scale

        c.drawImage(signature, x, y, width=sig_width, height=sig_height, mask="auto")
        c.save()

        # Merge the temporary PDF with the original PDF
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        with open(temp_pdf, "rb") as temp_pdf_file:
            temp_reader = PdfReader(temp_pdf_file)

            for i, page in enumerate(reader.pages):
                if (i + 1) in pages:  # Page numbers are 1-based
                    page.merge_page(temp_reader.pages[0])
                writer.add_page(page)

        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        os.remove(temp_pdf)


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSignatureApp(root)
    root.mainloop()
