import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Viabilidade - Allie", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #12141E; }
    [data-testid="stSidebar"] { background-color: #1A1D2A; border-right: 1px solid #2B2F42; }
    h1, h2, h3, p, label, .stMarkdown { color: #D1D4DC !important; }
    [data-testid="stMetric"] {
        background-color: #212534;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2E3346;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    hr { border-color: #2E3346 !important; }
    .stPlotlyChart { background-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.title("🏢 Análise de Viabilidade: Allie Empreendimentos")
st.markdown("Preencha os dados na barra lateral para iniciar a simulação.")

st.sidebar.header("1. Quadro de Áreas (m²)")
area_construida = st.sidebar.number_input("Área Total Construída", min_value=0.0, value=0.0, step=100.0)
area_privativa = st.sidebar.number_input("Área Privativa (Residencial)", min_value=0.0, value=0.0, step=100.0)
area_comercial = st.sidebar.number_input("Área Comercial (Mall)", min_value=0.0, value=0.0, step=100.0)
area_permuta = st.sidebar.number_input("Área de Permuta (Residencial)", min_value=0.0, value=0.0, step=100.0)
area_locacao = st.sidebar.number_input("Área de Locação (ABL)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.divider()

st.sidebar.header("2. Índices e Preços (R$)")
cub = st.sidebar.number_input("CUB atual (R$)", min_value=0.0, value=0.0, step=50.0)
venda_resid_m2 = st.sidebar.number_input("Venda Residencial (R$/m²)", min_value=0.0, value=0.0, step=100.0)
venda_com_m2 = st.sidebar.number_input("Venda Comercial (R$/m²)", min_value=0.0, value=0.0, step=100.0)
locacao_m2 = st.sidebar.number_input("Locação ABL (R$/m²)", min_value=0.0, value=0.0, step=5.0)

st.sidebar.divider()

st.sidebar.header("3. Cronograma (Datas)")
hoje = datetime.date.today()
inicio_vendas = st.sidebar.date_input("Início das Vendas", value=hoje)
inicio_obras = st.sidebar.date_input("Início das Obras", value=hoje)
entrega_obra = st.sidebar.date_input("Entrega da Obra", value=hoje)

st.sidebar.divider()

st.sidebar.header("4. Condições Comerciais (%)")
pct_entrada = st.sidebar.number_input("Sinal/Entrada (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
pct_mensais = st.sidebar.number_input("Parcelas Mensais (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
pct_chaves = st.sidebar.number_input("Financiamento/Chaves (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

if area_construida > 0:
    pct_privativa = (area_privativa / area_construida) * 100
else:
    pct_privativa = 0.0

vgv_residencial = area_privativa * venda_resid_m2
vgv_comercial = area_comercial * venda_com_m2
vgv_permuta = area_permuta * venda_resid_m2
vgv_locacao = area_locacao * locacao_m2 * 100 
vgv_total = vgv_residencial + vgv_comercial + vgv_permuta + vgv_locacao

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("VGV TOTAL ESTIMADO", f"R$ {vgv_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
kpi2.metric("Eficiência do Projeto", f"{pct_privativa:.1f}%")
custo_cub_base = area_construida * cub
kpi3.metric("Custo Físico Base", f"R$ {custo_cub_base:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

st.subheader("Custos e Despesas (% do VGV ou Fator CUB)")
col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    fator_obra = st.slider("Fator de Obra (x CUB)", 0.0, 2.0, 0.0, 0.05)
    pct_despesas = st.slider("Despesas Diversas (%)", 0.0, 15.0, 0.0, 0.1) / 100
    pct_outorga = st.slider("Outorga Onerosa (%)", 0.0, 10.0, 0.0, 0.1) / 100

with col_c2:
    pct_monitoramento = st.slider("Monitoramento/Medição (%)", 0.0, 5.0, 0.0, 0.1) / 100
    pct_comercial_com = st.slider("Comercial/Comissões (%)", 0.0, 15.0, 0.0, 0.5) / 100
    pct_tributario = st.slider("Tributos/RET (%)", 0.0, 10.0, 0.0, 0.5) / 100

with col_c3:
    pct_marketing = st.slider("Marketing (%)", 0.0, 10.0, 0.0, 0.1) / 100
    pct_adm = st.slider("Administração/Controle (%)", 0.0, 10.0, 0.0, 0.1) / 100
    pct_financeiro = st.slider("Custo Financeiro (%)", 0.0, 15.0, 0.0, 0.1) / 100

custos_totais = {
    "Obra": area_construida * cub * fator_obra,
    "Despesas": vgv_total * pct_despesas,
    "Outorga": vgv_total * pct_outorga,
    "Monitoramento": vgv_total * pct_monitoramento,
    "Comercial": vgv_total * pct_comercial_com,
    "Tributário": vgv_total * pct_tributario,
    "Marketing": vgv_total * pct_marketing,
    "Administração": vgv_total * pct_adm,
    "Custo Financeiro": vgv_total * pct_financeiro
}

total_custos_reais = sum(custos_totais.values())
vgv_liquido = vgv_total - total_custos_reais

st.metric("TOTAL DE CUSTOS ESTIMADOS", f"R$ {total_custos_reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.metric("VGV LÍQUIDO", f"R$ {vgv_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

if inicio_obras < entrega_obra:
    meses_projeto = pd.date_range(start=inicio_obras, end=entrega_obra, freq='MS')
    df_fc = pd.DataFrame({'Data': meses_projeto})
    df_fc['Mês/Ano'] = df_fc['Data'].dt.strftime('%m/%Y')
    df_fc['Receitas'] = 0.0
    df_fc['Custos'] = -(total_custos_reais / len(meses_projeto)) if len(meses_projeto) > 0 else 0
    df_fc['Saldo Acumulado'] = (df_fc['Receitas'] + df_fc['Custos']).cumsum()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_fc['Mês/Ano'], y=df_fc['Receitas'], name='Receitas', marker_color='#00E676'))
    fig.add_trace(go.Bar(x=df_fc['Mês/Ano'], y=df_fc['Custos'], name='Custos', marker_color='#FF7A00'))
    fig.add_trace(go.Scatter(x=df_fc['Mês/Ano'], y=df_fc['Saldo Acumulado'], name='Caixa Acumulado', line=dict(color='#B388FF', width=4)))
    fig.update_layout(plot_bgcolor='#212534', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#D1D4DC'), barmode='relative')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("📋 Quadro de Tipologias")
st.data_editor(pd.DataFrame({"Tipologia": ["-"], "Quantidade": [0], "Área": [0.0], "Vagas": [0]}), num_rows="dynamic", use_container_width=True)