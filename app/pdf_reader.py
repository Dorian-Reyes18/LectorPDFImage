import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageOps
from io import BytesIO
import easyocr
import concurrent.futures

# Instanciar el objeto EasyOCR fuera de la función process_image para reutilizarlo
reader = easyocr.Reader(["es"])

# Función para preprocesar una imagen antes de OCR
def preprocess_image(image):
    # Aumentar el contraste
    image = ImageOps.autocontrast(image)

    # Aplicar filtro de nitidez
    image = image.filter(ImageFilter.SHARPEN)

    # Aplicar inversión de color
    image = ImageOps.invert(image)

    return image

# Función para procesar una imagen y extraer el texto
def process_image(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes))
        preprocessed_image = preprocess_image(image)
        buffer = BytesIO()
        preprocessed_image.save(buffer, format="JPEG")
        buffer.seek(0)
        image_bytes = buffer.read()
        results = reader.readtext(image_bytes)
        return " ".join([result[1] for result in results])
    except Exception as e:
        print("Error al procesar la imagen:", e)
        return ""

# Función para leer el texto de las imágenes en un rango de páginas del PDF
def read_pdf(pdf_path, start_page, end_page):
    page_texts = []

    try:
        pdf_document = fitz.open(pdf_path)
        executor = concurrent.futures.ThreadPoolExecutor()

        for page_number in range(start_page - 1, min(end_page, len(pdf_document))):
            page = pdf_document.load_page(page_number)
            page_text = ""

            futures = [executor.submit(process_image, pdf_document.extract_image(img[0])["image"]) for img in page.get_images(full=True) if pdf_document.extract_image(img[0])["image"]]

            for future in concurrent.futures.as_completed(futures):
                page_text += future.result()

            page_texts.append(page_text)

        pdf_document.close()
    except Exception as e:
        print("Error al procesar el PDF:", e)

    return page_texts

# Ejemplo de uso:
pdf_path = "ruta/al/pdf.pdf"
start_page = 1
end_page = 3
texts = read_pdf(pdf_path, start_page, end_page)
