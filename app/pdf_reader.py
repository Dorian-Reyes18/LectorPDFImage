import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO

# Especifica la ruta directa donde se instaló Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Función para leer el texto de las imágenes en un PDF
def read_pdf(pdf_path):
    page_texts = []

    try:
        # Abrir el PDF
        pdf_document = fitz.open(pdf_path)

        # Configurar el tamaño del lote (número de páginas por lote)
        batch_size = 10
        num_pages = len(pdf_document)

        # Procesar el PDF por lotes
        for i in range(0, num_pages, batch_size):
            end_index = min(i + batch_size, num_pages)
            page_texts.extend(process_batch(pdf_document, i, end_index))

        pdf_document.close()
    except Exception as e:
        print("Error al procesar el PDF:", e)

    return page_texts


# Función para procesar un lote de páginas del PDF
def process_batch(pdf_document, start_index, end_index):
    batch_texts = []

    for page_number in range(start_index, end_index):
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

        batch_texts.append(page_text)

    return batch_texts
