import os
import re
import csv
import logging
from bs4 import BeautifulSoup
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Keywords to identify geographic revenue and FX risk information
REVENUE_KEYWORDS = [
    "revenue", "sales"
]

GEOGRAPHY_KEYWORDS = [
    "geographic", "region", "country", "location", "americas", "europe", "china", 
    "japan", "asia", "pacific", "north america", "international", "consolidated", 
    "fx risk", "foreign exchange", "currency risk"
]

# Function to extract geographic revenue tables from an HTML file
def extract_geographic_revenue_tables(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        geographic_revenue_tables = []

        # Check paragraphs or divs for keywords
        for element in soup.find_all(['p', 'div', 'span']):
            element_text = element.get_text(separator=' ', strip=True).lower()
            if any(keyword in element_text for keyword in GEOGRAPHY_KEYWORDS):
                logging.info(f"Found geography keyword in text: {element_text}")
                new_tables = extract_adjacent_tables(element)
                geographic_revenue_tables.extend(new_tables)

        # Check table headings for keywords
        for table in soup.find_all('table'):
            table_text = table.get_text(separator=' ', strip=True).lower()
            if any(keyword in table_text for keyword in GEOGRAPHY_KEYWORDS):
                logging.info(f"Found geography keyword in table heading: {table_text}")
                table_data = extract_table_data(table)
                if is_meaningful_table(table_data):
                    geographic_revenue_tables.append(table_data)
        
    # Remove duplicate tables
    unique_tables = remove_duplicate_tables(geographic_revenue_tables)
    return unique_tables

# Function to extract table data
def extract_table_data(table):
    table_data = []
    for row in table.find_all('tr'):
        row_data = [cell.get_text(separator=' ', strip=True) for cell in row.find_all(['th', 'td'])]
        if any(row_data):
            table_data.append(row_data)
    return table_data

# Function to extract tables adjacent to specific content
def extract_adjacent_tables(element):
    tables = []
    for sibling in element.find_next_siblings('table'):
        table_data = extract_table_data(sibling)
        if table_data and is_meaningful_table(table_data):
            tables.append(table_data)
    return tables

# Function to check if a table is meaningful
def is_meaningful_table(table_data):
    has_numeric = False
    has_revenue_keyword = False
    has_geography_keyword = False
    min_rows = 3
    min_cols = 2
    num_rows = len(table_data)
    num_cols = len(table_data[0]) if num_rows > 0 else 0

    for row in table_data:
        for cell in row:
            if re.search(r'\d', cell):
                has_numeric = True
            if any(keyword in cell.lower() for keyword in REVENUE_KEYWORDS):
                has_revenue_keyword = True
            if any(keyword in cell.lower() for keyword in GEOGRAPHY_KEYWORDS):
                has_geography_keyword = True

    if has_numeric and has_revenue_keyword and has_geography_keyword and num_rows >= min_rows and num_cols >= min_cols:
        return True
    return False

# Function to remove duplicate tables
def remove_duplicate_tables(tables):
    unique_tables = []
    seen_hashes = set()

    for table in tables:
        table_str = str(table)
        table_hash = hashlib.md5(table_str.encode('utf-8')).hexdigest()
        if table_hash not in seen_hashes:
            unique_tables.append(table)
            seen_hashes.add(table_hash)

    return unique_tables

# Function to save tables as CSV files
def save_tables_as_csv(tables, output_path_prefix):
    for i, table in enumerate(tables):
        csv_path = f"{output_path_prefix}_table_{i + 1}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(table)
        logging.info(f"Saved table to {csv_path}")

# Function to process HTML files in a directory and extract geographic revenue tables
def process_html_files(input_directory, output_directory):
    for ticker in os.listdir(input_directory):
        ticker_path = os.path.join(input_directory, ticker)
        if os.path.isdir(ticker_path):
            for root, dirs, files in os.walk(ticker_path):
                for file in files:
                    if file.endswith(".html"):
                        html_path = os.path.join(root, file)
                        logging.info(f"Processing {html_path}")

                        geographic_revenue_tables = extract_geographic_revenue_tables(html_path)
                        if geographic_revenue_tables:
                            ticker_output_directory = os.path.join(output_directory, ticker)
                            os.makedirs(ticker_output_directory, exist_ok=True)
                            base_filename = os.path.splitext(file)[0]
                            save_tables_as_csv(geographic_revenue_tables, os.path.join(ticker_output_directory, base_filename))

# Directories
html_directory = 'parsed_reports_html'
output_directory = 'extracted_geo_data'

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Process all HTML files and extract geographic revenue tables
process_html_files(html_directory, output_directory)
