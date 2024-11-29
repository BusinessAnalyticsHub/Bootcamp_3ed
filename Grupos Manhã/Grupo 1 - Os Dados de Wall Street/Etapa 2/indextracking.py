import gurobipy as gp
from gurobipy import GRB
import numpy as np

def create_portfolio(stock_data, index_data, portfolio_size=15, max_iterations=100000):
    I = np.array(stock_data.columns)  # Conjunto de ativos disponíveis
    T = range(len(stock_data))  # Número de períodos
    r = {(t, i): stock_data.iloc[t][i] for t in T for i in I} # Retornos individuais dos ativos
    R =  np.array(index_data) # Retornos do índice
    k = portfolio_size

    model = gp.Model("TrackingPortfolio")
    w = model.addVars(I, lb=0, ub=1, name="w")  # Pesos dos ativos
    z = model.addVars(I, vtype=GRB.BINARY, name="z")  # Seleção de ativos

    model.setObjective(
        (1 / len(T)) * gp.quicksum(
            (gp.quicksum(w[i] * r[t, i] for i in I) - R[t]) ** 2 for t in T
        ),
        GRB.MINIMIZE
    )

    model.addConstr(gp.quicksum(w[i] for i in I) == 1, "SomaPesos")  # Soma dos pesos deve ser 1
    model.addConstrs((w[i] <= z[i] for i in I), "VinculoPesos")      # Pesos vinculados a z
    model.addConstr(gp.quicksum(z[i] for i in I) == k, "MaxAtivos")  # Máximo de K ativos

    model.setParam(GRB.Param.IterationLimit, max_iterations)  # Teste inicial com 100.000 iterações

    model.optimize()

    print("\nAções da carteira:")
    for i in I:
        if z[i].x:
            print(f"Ativo {i}: Peso = {w[i].x:.4f}")
    
    print("\nAções não adicionadas na carteira:")
    for i in I:
        if not z[i].x:
            print(f"Ativo {i}: Peso = {w[i].x:.4f}")

    portfolio_weights = {i: w[i].x for i in I if z[i].x}
    
    return portfolio_weights