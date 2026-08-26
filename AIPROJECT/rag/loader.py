import os
import fitz  # PyMuPDF
from docx import Document


class DocumentLoader:
    """
    Loads PDF, DOCX, and TXT documents.
    Returns chunks with:
    - text
    - page
    - source
    - file_path
    - chunk_id
    """

    def __init__(self):
        pass


    # -----------------------------
    # Load PDF
    # -----------------------------
    def load_pdf(self, file_path):

        documents = []

        pdf = fitz.open(file_path)

        chunk_id = 0


        for page_number in range(len(pdf)):

            page = pdf.load_page(page_number)

            text = page.get_text()


            if text.strip():

                documents.append(

                    {
                        "text": text,

                        "page": page_number + 1,

                        "source": os.path.basename(file_path),

                        "file_path": file_path,

                        "chunk_id": chunk_id

                    }

                )

                chunk_id += 1


        pdf.close()


        return documents



    # -----------------------------
    # Load DOCX
    # -----------------------------
    def load_docx(self, file_path):

        doc = Document(file_path)


        text = "\n".join(

            paragraph.text

            for paragraph in doc.paragraphs

            if paragraph.text.strip()

        )


        return [

            {

                "text": text,

                "page": 1,

                "source": os.path.basename(file_path),

                "file_path": file_path,

                "chunk_id": 0

            }

        ]



    # -----------------------------
    # Load TXT
    # -----------------------------
    def load_txt(self, file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()



        return [

            {

                "text": text,

                "page": 1,

                "source": os.path.basename(file_path),

                "file_path": file_path,

                "chunk_id": 0

            }

        ]



    # -----------------------------
    # Auto Detect File Type
    # -----------------------------
    def load_document(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()


        if extension == ".pdf":

            return self.load_pdf(file_path)


        elif extension == ".docx":

            return self.load_docx(file_path)


        elif extension == ".txt":

            return self.load_txt(file_path)


        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )