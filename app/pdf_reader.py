# pdf_reader.py

import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
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

    # Ajustar brillo y contraste
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.2)  # Aumentar el brillo en un 20%

    return image


# Función para segmentar imágenes en áreas de interés
def segment_images(page_images):
    segmented_images = []
    for image in page_images:
        # Implementar lógica de segmentación aquí
        # Por ejemplo, se puede dividir la imagen en áreas de texto, encabezado, pie de página, etc.
        # y guardarlas en una lista de imágenes segmentadas
        segmented_images.append(
            image
        )  # Aquí se añade la imagen sin segmentar como ejemplo
    return segmented_images


# Función para aplicar filtros a las imágenes segmentadas
def filter_images(segmented_images):
    filtered_images = []
    for image in segmented_images:
        # Implementar lógica de filtrado aquí
        # Por ejemplo, se pueden aplicar filtros de suavizado, reducción de ruido, etc.
        # y guardar las imágenes filtradas en una lista de imágenes filtradas
        filtered_images.append(
            image
        )  # Aquí se añade la imagen sin filtrar como ejemplo
    return filtered_images


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

        for page_number in range(start_page - 1, min(end_page, len(pdf_document))):
            page = pdf_document.load_page(page_number)
            page_images = [
                pdf_document.extract_image(img[0])["image"]
                for img in page.get_images(full=True)
                if pdf_document.extract_image(img[0])["image"]
            ]

            # Segmentar imágenes
            segmented_images = segment_images(page_images)

            # Aplicar filtros a las imágenes segmentadas
            filtered_images = filter_images(segmented_images)

            page_text = ""
            for image in filtered_images:
                # Procesar cada imagen y extraer texto
                page_text += process_image(image)

            page_texts.append(page_text)

        pdf_document.close()
    except Exception as e:
        print("Error al procesar el PDF:", e)

    return page_texts
