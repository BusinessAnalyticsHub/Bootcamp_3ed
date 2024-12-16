from indextracking import IndexTracking
from dataset import build_dataset, get_tickers
import pandas as pd
import os
import json

def save_portfolio(result, filename):
    data = {
        'Error': result['error'],
        'Portfolio Weights': json.dumps(result['weights']),
        'Train Tracking Error': result['performance']['train_performance']['tracking_error'],
        'Train RMSE': result['performance']['train_performance']['root_mean_squared_error'],
        'Train Correlation': result['performance']['train_performance']['correlation'],
        'Test Tracking Error': result['performance']['test_performance']['tracking_error'],
        'Test RMSE': result['performance']['test_performance']['root_mean_squared_error'],
        'Test Correlation': result['performance']['test_performance']['correlation'],
        'Optimization Time': result['optimization_time'],
        'Mip Gap': result['mip_gap'],
        'Start train': result['dates']['train']['start'],
        'End train': result['dates']['train']['end'],
        'Start test': result['dates']['test']['start'],
        'End test': result['dates']['test']['end'],
    }
    
    df = pd.DataFrame([data])
    df.to_csv(filename, index=False)

def build_dataset_from_tickers(index_ticker):
    if os.path.exists(f'./data/stock_cumulative_returns_{index_ticker}.csv') and os.path.exists(f'./data/stock_variance_{index_ticker}.csv'):
        return
    stock_tickers = get_tickers(f'./data/tickers_{index_ticker}.csv')
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    build_dataset(index_ticker, stock_tickers, start_date, end_date)

def train_to_define_k(index_ticker, portfolio_size):
    if(index_ticker=='^BVSP'):
        ticker_name = 'bvsp'
        data = pd.read_csv('./data/stock_variance_^BVSP.csv', index_col=0)
        index_data = data[index_ticker]
        stock_data = data.drop(columns=[index_ticker])
    elif(index_ticker=='^OEX'):
        ticker_name = 'sp100'
        data = pd.read_csv('./data/stock_variance_^OEX.csv', index_col=0)
        index_data = data[index_ticker]
        stock_data = data.drop(columns=[index_ticker])
    else:
        print('ERROR')
        return
    
    time_limit = 30

    start_date_dataset = "2023-01-01"
    end_date_dataset = "2023-12-31"
    train_start = start_date_dataset
    train_end = "2023-03-31"
    test_start = "2023-04-01"
    test_end = end_date_dataset

    model = IndexTracking(stock_data=stock_data, index_data=index_data)
    model.split_data(train_start=train_start, train_end=train_end, test_start=test_start, test_end=test_end)
    portfolio = model.create_portfolio(portfolio_size=portfolio_size, time_limit=time_limit, initial_solution=True)

    filename = f'./portfolios/define_k/{ticker_name}_{portfolio_size}k.csv'

    save_portfolio(portfolio, filename=filename)

def train(index_ticker, portfolio_size=10, max_iterations=None, time_limit=None, initial_solution=False, rebalance=False):
    if(index_ticker=='^BVSP'):
        ticker_name = 'bvsp'
        data = pd.read_csv('./data/stock_variance_^BVSP.csv', index_col=0)
        index_data = data[index_ticker]
        stock_data = data.drop(columns=[index_ticker])
    elif(index_ticker=='^OEX'):
        ticker_name = 'sp100'
        data = pd.read_csv('./data/stock_variance_^OEX.csv', index_col=0)
        index_data = data[index_ticker]
        stock_data = data.drop(columns=[index_ticker])
    else:
        print('ERROR')
        return
    
    if(not rebalance):
        start_date_dataset = "2023-01-01"
        end_date_dataset = "2023-12-31"
        train_start = start_date_dataset
        train_end = "2023-03-31"
        test_start = "2023-04-01"
        test_end = end_date_dataset
    elif(rebalance):
        start_date_dataset = "2023-07-01"
        end_date_dataset = "2023-12-31"
        train_start = start_date_dataset
        train_end = "2023-09-30"
        test_start = "2023-10-01"
        test_end = end_date_dataset

    model = IndexTracking(stock_data=stock_data, index_data=index_data)
    model.split_data(train_start=train_start, train_end=train_end, test_start=test_start, test_end=test_end)
    portfolio = model.create_portfolio(portfolio_size=portfolio_size, max_iterations=max_iterations, time_limit=time_limit, initial_solution=initial_solution)

    if(initial_solution and not rebalance):
        filename = f'./portfolios/results/initial_{ticker_name}_{portfolio_size}stocks.csv'
    elif(not initial_solution and not rebalance):
        filename = f'./portfolios/results/regular_{ticker_name}_{portfolio_size}stocks.csv'
    elif(initial_solution and rebalance):
        filename = f'./portfolios/results/initial_rebalance_{ticker_name}_{portfolio_size}stocks.csv'
    elif(not initial_solution and rebalance):
        filename = f'./portfolios/results/initial_rebalance_{ticker_name}_{portfolio_size}stocks.csv'

    save_portfolio(portfolio, filename=filename)

def main():
    bvsp_index_ticker = '^BVSP'
    sp100_index_ticker = '^OEX'

    max_iterations = 10**(6)
    time_limit = 30

    build_dataset_from_tickers(bvsp_index_ticker)
    build_dataset_from_tickers(sp100_index_ticker)

    train(bvsp_index_ticker, portfolio_size=10, time_limit=30)
    train(sp100_index_ticker, portfolio_size=10, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=20, time_limit=30)
    train(sp100_index_ticker, portfolio_size=20, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=30, time_limit=30)
    train(sp100_index_ticker, portfolio_size=30, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=10, initial_solution=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=10, initial_solution=True, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=20, initial_solution=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=20, initial_solution=True, time_limit=30)
    
    train(bvsp_index_ticker, portfolio_size=30, initial_solution=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=30, initial_solution=True, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=10, rebalance=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=10, rebalance=True, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=20, rebalance=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=20, rebalance=True, time_limit=30)
    
    train(bvsp_index_ticker, portfolio_size=30, rebalance=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=30, rebalance=True, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=10, initial_solution=True, rebalance=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=10, initial_solution=True, rebalance=True, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=20, initial_solution=True, rebalance=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=20, initial_solution=True, rebalance=True, time_limit=30)

    train(bvsp_index_ticker, portfolio_size=30, initial_solution=True, rebalance=True, time_limit=30)
    train(sp100_index_ticker, portfolio_size=30, initial_solution=True, rebalance=True, time_limit=30)
    


if __name__ == "__main__":
    main()