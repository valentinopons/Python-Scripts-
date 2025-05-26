import re
import PyPDF2

def extract_dob_from_layout(pdf_path):
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    # Buscamos el bloque de texto que contiene "DATE OF BIRTH"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "date of birth" in line.lower():
            # Revisamos si en la misma línea está la fecha
            match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", line)
            if match:
                return match.group(1)
            # Si no, buscamos en las siguientes 3 líneas por si la fecha está separada
            for j in range(1, 4):
                if i + j < len(lines):
                    next_line = lines[i + j]
                    match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", next_line)
                    if match:
                        return match.group(1)

    return "Fecha de nacimiento no encontrada en el texto visible."

# Uso
pdf_path = "CREDIT APP - 8301.pdf"
fecha = extract_dob_from_layout(pdf_path)
print("Fecha de nacimiento:", fecha)
