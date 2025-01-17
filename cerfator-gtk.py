import os
import sys
import gi
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class PDFSignatureApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="PDF Signature App")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Main layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Signature file selection
        hbox_signature = Gtk.Box(spacing=10)
        vbox.pack_start(hbox_signature, False, False, 0)

        self.signature_label = Gtk.Label(label="Select Signature File:")
        hbox_signature.pack_start(self.signature_label, True, True, 0)

        self.signature_button = Gtk.FileChooserButton(title="Choose a Signature Image")
        self.signature_button.set_filter(self.create_image_filter())
        hbox_signature.pack_start(self.signature_button, True, True, 0)

        # PDF folder selection
        hbox_pdf_folder = Gtk.Box(spacing=10)
        vbox.pack_start(hbox_pdf_folder, False, False, 0)

        self.pdf_folder_label = Gtk.Label(label="Select PDF Folder:")
        hbox_pdf_folder.pack_start(self.pdf_folder_label, True, True, 0)

        self.pdf_folder_button = Gtk.FileChooserButton(title="Choose a Folder")
        self.pdf_folder_button.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        hbox_pdf_folder.pack_start(self.pdf_folder_button, True, True, 0)

        # X and Y position inputs
        hbox_position = Gtk.Box(spacing=10)
        vbox.pack_start(hbox_position, False, False, 0)

        self.x_label = Gtk.Label(label="X Position:")
        hbox_position.pack_start(self.x_label, False, False, 0)
        self.x_entry = Gtk.Entry()
        hbox_position.pack_start(self.x_entry, True, True, 0)

        self.y_label = Gtk.Label(label="Y Position:")
        hbox_position.pack_start(self.y_label, False, False, 0)
        self.y_entry = Gtk.Entry()
        hbox_position.pack_start(self.y_entry, True, True, 0)

        # Scale factor input
        hbox_scale = Gtk.Box(spacing=10)
        vbox.pack_start(hbox_scale, False, False, 0)

        self.scale_label = Gtk.Label(label="Scale Factor:")
        hbox_scale.pack_start(self.scale_label, False, False, 0)
        self.scale_entry = Gtk.Entry()
        hbox_scale.pack_start(self.scale_entry, True, True, 0)

        # Process button
        self.process_button = Gtk.Button(label="Add Signature to PDFs")
        self.process_button.connect("clicked", self.on_process_clicked)
        vbox.pack_start(self.process_button, False, False, 0)

    def create_image_filter(self):
        file_filter = Gtk.FileFilter()
        file_filter.add_mime_type("image/jpeg")
        file_filter.add_mime_type("image/png")
        file_filter.set_name("Image Files")
        return file_filter

    def on_process_clicked(self, widget):
        signature_path = self.signature_button.get_filename()
        pdf_folder = self.pdf_folder_button.get_filename()
        try:
            x_position = int(self.x_entry.get_text())
            y_position = int(self.y_entry.get_text())
            scale_factor = float(self.scale_entry.get_text())
        except ValueError:
            self.show_error_message("Invalid position or scale factor input.")
            return

        if not signature_path or not pdf_folder:
            self.show_error_message("Please select a signature file and a PDF folder.")
            return

        self.add_signature_to_pdfs(signature_path, pdf_folder, x_position, y_position, scale_factor)

    def add_signature_to_pdfs(self, signature_path, pdf_folder, x, y, scale):
        for file_name in os.listdir(pdf_folder):
            if file_name.endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, file_name)
                output_path = os.path.join(pdf_folder, f"signed_{file_name}")

                self.add_signature_to_pdf(pdf_path, signature_path, output_path, x, y, scale)
        self.show_info_message("Signature added to all PDFs in the folder.")

    def add_signature_to_pdf(self, pdf_path, signature_path, output_path, x, y, scale):
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

            for page in reader.pages:
                page.merge_page(temp_reader.pages[0])
                writer.add_page(page)

        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        os.remove(temp_pdf)

    def show_error_message(self, message):
        dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.CLOSE, text=message)
        dialog.run()
        dialog.destroy()

    def show_info_message(self, message):
        dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.CLOSE, text=message)
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    app = PDFSignatureApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
