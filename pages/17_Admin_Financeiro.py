import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from datetime import date
from auth import esta_logado
from config.empresa import EMPRESA
from database import (
    receita_mes,
    total_despesas_mes,
    despesas_por_categoria,
    receita_por_servico,
    evolucao_mensal,
    contar_marcacoes_mes,
    PONTOS_PARA_PREMIO,
)

cores = EMPRESA["cores"]
OURO = cores["secundaria"]

if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

st.markdown(f"""
<style>
    .fin-titulo {{
        color: {OURO};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .fin-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
    .lucro-card {{
        background: {cores["fundo"]};
        border: 1px solid #2a2a2a;
        border-left: 4px solid {OURO};
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
    }}
    .lucro-positivo {{
        border-left-color: #4a9d4a !important;
    }}
    .lucro-negativo {{
        border-left-color: #c0392b !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="fin-titulo">📊 Financeiro</div>', unsafe_allow_html=True)
st.markdown('<div class="fin-sub">Entradas, saídas e lucro da barbearia</div>', unsafe_allow_html=True)

st.divider()

# --- Seletor de mês/ano ---
hoje = date.today()
MESES_NOME = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
col_mes, col_ano = st.columns(2)
with col_mes:
    mes = st.selectbox(
        "Mês", list(range(1, 13)), index=hoje.month - 1,
        format_func=lambda m: MESES_NOME[m - 1],
    )
with col_ano:
    ano = st.number_input("Ano", min_value=2020, max_value=2100, value=hoje.year, step=1)

# --- Dados do mês ---
entradas = receita_mes(mes, ano)
saidas = total_despesas_mes(mes, ano)
lucro = entradas - saidas
n_concluidas = contar_marcacoes_mes(mes, ano, "concluida")
n_total = contar_marcacoes_mes(mes, ano)
ticket_medio = entradas / n_concluidas if n_concluidas > 0 else 0

# --- Bloco principal: Lucro ---
st.markdown(f"""
<div class="lucro-card {'lucro-positivo' if lucro >= 0 else 'lucro-negativo'}">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
            <div style="color:#888; font-size:0.85rem;">LUCRO DE {MESES_NOME[mes-1].upper()}/{ano}</div>
            <div style="color:{'#4a9d4a' if lucro >= 0 else '#c0392b'}; font-size:2.4rem; font-weight:bold;">
                {lucro:+.2f}€
            </div>
        </div>
        <div style="text-align:right; color:#b0b0b0; font-size:0.95rem; line-height:1.6;">
            <div>📥 Entradas: <b style="color:#4a9d4a;">{entradas:.2f}€</b></div>
            <div>📤 Saídas: <b style="color:#c0392b;">{saidas:.2f}€</b></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Métricas do mês ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("✂️ Marcações", n_total)
c2.metric("✅ Concluídas", n_concluidas)
c3.metric("🎯 Ticket médio", f"{ticket_medio:.2f}€")
c4.metric("📊 Margem", f"{(lucro/entradas*100) if entradas > 0 else 0:.0f}%")

st.divider()

# --- Gráfico: evolução 6 meses ---
st.markdown("### 📈 Evolução dos últimos 6 meses")

evolucao = evolucao_mensal(ano, meses=6)
df_evolucao = pd.DataFrame(evolucao)
df_evolucao["label"] = df_evolucao.apply(
    lambda r: f"{MESES_NOME[int(r['mes'])-1][:3]}/{int(r['ano']) % 100}", axis=1
)
df_evolucao = df_evolucao.set_index("label")[["receita", "despesas", "lucro"]]
df_evolucao.columns = ["Receita", "Despesas", "Lucro"]

st.bar_chart(df_evolucao, color=["#4a9d4a", "#c0392b", OURO])

st.divider()

# --- Duas colunas: receita por serviço + despesas por categoria ---
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### ✂️ Receita por serviço")
    rps = receita_por_servico(mes, ano)
    if rps.empty:
        st.info("Sem serviços concluídos neste mês.")
    else:
        rps_display = rps.copy()
        rps_display.columns = ["Serviço", "Nº", "Receita (€)"]
        rps_display["Receita (€)"] = rps_display["Receita (€)"].map(
            lambda v: f"{float(v):.2f}€"
        )
        st.dataframe(rps_display, use_container_width=True, hide_index=True)

with col_b:
    st.markdown("### 💸 Despesas por categoria")
    dpc = despesas_por_categoria(mes=mes, ano=ano)
    if dpc.empty:
        st.info("Sem despesas registadas neste mês.")
    else:
        dpc_display = dpc.copy()
        dpc_display.columns = ["Categoria", "Total (€)", "Nº"]
        dpc_display["Total (€)"] = dpc_display["Total (€)"].map(
            lambda v: f"{float(v):.2f}€"
        )
        st.dataframe(dpc_display, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    f"📥 {entradas:.2f}€ · 📤 {saidas:.2f}€ · "
    f"{'🟢' if lucro >= 0 else '🔴'} Lucro: {lucro:+.2f}€"
)