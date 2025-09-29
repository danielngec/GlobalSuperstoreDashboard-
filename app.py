import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf

sales_df = pd.read_csv("train.csv")


sales_df['Order Date'] = pd.to_datetime(sales_df['Order Date'], format='%d/%m/%Y')   
sales_df['Ship Date'] = pd.to_datetime(sales_df['Ship Date'], format='%d/%m/%Y')    
sales_df.sort_values(by=['Order Date'], inplace=True, ascending=True)  
sales_df['Postal Code'] = sales_df['Postal Code'].fillna(9999)

sales_df['Year'] = sales_df['Order Date'].dt.year
sales_df['Month'] = sales_df['Order Date'].dt.month
sales_df['Quarter'] = sales_df['Order Date'].dt.quarter

 

sales_df['Order Date'] = pd.to_datetime(sales_df['Order Date'])
sales_df.set_index('Order Date', inplace=True)


daily_sales = sales_df['Sales'].resample('D').sum()
monthly_sales_ts = sales_df['Sales'].resample('ME').sum()




 

start_date = monthly_sales_ts.index.min().date()
end_date = monthly_sales_ts.index.max().date()

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")


with st.container():
    st.subheader("Vendas Mensais")
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        date_range = st.slider(
            "Intervalo de datas",
            min_value=start_date,
            max_value=end_date,
            value=(start_date, end_date),
            format="YYYY-MM-DD"
        )
        
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_sales = monthly_sales_ts.loc[start:end].reset_index()

        fig = px.line(
            filtered_sales,
            x='Order Date',
            y='Sales',
            markers=True,
            title="Vendas Mensais no Período",
            hover_data={'Order Date': True, 'Sales': ':.2f'}
        )
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Vendas"
        )

        st.plotly_chart(fig, use_container_width=True)

    
    st.write(f"Período: **{start.date()}** a **{end.date()}**")

with st.container():
    st.subheader("Comparativos de Vendas")

    col1, col2 = st.columns(2)

    with col1:
        option = st.selectbox(
            "Granularidade do gráfico",
            ["Diário", "Mensal", "Trimestral", "Anual"]
        )

        if option == "Diário":
            data_to_plot = sales_df['Sales'].resample('D').sum().reset_index()
            title = "Vendas Diárias"
            x_col = 'Order Date'
        elif option == "Mensal":
            data_to_plot = sales_df.groupby(['Year', 'Month'])['Sales'].sum().reset_index()
            data_to_plot['Date'] = pd.to_datetime(data_to_plot['Year'].astype(str) + '-' + data_to_plot['Month'].astype(str) + '-01')
            x_col = 'Date'
            title = "Vendas Mensais"
        elif option == "Trimestral":
            data_to_plot = sales_df.groupby(['Year', 'Quarter'])['Sales'].sum().reset_index()
            data_to_plot['Date'] = pd.to_datetime(data_to_plot['Year'].astype(str) + '-' + ((data_to_plot['Quarter']-1)*3+1).astype(str) + '-01')
            x_col = 'Date'
            title = "Vendas Trimestrais"
        elif option == "Anual":
            data_to_plot = sales_df.groupby('Year')['Sales'].sum().reset_index()
            data_to_plot['Date'] = pd.to_datetime(data_to_plot['Year'].astype(str) + '-01-01')
            x_col = 'Date'
            title = "Vendas Anuais"
        fig1 = px.line(
            data_to_plot,
            x=x_col,
            y='Sales',
            markers=True,
            title=title,
            hover_data={x_col: True, 'Sales': ':.2f'}
        )
        fig1.update_layout(xaxis_title="Período", yaxis_title="Vendas")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        anos_disponiveis = sales_df['Year'].unique()
        anos_selecionados = st.multiselect(
            "Anos para comparar",
            options=anos_disponiveis,
            default=anos_disponiveis
        )

        df_filtrado = sales_df[sales_df['Year'].isin(anos_selecionados)]
        monthly_sales_filtrado = df_filtrado.groupby(['Year', 'Month'])['Sales'].sum().reset_index()

        fig2 = px.line(
            monthly_sales_filtrado,
            x='Month',
            y='Sales',
            color='Year',
            markers=True,
            title="Vendas Mensais por Ano",
            hover_data={'Month': True, 'Sales': ':.2f', 'Year': True}
        )
        fig2.update_layout(
            xaxis_title="Mês",
            yaxis_title="Vendas",
            xaxis=dict(tickmode='linear', tick0=1, dtick=1)
        )
        st.plotly_chart(fig2, use_container_width=True)

