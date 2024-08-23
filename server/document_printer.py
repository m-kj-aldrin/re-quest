import os
import win32com.client as win32
import pythoncom
from docxtpl import DocxTemplate
from tempfile import NamedTemporaryFile


class DocumentPrinter:
    def __init__(self, templates_folder):
        """
        Initializes the DocumentPrinter with the path to the templates folder.
        """
        self.templates_folder = templates_folder

    def load_template(self, template_name):
        """
        Loads a Word template by its filename from the templates folder.
        """
        template_path = os.path.join(self.templates_folder, template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_folder}"
            )
        return DocxTemplate(template_path)

    def render_template(self, template, data):
        """
        Renders the template using the provided data dictionary.
        """
        template.render(data)

    def print_document(self, doc_path):
        """
        Sends the rendered document to the default printer using MS Word.
        """
        # Initialize COM for the current thread
        pythoncom.CoInitialize()

        try:
            word = win32.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(doc_path)
            doc.PrintOut()  # Sends the document to the default printer
            doc.Close()
            word.Quit()
        finally:
            # Ensure COM is uninitialized to avoid issues
            pythoncom.CoUninitialize()

    def process_template(self, template_name, data):
        """
        Loads, renders, and prints the template with the provided data.
        """
        # Load the template
        template = self.load_template(template_name)

        # Render the data into the template
        self.render_template(template, data)

        # Save the rendered document to a temporary file
        with NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_path = temp_file.name
            template.save(temp_path)

        # Print the rendered document
        self.print_document(temp_path)

        # Clean up the temporary file
        os.remove(temp_path)
