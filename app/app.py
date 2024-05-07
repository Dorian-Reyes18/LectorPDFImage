from flask import Flask, render_template, request, redirect, flash, url_for
import os
from pdf_reader import read_pdf  # Importar la función read_pdf desde pdf_reader
from PyPDF2 import PdfReader  # Importa la clase PdfReader de PyPDF2
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


# Ruta para la búsqueda por texto
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    pdf_file = request.form["pdf_file"]
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file)
    page_texts = read_pdf(pdf_path)  # Utilizar la función read_pdf importada
    results = []
    for i, text in enumerate(page_texts):
        if query in text:
            results.append(i + 1)  # +1 porque las páginas comienzan en 1, no en 0

    pages_with_results = []
    for result in results:
        page_text = page_texts[result - 1]  # Restamos 1 para obtener el índice correcto
        pages_with_results.append(
            {
                "page_number": result,
                "text": page_text,
                "count": page_text.lower().count(query.lower()),
            }
        )

    return render_template(
        "search_results.html",
        query=query,
        pages_with_results=pages_with_results,
        pdf_file=pdf_file,
    )


if __name__ == "__main__":
    app.secret_key = "super_secret_key"  # Clave secreta para mensajes flash
    app.run(debug=True)
