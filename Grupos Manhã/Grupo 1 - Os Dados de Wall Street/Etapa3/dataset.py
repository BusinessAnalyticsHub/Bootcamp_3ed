import pandas as pd
import numpy as np
import yfinance as yf

def build_dataset(index_ticker, stock_tickers, start_date, end_date, max_missing_days=30):
    """
    Builds a dataset by downloading, cleaning, and calculating variance and cumulative returns for a list of stock tickers.

    Parameters:
    - index_ticker: Ticker symbol for the index to include in the dataset
    - stock_tickers: List of stock tickers to include in the dataset
    - start_date: Starting date for the historical data download
    - end_date: Ending date for the historical data download
    - max_missing_days: Maximum allowed consecutive days of missing data per stock

    Returns:
    - DataFrames with historical stock variance and cumulative returns
    """
    # Download data
    values = download_data(index_ticker, stock_tickers, start_date, end_date)
    values = clean_data(values, max_missing_days)

    variance, cumulative_returns = calculate_variance_and_cumulative_returns(values)

    variance_filename = f"./data/stock_variance_{index_ticker}.csv"
    variance.to_csv(variance_filename)
    print(f"Stock variance saved to {variance_filename}")

    cumulative_returns_filename = f"./data/stock_cumulative_returns_{index_ticker}.csv"
    cumulative_returns.to_csv(cumulative_returns_filename)
    print(f"Stock cumulative returns saved to {cumulative_returns_filename}")

    return values, variance, cumulative_returns

def download_data(index_ticker, stock_tickers, start_date, end_date):
    """
    Downloads historical adjusted close prices for an index and a list of stocks.

    Parameters:
    - index_ticker: Ticker symbol for the index
    - stock_tickers: List of stock tickers to download
    - start_date: Starting date for data download
    - end_date: Ending date for data download

    Returns:
    - DataFrame containing the adjusted close prices for all tickers
    """
    try:
        all_tickers = [index_ticker] + stock_tickers
        data = yf.download(all_tickers, start=start_date, end=end_date)['Adj Close']
        data.index = data.index.strftime('%Y-%m-%d')
        print("Data downloaded successfully.")
        return data
    except Exception as e:
        print(f"An error occurred on data download: {e}")
        return None

def clean_data(data, max_missing_days=30):
    """
    Cleans stock data by removing stocks with prolonged missing data and interpolating gaps.

    Parameters:
    - data: DataFrame with stock price data
    - max_missing_days: Maximum allowed consecutive missing days per stock

    Returns:
    - Cleaned DataFrame with interpolated data and stocks with prolonged gaps removed
    """
    try:
        data = remove_stocks_with_prolonged_missing_data(data, days_limit=max_missing_days)
        data = data.interpolate(method='linear')
        print("Data cleaned successfully.")
        return data
    except Exception as e:
        print(f"An error occurred on clean data: {e}")
        return None

def remove_stocks_with_prolonged_missing_data(data, days_limit=30):
    """
    Removes stocks with consecutive missing data days exceeding the specified limit.

    Parameters:
    - data: DataFrame with stock price data
    - days_limit: Maximum allowed consecutive missing days per stock

    Returns:
    - DataFrame with only stocks that meet the missing data criteria
    """
    def check_consecutive_nans(column):
        nan_seq = column.isna().astype(int)
        max_nan_streak = nan_seq.groupby((nan_seq != nan_seq.shift()).cumsum()).transform('sum').max()
        return max_nan_streak >= days_limit

    try:
        valid_columns = [col for col in data.columns if not check_consecutive_nans(data[col])]
        filtered_data = data[valid_columns]
        print(f"Removed stocks: {set(data.columns) - set(valid_columns)}")
        return filtered_data
    except Exception as e:
        print(f"An error occurred to remove stocks with consecutive missing data: {e}")
        return None

def calculate_variance_and_cumulative_returns(data):
    """
    Calculates daily variance for the given stock data.

    Parameters:
    - data: DataFrame with cleaned stock price data

    Returns:
    - DataFrame with daily variance for each stock
    - DataFrame with cumulative returns for each stock
    """
    try:
        variance = data.pct_change()
        variance = variance.iloc[1:, :]
        cumulative_returns = (1 + variance).cumprod()
        return variance, cumulative_returns
    except Exception as e:
        print(f"An error occurred in calculate variance and cumulative returns: {e}")
        return None, None

def get_tickers(csv_file):
    """
    Reads a CSV file and extracts stock tickers from the 'Symbol' column.

    Parameters:
    - csv_file: Path to the CSV file containing stock tickers

    Returns:
    - List of stock ticker symbols
    """
    try:
        df = pd.read_csv(csv_file)
        symbols = df['Symbol'].tolist()
        print(symbols)
        return symbols
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        return []
