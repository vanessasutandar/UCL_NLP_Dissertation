from fpdf import FPDF
import os

class PDF(FPDF):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name

    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 8, f"FX Risk Rating Analysis for {self.company_name}", align="C", ln=True)
        self.set_font("Arial", "", 12)
        self.cell(0, 8, f"Company: {self.company_name}", align="C", ln=True)
        self.cell(0, 8, "Report Date: August 2024", align="C", ln=True)
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, "L", fill=True)
        self.ln(3)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, title, 0, 1, "L")
        self.ln(3)

    def sub_section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, title, 0, 1, "L")
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        body = body.replace("**", "")  # Remove all Markdown-style bold markers
        body = body.encode('latin1', 'replace').decode('latin1')
        self.multi_cell(0, 8, body)
        self.ln(1)

    def add_bullet_point(self, text):
        self.set_font("Arial", "", 12)
        self.cell(5)  # Add an indent for the bullet point
        self.cell(0, 8, u"\u2022 " + text, ln=True)
        self.ln(1)

    def add_numbered_item(self, number, text):
        self.set_font("Arial", "", 12)
        self.cell(5)
        self.cell(0, 8, f"{number}. {text}", ln=True)
        self.ln(1)

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        # Replace Markdown-style headers with actual bold/large text
        for line in body.splitlines():
            if line.startswith("### "):
                self.section_title(line.replace("### ", "").strip())
            elif line.startswith("#### "):
                self.sub_section_title(line.replace("#### ", "").strip())
            elif "**" in line:
                bold_parts = line.split("**")
                for i, part in enumerate(bold_parts):
                    if i % 2 == 0:
                        self.chapter_body(part)
                    else:
                        self.set_font("Arial", "B", 12)
                        self.chapter_body(part)
                        self.set_font("Arial", "", 12)
            else:
                self.chapter_body(line)

def save_output_to_pdf(title, analysis_data, company_name, output_path):
    # Initialize the PDF object with the company name
    pdf = PDF(company_name)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add the chapter with the title and analysis data
    pdf.add_chapter(title, analysis_data)
    
    # Save the PDF to the specified output path
    pdf.output(output_path)
    
    print(f"PDF saved at {output_path}")