with st.container():
    region_analysis = sales_df.groupby('Region').agg(
        Customer_Count=('Customer ID', 'nunique'),
        Total_Sales=('Sales', 'sum')
    ).reset_index()
    st.subheader("Análise por Região")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(
            region_analysis,
            names='Region',
            values='Customer_Count',
            hole=0.4,
            title="Distribuição de Clientes por Região",
            hover_data=['Customer_Count']
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            region_analysis,
            x='Region',
            y='Total_Sales',
            text='Total_Sales',
            hover_data=['Total_Sales'],
            color='Region',
            title="Distribuição de Vendas por Região"
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(yaxis_title='Total de Vendas', xaxis_title='Região')
        st.plotly_chart(fig2, use_container_width=True)

with st.container():
    st.subheader("Análise de Vendas – Pareto")

    mes_dict = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    meses_disponiveis = sales_df['Month'].unique()
    meses_disponiveis.sort()

    meses_nomes = [mes_dict[m] for m in meses_disponiveis]

    meses_selecionados_nomes = st.multiselect(
        "Meses",
        options=meses_nomes,
        default=meses_nomes
    )

    meses_selecionados_numeros = [k for k,v in mes_dict.items() if v in meses_selecionados_nomes]

    df_filtrado = sales_df[sales_df['Month'].isin(meses_selecionados_numeros)]
    col1, col2 = st.columns(2)

    category_sales = df_filtrado.groupby('Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    subcategory_sales = df_filtrado.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)

    with col1:
        category_sales['Cumulative'] = category_sales['Sales'].cumsum()
        category_sales['Cumulative_Percent'] = 100 * category_sales['Cumulative'] / category_sales['Sales'].sum()

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=category_sales['Category'],
            y=category_sales['Sales'],
            name='Sales',
            marker_color='lightblue'
        ))
        fig1.add_trace(go.Scatter(
            x=category_sales['Category'],
            y=category_sales['Cumulative_Percent'],
            name='Cumulative %',
            yaxis='y2',
            mode='lines+markers',
            marker_color='red'
        ))
        fig1.update_layout(
            title="Pareto de Vendas por Categoria",
            yaxis=dict(title='Vendas'),
            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0,110]),
            legend=dict(x=0.7, y=1.1)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        subcategory_sales['Cumulative'] = subcategory_sales['Sales'].cumsum()
        subcategory_sales['Cumulative_Percent'] = 100 * subcategory_sales['Cumulative'] / subcategory_sales['Sales'].sum()

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=subcategory_sales['Sub-Category'],
            y=subcategory_sales['Sales'],
            name='Sales',
            marker_color='lightblue'
        ))
        fig2.add_trace(go.Scatter(
            x=subcategory_sales['Sub-Category'],
            y=subcategory_sales['Cumulative_Percent'],
            name='Cumulative %',
            yaxis='y2',
            mode='lines+markers',
            marker_color='red'
        ))
        fig2.update_layout(
            title="Pareto de Vendas por Subcategoria",
            yaxis=dict(title='Vendas'),
            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0,110]),
            legend=dict(x=0.7, y=1.1)
        )
        st.plotly_chart(fig2, use_container_width=True)
with st.container():
    top_10_customers = sales_df.groupby('Customer Name').agg(
        Total_Sales=('Sales','sum'), Segment=('Segment','first')
    ).reset_index().sort_values('Total_Sales', ascending=False).head(10)

    bottom_10_customers = sales_df.groupby('Customer Name').agg(
        Total_Sales=('Sales','sum'), Segment=('Segment','first')
    ).reset_index().sort_values('Total_Sales', ascending=True).head(10)
    st.subheader("Clientes – Top 10 e Bottom 10")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Top 10 clientes com maior faturamento")
        fig_top = px.bar(
            top_10_customers,
            x='Customer Name',
            y='Total_Sales',
            text='Total_Sales',
            hover_data={'Customer Name':True, 'Total_Sales':True},
            labels={'Total_Sales':'Total de Vendas (R$)', 'Customer Name':'Cliente'}
        )
        fig_top.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        fig_top.update_layout(yaxis=dict(title='Total de Vendas (R$)'), xaxis_tickangle=-45, showlegend=True)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        st.write("Top 10 clientes com menor faturamento")
        fig_bottom = px.bar(
            bottom_10_customers,
            x='Customer Name',
            y='Total_Sales',
            text='Total_Sales',
            hover_data={'Customer Name':True, 'Total_Sales':True},
            labels={'Total_Sales':'Total de Vendas (R$)', 'Customer Name':'Cliente'}
        )
        fig_bottom.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        fig_bottom.update_layout(yaxis=dict(title='Total de Vendas (R$)'), xaxis_tickangle=-45, showlegend=True)
        st.plotly_chart(fig_bottom, use_container_width=True)

