import os
from bs4 import BeautifulSoup
import re
from secedgar import FilingType, CompanyFilings

# Function to read file content with error handling
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

# Function to generate pretty HTML content
def generate_html(content):
    soup = BeautifulSoup(content, 'lxml')
    return soup.prettify()

# Function to save HTML content to a file with error handling
def save_html(html_content, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
    except Exception as e:
        print(f"Error saving HTML to {output_path}: {e}")

# Function to download filings if not already downloaded
def download_filings():
    save_dir = "annual_reports"
    cik_lookup = [
        'aapl', 'msft', 'fb', 'amzn', 'goog', 'tsla', 'brk-a', 
        'v', 'jnj', 'wmt', 'jpm', 'nvda', 'pg', 'hd', 'dis', 
        'pypl', 'cmcsa', 'adbe', 'nflx', 'intc', 'csco', 'pfe',
        'ko', 'pep', 'dell', 'mrk', 'xom', 'nke', 'ibm', 'orcl', 
        'crm', 'c', 'ba', 'mcd', 'cost', 'abt', 'cvx', 'lloyd', 
        'ms', 'hsbc', 'hpe', 'gs', 'bac', 'wfc', 'axp', 'tsm', 
        'hdb', 'sne', 'unh', 'mpc',  'fxe', 'uup', 'fxb', 'fxc',
        'fxa', 'fxy', 'fxf', 'cew', 'cyb', 'icln', 'googl', 'baba', 
        'nflx', 'bidu', 'twtr', 'spot', 'uber', 
        'lyft', 'snap', 'zm', 'docu', 'sq', 'shop', 'roku', 
        'amd', 'avgo', 'qcom', 'mu', 'mrna', 'regn', 'amgn', 
        't', 'vz', 'tmus', 'sbux', 'nke', 'lmt', 'rtx', 
        'cat', 'mmm'
    ]
    filing_type = FilingType.FILING_10Q
    user_agent = "Your Name (your.email@example.com)"

    for ticker in cik_lookup:
        ticker_dir = os.path.join(save_dir, ticker)
        
        # Check if filings are already downloaded
        if os.path.exists(ticker_dir) and any(os.scandir(ticker_dir)):
            print(f"Filings already exist for '{ticker}'. Skipping download.")
            continue
        
        # Download filings
        try:
            all_filings = CompanyFilings(
                cik_lookup=[ticker],
                filing_type=filing_type,
                user_agent=user_agent,
                count=1
            )
            os.makedirs(ticker_dir, exist_ok=True)
            all_filings.save(ticker_dir)
            print(f"Downloaded and saved filings for '{ticker}' in '{ticker_dir}'")
        except Exception as e:
            print(f"Error downloading filings for '{ticker}': {e}")

# Function to convert downloaded filings to HTML
def convert_filings_to_html():
    directory = "annual_reports"  # Source directory containing text files
    output_directory = "parsed_reports_html"  # Destination directory for HTML files
    os.makedirs(output_directory, exist_ok=True)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                # Get the relative path of the file within the "annual_reports" directory
                relative_path = os.path.relpath(root, directory)
                
                # Define the output directory and output file path
                output_dir = os.path.join(output_directory, relative_path)
                os.makedirs(output_dir, exist_ok=True)
                
                output_html_path = os.path.join(output_dir, file.replace(".txt", ".html"))

                # Skip conversion if the HTML file already exists
                if os.path.exists(output_html_path):
                    print(f"HTML file already exists for '{relative_path}/{file}'. Skipping conversion.")
                    continue

                # Read the content of the text file
                file_path = os.path.join(root, file)
                content = read_file(file_path)

                if content:
                    # Convert the content to pretty HTML
                    parsed_content = generate_html(content)
                    
                    # Save the HTML content
                    save_html(parsed_content, output_html_path)
                    print(f"Converted and saved HTML for '{relative_path}/{file}' in '{output_html_path}'")

# Main function to run both download and conversion
def main():
    download_filings()
    convert_filings_to_html()

if __name__ == "__main__":
    main()
