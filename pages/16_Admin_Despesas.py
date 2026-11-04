import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import date
from auth import esta_logado
from config.empresa import EMPRESA
from database import (
    criar_despesa,
    listar_despesas,
    remover_despesa,
    total_despesas_mes,
)

cores = EMPRESA["cores"]

if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

st.markdown(f"""
<style>
    .desp-titulo {{
        color: {cores["secundaria"]};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .desp-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="desp-titulo">💸 Despesas</div>', unsafe_allow_html=True)
st.markdown('<div class="desp-sub">Registar e gerir as saídas da barbearia</div>', unsafe_allow_html=True)

st.divider()

# --- Seletor de mês/ano ---
hoje = date.today()
col_mes, col_ano = st.columns(2)
with col_mes:
    mes = st.selectbox(
        "Mês",
        options=list(range(1, 13)),
        index=hoje.month - 1,
        format_func=lambda m: [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        ][m - 1],
    )
with col_ano:
    ano = st.number_input("Ano", min_value=2020, max_value=2100, value=hoje.year, step=1)

despesas = listar_despesas(mes=mes, ano=ano)
total_mes = total_despesas_mes(mes, ano)

# --- Métricas ---
c1, c2 = st.columns(2)
c1.metric("📊 Nº de despesas", len(despesas))
c2.metric("💸 Total do mês", f"{total_mes:.2f}€")

st.divider()

# --- Formulário: nova despesa ---
with st.expander("➕ Adicionar despesa", expanded=(despesas.empty)):
    with st.form("form_nova_despesa", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            nova_data = st.date_input("Data", value=hoje)
        with col2:
            nova_categoria = st.selectbox(
                "Categoria",
                options=EMPRESA.get("categorias_despesa", ["📦 Outros"]),
            )

        col3, col4 = st.columns([2, 1])
        with col3:
            nova_descricao = st.text_input(
                "Descrição",
                placeholder="Ex.: Lâminas para máquina",
            )
        with col4:
            novo_valor = st.number_input(
                "Valor (€)",
                min_value=0.0,
                max_value=99999.99,
                value=10.0,
                step=0.5,
                format="%.2f",
            )

        criar = st.form_submit_button(
            "➕ Adicionar despesa", use_container_width=True, type="primary"
        )

        if criar:
            if novo_valor <= 0:
                st.error("O valor tem de ser maior que 0.")
            else:
                criar_despesa(
                    nova_data.strftime("%Y-%m-%d"),
                    nova_categoria,
                    nova_descricao.strip() or None,
                    float(novo_valor),
                )
                st.success(
                    f"✅ Despesa de **{novo_valor:.2f}€** adicionada "
                    f"({nova_categoria})."
                )
                st.rerun()

st.divider()

# --- Lista de despesas ---
st.markdown(f"### 📋 Despesas de {mes:02d}/{ano}")

if despesas.empty:
    st.info("📭 Sem despesas registadas neste mês.")
else:
    for _, d in despesas.iterrows():
        did = int(d["id"])
        data_fmt = d["data"]
        try:
            data_fmt = date.fromisoformat(str(d["data"])).strftime("%d/%m/%Y")
        except Exception:
            pass

        col_info, col_valor, col_acao = st.columns([4, 1, 1])
        with col_info:
            desc = d["descricao"] or "(sem descrição)"
            st.markdown(
                f"**{d['categoria']}** · {desc}  \n"
                f"<span style='color:#888; font-size:0.85rem;'>📅 {data_fmt}</span>",
                unsafe_allow_html=True,
            )
        with col_valor:
            st.markdown(
                f"<div style='text-align:right; color:{cores['secundaria']}; "
                f"font-weight:600; font-size:1.1rem;'>{float(d['valor']):.2f}€</div>",
                unsafe_allow_html=True,
            )
        with col_acao:
            if st.button("🗑️", key=f"del_desp_{did}", help="Remover despesa"):
                remover_despesa(did)
                st.success("Despesa removida.")
                st.rerun()

st.divider()
st.caption(f"Total do mês: **{total_mes:.2f}€** · {len(despesas)} despesa(s)")