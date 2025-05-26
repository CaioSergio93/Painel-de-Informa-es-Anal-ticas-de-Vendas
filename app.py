import pandas as pd
import streamlit as st
import plotly.express as px
import locale
import os

# Configuração para evitar problemas de locale
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    # Fallback para locale padrão se pt_BR não estiver disponível
    locale.setlocale(locale.LC_ALL, '')

# Configurações iniciais
st.set_page_config(page_title="Painel de Vendas", layout="wide")

# Solução alternativa para nomes de meses em português
MESES_PT_BR = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Carregar dados
@st.cache_data  # Cache para melhor performance
def load_data():
    clientes = pd.read_csv('data/clientes.csv')
    produtos = pd.read_csv('data/produtos.csv')
    vendedores = pd.read_csv('data/vendedores.csv')
    fornecedores = pd.read_csv('data/fornecedores.csv')
    vendas = pd.read_csv('data/vendas.csv')
    
    # Pré-processamento
    vendas['data'] = pd.to_datetime(vendas['data'])
    vendas['ano'] = vendas['data'].dt.year
    vendas['mes'] = vendas['data'].dt.month
    vendas['mes_nome'] = vendas['mes'].map(MESES_PT_BR)  # Usando nosso mapeamento
    
    # Merge das tabelas com padronização de nomes
    df = vendas.merge(clientes, on='id_cliente') \
               .merge(produtos, on='id_produto') \
               .merge(vendedores, on='id_vendedor') \
               .merge(fornecedores, left_on='fornecedor_id', right_on='id_fornecedor') \
               .rename(columns={
                   'nome_x': 'cliente',
                   'nome_y': 'vendedor',
                   'estado_x': 'estado_cliente',
                   'estado_y': 'estado_fornecedor',
                   'cidade_x': 'cidade_cliente',
                   'cidade_y': 'cidade_fornecedor'
               })
    return df

df = load_data()

# Sidebar
aba = st.sidebar.radio("Selecione a aba", ['Visão Geral', 'Produtos & Clientes', 'Análise Geográfica'])

# Filtros globais
anos = sorted(df['ano'].unique())
ano_selecionado = st.sidebar.selectbox("Selecione o ano", anos, index=len(anos)-1)

meses = sorted(df['mes'].unique())
mes_selecionado = st.sidebar.selectbox("Selecione o mês", ['Todos'] + meses)

# Aplicar filtros
df_filtrado = df[df['ano'] == ano_selecionado]
if mes_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['mes'] == mes_selecionado]

# Aba Visão Geral
if aba == 'Visão Geral':
    st.title(f"📊 Painel de Vendas - {ano_selecionado}")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Vendido", f"R$ {df_filtrado['valor_total'].sum():,.2f}")
    col2.metric("Quantidade de Vendas", len(df_filtrado))
    col3.metric("Clientes Atendidos", df_filtrado['id_cliente'].nunique())
    
    # Gráfico de vendas mensais
    vendas_mes = df_filtrado.groupby(['mes', 'mes_nome'])['valor_total'].sum().reset_index().sort_values('mes')
    fig = px.bar(vendas_mes, x='mes_nome', y='valor_total', 
                 labels={'mes_nome': 'Mês', 'valor_total': 'Total Vendido (R$)'},
                 title=f'Vendas Mensais - {ano_selecionado}')
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de vendas
    st.subheader("📅 Últimas Vendas")
    st.dataframe(df_filtrado[['data', 'cliente', 'nome_produto', 'quantidade', 'valor_total']]
                 .sort_values('data', ascending=False)
                 .head(20))

# Aba Produtos & Clientes
elif aba == 'Produtos & Clientes':
    st.title("📦 Produtos e 👥 Clientes")
    
    tab1, tab2 = st.tabs(["Produtos", "Clientes"])
    
    with tab1:
        # Top produtos por quantidade
        top_produtos_qtd = df_filtrado.groupby('nome_produto')['quantidade'].sum().sort_values(ascending=False).reset_index()
        st.subheader("Top Produtos (Quantidade Vendida)")
        fig_prod_qtd = px.bar(top_produtos_qtd.head(10), x='nome_produto', y='quantidade', 
                             labels={'quantidade': 'Quantidade', 'nome_produto': 'Produto'},
                             title='Top 10 Produtos Mais Vendidos (Unidades)')
        st.plotly_chart(fig_prod_qtd, use_container_width=True)
        
        # Top produtos por valor
        top_produtos_valor = df_filtrado.groupby('nome_produto')['valor_total'].sum().sort_values(ascending=False).reset_index()
        st.subheader("Top Produtos (Valor Total)")
        fig_prod_valor = px.bar(top_produtos_valor.head(10), x='nome_produto', y='valor_total', 
                               labels={'valor_total': 'Valor Total (R$)', 'nome_produto': 'Produto'},
                               title='Top 10 Produtos em Valor de Venda')
        st.plotly_chart(fig_prod_valor, use_container_width=True)
    
    with tab2:
        # Top clientes
        top_clientes = df_filtrado.groupby('cliente')['valor_total'].sum().sort_values(ascending=False).reset_index()
        st.subheader("Clientes com Maior Valor de Compra")
        fig_cli = px.bar(top_clientes.head(10), x='cliente', y='valor_total', 
                         labels={'cliente': 'Cliente', 'valor_total': 'Valor Total (R$)'},
                         title='Top 10 Clientes por Valor de Compra')
        st.plotly_chart(fig_cli, use_container_width=True)
        
        # Distribuição por idade
        st.subheader("Distribuição de Vendas por Idade")
        fig_idade = px.histogram(df_filtrado, x='idade', nbins=10, 
                                labels={'idade': 'Idade', 'count': 'Quantidade de Vendas'},
                                title='Distribuição de Vendas por Faixa Etária')
        st.plotly_chart(fig_idade, use_container_width=True)

# Aba Análise Geográfica
elif aba == 'Análise Geográfica':
    st.title("📍 Análise Geográfica das Vendas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendas por estado do cliente
        vendas_estado = df_filtrado.groupby('estado_cliente')['valor_total'].sum().reset_index()
        st.subheader("Vendas por Estado do Cliente")
        fig_estado = px.pie(vendas_estado, names='estado_cliente', values='valor_total', 
                           title='Distribuição de Vendas por Estado do Cliente')
        st.plotly_chart(fig_estado, use_container_width=True)
    
    with col2:
        # Vendas por cidade do cliente
        vendas_cidade = df_filtrado.groupby('cidade_cliente')['valor_total'].sum().sort_values(ascending=False).reset_index()
        st.subheader("Top Cidades por Vendas")
        fig_cidade = px.bar(vendas_cidade.head(10), x='cidade_cliente', y='valor_total',
                           labels={'valor_total': 'Valor Total (R$)', 'cidade_cliente': 'Cidade'},
                           title='Top 10 Cidades por Valor de Vendas')
        st.plotly_chart(fig_cidade, use_container_width=True)
    
    # Mapa de vendas por estado
    st.subheader("Mapa de Vendas por Estado")
    estado_vendas = df_filtrado.groupby('estado_cliente').agg({
        'valor_total': 'sum',
        'id_venda': 'count'
    }).reset_index().rename(columns={'id_venda': 'quantidade_vendas'})
    
    fig_mapa = px.choropleth(
        estado_vendas,
        locations='estado_cliente',
        locationmode='ISO-3',
        color='valor_total',
        hover_name='estado_cliente',
        hover_data=['quantidade_vendas'],
        scope='south america',
        color_continuous_scale='Blues',
        title='Vendas por Estado (Valor Total)'
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_mapa, use_container_width=True)