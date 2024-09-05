import os
import fitz  # PyMuPDF
import pandas as pd

def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def parse_fx_risk_analysis(text):
    company_info = {
        "Company": extract_value(text, "Company:"),
        "Category": extract_value(text, "Category:"),
        "Sub-Category": extract_value(text, "Sub-Category:"),
        "Overall_Rating": extract_value(text, "Overall FX Risk Rating"),
        "Hedging_Ratio": extract_value(text, "Hedging Ratio"),
        "Best_Scenario_number": extract_value(text, "Best-Case Scenario"),
        "Best_Scenario_text": extract_value(text, "Best-Case Scenario Impact"),
        "Worst_Scenario_number": extract_value(text, "Worst-Case Scenario"),
        "Worst_Scenario_text": extract_value(text, "Worst-Case Scenario Impact"),
        "Likely_Scenario_number": extract_value(text, "Most Likely Scenario"),
        "Likely_Scenario_text": extract_value(text, "Most Likely Scenario Impact"),
        "Translational_Rating": extract_value(text, "Translational Risk"),
        "Translational_Reason": extract_value(text, "Assessment"),
        "Transactional_Rating": extract_value(text, "Transactional Risk"),
        "Transactional_Reason": extract_value(text, "Assessment"),
        "Economic_Category": extract_value(text, "Economic Risk"),
        "Economic_Reason": extract_value(text, "Assessment"),
        "Distribution_of_Revenue_by_Currency": extract_value(text, "Key Currencies Exposure"),
        "Hedging_Strategy_Type": extract_value(text, "Hedging Ratio"),
        "Mitigation_Strategies": extract_value(text, "Mitigation Strategies"),
        "FX_Sensitivity_Analysis": extract_value(text, "Sensitivity Analysis"),
        "Industry_Benchmarking": extract_value(text, "Industry Benchmarking"),
        "Historical_FX_Impact": extract_value(text, "Historical Data Analysis"),
        "Real_Time_Data_Integration": extract_value(text, "Real-Time Data Integration"),
    }
    return company_info

def extract_value(text, label):
    try:
        start = text.index(label) + len(label)
        end = text.index("\n", start)
        return text[start:end].strip()
    except ValueError:
        return "No Information/Not Found"

def process_all_pdfs(base_directory):
    data = []
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                text = extract_text_from_pdf(pdf_path)
                company_info = parse_fx_risk_analysis(text)
                company_info['Company'] = os.path.basename(root)  # Set company name from the folder name
                data.append(company_info)
    
    df = pd.DataFrame(data)
    output_path = os.path.join(base_directory, "FX_Risk_Analysis_Compiled_coba_coba.csv")
    df.to_csv(output_path, index=False)
    print(f"Data compiled and saved to {output_path}")

# Example usage:
base_directory = "/Users/vanessasutandar/Downloads/financial_reports/fx_risk_analysis_output"
process_all_pdfs(base_directory)
