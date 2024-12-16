import numpy as np
import gurobipy as gp
from gurobipy import GRB
import time

class IndexTracking:
    # Portfolio Configuration Constants
    DEFAULT_PORTFOLIO_SIZE = 15
    DEFAULT_TRAIN_RATIO = 0.7
    DEFAULT_MAX_ITERATIONS = 100000
    DEFAULT_TIME_LIMIT = 30
    DEFAULT_MULTI_START_ITERATIONS = 10

    def __init__(self, stock_data, index_data):
        """
        Initialize the IndexTracking class
        
        Parameters:
        - stock_data: Full DataFrame with stock returns
        - index_data: Full array or Series with index returns
        """
        self.full_data = {
            'stock': stock_data,
            'index': index_data,
        }
        
        # Default train-test split
        self.data = {
            'train': {
                'stock': None,
                'index': None,
            },
            'test': {
                'stock': None,
                'index': None,
            }
        }

        self.dates = {
            'train': {
                'start': None,
                'end': None
            },
            'test': {
                'start': None,
                'end': None
            }
        }

        self.portfolio = {
            'error': None,
            'weights': None,
            'performance': None,
            'dates': self.dates,
            'optimization_time': None
        }
    
    def split_data(self, train_start, train_end, test_start, test_end):
        """
        Split data into training and testing sets

        Parameters:
        - train_start: Start date for the training data
        - train_end: End date for the training data
        - test_start: Start date for the testing data
        - test_end: End date for the testing data
        """
        self.data['train']['stock'] = self.full_data['stock'].loc[train_start:train_end]
        self.data['test']['stock'] = self.full_data['stock'].loc[test_start:test_end]

        self.data['train']['index'] = self.full_data['index'].loc[train_start:train_end]
        self.data['test']['index'] = self.full_data['index'].loc[test_start:test_end]

        self.dates['train']['start'] = train_start
        self.dates['train']['end'] = train_end

        self.dates['test']['start'] = test_start
        self.dates['test']['end'] = test_end
    
    def create_portfolio(self, 
                         portfolio_size=DEFAULT_PORTFOLIO_SIZE, 
                         max_iterations=None,
                         time_limit=None,
                         initial_solution=False):
        """
        Create an optimized portfolio that tracks the index
        
        Parameters:
        - portfolio_size: Number of stocks to select
        - max_iterations: Maximum Gurobi iterations
        - time_limit: Time limit for Gurobi
        - initial_solution: Whether to use our initial solution to warm start the optimization

        Returns:
        - Dictionary with portfolio weights and tracking error
        """
        if self.data['train']['stock'] is None:
            print('Error')
            return

        stock_data = self.data['train']['stock']
        index_data = self.data['train']['index']

        I = np.array(stock_data.columns)
        T = range(len(stock_data))
        r = {(t, i): stock_data.iloc[t][i] for t in T for i in I}
        R = np.array(index_data)
        k = portfolio_size

        model = gp.Model("TrackingPortfolio")
        w = model.addVars(I, lb=0, ub=1, name="w")  # Stock weights
        z = model.addVars(I, vtype=GRB.BINARY, name="z")  # Stock selection

        model.setObjective(
            (1 / len(T)) * gp.quicksum(
                (gp.quicksum(w[i] * r[t, i] for i in I) - R[t]) ** 2 for t in T
            ),
            GRB.MINIMIZE
        )

        model.addConstr(gp.quicksum(w[i] for i in I) == 1, "WeightSum")
        model.addConstrs((w[i] <= z[i] for i in I), "WeightBinding")
        model.addConstr(gp.quicksum(z[i] for i in I) == k, "MaxStocks")

        if(max_iterations != None):
            model.setParam(GRB.Param.IterationLimit, max_iterations)
        
        if(time_limit != None):
            model.setParam(GRB.Param.TimeLimit, 60*time_limit)

        start = time.time()

        if(initial_solution):
            w_initial, z_initial = self.generate_initial_solution(portfolio_size)
            model.setAttr("Start", w, w_initial)
            model.setAttr("Start", z, z_initial)

        model.optimize()

        end = time.time()

        if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
            error = model.ObjVal
            weights = {i: w[i].x for i in I if z[i].x}
            performance = self.compare_train_test_performance(weights)
            optimization_time = end - start
            mip_gap = model.MIPGap

            portfolio = {
                'error': error,
                'weights': weights,
                'performance': performance,
                'dates': self.dates,
                'optimization_time': optimization_time,
                "mip_gap": mip_gap
            }

            self.portfolio = portfolio
        
        return self.portfolio
    
    def calculate_tracking_error(self, portfolio_weights, is_train=True):
        """
        Calculate tracking error metrics for the portfolio
        
        Parameters:
        - portfolio_weights: Dictionary of stock weights
        - is_train: Whether to use training or testing data
        
        Returns:
        - Dictionary of tracking error metrics
        """
        if is_train:
            stock_data = self.data['train']['stock']
            index_data = self.data['train']['index']
        else:
            stock_data = self.data['test']['stock']
            index_data = self.data['test']['index']
        
        selected_stocks = list(portfolio_weights.keys())
        selected_stock_returns = stock_data[selected_stocks]
        
        weighted_portfolio_returns = (selected_stock_returns * list(portfolio_weights.values())).sum(axis=1)
        
        tracking_error_metrics = {
            'tracking_error': np.std(weighted_portfolio_returns - index_data),
            'root_mean_squared_error': np.sqrt(np.mean((weighted_portfolio_returns - index_data)**2)),
            'correlation': np.corrcoef(weighted_portfolio_returns, index_data)[0, 1],
        }
        
        return tracking_error_metrics
    
    def compare_train_test_performance(self, portfolio_weights):
        """
        Compare portfolio performance on training and testing data
        
        Parameters:
        - portfolio_weights: Dictionary of stock weights
        
        Returns:
        - Dictionary with train and test performance metrics
        """
        train_metrics = self.calculate_tracking_error(portfolio_weights, is_train=True)
        test_metrics = self.calculate_tracking_error(portfolio_weights, is_train=False)
        
        return {
            'train_performance': train_metrics,
            'test_performance': test_metrics
        }
    
    def generate_initial_solution(self, portfolio_size=DEFAULT_PORTFOLIO_SIZE):
        """
        Generate initial solution for the portfolio optimization problem.
        
        Parameters:
        - portfolio_size: Number of stocks to select (k)
        
        Returns:
        - Tuple (w_initial, z_initial) where:
            - w_initial: Dictionary with initial weights for stocks
            - z_initial: Dictionary with initial binary selection for stocks
        """

        if self.data['train']['stock'] is None:
            print('Error')
            return

        stock_data = self.data['train']['stock']
        index_data = self.data['train']['index']

        I = np.array(stock_data.columns)
        T = range(len(stock_data))
        r = {(t, i): stock_data.iloc[t][i] for t in T for i in I}
        R = np.array(index_data)
        k = portfolio_size

        relaxed_model = gp.Model("RelaxedPortfolio")
        w_relaxed = relaxed_model.addVars(I, lb=0, ub=1, name="w")

        relaxed_model.setObjective(
            (1 / len(T)) * gp.quicksum(
                (gp.quicksum(w_relaxed[i] * r[t, i] for i in I) - R[t]) ** 2 for t in T
            ),
            GRB.MINIMIZE
        )

        relaxed_model.addConstr(gp.quicksum(w_relaxed[i] for i in I) == 1, "WeightSum")
        relaxed_model.optimize()

        if relaxed_model.Status != GRB.OPTIMAL:
            print("Relaxed model did not converge.")
            return None, None

        relaxed_weights = {i: w_relaxed[i].x for i in I}

        top_k_stocks = sorted(relaxed_weights, key=relaxed_weights.get, reverse=True)[:k]

        w_initial = {i: relaxed_weights[i] if i in top_k_stocks else 0 for i in I}
        total_weight_top_k = sum(w_initial[i] for i in top_k_stocks)
        w_initial = {i: (w_initial[i] / total_weight_top_k) if i in top_k_stocks else 0 for i in I}
        z_initial = {i: 1 if i in top_k_stocks else 0 for i in I}

        return w_initial, z_initial
