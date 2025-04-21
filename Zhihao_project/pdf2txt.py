import fitz  # PyMuPDF
import os

def pdf_a_txt(ruta_pdf, ruta_txt):
    try:
        doc = fitz.open(ruta_pdf)
        with open(ruta_txt, 'w', encoding='utf-8') as archivo_txt:
            for pagina in doc:
                texto = pagina.get_text()
                archivo_txt.write(texto + '\n')
        print(f"✅ Texto extraído y guardado en '{ruta_txt}'")
    except Exception as e:
        print(f"❌ Error al procesar el PDF: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "products", "8VM3BlueGIS.pdf")
    output_path = os.path.join(current_dir, "products", "8VM3BlueGIS.txt")
    pdf_a_txt(file_path, output_path)