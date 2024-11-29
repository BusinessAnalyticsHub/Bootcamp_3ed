
# Bootcamp de Introdução à Ciência de Dados : PROJETO FINOR

O projeto **FINOR** visa desenvolver um modelo de rastreamento de índices para os índices **S&P 100** e **IBOVESPA** . O objetivo é simplificar a composição do portfólio, utilizando um número limitado de ações para replicar o comportamento do índice original,buscando também reduzir os custos de manutenção do portfólio.

## Etapas do Desenvolvimento
O desenvolvimento do modelo de otimização foi realizado em Python , utilizando bibliotecas específicas e solucionadores como Gurobi ou alternativas de código aberto. Abaixo as etapas principais:

   1. **Importação de Bibliotecas:**  
   As bibliotecas principais são importadas no início, incluindo `pandas` para manipulação de dados, `yfinance` para download dos dados de mercado, e `matplotlib` para visualização dos dados.

   2. **Coleta de Dados:**  
   Os dados históricos dos índices **S&P100** e **IBOV** são baixados diretamente do [Yahoo Finance](https://finance.yahoo.com/), enquanto as composições dos índices foram coletadas de fontes confiáveis como [iShares](https://www.ishares.com/).

   3. **Limpeza e Organização dos Dados:**  
   Realiza-se uma limpeza dos dados baixados, mantendo apenas as colunas essenciais (`Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`), com exportação em arquivos `.csv`. É possível também visualizar informações sobre os arquivos usados,      como número de linhas e colunas, tamanho e número de dados ausentes.

   4. **Visualização de Dados:**  
   Exemplos de gráficos e visualizações, como uma série temporal para o preço de fechamento ajustado dos índices e seus ativos, são construídos para análise inicial. Há também visualizações a respeito da distribuição setorial dos índices levando em        conta se valor de mercado. Para finalizar, heatmaps e boxplots são apresentados para uma aprofundamento sobre os índices e ativos.

   ## Como Usar

### Pré-requisitos

- **Python 3.7+**
- **Versões das bibliotecas:**
  
  pandas 2.2.2

  yfinance 0.2.44

  matplotlib 3.7.1

  seaborn 0.13.2
- **Instalação das versões das bibliotecas:**  
  pip install biblioteca==versão

## Execução
   - Baixe o notebook e os arquivos .csv de composição de índice. 
   - Execute cada célula do notebook para baixar, limpar e visualizar os dados.   
   - Visualize os gráficos para análise exploratória dos preços e tendências dos índices e seus ativos.

## Estrutura de Arquivos
   - **analise_exploratoria.ipynb**: Notebook principal com o código e as visualizações.   
   - **OEF_holdings.csv** e **BOVA11_holdings.csv**: Arquivos de composição dos índices S&P100 e IBOV.   
   - **sp100_historico_dados.csv** e **bvsp_historico_dados.csv**: Dados históricos limpos dos índices, após processamento.

## **Projeto desenvolvido pelo:**  Grupo Dale Science

 **Estudantes da Universidade federal do rio grande do sul (UFRGS)**
- Luã Greski Diel 
- Rodrigo Aschidamini João  
- Lorenzo Menezes Silveira  
- Chrinovic Tshibambe 
- Igor Morais Telles  
