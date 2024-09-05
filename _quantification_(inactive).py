import os
import pandas as pd

# Paths to input and output folders
input_folder_path = '/Users/vanessasutandar/Downloads/financial_reports/quantitative'
output_folder_path = '/Users/vanessasutandar/Downloads/financial_reports/output'

# Ensure the output directory exists
os.makedirs(output_folder_path, exist_ok=True)

# Function to calculate year-over-year growth rate
def calculate_growth_rate(data, column_name):
    if column_name not in data.columns:
        raise KeyError(f"Column '{column_name}' not found in data.")
    return (data[column_name].pct_change()) * 100

# Function to analyze one company and save the results
def analyze_company(company_name, balance_sheet_path, cash_flow_path, income_statement_path):
    # Load the data
    balance_sheet = pd.read_csv(balance_sheet_path)
    cash_flow = pd.read_csv(cash_flow_path)
    income_statement = pd.read_csv(income_statement_path)

    # Clean and prepare the data
    balance_sheet.set_index('Unnamed: 0', inplace=True)
    cash_flow.set_index('Unnamed: 0', inplace=True)
    income_statement.set_index('Unnamed: 0', inplace=True)
    
    balance_sheet = balance_sheet.transpose()
    cash_flow = cash_flow.transpose()
    income_statement = income_statement.transpose()

    # Initialize an empty dictionary to store results and check for required columns
    metrics = {}

    # Check and calculate metrics if the columns exist
    columns_found = True
    
    if 'Total Debt' in balance_sheet.columns:
        balance_sheet['Total Debt Growth'] = calculate_growth_rate(balance_sheet, 'Total Debt')
        metrics['Total Debt'] = balance_sheet['Total Debt']
        metrics['Total Debt Growth (%)'] = balance_sheet['Total Debt Growth']
    else:
        print(f"Warning: 'Total Debt' column not found for {company_name}")
        columns_found = False

    if 'Net Debt' in balance_sheet.columns:
        balance_sheet['Net Debt Growth'] = calculate_growth_rate(balance_sheet, 'Net Debt')
        metrics['Net Debt'] = balance_sheet['Net Debt']
        metrics['Net Debt Growth (%)'] = balance_sheet['Net Debt Growth']
    else:
        print(f"Warning: 'Net Debt' column not found for {company_name}")
        columns_found = False
    
    if 'Free Cash Flow' in cash_flow.columns:
        cash_flow['Free Cash Flow Growth'] = calculate_growth_rate(cash_flow, 'Free Cash Flow')
        metrics['Free Cash Flow'] = cash_flow['Free Cash Flow']
        metrics['Free Cash Flow Growth (%)'] = cash_flow['Free Cash Flow Growth']
    else:
        print(f"Warning: 'Free Cash Flow' column not found for {company_name}")
        columns_found = False
    
    if 'Net Income From Continuing Operation Net Minority Interest' in income_statement.columns:
        income_statement['Net Income Growth'] = calculate_growth_rate(income_statement, 'Net Income From Continuing Operation Net Minority Interest')
        metrics['Net Income'] = income_statement['Net Income From Continuing Operation Net Minority Interest']
        metrics['Net Income Growth (%)'] = income_statement['Net Income Growth']
    else:
        print(f"Warning: 'Net Income From Continuing Operation Net Minority Interest' column not found for {company_name}")
        columns_found = False

    # If required columns are not found, skip this company
    if not columns_found:
        return None
    
    # Combine key metrics into a single DataFrame for easier analysis
    combined_metrics = pd.DataFrame(metrics)
    
    # Save the results
    metrics_filename = os.path.join(output_folder_path, f"{company_name}_metrics.csv")
    combined_metrics.to_csv(metrics_filename, index=True)
    
    return combined_metrics

# List to store summary for each company
all_summaries = []

# Loop through each company folder and analyze
for filename in os.listdir(input_folder_path):
    if 'balance_sheet' in filename:
        company_name = filename.split('_')[0]
        balance_sheet_path = os.path.join(input_folder_path, f"{company_name}_balance_sheet.csv")
        cash_flow_path = os.path.join(input_folder_path, f"{company_name}_cash_flow.csv")
        income_statement_path = os.path.join(input_folder_path, f"{company_name}_income_statement.csv")

        summary = analyze_company(company_name, balance_sheet_path, cash_flow_path, income_statement_path)
        if summary is not None:
            all_summaries.append(summary)

# Only concatenate if there are valid summaries
if all_summaries:
    combined_summary = pd.concat(all_summaries, keys=[f"{company_name}" for company_name in os.listdir(input_folder_path) if 'balance_sheet' in company_name.split('_')[0]])
    combined_summary_filename = os.path.join(output_folder_path, "all_companies_summary.csv")
    combined_summary.to_csv(combined_summary_filename, index=True)
else:
    print("No valid summaries were generated due to missing columns.")
