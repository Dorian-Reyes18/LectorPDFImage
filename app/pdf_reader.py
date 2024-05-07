import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO

# Especifica la ruta directa donde se instaló Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Función para leer el texto de las imágenes en un rango de páginas del PDF
def read_pdf(pdf_path, start_page, end_page):
    page_texts = []

    try:
        # Abrir el PDF
        pdf_document = fitz.open(pdf_path)

        # Procesar el rango de páginas
        for page_number in range(start_page - 1, min(end_page, len(pdf_document))):
            page = pdf_document.load_page(page_number)

            images = page.get_images(full=True)

            page_text = ""
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                # Verificar si la imagen es válida
                if image_bytes is not None:
                    # Convertir bytes a imagen PIL
                    image = Image.open(BytesIO(image_bytes))

                    # Verificar si la imagen se puede procesar con pytesseract
                    if image.mode in ["RGB", "L"]:
                        # Convertir imagen PIL a texto
                        image_text = pytesseract.image_to_string(image)
                        page_text += image_text

            page_texts.append(page_text)

        pdf_document.close()
    except Exception as e:
        print("Error al procesar el PDF:", e)

    return page_texts
