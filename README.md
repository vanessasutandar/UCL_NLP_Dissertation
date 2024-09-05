# UCL_NLP_Dissertation

This repository contains the code and methodology for the UCL NLP Dissertation, focused on the application of Natural Language Processing (NLP) techniques to analyze Foreign Exchange (FX) risk from financial filings, using web scraping and machine learning models.

## Abstract

In the era of globalization, businesses face increasing exposure to Foreign Exchange (FX) risk, which can significantly impact profitability and financial stability. This project uses NLP and web scraping techniques to extract relevant information from SEC filings (10-Q), enabling companies to mitigate FX risks. The data-driven approach enhances FX risk prediction and management strategies, benefiting businesses, policymakers, and investors.

## Project Structure

📁 UCL_NLP_Dissertation ├── 1_download_fillings.py # Downloads 10-Q filings from the SEC ├── 2_convert_ixbrl_to_html.py # Converts IXBRL files to HTML for text extraction ├── 2b_descriptive.py # Performs descriptive analysis on extracted data ├── 3_extract_qualitative_1.py # Extracts qualitative FX-related data from filings ├── 3_extract_qualitative.py # Additional qualitative data extraction ├── 4a_extract_table_attempt1_(inactive).py # First attempt at extracting table data (inactive) ├── 4a_extract_table_attempt2_(inactive).py # Second attempt at extracting table data (inactive) ├── 5_openAI_structured.py # GPT-based FX risk analysis using structured prompts ├── 6_compiled_document.py # Compiles extracted FX data into a final report └── README.md # Project documentation (this file)


## Installation

### Requirements

To run the project, you'll need the following dependencies:

- `requests`
- `beautifulsoup4`
- `lxml`
- `pandas`
- `openai`
- `secedgar`
- `PyMuPDF`
- `re`

You can install them using the following command: ```bash
pip install -r requirements.txt`


###  OpenAI API Key
To use the OpenAI models, you need to set your OPENAI_API_KEY as an environment variable for safety and security:

export OPENAI_API_KEY='your_openai_api_key'

Alternatively, you can use a .env file to securely store your API key. Add this line to the .env file:

OPENAI_API_KEY='your_openai_api_key'

Then load the environment variables in your Python code using:

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


 ## Running the Code

Follow these steps to run the project in sequence:

1. Download Financial Filings
The first step is to download the 10-Q financial filings using the SEC Edgar API.

python 1_download_fillings.py

2. Convert IXBRL to HTML
Once the filings are downloaded, you will convert IXBRL format to HTML.

python 2_convert_ixbrl_to_html.py

3. Extract Qualitative Data
Run the script to extract qualitative FX-related data from the HTML filings.

python 3_extract_qualitative_1.py

4. Analyze Data Using GPT
Use the OpenAI GPT model to analyze FX risk in the filings.

python 5_openAI_structured.py

5. Compile Data and Generate Reports
Finally, compile all extracted data into a report.
python 6_compiled_document.py

## Disclaimer
Make sure to follow SEC guidelines when scraping data and respect the rate limits. Use your OpenAI API responsibly and ensure that you do not expose sensitive API keys in your codebase.


## License
This project is licensed under the MIT License. See the LICENSE file for more details.

This README provides a structured and clear explanation of your project, how to run it, and some best practices regarding the usage of sensitive API keys.







