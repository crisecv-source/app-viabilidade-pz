import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go

# Configuração inicial da página para tela cheia
st.set_page_config(page_title="Viabilidade", layout="wide")

# ==========================================
# ESTILO VISUAL (CSS) - INSPIRADO NO DASHBOARD
# ==========================================
st.markdown("""
<style>
    /* Fundo geral da página (Azul Escuro/Roxo) */
    .stApp {
        background-color: #12141E;
    }
    
    /* Fundo da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #1A1D2A;
        border-right: 1px solid #2B2F42;
    }
    
    /* Textos principais e cabeçalhos em cinza claro/branco */
    h1, h2, h3, p, label, .stMarkdown {
        color: #D1D4DC !important;
    }
    
    /* Personalização das "Caixas" dos KPIs (Métricas) */
    [data-testid="stMetric"] {
        background-color: #212534;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2E3346;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }
    
    /* Valor numérico gigante do KPI em branco para destacar */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: bold;
    }
    
    /* Separadores (linhas) do aplicativo */
    hr {
        border-color: #2E3346 !important;
    }
    
    /* Fundo dos gráficos para bater com os cards */
    .stPlotlyChart {
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏢 Análise de Viabilidade:")
st.markdown("Preencha os dados na barra lateral esquerda para simular os indicadores e o fluxo do caixa do empreendimento.")

# ==========================================
# BARRA LATERAL: ENTRADAS BASE DE DADOS
# ==========================================
st.sidebar.header("1. Quadro de Áreas (m²)")
area_construida = st.sidebar.number_input("Área Total Construída", min_value=0.0, value=10000.0, step=100.0)
area_privativa = st.sidebar.number_input("Área Privativa (Residencial)", min_value=0.0, value=6500.0, step=100.0)
area_comercial = st.sidebar.number_input("Área Comercial (Mall)", min_value=0.0, value=1000.0, step=100.0)
area_permuta = st.sidebar.number_input("Área de Permuta (Residencial)", min_value=0.0, value=500.0, step=100.0)
area_locacao = st.sidebar.number_input("Área de Locação (ABL)", min_value=0.0, value=500.0, step=100.0)

st.sidebar.divider()

st.sidebar.header("2. Índices e Preços (R$)")
cub = st.sidebar.number_input("CUB atual (R$)", min_value=0.0, value=3000.0, step=50.0)
venda_resid_m2 = st.sidebar.number_input("Venda Residencial (R$/m²)", min_value=0.0, value=9500.0, step=100.0)
venda_com_m2 = st.sidebar.number_input("Venda Comercial (R$/m²)", min_value=0.0, value=12000.0, step=100.0)
locacao_m2 = st.sidebar.number_input("Locação ABL (R$/m²)", min_value=0.0, value=80.0, step=5.0)

st.sidebar.divider()

st.sidebar.header("3. Cronograma (Datas)")
# Usando ano base atual
hoje = datetime.date.today()
inicio_vendas = st.sidebar.date_input("Início das Vendas", value=hoje)
inicio_obras = st.sidebar.date_input("Início das Obras", value=hoje.replace(month=(hoje.month % 12) + 1))
entrega_obra = st.sidebar.date_input("Entrega da Obra", value=hoje.replace(year=hoje.year + 3))

st.sidebar.divider()

st.sidebar.header("4. Condições Comerciais (%)")
st.sidebar.caption("Como os clientes vão pagar:")
pct_entrada = st.sidebar.number_input("Sinal/Entrada (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
pct_mensais = st.sidebar.number_input("Parcelas Mensais (Obra) (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
pct_chaves = st.sidebar.number_input("Financiamento/Chaves (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)

if (pct_entrada + pct_mensais + pct_chaves) != 100.0:
    st.sidebar.error("A soma das condições comerciais deve ser exatamente 100%.")

# ==========================================
# CÁLCULOS: COLUNA G E VGV TOTAL
# ==========================================
if area_construida > 0:
    pct_privativa = (area_privativa / area_construida) * 100
    pct_comercial = (area_comercial / area_construida) * 100
    pct_permuta = (area_permuta / area_construida) * 100
    pct_locacao = (area_locacao / area_construida) * 100
else:
    pct_privativa = pct_comercial = pct_permuta = pct_locacao = 0.0

vgv_residencial = area_privativa * venda_resid_m2
vgv_comercial = area_comercial * venda_com_m2
vgv_permuta = area_permuta * venda_resid_m2
vgv_locacao = area_locacao * locacao_m2 * 100 

vgv_total = vgv_residencial + vgv_comercial + vgv_permuta + vgv_locacao

# ==========================================
# TELA PRINCIPAL: KPIs DE DESTAQUE
# ==========================================
st.subheader("🏆 Principais Indicadores")

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("VGV TOTAL ESTIMADO", f"R$ {vgv_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

delta_color = "normal" if pct_privativa >= 50 else "inverse"
kpi2.metric(
    "Eficiência do Projeto", 
    f"{pct_privativa:.1f}%",
    delta="Atenção à eficiência" if pct_privativa < 50 else "Boa eficiência",
    delta_color=delta_color
)

custo_cub_estimado = area_construida * cub
kpi3.metric("Custo Físico Base", f"R$ {custo_cub_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

# ==========================================
# TELA PRINCIPAL: RESUMO DE ÁREAS E COMPOSIÇÃO
# ==========================================
col_vgv, col_areas = st.columns([2, 1])

with col_vgv:
    st.markdown("##### 💰 Composição do VGV")
    df_vgv = pd.DataFrame({
        "Categoria": ["Residencial", "Comercial (Mall)", "Permuta Residencial", "Locação (Ativo)"],
        "Valor (R$)": [vgv_residencial, vgv_comercial, vgv_permuta, vgv_locacao]
    })
    st.dataframe(df_vgv.style.format({"Valor (R$)": "R$ {:,.2f}"}), hide_index=True, use_container_width=True)

with col_areas:
    st.markdown("##### 📐 Quadro de Áreas")
    st.write(f"**Área Total Construída:** {area_construida} m² (100%)")
    st.write(f"**Comercial / Total:** {pct_comercial:.1f}%")
    st.write(f"**Permuta / Total:** {pct_permuta:.1f}%")
    st.write(f"**Locação / Total:** {pct_locacao:.1f}%")

st.divider()

# ==========================================
# CÁLCULOS E TELA: CUSTOS E VGV LÍQUIDO
# ==========================================
st.subheader("📉 Custos e VGV Líquido")

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    pct_obra = st.slider("Obra (% do VGV)", 0.0, 80.0, 40.0, 0.5) / 100
    pct_despesas = st.slider("Despesas Diversas (%)", 0.0, 15.0, 2.0, 0.1) / 100
    pct_outorga = st.slider("Outorga Onerosa (%)", 0.0, 10.0, 1.0, 0.1) / 100

with col_c2:
    pct_monitoramento = st.slider("Monitoramento/Medição (%)", 0.0, 5.0, 0.5, 0.1) / 100
    pct_comercial_com = st.slider("Comercial/Comissões (%)", 0.0, 15.0, 4.0, 0.5) / 100
    pct_tributario = st.slider("Tributos/RET (%)", 0.0, 10.0, 4.0, 0.5) / 100

with col_c3:
    pct_marketing = st.slider("Marketing (%)", 0.0, 10.0, 2.0, 0.1) / 100
    pct_adm = st.slider("Administração/Controle (%)", 0.0, 10.0, 3.0, 0.1) / 100
    pct_financeiro = st.slider("Custo Financeiro (%)", 0.0, 15.0, 1.5, 0.1) / 100

custos_totais = {
    "Obra": vgv_total * pct_obra,
    "Despesas": vgv_total * pct_despesas,
    "Outorga": vgv_total * pct_outorga,
    "Monitoramento/Medição": vgv_total * pct_monitoramento,
    "Comercial (Comissões)": vgv_total * pct_comercial_com,
    "Tributário (RET)": vgv_total * pct_tributario,
    "Marketing": vgv_total * pct_marketing,
    "Administração/Controle": vgv_total * pct_adm,
    "Custo Financeiro": vgv_total * pct_financeiro
}

total_custos_reais = sum(custos_totais.values())
vgv_liquido = vgv_total - total_custos_reais

df_custos = pd.DataFrame(list(custos_totais.items()), columns=['Item de Custo', 'Valor (R$)'])

col_res1, col_res2 = st.columns([1, 1])

with col_res1:
    st.dataframe(df_custos.style.format({"Valor (R$)": "R$ {:,.2f}"}), hide_index=True, use_container_width=True)

with col_res2:
    st.info("📊 **RESULTADO DA SIMULAÇÃO (VGV LÍQUIDO)**")
    st.metric("Total de Custos Estimados", f"R$ {total_custos_reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("VGV LÍQUIDO", f"R$ {vgv_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    if vgv_total > 0:
        margem_liquida = (vgv_liquido / vgv_total) * 100
        st.metric("Margem Líquida (% do VGV)", f"{margem_liquida:.2f}%")

st.divider()

# ==========================================
# CÁLCULOS: FLUXO DE CAIXA E EXPOSIÇÃO
# ==========================================
st.subheader("📈 Fluxo de Caixa (Dashboard Neon)")

dt_inicio_vendas = pd.to_datetime(inicio_vendas).replace(day=1)
dt_inicio_obras = pd.to_datetime(inicio_obras).replace(day=1)
dt_entrega_obra = pd.to_datetime(entrega_obra).replace(day=1)

start_date = min(dt_inicio_vendas, dt_inicio_obras)
end_date = dt_entrega_obra

if start_date < end_date:
    meses_projeto = pd.date_range(start=start_date, end=end_date, freq='MS')
    df_fc = pd.DataFrame({'Data': meses_projeto})
    df_fc['Mês/Ano'] = df_fc['Data'].dt.strftime('%m/%Y')
    df_fc['Receitas (Entradas)'] = 0.0
    df_fc['Custos (Saídas)'] = 0.0

    mask_obras = (df_fc['Data'] >= dt_inicio_obras) & (df_fc['Data'] <= dt_entrega_obra)
    meses_de_obra = mask_obras.sum()
    if meses_de_obra > 0:
        df_fc.loc[mask_obras, 'Custos (Saídas)'] = -(total_custos_reais / meses_de_obra)
        
    vgv_para_venda = vgv_residencial + vgv_comercial
    val_entrada = vgv_para_venda * (pct_entrada / 100)
    val_mensais = vgv_para_venda * (pct_mensais / 100)
    val_chaves = vgv_para_venda * (pct_chaves / 100)

    if dt_inicio_vendas in df_fc['Data'].values:
        df_fc.loc[df_fc['Data'] == dt_inicio_vendas, 'Receitas (Entradas)'] += val_entrada
    if dt_entrega_obra in df_fc['Data'].values:
        df_fc.loc[df_fc['Data'] == dt_entrega_obra, 'Receitas (Entradas)'] += val_chaves
        
    mask_vendas = (df_fc['Data'] > dt_inicio_vendas) & (df_fc['Data'] <= dt_entrega_obra)
    meses_de_venda = mask_vendas.sum()
    if meses_de_venda > 0:
        df_fc.loc[mask_vendas, 'Receitas (Entradas)'] += (val_mensais / meses_de_venda)
        
    df_fc['Saldo Mês'] = df_fc['Receitas (Entradas)'] + df_fc['Custos (Saídas)']
    df_fc['Saldo Acumulado'] = df_fc['Saldo Mês'].cumsum()

    # --- GRÁFICO (PLOTLY) COM TEMA DARK NEON ---
    fig = go.Figure()
    
    # Barra de Receitas (Verde Neon)
    fig.add_trace(go.Bar(x=df_fc['Mês/Ano'], y=df_fc['Receitas (Entradas)'], name='Receitas (+)', marker_color='#00E676'))
    
    # Barra de Custos (Laranja Neon)
    fig.add_trace(go.Bar(x=df_fc['Mês/Ano'], y=df_fc['Custos (Saídas)'], name='Custos (-)', marker_color='#FF7A00'))
    
    # Linha de Saldo Acumulado (Roxo brilhante com preenchimento)
    fig.add_trace(go.Scatter(
        x=df_fc['Mês/Ano'], y=df_fc['Saldo Acumulado'], 
        name='Caixa Acumulado', 
        mode='lines+markers', 
        line=dict(color='#B388FF', width=4),
        marker=dict(size=6, color='#FFFFFF', line=dict(width=2, color='#B388FF'))
    ))

    # Layout com fundo igual ao dos Cards
    fig.update_layout(
        plot_bgcolor='#212534',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#D1D4DC'),
        barmode='relative',
        xaxis=dict(showgrid=True, gridcolor='#2E3346', title="Meses do Empreendimento"),
        yaxis=dict(showgrid=True, gridcolor='#2E3346', title="Valores (R$)"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    exposicao_maxima = df_fc['Saldo Acumulado'].min()
    if exposicao_maxima < 0:
        mes_pior_cenario = df_fc.loc[df_fc['Saldo Acumulado'].idxmin(), 'Mês/Ano']
        st.error(f"⚠️ **Exposição Máxima de Caixa:** R$ {abs(exposicao_maxima):,.2f} (atingida no mês {mes_pior_cenario})".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.success("✅ Nenhuma exposição de caixa prevista.")

else:
    st.error("Erro nas Datas: A entrega da obra não pode ser antes do início das vendas/obras.")

st.divider()

# ==========================================
# TABELA DE TIPOLOGIAS (Editável)
# ==========================================
st.subheader("📋 Quadro de Tipologias")

dados_iniciais = pd.DataFrame({
    "Tipologia": ["2 Quartos (Suíte)", "3 Quartos (Suíte)", "Cobertura", "Loja"],
    "Quantidade": [40, 20, 4, 5],
    "Área Privativa Unit. (m²)": [65.0, 90.0, 150.0, 200.0],
    "Vagas por Unidade": [1, 2, 3, 0]
})

df_tipologias = st.data_editor(dados_iniciais, num_rows="dynamic", use_container_width=True)

total_unidades = df_tipologias["Quantidade"].sum()
st.caption(f"**Total de unidades:** {total_unidades}")