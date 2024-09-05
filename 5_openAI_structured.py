import os
import re
import requests
from dotenv import load_dotenv
from pdf_generation import save_output_to_pdf
from docsx_generation import save_output_to_docx
import openai

# Load environment variables from the .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("Please set the OpenAI API key in environment variables")

# Initialize the OpenAI client with the API key
openai.api_key = openai_api_key

def preprocess_text(text):
    """
    Cleans and normalizes the input text for better model performance.
    """
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = re.sub(r'\bUSD\b', 'dollar', text)
    text = re.sub(r'\bEUR\b', 'euro', text)
    text = re.sub(r'\bJPY\b', 'yen', text)
    return text

def detect_currencies(text):
    """
    Detects all unique currencies mentioned in the text.
    """
    currency_pattern = re.compile(r'\b[A-Z]{3}\b')  # Regex pattern to match currency codes
    return list(set(currency_pattern.findall(text)))  # Extract unique currency codes found in the text

def get_real_time_exchange_rates(base_currency, target_currencies, api_url):
    """
    Fetches real-time exchange rates for the base currency against target currencies.
    """
    try:
        response = requests.get(f"{api_url}/{base_currency}")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()  # Parse the JSON response
        return {currency: data['rates'].get(currency, 'N/A') for currency in target_currencies}  # Map exchange rates to target currencies
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates: {e}")
        return {}

def retrieve_industry_benchmarks():
    """
    Retrieve industry benchmarking data for FX risk management.

    This function provides key industry benchmarks that serve as standard practices 
    for managing foreign exchange (FX) risk, including hedging strategies, 
    currency diversification, and risk mitigation techniques. These benchmarks 
    are essential for assessing a company's FX risk management practices against 
    industry norms.

    Returns:
        dict: A dictionary containing FX risk management benchmarks with descriptions.
    """
    return {
        "Benchmark_1": {
            "description": "Standard hedging ratio of 80%",
            "details": "In FX risk management, this benchmark refers to hedging 80% of "
                       "anticipated foreign currency exposure using financial instruments like forwards "
                       "or options to reduce potential losses from currency fluctuations."
        },
        "Benchmark_2": {
            "description": "Diversification into multiple currencies",
            "details": "This benchmark encourages diversification of assets or revenue streams "
                       "across multiple currencies to reduce dependency on any single currency's fluctuations."
        },
        "Benchmark_3": {
            "description": "Value-at-Risk (VaR) under 5%",
            "details": "A common benchmark in FX risk management where the company’s "
                       "potential loss from currency volatility should not exceed 5% of the portfolio "
                       "value, based on statistical analysis."
        },
        "Benchmark_4": {
            "description": "Use of natural hedging",
            "details": "Natural hedging involves structuring operations (e.g., sourcing "
                       "and selling in the same currency) to minimize FX exposure without the need for "
                       "financial instruments."
        },
        "Benchmark_5": {
            "description": "FX exposure monitoring every quarter",
            "details": "Regular monitoring and reporting of FX exposure to ensure that "
                       "management can respond quickly to currency volatility. A quarterly review is the "
                       "industry standard."
        },
        # Add more FX risk management benchmarks here
    }


