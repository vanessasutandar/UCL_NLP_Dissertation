import os
import logging
import re
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Keywords related to geographic data
GEO_KEYWORDS = ["geography", "geographic", "domestic", "hedging effect"]

# Function to extract table from HTML file
def extract_table_from_html(html_file_path, keywords):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all tables in the HTML file
    tables = soup.find_all('table')
    logging.info(f"Found {len(tables)} tables in {html_file_path}")

    # Refine the search to locate the specific table based on the keywords
    target_table = None

    for table in tables:
        table_text = table.get_text().lower()
        if any(keyword in table_text for keyword in keywords):
            target_table = table
            logging.info(f"Found target table in {html_file_path}")
            break

    if target_table:
        data = []
        rows = target_table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.get_text(separator=' ').strip() for ele in cols]
            # Unify $ and number
            cols = [re.sub(r'\$\s+', '$', col) for col in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values
        
        # Convert the extracted data to a DataFrame
        df_extracted = pd.DataFrame(data)

        # Extract only the first two columns
        df_extracted = df_extracted.iloc[:, :2]
        df_extracted.columns = ['Description', 'Revenue']

        return df_extracted
    else:
        logging.info(f"No target table found in {html_file_path}")
        return None

# Function to save DataFrame as CSV file
def save_dataframe_as_csv(df, output_path):
    df.to_csv(output_path, index=False)
    logging.info(f"Saved data to {output_path}")

# Function to process HTML files in a directory and extract geographic tables
def process_html_files(input_directory, output_directory, keywords):
    logging.info(f"Processing HTML files in directory: {input_directory}")
    
    # Walk through all subdirectories and files
    for root, _, files in os.walk(input_directory):
        for filename in files:
            if filename.endswith('.html'):
                html_file_path = os.path.join(root, filename)
                logging.info(f"Processing file: {html_file_path}")

                # Extract the table from the HTML file
                df = extract_table_from_html(html_file_path, keywords)

                if df is not None:
                    # Define the output CSV file path, preserving subdirectory structure
                    relative_path = os.path.relpath(root, input_directory)
                    output_subdir = os.path.join(output_directory, relative_path)
                    os.makedirs(output_subdir, exist_ok=True)
                    output_csv_file_path = os.path.join(output_subdir, f"{os.path.splitext(filename)[0]}_geo.csv")

                    # Save the extracted DataFrame to a CSV file
                    save_dataframe_as_csv(df, output_csv_file_path)
                else:
                    logging.info(f"No relevant table found in file: {html_file_path}")

# Directories
html_directory = 'parsed_reports_html'
geo_output_directory = 'extracted_geo_data'

# Ensure the output directory exists
os.makedirs(geo_output_directory, exist_ok=True)

# Keywords to search for the relevant table
keywords = ["geography", "geographic", "domestic", "hedging effect"]

# Process all HTML files and extract geographic tables
process_html_files(html_directory, geo_output_directory, keywords)
