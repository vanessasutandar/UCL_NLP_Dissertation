import os
from bs4 import BeautifulSoup
from secedgar import FilingType, CompanyFilings

# Function to read file content with error handling
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

# Function to generate HTML from content with error handling
def generate_html(content):
    try:
        soup = BeautifulSoup(content, 'lxml')
        return soup.prettify()
    except Exception as e:
        print(f"Error parsing file content: {e}")
        return None

# Function to save HTML content to a file with error handling
def save_html(html_content, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
    except Exception as e:
        print(f"Error saving HTML to {output_path}: {e}")

# Function to check if a file has already been processed
def is_already_processed(file_name, log_file):
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as log:
                return file_name in log.read().splitlines()
        return False
    except Exception as e:
        print(f"Error checking log file {log_file}: {e}")
        return False

# Function to log processed files with error handling
def log_processed_file(file_name, log_file):
    try:
        with open(log_file, 'a') as log:
            log.write(file_name + '\n')
    except Exception as e:
        print(f"Error logging processed file {file_name} to {log_file}: {e}")

# Function to download filings with error handling
def download_filings():
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
    save_dir = "annual_reports"
    os.makedirs(save_dir, exist_ok=True)

    for cik in cik_lookup:
        company_dir = os.path.join(save_dir, cik)
        os.makedirs(company_dir, exist_ok=True)
        
        # Check if filings already exist
        if os.listdir(company_dir):
            print(f"Skipping download for {cik}, filings already exist.")
            continue
        
        try:
            all_filings = CompanyFilings(
                cik_lookup=[cik],
                filing_type=filing_type,
                user_agent=user_agent,
                count=1
            )
            all_filings.save(company_dir)
            print(f"Downloaded filings for {cik} and saved in '{company_dir}'")
        except Exception as e:
            print(f"Error downloading filings for {cik}: {e}")

# Function to convert downloaded filings to HTML with logging
def convert_filings_to_html():
    directory = "annual_reports"
    output_directory = "parsed_reports_html"
    log_file = "processed_files.log"
    os.makedirs(output_directory, exist_ok=True)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                if is_already_processed(file, log_file):
                    print(f"Skipping {file}, already processed.")
                    continue

                file_path = os.path.join(root, file)
                content = read_file(file_path)
                parsed_content = generate_html(content)
                
                if parsed_content:
                    output_html_path = os.path.join(output_directory, os.path.relpath(file_path, directory)).replace(".txt", ".html")
                    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
                    save_html(parsed_content, output_html_path)
                    print(f"Saved to {output_html_path}")

                    log_processed_file(file, log_file)
                else:
                    print(f"Failed to parse and save {file_path}")

# Main function to run both download and conversion
def main():
    download_filings()
    convert_filings_to_html()

if __name__ == "__main__":
    main()