def create_fx_risk_prompt(document_content, base_currency, exchange_rate_data, benchmarks, company_name):
    """
    Constructs a comprehensive prompt for FX risk analysis, emphasizing the quantification of specific currency exposures,
    risk categorization, and the integration of real-time data and industry benchmarks. The prompt includes detailed steps
    for both quantitative and qualitative assessments and provides conditional logic for handling incomplete data without
    using discouraging language.
    """
    return f"""
    You are a financial analyst specializing in FX (foreign exchange) risk management. Your task is to evaluate and rate 
    the FX risk presented in the following document for {company_name}, with a focus on providing actionable insights. 
    If certain data or details are missing, adjust your analysis accordingly without explicitly mentioning the absence.

    **Company Profile:**
    - Company Name: {company_name}
    - Industry: [Industry type]
    - Region: [Primary operational region]
    - Currency Exposure: [List key currencies the company is exposed to, the percentage of total exposure each represents, 
    and their respective impact on financial statements.]
    - Hedging Strategy: [Describe the primary hedging instruments used.]

    **Real-Time Exchange Rate Data:**
    - Base Currency: {base_currency}
    - Exchange Rates: {exchange_rate_data}

    **Industry Benchmarks:**
    {benchmarks}

    **Risk Categories and Their Impact:**
    Below is a risk categorization table defining low, moderate, and high risk levels for Translational, Transactional, and Economic risks. Please categorize the company's risk based on the available data and provide both quantitative and qualitative assessments. Adjust your analysis based on the data provided.

    | **Risk Type**      | **Low Risk**                                             | **Moderate Risk**                                            | **High Risk**                                               |
    |--------------------|----------------------------------------------------------|--------------------------------------------------------------|-------------------------------------------------------------|
    | **Translational Risk** | - Foreign operations < 10% of total revenue.<br>- Currency volatility < ±5%.<br>- Comprehensive hedging in place covering > 90% exposure. | - Foreign operations between 10%-30% of total revenue.<br>- Currency volatility ±5% to ±10%.<br>- Partial hedging in place covering 50%-90% exposure. | - Foreign operations > 30% of total revenue.<br>- Currency volatility > ±10%.<br>- Minimal or no hedging strategies. |
    | **Transactional Risk** | - < 10% of transactions in foreign currency.<br>- Hedging coverage > 90%.<br>- Low sensitivity to currency fluctuations. | - 10%-30% of transactions in foreign currency.<br>- Hedging coverage 50%-90%.<br>- Moderate sensitivity to currency fluctuations. | - > 30% of transactions in foreign currency.<br>- Minimal or no hedging coverage.<br>- High sensitivity to currency fluctuations. |
    | **Economic Risk** | - Operations primarily in stable economies (GDP growth > 2%, inflation < 3%).<br>- < 10% revenue from unstable economies.<br>- Insignificant impact from foreign economic changes. | - Operations in both stable and unstable economies (GDP growth 1%-2%, inflation 3%-5%).<br>- 10%-30% revenue from unstable economies.<br>- Moderate impact from foreign economic changes. | - Operations in unstable economies (GDP growth < 1%, inflation > 5%).<br>- > 30% revenue from unstable economies.<br>- Significant impact from foreign economic changes. |

    **Instructions:**
    1. **Risk Rating**: Provide an overall FX risk rating for the company (Low, Moderate, High). Clearly state which category each risk type (Translational, Transactional, Economic) falls under, and justify your rating with both numerical data and qualitative reasoning.
    2. **Quantification of Specific Currency Exposures**: Clearly quantify the company’s exposure to each key currency. Include detailed numerical data on the percentage of revenue, transactions, and costs associated with each currency. Highlight which currencies pose the greatest risk or benefit to the company’s financial statements.
    3. **Quantitative Assessment of FX Risk**: For each risk type (Translational, Transactional, Economic), provide a detailed quantitative analysis using the available data. Specify any assumptions or methodologies used, and if data is missing, adjust your analysis accordingly.
    4. **Qualitative Assessment of FX Risk**: Complement the quantitative analysis with a qualitative assessment. Discuss factors such as the company’s strategic positioning, industry context, management practices, and any external factors influencing the risk profile.
    5. **Analyze Historical Data**: Evaluate historical exchange rate trends and compare them with real-time data to assess potential impacts on the company’s financials.
    6. **Scenario and Sensitivity Analysis**:
        - **Best-Case Scenario Impact**: [Describe the best-case scenario impact]
        - **Worst-Case Scenario Impact**: [Describe the worst-case scenario impact]
        - **Most Likely Scenario Impact**: [Describe the most likely scenario impact]
        - Conduct a sensitivity analysis assessing how small changes in exchange rates impact key financial metrics. Identify which currencies are most sensitive and recommend strategies to hedge these currencies more aggressively.
    7. **Evaluate Hedging Strategy**:
        - **Hedging Ratio**: [Percentage of exposure hedged]
        - **Effectiveness**: [Assessment of hedging effectiveness]
        - **Advanced Instruments**: [Describe the use of advanced financial instruments]
        - Provide recommendations on improving hedging strategies, considering the latest exchange rate movements and specific currency exposures.
    8. **Industry Benchmarking**: Compare the company’s FX risk management strategies with industry benchmarks. Provide specific examples or metrics from competitors who have successfully managed FX risks. Identify gaps and recommend best practices.
    9. **Propose Mitigation Strategies**: Suggest additional mitigation strategies, such as increasing hedging coverage, diversifying currency exposure, or adopting sophisticated financial instruments. Prioritize these strategies based on potential impact and ease of implementation.
    10. **Integrate Real-Time Data**: Incorporate real-time exchange rate data into your analysis. Provide a detailed plan for integrating real-time data into future analyses, including potential vendors, technology platforms, or internal resources needed.
    11. **Forecast and Projections**: Utilize the real-time data to forecast future exchange rate movements and project their potential financial impact on the company. Provide projections across multiple scenarios (best-case, worst-case, most likely).

    **Enhanced Clustering-Friendly Tags**:
    - FX Risk Profile: [Transactional, Translational, Economic]
    - Industry Category: [Technology, Retail, Manufacturing, etc.]
    - Geographic Focus: [North America, Europe, Asia, Global]
    - Asset : Net worth
    - Risk Level: [Low, Moderate, High]
    - Hedging Strategy Type: [Basic, Intermediate, Advanced]
    - **Risk Drivers**: [Currency Volatility, Operational Exposure, Economic Stability]
    - **Scenario Outcomes**: [Best-Case, Worst-Case, Most Likely]
    - **Benchmark Comparison**: [Above Industry Average, At Industry Average, Below Industry Average]
    - **Specific Currency Exposures**: [USD, EUR, JPY, etc., with percentages]

    **Output Format**:
    - **Company Profile:**
    - Company Name: {company_name}
    - Industry: [Industry type]
    - Region: [Primary operational region]
    - Asset : [Net worth]
    - Currency Exposure: [List key currencies the company is exposed to, the percentage of total exposure each represents, 
    and their respective impact on financial statements.]
    - Hedging Strategy: [Describe the primary hedging instruments used.
    - **Risk Rating**: [Provide the overall FX risk rating here]
    - **Executive Summary**: [Provide a brief summary of the key risks, potential impacts, and recommended actions]
    - **Detailed Analysis**:
      1. Quantification of Specific Currency Exposures: [Provide detailed numerical data on currency exposures and their impacts]
      2. Quantitative Assessment: [Provide detailed quantitative analysis and numerical data]
      3. Qualitative Assessment: [Provide qualitative analysis, discussing strategic positioning and external influences]
      4. Historical Data Analysis: [Provide findings, including comparisons to industry peers or broader market trends]
      5. Scenario Analysis: [Provide findings across multiple scenarios]
      6. Sensitivity Analysis: [Provide findings, focusing on the most sensitive currencies]
      7. Hedging Strategies: [Provide detailed assessment and recommendations, including specific examples of financial instruments]
      8. Industry Benchmarking: [Provide comparison and recommendations, including specific examples from competitors]
      9. Mitigation Strategies: [Provide proposed strategies, prioritized based on impact and ease of implementation]
      10. Real-Time Data Integration: [Provide findings and a detailed plan for future integration]
      11. Forecast and Projections: [Provide projections across a range of scenarios]

    Please ensure the analysis is based on the data provided and avoid speculative conclusions. Adjust your analysis as necessary based on the available data.
    Please ensure the analysis is strictly based on the data provided or established industry standards. Avoid speculative conclusions or assumptions not supported by the document content or widely recognized best practices. Adjust your analysis as necessary based on the available data, and if certain data is insufficient, refrain from filling gaps with unverified information.


    **Document Content:**
    {document_content}
    """



