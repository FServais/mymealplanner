from pypdf import PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Grandma's Pancakes")
    c.drawString(100, 730, "Ingredients:")
    c.drawString(120, 710, "- 1 cup Flour")
    c.drawString(120, 690, "- 2 Eggs")
    c.drawString(120, 670, "- 1 cup Milk")
    c.drawString(120, 650, "- 1 tbsp Sugar")
    c.drawString(100, 620, "Instructions:")
    c.drawString(120, 600, "1. Mix all ingredients in a bowl.")
    c.drawString(120, 580, "2. Heat a pan over medium heat.")
    c.drawString(120, 560, "3. Pour batter and cook until bubbly.")
    c.save()

if __name__ == "__main__":
    create_sample_pdf("sample_recipe.pdf")
    print("Created sample_recipe.pdf")
