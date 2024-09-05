import os
import re
import logging
from lxml import etree
from html import unescape

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Expanded keywords related to FX risk, converted to lowercase for faster matching
FX_KEYWORDS = {kw.lower() for kw in [
    "FX risk", "foreign exchange", "hedging", "currency risk", "exchange rate", "forex", "risk",
    "derivatives", "forward contract", "swap", "options", "currency exposure", "economic exposure",
    "transaction exposure", "translation exposure", "foreign currency", "monetary assets", "monetary liabilities",
    "natural hedge", "synthetic hedge", "risk management"
]}

# Categorization of FX risks
FX_CATEGORIES = {
    "transaction exposure": ["transaction exposure", "contractual exposure", "cash flow exposure"],
    "translation exposure": ["translation exposure", "balance sheet exposure"],
    "economic exposure": ["economic exposure", "competitive exposure"],
    "general_fx_risk": []  # For any general FX-related content that doesn't fit other categories
}

# Function to categorize FX risks based on keywords
def categorize_fx_risk(paragraph_text):
    paragraph_text_lower = paragraph_text.lower()
    for category, keywords in FX_CATEGORIES.items():
        if any(keyword in paragraph_text_lower for keyword in keywords):
            return category
    return "general_fx_risk"

# Function to extract FX-related content and metadata from a large HTML file
def extract_fx_related_content_large_file(html_path):
    try:
        fx_related_paragraphs = {}
        company_name = "Unknown Company"
        document_year = "Unknown Year"
        current_section = "Unknown Section"

        context = etree.iterparse(html_path, events=('end',), html=True)

        for event, element in context:
            if element.tag == 'title':
                company_name = extract_company_name_from_title(element.text)
            elif element.tag in ['h1', 'h2', 'h3']:
                current_section = element.text.strip()
                if company_name == "Unknown Company":
                    company_name = current_section
            elif element.tag in ['p', 'div', 'span']:
                paragraph_text = unescape(' '.join(element.itertext()).strip())
                if is_meaningful_and_contains_keywords(paragraph_text):
                    cleaned_paragraph = clean_text(paragraph_text)
                    category = categorize_fx_risk(paragraph_text)
                    full_paragraph = f"Section: {current_section}\n\n{cleaned_paragraph}"
                    if category not in fx_related_paragraphs:
                        fx_related_paragraphs[category] = []
                    fx_related_paragraphs[category].append(full_paragraph)
            
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]

        document_year = extract_year_from_file(html_path)

        combined_paragraphs = "\n\n".join(
            f"Category: {category}\n\n" + "\n\n".join(paragraphs)
            for category, paragraphs in fx_related_paragraphs.items()
        )

        return company_name, document_year, combined_paragraphs
    except Exception as e:
        logging.error(f"Error processing HTML file {html_path}: {str(e)}")
        return None, None, ""

# Helper function to extract company name from the title tag
def extract_company_name_from_title(title_text):
    if title_text:
        return title_text.split("-")[0].strip()
    return "Unknown Company"

# Function to check if a paragraph is meaningful and contains FX keywords
def is_meaningful_and_contains_keywords(paragraph_text):
    if 'http' in paragraph_text or len(paragraph_text.split()) < 5:
        return False
    paragraph_text_lower = paragraph_text.lower()
    return any(keyword in paragraph_text_lower for keyword in FX_KEYWORDS)

# Function to clean the text
def clean_text(text):
    text = re.sub(r'\b(Name|Namespace Prefix|Data Type|Balance Type|Period Type):.*', '', text)
    text = re.sub(r'\b(References|Details).*', '', text)
    text = re.sub(r'Page \d+', '', text)  # Remove page numbers
    return re.sub(r'\s+', ' ', text).strip()

# Function to extract the year from the file
def extract_year_from_file(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        text = file.read()
        year_match = re.search(r'(\b19|\b20)\d{2}', text)
        if year_match:
            return year_match.group(0)
    return "Unknown Year"

# Function to save extracted text to a file
def save_text(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

# Function to process HTML files in a directory and extract FX risk-related content
def process_html_files(directory, qualitative_output_directory):
    for company in os.listdir(directory):
        company_path = os.path.join(directory, company)
        output_company_path = os.path.join(qualitative_output_directory, company)
        
        if os.path.exists(output_company_path):
            logging.info(f"Skipping directory {company_path} as it has already been processed.")
            continue
        
        if os.path.isdir(company_path):
            logging.info(f"Processing directory: {company_path}")

            all_fx_paragraphs = set()

            for root, _, files in os.walk(company_path):
                logging.info(f"Traversing directory: {root}")
                for file in files:
                    if file.endswith(".html"):
                        html_path = os.path.join(root, file)
                        logging.info(f"Processing file: {html_path}")

                        company_name, document_year, fx_paragraphs = extract_fx_related_content_large_file(html_path)
                        if fx_paragraphs:
                            all_fx_paragraphs.add(fx_paragraphs)

            if all_fx_paragraphs:
                all_fx_paragraphs_combined = '\n\n'.join(all_fx_paragraphs)
                qualitative_output_text_path = os.path.join(output_company_path, f"{company_name}_{document_year}_fx_risk_text.txt")
                os.makedirs(os.path.dirname(qualitative_output_text_path), exist_ok=True)
                save_text(all_fx_paragraphs_combined, qualitative_output_text_path)
                logging.info(f"Saved FX-related text to {qualitative_output_text_path}")

# Directories
html_directory = 'parsed_reports_html'
qualitative_output_directory = 'extracted_qualitative_data_1'

# Ensure the output directory exists
os.makedirs(qualitative_output_directory, exist_ok=True)

# Process all HTML files and extract FX risk-related text
process_html_files(html_directory, qualitative_output_directory)
