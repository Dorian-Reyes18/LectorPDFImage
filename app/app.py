from flask import Flask, render_template, request, redirect, flash, url_for
import os
from pdf_reader import read_pdf
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")

# Definir la carpeta de carga de archivos PDF
UPLOAD_FOLDER = "static/pdf_files"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Definir las extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {"pdf"}


# Función para verificar la extensión del archivo
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Ruta para la página principal
@app.route("/")
def index():
    # Obtener la lista de archivos PDF en la carpeta pdf_files
    pdf_files = [file for file in os.listdir(UPLOAD_FOLDER) if file.endswith(".pdf")]
    return render_template("index.html", pdf_files=pdf_files)


# Ruta para cargar el documento PDF
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if "pdf_file" not in request.files:
        flash("No se ha seleccionado ningún archivo PDF", "error")
        return redirect(url_for("index"))

    pdf_file = request.files["pdf_file"]

    if pdf_file.filename == "":
        flash("No se ha seleccionado ningún archivo PDF", "error")
        return redirect(url_for("index"))

    if pdf_file and allowed_file(pdf_file.filename):
        filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        pdf_file.save(pdf_path)
        flash("El archivo PDF se ha cargado correctamente", "success")
        return redirect(url_for("dashboard", pdf_file=filename))

    flash("El archivo seleccionado no es un PDF válido", "error")
    return redirect(url_for("index"))


# Ruta para el dashboard (preview del PDF seleccionado)
@app.route("/dashboard/<pdf_file>")
def dashboard(pdf_file):
    pdf_path = os.path.join(app.static_folder, "pdf_files", pdf_file)
    if os.path.exists(pdf_path):
        # Obtener el número de páginas del PDF
        with open(pdf_path, "rb") as f:
            pdf_reader = PdfReader(f)
            num_pages = len(pdf_reader.pages)
        return render_template("dashboard.html", pdf_file=pdf_file, num_pages=num_pages)
    else:
        flash("El PDF seleccionado no existe", "error")
        return redirect(url_for("index"))


# Ruta para la búsqueda por texto con paginación
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    pdf_file = request.form["pdf_file"]
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file)

    # Obtener el rango de páginas del formulario
    start_page = int(request.form["start_page"])
    end_page = int(request.form["end_page"])

    # Extraer texto del PDF con EasyOCR
    page_texts = read_pdf(pdf_path, start_page, end_page)

    # Resultados de búsqueda
    results = []
    for i, text in enumerate(page_texts):
        if query in text:
            results.append(
                i + start_page
            )  # Número de página, comenzando desde start_page

    # Calcular el total de páginas
    total_pages = (len(results) + end_page - start_page) // (end_page - start_page + 1)

    # Página actual
    page_number = int(request.args.get("page", start_page))

    # Calcular el rango de resultados para la página actual
    start_index = (page_number - start_page) * (end_page - start_page + 1)
    end_index = min(start_index + (end_page - start_page + 1), len(results))

    # Obtener los resultados para la página actual
    current_results = results[start_index:end_index]

    # Obtener información de las páginas con resultados para la página actual
    pages_with_results = []
    for result in current_results:
        page_number = result
        page_text = page_texts[page_number - start_page]
        # Verificar si la página ya está en la lista
        if page_number not in [page["page_number"] for page in pages_with_results]:
            pages_with_results.append(
                {
                    "page_number": page_number,
                    "text": page_text,
                    "count": page_text.lower().count(query.lower()),
                }
            )

    # Mensaje si no se encontraron coincidencias
    if not pages_with_results:
        flash("No se encontraron coincidencias", "info")
        print("No se encontraron coincidencias para la búsqueda:", query)

    return render_template(
        "search_results.html",
        query=query,
        pages_with_results=pages_with_results,
        pdf_file=pdf_file,
        total_pages=total_pages,
        current_page=page_number,
    )


if __name__ == "__main__":
    app.secret_key = "super_secret_key"  # Clave secreta para mensajes flash
    app.run(debug=False)
