import pandas as pd

# Load the provided CSV files from the specified path
balance_sheet_path = '/Users/vanessasutandar/Downloads/financial_reports/quantitative/AAPL_balance_sheet.csv'
cash_flow_path = '/Users/vanessasutandar/Downloads/financial_reports/quantitative/AAPL_cash_flow.csv'
income_statement_path = '/Users/vanessasutandar/Downloads/financial_reports/quantitative/AAPL_income_statement.csv'

balance_sheet = pd.read_csv(balance_sheet_path)
cash_flow = pd.read_csv(cash_flow_path)
income_statement = pd.read_csv(income_statement_path)

# Extract relevant financial data from the dataframes
# Balance Sheet
total_debt = balance_sheet.loc[balance_sheet['Unnamed: 0'] == 'Total Debt', '2023-09-30'].values[0]
net_debt = balance_sheet.loc[balance_sheet['Unnamed: 0'] == 'Net Debt', '2023-09-30'].values[0]

# Cash Flow Statement
free_cash_flow = cash_flow.loc[cash_flow['Unnamed: 0'] == 'Free Cash Flow', '2023-09-30'].values[0]

# Income Statement
net_income = income_statement.loc[income_statement['Unnamed: 0'] == 'Net Income From Continuing Operation Net Minority Interest', '2023-09-30'].values[0]

# Assumptions for foreign currency exposure
foreign_debt_percentage = 0.50
foreign_income_percentage = 0.30
foreign_cash_flow_percentage = 0.40

# Assumed depreciation of foreign currency
depreciation_rate = 0.05

# Calculate foreign currency-denominated amounts
foreign_currency_debt = total_debt * foreign_debt_percentage
foreign_currency_income = net_income * foreign_income_percentage
foreign_currency_cash_flow = free_cash_flow * foreign_cash_flow_percentage

# Calculate the impact of 5% depreciation of foreign currency
impact_debt = foreign_currency_debt * depreciation_rate
impact_income = foreign_currency_income * depreciation_rate
impact_cash_flow = foreign_currency_cash_flow * depreciation_rate

# Output the results
impact_results = {
    "Foreign Currency-Denominated Debt (USD)": foreign_currency_debt,
    "Impact on Debt (5% Depreciation) (USD)": impact_debt,
    "Foreign Currency-Denominated Income (USD)": foreign_currency_income,
    "Impact on Income (5% Depreciation) (USD)": impact_income,
    "Foreign Currency-Denominated Cash Flow (USD)": foreign_currency_cash_flow,
    "Impact on Cash Flow (5% Depreciation) (USD)": impact_cash_flow,
}

print(impact_results)
