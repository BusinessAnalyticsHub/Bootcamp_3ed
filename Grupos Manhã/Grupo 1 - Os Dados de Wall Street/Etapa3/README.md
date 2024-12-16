# Projeto de **Index Tracking**  
Este projeto implementa um pipeline completo para **Index Tracking**, desde a criação de datasets de ações até a otimização de uma carteira que busca replicar o desempenho de um índice de mercado.

## **Objetivo**  
Criar um modelo de **tracking** que minimiza o **erro de rastreamento** entre um índice e uma carteira composta por um subconjunto de ações do índice.

---

## **Funcionalidades Principais**  

### 1. **Criação do Dataset**  

**Pipeline de Criação do Dataset**:  
- **Download**: Baixa dados de um índice e suas ações via API *Yahoo Finance*.  
- **Limpeza**: Remove ações com dados faltantes consecutivos acima de um limite (`max_missing_days`).  
- **Interpolação**: Gaps nos dados restantes são preenchidos via interpolação linear.  
- **Cálculos**: Calcula retornos diários (variância) e retornos acumulados.  
- **Exportação**: Salva resultados em CSV:  
  - `stock_variance_<index_ticker>.csv`  
  - `stock_cumulative_returns_<index_ticker>.csv`

---

### 2. **Otimização da Carteira**  
Utiliza **Gurobi** para otimizar uma carteira que minimiza o **erro de rastreamento** em relação ao índice.

**Destaques**:
- Resolve o problema via **MIP** (programação inteira mista), com controle de parâmetros como limite de tempo e número máximo de iterações.
- Utiliza uma **solução inicial personalizada**, desenvolvida internamente, para reduzir o tempo de convergência do solver.
- Calcula métricas de desempenho, como:  
  - **Erro de Rastreamento (Tracking Error)**  
  - **RMSE (Root Mean Squared Error)**  
  - **Correlação**  

---

### 3. **Execução Principal**  
O script principal (`main`) organiza o fluxo do projeto:  
1. Criação do dataset  
2. Treinamento da carteira  
3. Armazenamento dos resultados em arquivos CSV

## **Instalação e Configuração**  

1. Clone o repositório:  
   ```bash
   git clone <repo-url>
   cd index-tracking
   ```

2. Instale as dependências:  
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o **Gurobi** corretamente (necessário para otimização):  
   - Baixe o Gurobi e configure a licença.  
   - Referência: [Instalação do Gurobi](https://www.gurobi.com/documentation/).

---

## **Dependências**  
- **Python 3.9+**  
- **Pandas**  
- **Numpy**  
- **Yahoo Finance**  
- **Gurobi**  

---

## **Resultados**  

Os resultados da carteira otimizada são salvos no diretório `data/` no formato **CSV** com as seguintes informações:
- **Tracking Error**, **RMSE**, **Correlação** no treino e teste  
- **Tempo de otimização**  
- **Gap** do MIP  
- **Pesos das Ações Selecionadas**  

É possível visualizar os resultados utilizando as funções de plotagem de gráficos presentes nos notebooks **"flowers"** do projeto.

