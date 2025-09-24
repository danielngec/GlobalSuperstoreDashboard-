Dashboard de Vendas (Streamlit)

Aplicação Streamlit para análise de vendas com séries temporais, comparativos por período, análise regional, gráficos de Pareto por categoria e subcategoria, ranking de clientes (Top/Bottom 10) e decomposição/ACF.

## Requisitos

- Python 3.9 ou superior
- Sistema operacional: Windows, macOS ou Linux

## Instalação

1. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
# ou
source .venv/bin/activate  # macOS/Linux
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executando a aplicação

Certifique-se de que o arquivo `train.csv` está no mesmo diretório do `app.py`.

```bash
streamlit run app.py
```

O Streamlit abrirá automaticamente no navegador

## Estrutura dos dados esperada (train.csv)

A aplicação espera as seguintes colunas (nomes em inglês conforme o dataset original):

- `Order Date` (formato dd/mm/YYYY)
- `Ship Date` (formato dd/mm/YYYY)
- `Postal Code`
- `Sales` (numérico)
- `Customer ID`
- `Customer Name`
- `Region`
- `Segment`
- `Category`
- `Sub-Category`

Outras colunas podem existir e serão ignoradas.

## Funcionalidades

- Vendas mensais com seletor de intervalo de datas
- Comparativos de vendas por granularidade (diária, mensal, trimestral, anual)
- Comparação de vendas mensais entre anos
- Análise por região (clientes e total de vendas)
- Análise de Pareto por categoria e subcategoria
- Top 10 e Bottom 10 clientes por faturamento
- Decomposição (tendência e sazonalidade) e autocorrelação (ACF) das vendas mensais
- KPIs de metas do próximo mês (vendas e clientes)

## Dependências e bibliotecas utilizadas

- `streamlit`: Interface web interativa
- `pandas`: Manipulação e agregação de dados
- `plotly`: Visualizações interativas (linhas, barras, pizza)
- `statsmodels`: Decomposição de séries temporais e autocorrelação

## Notas de implementação

- Colunas e rótulos da interface foram padronizados para português brasileiro.
- Comentários supérfluos e código não utilizado foram removidos.
- Apenas gráficos interativos (Plotly) são exibidos na interface.

## Link do DashBoard

[Streamlit dashboard](https://ardrfsxsg3ekcxfun6uizz.streamlit.app/)
