import os
import re
import csv
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Thresholds for minimum meaningful table size
MIN_ROWS = 5
MIN_COLUMNS = 4

# Data density threshold (minimum proportion of non-empty cells)
DATA_DENSITY_THRESHOLD = 0.7  # Stricter to ensure the table contains rich information

# Keywords relevant to revenue and segment information
RELEVANT_REVENUE_KEYWORDS = [
    "revenue", "sales", "income", "net sales", "total revenue"
]

# Keywords relevant to geographic information
RELEVANT_GEOGRAPHIC_KEYWORDS = [
    "segment", "geographic", "region", "americas", "europe", 
    "greater china", "japan", "asia pacific", "geographic data",
    "segment information"
]

# Exclude overly generic or misleading keywords
EXCLUDE_KEYWORDS = [
    "oil and gas", "power generation", "industrial", "transportation", 
    "external sales", "inter-segment", "application", "product", "service",
    "cost", "expenses", "revenue recognition", "technology", "research"
]

def extract_relevant_tables(html_path):
    """Extracts tables containing revenue and segment information from an HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

            relevant_tables = []
            seen_tables = set()  # To store unique table string representations
            for table in soup.find_all('table'):
                table_data = extract_table_data(table)
                if is_relevant_table(table_data):
                    table_str = table_to_string(table_data)
                    if table_str not in seen_tables:
                        relevant_tables.append(table_data)
                        seen_tables.add(table_str)

        return relevant_tables
    except Exception as e:
        logging.error(f"Error processing HTML file {html_path}: {str(e)}")
        return []

def extract_table_data(table):
    """Extracts and cleans data from an HTML table, applying filters to avoid irrelevant tables."""
    table_data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all(['th', 'td']):
            text = cell.get_text(strip=True)
            # Combine "$" with numbers
            if re.match(r'\$\s*\d', text):
                text = text.replace(" ", "")
            row_data.append(text)
        table_data.append(row_data)
    
    # Remove empty rows and columns
    table_data = [row for row in table_data if any(cell.strip() for cell in row)]
    table_data = list(filter(lambda x: any(x), zip(*table_data)))

    return table_data

def table_to_string(table_data):
    """Converts a table's data into a string representation for easy comparison."""
    return '\n'.join(['\t'.join(row) for row in table_data])

def is_relevant_table(table_data):
    """Determine if a table is relevant based on revenue and geographic information."""
    # Check if the table meets the minimum size criteria
    if len(table_data) < MIN_ROWS or len(table_data[0]) < MIN_COLUMNS:
        return False

    # Check for data density
    total_cells = len(table_data) * len(table_data[0])
    non_empty_cells = sum(1 for row in table_data for cell in row if cell.strip())
    data_density = non_empty_cells / total_cells

    if data_density < DATA_DENSITY_THRESHOLD:
        return False

    # Combine the header and data row text for analysis
    combined_text = " ".join(cell for row in table_data for cell in row).lower()

    # Ensure the table has both revenue and geographic keywords
    has_revenue_keyword = any(re.search(keyword, combined_text, re.IGNORECASE) for keyword in RELEVANT_REVENUE_KEYWORDS)
    has_geographic_keyword = any(re.search(keyword, combined_text, re.IGNORECASE) for keyword in RELEVANT_GEOGRAPHIC_KEYWORDS)
    has_exclude_keyword = any(re.search(keyword, combined_text, re.IGNORECASE) for keyword in EXCLUDE_KEYWORDS)
    has_numeric_data = any(re.search(r'\d', cell) for row in table_data for cell in row)

    # Exclude tables that contain exclusion keywords
    if has_exclude_keyword:
        return False

    # Only consider the table relevant if it contains both relevant revenue and geographic keywords, along with numeric data
    return has_revenue_keyword and has_geographic_keyword and has_numeric_data

def save_tables_as_csv(tables, output_path_prefix):
    """Saves the extracted tables as CSV files."""
    for i, table in enumerate(tables):
        if table:  # Only save non-empty tables
            csv_path = f"{output_path_prefix}_table_{i + 1}.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(table)
            logging.info(f"Saved table to {csv_path}")

def process_html_files(directory, output_directory):
    """Processes HTML files in a directory and extracts relevant revenue and segment-related tables."""
    for company in os.listdir(directory):
        company_path = os.path.join(directory, company)
        if os.path.isdir(company_path):
            logging.info(f"Processing directory: {company_path}")
            all_relevant_tables = []

            for root, _, files in os.walk(company_path):
                for file in files:
                    if file.endswith(".html"):
                        html_path = os.path.join(root, file)
                        logging.info(f"Processing file: {html_path}")

                        relevant_tables = extract_relevant_tables(html_path)
                        all_relevant_tables.extend(relevant_tables)

            if all_relevant_tables:
                output_prefix = os.path.join(output_directory, company, "revenue_segmented_by_geography")
                os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
                save_tables_as_csv(all_relevant_tables, output_prefix)

# Directories
html_directory = 'parsed_reports_html'
quantitative_output_directory = 'extracted_quantitative_data'

# Ensure the output directory exists
os.makedirs(quantitative_output_directory, exist_ok=True)

# Process all HTML files and extract relevant revenue and segment-related tables
process_html_files(html_directory, quantitative_output_directory)