with st.container():
    st.subheader("Decomposição e Autocorrelação – Vendas Mensais")

    col1, col2, col3 = st.columns(3)
    decomposition = seasonal_decompose(monthly_sales_ts, model='additive', period=12)

    with col1:
        df_trend = decomposition.trend.reset_index()
        fig_trend = px.line(
            df_trend,
            x='Order Date',
            y='trend',
            markers=True,
            title="Trend",
            hover_data={'Order Date': True, 'trend': ':.2f'}
        )
        fig_trend.update_layout(yaxis_title="Vendas", xaxis_title="Data")
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        df_seasonal = decomposition.seasonal.reset_index()
        fig_seasonal = px.line(
            df_seasonal,
            x='Order Date',
            y='seasonal',
            markers=True,
            title="Seasonal",
            hover_data={'Order Date': True, 'seasonal': ':.2f'}
        )
        fig_seasonal.update_layout(yaxis_title="Vendas", xaxis_title="Data")
        st.plotly_chart(fig_seasonal, use_container_width=True)

    with col3:
        acf_vals = acf(monthly_sales_ts, nlags=12)
        df_acf = pd.DataFrame({
            'Lag': range(len(acf_vals)),
            'Autocorrelation': acf_vals
        })
        fig_acf = px.bar(
            df_acf,
            x='Lag',
            y='Autocorrelation',
            title="Autocorrelação",
            hover_data={'Lag': True, 'Autocorrelation': ':.2f'}
        )
        fig_acf.update_layout(yaxis_title="Autocorrelação", xaxis_title="Defasagem")
        st.plotly_chart(fig_acf, use_container_width=True)


with st.container():
    st.subheader("KPIs – Metas do Próximo Mês")

    last_sales_values = df_trend['trend'].dropna().iloc[-10:]
    sales_growth_rates = last_sales_values.pct_change().dropna()
    avg_sales_growth = sales_growth_rates.mean()
    next_sales_estimate = last_sales_values.iloc[-1] * (1 + avg_sales_growth)

    customer_monthly = sales_df.groupby(['Year', 'Month'])['Customer ID'].nunique().reset_index(name='Customer_Count')
    customer_monthly['Date'] = pd.to_datetime(customer_monthly[['Year', 'Month']].assign(DAY=1))
    customer_monthly.set_index('Date', inplace=True)
    customer_monthly = customer_monthly.sort_index()

    last_10_customers = customer_monthly['Customer_Count'].iloc[-10:]
    customer_growth_rates = last_10_customers.pct_change().dropna()
    avg_customer_growth = customer_growth_rates.mean()
    next_customer_estimate = last_10_customers.iloc[-1] * (1 + avg_customer_growth)

    kpi1, kpi2, kpi3 = st.columns([1, 1, 4])

    with kpi1:
        st.metric(
            label="Meta de Vendas (Próximo Mês)",
            value=f"R$ {next_sales_estimate:,.2f}",
            delta=f"{avg_sales_growth*100:.2f}% vs último mês"
        )

    with kpi2:
        st.metric(
            label="Meta de Clientes (Próximo Mês)",
            value=f"{int(next_customer_estimate)}",
            delta=f"{avg_customer_growth*100:.2f}% vs último mês"
        )

with st.container():
    st.subheader("Insights de Vendas")
    st.markdown("""
    <p style="font-size:22px;">
Os dados mostram que a empresa segue um crescimento constante.<br>
Além disso, observa-se que existem períodos em que a empresa vende mais, como em <b>Dezembro</b>.<br>
Apesar da tendência de vender mais <b>tecnologia</b> durante o ano, em <b>Dezembro</b> se vendem mais <b>móveis</b>, sendo que os produtos mais vendidos são <b>cadeiras e mesas</b>, correspondendo aproximadamente a <b>30%</b> das vendas nesse mês.<br>
Esse aumento nas vendas em Dezembro está relacionado a datas comemorativas e ao período de férias, quando os consumidores costumam reformar ou decorar suas casas.<br>
Os <b>telefones</b> representam cerca de <b>10%</b> das vendas em Dezembro, enquanto no período completo correspondem a <b>14%</b> das vendas.
</p>
    </p>

    """, unsafe_allow_html=True)