def rate_fx_risk(document_content, base_currency, api_url, company_name):
    """
    Main function to analyze and rate FX risk using OpenAI's GPT.
    """
    # Preprocess text
    cleaned_content = preprocess_text(document_content)
    
    # Detect currencies mentioned in the document
    detected_currencies = detect_currencies(cleaned_content)
    if base_currency in detected_currencies:
        detected_currencies.remove(base_currency)  # Avoid redundant exchange rate retrieval for the base currency

    # Fetch real-time exchange rates for the detected currencies
    exchange_rate_data = get_real_time_exchange_rates(base_currency, detected_currencies, api_url)

    # Retrieve industry benchmarks for comparison
    benchmarks = retrieve_industry_benchmarks()

    # Create a prompt for GPT to generate the FX risk analysis
    fx_risk_prompt = create_fx_risk_prompt(cleaned_content, base_currency, exchange_rate_data, benchmarks, company_name)

    # Generate the analysis using OpenAI's GPT model
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert financial analyst specializing in FX risk management."},
                {"role": "user", "content": fx_risk_prompt}
            ]
        )
        return completion.choices[0].message['content']
    except openai.error.OpenAIError as e:
        return f"An error occurred while generating the response: {e}"

# Root directory containing the subfolders
input_root_directory = '/Users/vanessasutandar/Downloads/financial_reports/extracted_qualitative_data/'

# Root directory for saving the output
output_root_directory = '/Users/vanessasutandar/Downloads/financial_reports/fx_risk_analysis_output/'

# Create the output root directory if it doesn't exist
if not os.path.exists(output_root_directory):
    os.makedirs(output_root_directory)

# Iterate through each subfolder in the root directory
for company_folder in os.listdir(input_root_directory):
    company_folder_path = os.path.join(input_root_directory, company_folder)
    
    # Check if it's a directory
    if os.path.isdir(company_folder_path):
        # Create a corresponding output directory
        output_company_folder = os.path.join(output_root_directory, company_folder)
        if not os.path.exists(output_company_folder):
            os.makedirs(output_company_folder)
        
        # Iterate through each file in the company folder
        for filename in os.listdir(company_folder_path):
            file_path = os.path.join(company_folder_path, filename)
            
            # Only process text files
            if filename.endswith('.txt'):
                # Extract the company name from the folder name
                company_name = company_folder.upper()

                # Read the content of the file
                with open(file_path, 'r') as file:
                    fx_risk_document_content = file.read()

                # Define the API URL and base currency
                api_url = "https://api.exchangerate-api.com/v4/latest"
                base_currency = 'USD'

                # Perform FX risk rating
                fx_risk_rating = rate_fx_risk(fx_risk_document_content, base_currency, api_url, company_name)
                print(company_name)
                print(fx_risk_rating)

                # Define the output file paths
                pdf_output_path = os.path.join(output_company_folder, f"{company_name}_FX_Risk_Analysis_Report.pdf")
                docx_output_path = os.path.join(output_company_folder, f"{company_name}_FX_Risk_Analysis_Report.docx")

                # Save the output to PDF and DOCX in the corresponding folder
                save_output_to_pdf("FX Risk Analysis Report", fx_risk_rating, company_name, pdf_output_path)
                save_output_to_docx("FX Risk Analysis Report", fx_risk_rating, company_name, docx_output_path)