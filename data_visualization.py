import pdfplumber
import re
import os
import pandas as pd

def extract_text_from_pdf(pdf_path):
    """Extract text from each page of the PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_fx_risk_analysis(text):
    """Parse the text to extract relevant data."""
    data = {}

    # Regular expressions with improved precision
    company_match = re.search(r'Company\s*:\s*([A-Za-z0-9\s]+)', text, re.IGNORECASE)
    overall_rating_match = re.search(r'(Overall\s+FX\s+)?Risk\s+Rating\s*:\s*\n?\s*([A-Za-z]+)', text, re.IGNORECASE)
    
    # Improved regex to handle ranges and comparative statements
    hedging_ratio_match = re.search(r'hedging\s+(coverage\s*(is\s*)?)?(applies|at|over|above|below)?\s*(approximately\s*)?([0-9]+%-[0-9]+%|[0-9]+%)', text, re.IGNORECASE)

    # Improved scenario matching to capture specific scenarios
    best_scenario_match = re.search(r'Best[-\s]?Case\s*:\s*([^\n]+)', text, re.IGNORECASE)
    worst_scenario_match = re.search(r'Worst[-\s]?Case\s*:\s*([^\n]+)', text, re.IGNORECASE)
    likely_scenario_match = re.search(r'Most[-\s]?Likely\s*:\s*([^\n]+)', text, re.IGNORECASE)

    translational_risk_match = re.search(r'Translational\s*Risk\s*[:\-\s]*\n?\s*(Falls under\s*)?([A-Za-z]+)\s*Risk', text, re.IGNORECASE)
    transactional_risk_match = re.search(r'Transactional\s*Risk\s*[:\-\s]*\n?.*?\b([A-Za-z]+\s+Risk)\b', text, re.IGNORECASE | re.DOTALL)
    economic_risk_match = re.search(r'Economic\s*Risk\s*:\s*([A-Za-z\s]+)', text, re.IGNORECASE)

    # Handling multiline revenue distribution
    currency_distribution_matches = re.findall(r'(EUR|JPY|GBP|CNH|AUD|USD|British Pound|Euro|Japanese Yen|Other currencies)\s*:\s*([0-9]+%)', text, re.IGNORECASE)
    
    hedging_strategy_type_match = re.search(r'Hedging\s*(Strategies|Strategy)\s*(involves|using)?\s*([\w\s,]+)', text, re.IGNORECASE)
    mitigation_strategies_match = re.search(r'Mitigation\s*Strategies\s*:\s*([^\n]+)', text, re.IGNORECASE)
    fx_sensitivity_analysis_match = re.search(r'Sensitivity\s*Analysis\s*:\s*([^\n]+)', text, re.IGNORECASE)
    industry_benchmarking_match = re.search(r'Industry\s*Benchmarking\s*:\s*([^\n]+)', text, re.IGNORECASE)
    historical_fx_impact_match = re.search(r'Historical\s*Data\s*Analysis\s*:\s*([^\n]+)', text, re.IGNORECASE)
    real_time_data_integration_match = re.search(r'Real[-\s]?Time\s*Data\s*Integration\s*:\s*([^\n]+)', text, re.IGNORECASE)

    # Filling the dictionary with extracted data
    data["Company"] = company_match.group(1).strip() if company_match else "Unknown"
    data["Overall_Rating"] = overall_rating_match.group(2).strip() if overall_rating_match else "Unknown"

    # Process the hedging ratio information
    data["Hedging_Ratio"] = hedging_ratio_match.group(5).strip() if hedging_ratio_match else "Unknown"

    # Ensure scenarios are captured without including additional data
    data["Best_Scenario"] = best_scenario_match.group(1).strip() if best_scenario_match else "Unknown"
    data["Worst_Scenario"] = worst_scenario_match.group(1).strip() if worst_scenario_match else "Unknown"
    data["Likely_Scenario"] = likely_scenario_match.group(1).strip() if likely_scenario_match else "Unknown"

    # Improved risk parsing
    data["Translational_Risk"] = translational_risk_match.group(2).strip() + " Risk" if translational_risk_match else "Unknown"
    data["Transactional_Risk"] = transactional_risk_match.group(1).strip() + " Risk" if transactional_risk_match else "Unknown"
    data["Economic_Risk"] = economic_risk_match.group(1).strip() if economic_risk_match else "Unknown"
    
    # Summarize currency revenue distribution
    if currency_distribution_matches:
        data["Distribution_of_Revenue_by_Currency"] = "; ".join([f"{curr}: {perc}" for curr, perc in currency_distribution_matches])
    else:
        data["Distribution_of_Revenue_by_Currency"] = None

    data["Hedging_Strategy_Type"] = hedging_strategy_type_match.group(3).strip() if hedging_strategy_type_match else "Unknown"
    data["Mitigation_Strategies"] = mitigation_strategies_match.group(1).strip() if mitigation_strategies_match else "Unknown"
    
    data["FX_Sensitivity_Analysis"] = fx_sensitivity_analysis_match.group(1).strip() if fx_sensitivity_analysis_match else "Unknown"
    data["Industry_Benchmarking"] = industry_benchmarking_match.group(1).strip() if industry_benchmarking_match else "Unknown"
    data["Historical_FX_Impact"] = historical_fx_impact_match.group(1).strip() if historical_fx_impact_match else "Unknown"
    
    data["Real_Time_Data_Integration"] = real_time_data_integration_match.group(1).strip() if real_time_data_integration_match else "Unknown"
    
    data["Additional_Currency_Exposures"] = None  # Placeholder, can be filled based on document specifics

    return data

def process_all_pdfs_in_directory(root_dir):
    """Process all PDFs in the given directory and subdirectories."""
    all_data = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(subdir, file)
                text = extract_text_from_pdf(pdf_path)
                data = parse_fx_risk_analysis(text)
                all_data.append(data)
    
    return all_data

def save_to_csv(data, csv_path):
    """Save the extracted data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

def main():
    root_dir = '/Users/vanessasutandar/Downloads/financial_reports/fx_risk_analysis_output'
    csv_path = '/Users/vanessasutandar/Downloads/financial_reports/fx_risk_analysis_output/FX_Risk_Analysis_Compiled.csv'
    
    # Process all PDFs in the root directory and its subdirectories
    all_data = process_all_pdfs_in_directory(root_dir)
    
    # Save all parsed data to a single CSV file
    save_to_csv(all_data, csv_path)
    print(f"Data saved to {csv_path}")

# Execute the script
main()

