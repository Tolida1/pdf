import re
import os
from PyPDF2 import PdfReader
from googletrans import Translator
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# ------------------ AYARLAR ------------------
INPUT_PDF = "input/book.pdf"
OUTPUT_PDF = "output/result.pdf"
WORDS_PER_PAGE = 10   # 🔴 HER SAYFADA 10 KELİME
MAX_WORDS = 1000      # ister 500 / 1000 / 3000 yap
# --------------------------------------------

os.makedirs("output", exist_ok=True)

# Türkçe karakter
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

translator = Translator()

# ------------------ PDF OKU ------------------
reader = PdfReader(INPUT_PDF)
raw_text = ""

for page in reader.pages:
    t = page.extract_text()
    if t:
        raw_text += t + " "

# ------------------ KELİME AYIKLA ------------------
words = re.findall(r"\b[a-zA-Z]{3,}\b", raw_text.lower())
unique_words = list(dict.fromkeys(words))  # sıralı unique
unique_words = unique_words[:MAX_WORDS]

print(f"Toplam {len(unique_words)} kelime kullanılacak.")

# ------------------ PDF YAZ ------------------
pdf = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()
style = styles["Normal"]
style.fontName = "HeiseiMin-W3"
style.spaceAfter = 12

content = []

# Kapak
content.append(Paragraph(
    "<b>English – Turkish Vocabulary Book</b><br/>"
    "Generated from original PDF<br/><br/>",
    style
))
content.append(PageBreak())

count = 0

for i, word in enumerate(unique_words, start=1):
    try:
        tr = translator.translate(word, src="en", dest="tr").text
        explanation = f"A commonly used English word."
    except:
        tr = "çeviri hatası"
        explanation = "Explanation unavailable."

    block = f"""
    <b>{i}. {word}</b><br/>
    Türkçe: {tr}<br/>
    Açıklama: {explanation}
    """
    content.append(Paragraph(block, style))
    count += 1

    # 🔴 10 kelimede bir sayfa kır
    if count % WORDS_PER_PAGE == 0:
        content.append(PageBreak())

pdf.build(content)

print("✅ Kitap formatlı PDF hazır → output/result.pdf")
