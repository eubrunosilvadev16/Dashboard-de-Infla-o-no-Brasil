import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard de Inflação no Brasil", layout="wide")

# CSS para compactar margens e centralizar título com imagem
st.markdown("""
    <style>
        /* Container principal sem padding */
        .main .block-container {
            padding: 0.5rem 0.5rem 0.5rem 0.5rem !important;
            max-width: 100% !important;
        }
        /* Sidebar mais estreita */
        .css-1d391kg {
            font-family: Arial, sans-serif;
            font-size: 18px;
            color: white;
            padding-top: 10px;
            width: 280px;
        }
        label {
            font-size: 18px !important;
            font-weight: 600;
            margin-bottom: 5px;
            color: white !important;
        }
        /* Container do topo: alinhamento horizontal */
        .top-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        /* Título estilizado */
        .main-title {
            font-family: Arial, sans-serif;
            font-size: 44px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            line-height: 1.1;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("inflacao.csv", parse_dates=["referencia"])
    df.sort_values("referencia", inplace=True)
    return df

df = carregar_dados()

# SIDEBAR com imagem e filtros
with st.sidebar:
    if os.path.exists("br.jpeg"):
        st.image("br.jpeg", width=220)  # Aumentei o tamanho aqui
    else:
        st.warning("Imagem da bandeira do Brasil não encontrada.")
    st.markdown(
        "<h2 style='font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; color: #FFFFFF; margin-top: 20px; margin-bottom: 10px;'>Filtros</h2>",
        unsafe_allow_html=True
    )
    ano_inicio = st.selectbox("Ano inicial", sorted(df['ano'].unique()), index=0)
    ano_fim = st.selectbox("Ano final", sorted(df['ano'].unique())[::-1], index=0)
    df = df[(df["ano"] >= ano_inicio) & (df["ano"] <= ano_fim)]

    indices_opcoes = {
        "IPCA": "ipca_variacao",
        "INPC": "inpc_variacao",
        "IPCA-15": "ipca15_variacao"
    }
    indices_selecionados = st.multiselect(
        "Selecione os índices para comparação (variação mensal)",
        options=list(indices_opcoes.keys()),
        default=["IPCA", "INPC", "IPCA-15"]
    )

    min_ipca12 = float(df["ipca_acumulado_doze_meses"].min())
    max_ipca12 = float(df["ipca_acumulado_doze_meses"].max())
    ipca12_range = st.slider("IPCA acumulado em 12 meses (faixa %)",
                             min_value=min_ipca12,
                             max_value=max_ipca12,
                             value=(min_ipca12, max_ipca12))
    df = df[df["ipca_acumulado_doze_meses"].between(*ipca12_range)]

    min_selic = float(df["selic_meta"].min())
    max_selic = float(df["selic_meta"].max())
    selic_range = st.slider("Faixa da taxa Selic (%)",
                            min_value=min_selic,
                            max_value=max_selic,
                            value=(min_selic, max_selic))
    df = df[df["selic_meta"].between(*selic_range)]

    min_sal = float(df["salario_minimo"].min())
    max_sal = float(df["salario_minimo"].max())
    sal_range = st.slider("Salário mínimo (R$)", 
                          min_value=min_sal, 
                          max_value=max_sal,
                          value=(min_sal, max_sal))
    df = df[df["salario_minimo"].between(*sal_range)]

# Título centralizado sem nenhuma imagem corrompida
st.markdown(
    "<h1 class='main-title'>Dashboard de Inflação no Brasil</h1>",
    unsafe_allow_html=True
)

def configurar_layout(fig, titulo):
    fig.update_layout(
        title=dict(text=titulo, font=dict(family="Arial", size=28, color="#FFFFFF")),
        xaxis_title_font=dict(family="Arial", size=18, color="#FFFFFF"),
        yaxis_title_font=dict(family="Arial", size=18, color="#FFFFFF"),
        xaxis=dict(tickfont=dict(family="Arial", size=14, color="#FFFFFF")),
        yaxis=dict(tickfont=dict(family="Arial", size=14, color="#FFFFFF")),
        legend=dict(font=dict(family="Arial", size=14, color="#FFFFFF")),
        font=dict(family="Arial", size=14, color="#FFFFFF"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

fig1 = px.line(df, x="referencia", y="ipca_acumulado_doze_meses")
fig1 = configurar_layout(fig1, "IPCA Acumulado em 12 Meses")
fig1.update_layout(xaxis_title="Data", yaxis_title="IPCA (12M)")

colunas_indices = [indices_opcoes[i] for i in indices_selecionados]
somas = df[colunas_indices].sum().rename({v: k for k, v in indices_opcoes.items()})

fig2 = px.pie(
    names=somas.index,
    values=somas.values,
    title="Participação Total - Variação Mensal dos Índices Selecionados",
    color=somas.index,
    color_discrete_map={
        "IPCA": "#E74C3C",      # vermelho
        "INPC": "#F1C40F",      # amarelo
        "IPCA-15": "#5DADE2"    # azul claro
    }
)
fig2.update_traces(textinfo='percent+label', textfont_color="white")
fig2.update_layout(
    title_font=dict(family="Arial", size=28, color="#FFFFFF"),
    font=dict(family="Arial", size=14, color="#FFFFFF"),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend_font=dict(size=14, color="#FFFFFF")
)

fig3 = px.line(df, x="referencia", y=["selic_meta", "ipca_variacao"])
fig3 = configurar_layout(fig3, "Relação entre Selic e IPCA (Variação Mensal)")
fig3.update_layout(xaxis_title="Data", yaxis_title="Taxa (%)")

fig4 = px.line(df, x="referencia", y="salario_minimo")
fig4 = configurar_layout(fig4, "Evolução do Salário Mínimo")
fig4.update_layout(xaxis_title="Data", yaxis_title="Salário Mínimo (R$)")

# Gráficos organizados lado a lado, com gap pequeno
with st.container():
    col1, col2 = st.columns([1,1], gap="small")
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

with st.container():
    col3, col4 = st.columns([1,1], gap="small")
    with col3:
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.plotly_chart(fig4, use_container_width=True)
