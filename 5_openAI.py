import os
import re
import requests
from dotenv import load_dotenv
from pdf_generation import save_output_to_pdf
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
    currency_pattern = re.compile(r'\b[A-Z]{3}\b')
    return list(set(currency_pattern.findall(text)))

def get_real_time_exchange_rates(base_currency, target_currencies, api_url):
    """
    Fetches real-time exchange rates for the base currency against target currencies.
    """
    try:
        response = requests.get(f"{api_url}/{base_currency}")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        return {currency: data['rates'].get(currency, 'N/A') for currency in target_currencies}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates: {e}")
        return {}

def retrieve_industry_benchmarks():
    """
    Placeholder function to retrieve industry benchmarking data.
    """
    return {
        "Benchmark_1": "Standard hedging ratio of 80%",
        "Benchmark_2": "Diversification into multiple currencies",
        # Add more industry benchmarks here
    }

def create_fx_risk_prompt(document_content, base_currency, exchange_rate_data, benchmarks):
    """
    Constructs the prompt for FX risk analysis using real-time exchange rate data and industry benchmarks.
    """
    return f"""
    You are a financial analyst with expertise in FX (foreign exchange) risk management.
    Your task is to evaluate and rate the FX risk presented in the following document.

    **Real-Time Exchange Rate Data:**
    - Base Currency: {base_currency}
    - Exchange Rates: {exchange_rate_data}

    **Industry Benchmarks:**
    {benchmarks}

    **Instructions:**
    1. **Risk Rating**: Provide an overall FX risk rating for the company (Low, Moderate, High). Base this on the quantified risks and your analysis.
    2. **Quantify FX Risk**: Identify and quantify specific FX risks mentioned in the document. Provide assumptions or methodologies used to arrive at these figures. Use the real-time numerical data to support your findings.
    3. **Analyze Historical Data**: Evaluate historical exchange rate trends, comparing them with real-time data to assess potential impacts on the company’s financials. Contextualize these impacts by comparing them to industry peers or broader market trends.
    4. **Scenario Analysis**: Conduct an enhanced scenario analysis that includes potential geopolitical events, economic downturns, and shifts in trade policies, alongside percentage changes in exchange rates. Provide a range of scenarios (best-case, worst-case, most likely) to give a nuanced view of potential outcomes.
    5. **Sensitivity Analysis**: Perform a sensitivity analysis, assessing how small changes in exchange rates impact key financial metrics. Identify which currencies are most sensitive to adverse changes and provide targeted recommendations on hedging these currencies more aggressively.
    6. **Assess and Recommend Hedging Strategies**: Evaluate the effectiveness of current hedging strategies. Provide detailed examples of how different financial instruments could be implemented, including potential costs and benefits. Suggest improvements or new strategies to mitigate FX risks, considering the latest exchange rate movements.
    7. **Industry Benchmarking**: Compare the company’s FX risk management strategies with industry benchmarks. Provide specific examples or metrics from competitors who have successfully managed FX risks. Identify gaps and provide recommendations to align with best practices in the industry.
    8. **Propose Mitigation Strategies**: Suggest additional mitigation strategies, such as increasing hedging coverage, diversifying currency exposure, or adopting sophisticated financial instruments. Prioritize these strategies based on potential impact and ease of implementation, and recommend a phased approach if applicable.
    9. **Integrate Real-Time Data**: Incorporate real-time exchange rate data into your analysis, examining how current rates might influence near-term financial outcomes. Provide a detailed plan or roadmap for integrating real-time data into future analyses, including potential vendors, technology platforms, or internal resources needed.
    10. **Forecast and Projections**: Utilize the real-time data to forecast future exchange rate movements and project their potential financial impact on the company. Acknowledge the speculative nature of projections, and consider providing a range of scenarios (best-case, worst-case, most likely).

    **Output Format**:
    - **Risk Rating**: [Provide the overall FX risk rating here]
    - **Executive Summary**: [Provide a brief summary of the key risks, potential impacts, and recommended actions]
    - **Detailed Analysis**:
      1. Quantified FX Risks: [Provide detailed findings, including methodologies and assumptions]
      2. Historical Data Analysis: [Provide findings, including comparisons to industry peers or broader market trends]
      3. Scenario Analysis: [Provide findings across multiple scenarios]
      4. Sensitivity Analysis: [Provide findings, focusing on the most sensitive currencies]
      5. Hedging Strategies: [Provide detailed assessment and recommendations, including specific examples of financial instruments]
      6. Industry Benchmarking: [Provide comparison and recommendations, including specific examples from competitors]
      7. Mitigation Strategies: [Provide proposed strategies, prioritized based on impact and ease of implementation]
      8. Real-Time Data Integration: [Provide findings and a detailed plan for future integration]
      9. Forecast and Projections: [Provide projections across a range of scenarios]

    Please ensure the analysis is based on the data provided and avoid speculative conclusions.
    **Document Content:**
    {document_content}
    """

def rate_fx_risk(document_content, base_currency, api_url):
    """
    Main function to analyze and rate FX risk using OpenAI's GPT.
    """
    # Preprocess text
    cleaned_content = preprocess_text(document_content)
    
    # Detect currencies
    detected_currencies = detect_currencies(cleaned_content)
    if base_currency in detected_currencies:
        detected_currencies.remove(base_currency)

    # Fetch real-time exchange rates
    exchange_rate_data = get_real_time_exchange_rates(base_currency, detected_currencies, api_url)

    # Retrieve industry benchmarks
    benchmarks = retrieve_industry_benchmarks()

    # Create prompt
    fx_risk_prompt = create_fx_risk_prompt(cleaned_content, base_currency, exchange_rate_data, benchmarks)

    # Generate response
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

# Main Execution
file_path = '/Users/vanessasutandar/Downloads/financial_reports/extracted_data/amzn/amzn_2024_fx_risk_text.txt'
with open(file_path, 'r') as file:
    fx_risk_document_content = file.read()

api_url = "https://api.exchangerate-api.com/v4/latest"
base_currency = 'USD'

# Perform FX risk rating
fx_risk_rating = rate_fx_risk(fx_risk_document_content, base_currency, api_url)
print(fx_risk_rating)

# Save the output to PDF
save_output_to_pdf("FX Risk Analysis Report", fx_risk_rating, "FX_Risk_Report")
