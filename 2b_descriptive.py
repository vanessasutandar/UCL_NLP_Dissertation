from bs4 import BeautifulSoup
import re
import os
import csv

# Define the root directory where all HTML files are stored
root_dir = '/Users/vanessasutandar/Downloads/financial_reports/parsed_reports_html/'
output_dir = '/Users/vanessasutandar/Downloads/financial_reports/descriptive_information/'
output_file = os.path.join(output_dir, 'financial_reports_summary.csv')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to extract the year and quarter
def get_year_and_quarter(soup):
    text = soup.get_text()
    year_match = re.search(r'\b(20\d{2})\b', text)
    quarter_match = re.search(r'\b(Q[1-4])\b', text)
    year = year_match.group(1) if year_match else "Unknown Year"
    quarter = quarter_match.group(1) if quarter_match else "Unknown Quarter"
    return year, quarter

# Function to estimate page count using multiple strategies
def get_page_count(soup):
    text = soup.get_text()
    
    # Strategy 1: Look for specific page number patterns
    page_pattern = re.findall(r'Page\s\d+', text)
    if page_pattern:
        return len(page_pattern)
    
    # Strategy 2: Count occurrences of common page or section markers
    hr_tags = soup.find_all('hr')
    if hr_tags:
        return len(hr_tags)
    
    # Strategy 3: Look for repeated headers/footers
    headers = soup.find_all(['header', 'footer', 'div'], class_=re.compile(r'header|footer'))
    if headers:
        return len(headers)
    
    return "Unknown Page Count"

# Function to count words
def get_word_count(soup):
    text = soup.get_text()
    words = text.split()
    return len(words)

# Collecting results
results = []

# Loop through all directories and files
for subdir, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(subdir, file)
            folder_name = os.path.basename(os.path.dirname(file_path))  # Get the folder name as company name
            print(f"Processing file: {file_path}")
            
            # Read the content of the HTML file
            with open(file_path, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
            
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract the information
            company_name = folder_name  # Use the folder name as the company name
            year, quarter = get_year_and_quarter(soup)
            page_count = get_page_count(soup)
            word_count = get_word_count(soup)
            
            # Store the results
            results.append([company_name, year, quarter, page_count, word_count])

# Write results to CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Company Name', 'Year', 'Quarter', 'Page Count', 'Word Count'])
    writer.writerows(results)

print(f"Results have been saved to {output_file}")
