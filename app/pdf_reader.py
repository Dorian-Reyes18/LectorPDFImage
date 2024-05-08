import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from io import BytesIO
import easyocr


# Función para preprocesar una imagen antes de OCR
def preprocess_image(image):
    # Aumentar el contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Aumentar el contraste al 200%

    # Aplicar filtro de nitidez
    image = image.filter(ImageFilter.SHARPEN)

    # Aplicar inversión de color
    image = ImageOps.invert(image)

    return image


# Función para leer el texto de las imágenes en un rango de páginas del PDF
def read_pdf(pdf_path, start_page, end_page):
    page_texts = []

    try:
        # Inicializar EasyOCR
        reader = easyocr.Reader(["es"])

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

                    # Preprocesar la imagen antes de OCR
                    preprocessed_image = preprocess_image(image)

                    # Convertir la imagen preprocesada a bytes
                    buffer = BytesIO()
                    preprocessed_image.save(buffer, format="JPEG")
                    buffer.seek(0)
                    image_bytes = buffer.read()

                    # Utilizar EasyOCR para extraer el texto
                    results = reader.readtext(image_bytes)

                    # Imprimir el texto extraído de la imagen
                    print("Texto extraído de la imagen:", results)

                    # Concatenar los resultados de EasyOCR en una sola cadena
                    image_text = " ".join([result[1] for result in results])

                    page_text += image_text

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
