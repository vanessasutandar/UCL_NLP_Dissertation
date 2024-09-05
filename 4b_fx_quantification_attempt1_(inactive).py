import os
import logging
import pandas as pd

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base directory containing preprocessed data and to save FX risk analysis results
BASE_OUTPUT_DIR = '/Users/vanessasutandar/Downloads/financial_reports'
PROCESSED_DATA_DIR = os.path.join(BASE_OUTPUT_DIR, 'processed_data')
FX_EXPOSURE_DIR = os.path.join(BASE_OUTPUT_DIR, 'fx_exposure')
os.makedirs(FX_EXPOSURE_DIR, exist_ok=True)

# List of tickers to process data for
TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "FB", "TSLA", "BRK-B", "JNJ", "JPM", "V",
           "PG", "MA", "UNH", "HD", "NVDA", "PFE", "VZ", "WMT", "DIS", "KO", "NKE",
           "PEP", "INTC", "CSCO", "MRK", "ABBV", "CVX", "XOM", "CMCSA", "NFLX",
           "CRM", "ADBE", "MDT", "COST", "QCOM", "BMY", "GS", "MS", "BA", "IBM",
           "AMGN", "T", "CAT", "LMT", "AXP", "SBUX", "F", "GM", "MMM", "RTX"]

def calculate_fx_exposure(df):
    """Calculate FX exposure based on the available data."""
    required_columns = ['foreign_currency_assets', 'foreign_currency_liabilities', 'foreign_currency_revenue', 'foreign_currency_expenses']
    
    # Check if all required columns are in the dataframe
    if all(col in df.columns for col in required_columns):
        df['net_foreign_currency_exposure'] = (
            df['foreign_currency_assets'] - df['foreign_currency_liabilities'] +
            df['foreign_currency_revenue'] - df['foreign_currency_expenses']
        )
    else:
        missing_columns = [col for col in required_columns if col not in df.columns]
        logging.warning(f"Necessary columns for FX risk analysis are missing in the data: {missing_columns}")
    return df

def process_and_save_fx_exposure(ticker, processed_data_dir, fx_exposure_dir):
    """Process the preprocessed data to calculate and save FX exposure for a company."""
    file_path = os.path.join(processed_data_dir, ticker.lower(), f'{ticker.lower()}_financial_data.csv')
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = calculate_fx_exposure(df)

        if 'net_foreign_currency_exposure' in df.columns:
            fx_df = df[['date', 'net_foreign_currency_exposure']]
            fx_company_dir = os.path.join(fx_exposure_dir, ticker.lower())
            os.makedirs(fx_company_dir, exist_ok=True)
            fx_df.to_csv(os.path.join(fx_company_dir, f'{ticker.lower()}_fx_exposure.csv'), index=False)
            logging.info(f"Processed and saved FX exposure data for {ticker}")
        else:
            logging.warning(f"No FX exposure data available for {ticker}")
    else:
        logging.warning(f"No processed data available for {ticker}")

def main():
    # Process and save FX exposure data per company
    for ticker in TICKERS:
        process_and_save_fx_exposure(ticker, PROCESSED_DATA_DIR, FX_EXPOSURE_DIR)

if __name__ == "__main__":
    main()
