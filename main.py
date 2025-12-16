import re
import os
from PyPDF2 import PdfReader
from googletrans import Translator
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# ------------------ AYARLAR ------------------
INPUT_PDF = "input/book.pdf"
OUTPUT_PDF = "output/result.pdf"
WORD_LIMIT = 300  # Kaç kelime üretilecek
# --------------------------------------------

os.makedirs("output", exist_ok=True)

# Türkçe karakter desteği
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

translator = Translator()

# ------------------ PDF OKU ------------------
reader = PdfReader(INPUT_PDF)
raw_text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        raw_text += page_text + " "

# ------------------ KELİME AYIKLA ------------------
words = re.findall(r"\b[a-zA-Z]{3,}\b", raw_text.lower())
unique_words = sorted(set(words))[:WORD_LIMIT]

print(f"Toplam {len(unique_words)} kelime bulundu.")

# ------------------ PDF YAZ ------------------
pdf = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4)
styles = getSampleStyleSheet()
style = styles["Normal"]
style.fontName = "HeiseiMin-W3"

content = []

content.append(Paragraph(
    "<b>English – Turkish Vocabulary Book</b><br/>"
    "Automatically generated from PDF<br/><br/>",
    style
))

for i, word in enumerate(unique_words, start=1):
    try:
        tr = translator.translate(word, src="en", dest="tr").text
        explanation = f"Commonly used English word meaning '{word}'."
    except:
        tr = "çeviri hatası"
        explanation = "Explanation unavailable."

    block = f"""
    <b>{i}. {word}</b><br/>
    Türkçe: {tr}<br/>
    Açıklama: {explanation}<br/><br/>
    """
    content.append(Paragraph(block, style))

pdf.build(content)

print("✅ PDF hazır → output/result.pdf")

