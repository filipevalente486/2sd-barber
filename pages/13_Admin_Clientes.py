import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from auth import esta_logado
from config.empresa import EMPRESA
from database import (
    get_conn,
    EMPRESA_ID,
    obter_pontos_cliente,
    resgatar_premio,
    historico_cliente,
    PONTOS_PARA_PREMIO,
    DESCRICAO_PREMIO,
)

cores = EMPRESA["cores"]

if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

st.markdown(f"""
<style>
    .cli-titulo {{
        color: {cores["secundaria"]};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .cli-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="cli-titulo">👥 Clientes</div>', unsafe_allow_html=True)
st.markdown('<div class="cli-sub">Lista, ranking e resgate de prémios</div>', unsafe_allow_html=True)

st.divider()


# --- Carregar todos os clientes ---
def _carregar_clientes():
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT id, nome, telefone, email, pontos, total_visitas, total_gasto, criado_em "
            "FROM clientes WHERE empresa_id = ? ORDER BY total_visitas DESC, nome",
            conn, params=(EMPRESA_ID,),
        )


clientes = _carregar_clientes()

if clientes.empty:
    st.info("Ainda não há clientes registados. As marcações criam automaticamente o cliente.")
    st.stop()

# --- Métricas gerais ---
total_clientes = len(clientes)
total_visitas = int(clientes["total_visitas"].sum())
pontos_circulacao = int(clientes["pontos"].sum())
clientes_com_premio = int((clientes["pontos"] >= PONTOS_PARA_PREMIO).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Clientes", total_clientes)
c2.metric("✂️ Visitas totais", total_visitas)
c3.metric("🎯 Pontos em circulação", pontos_circulacao)
c4.metric(f"🎁 Prémios disponíveis", clientes_com_premio)

st.divider()

# --- Pesquisa ---
st.markdown("### 🔍 Pesquisar cliente")
col_pesq, col_filtro = st.columns([3, 1])
with col_pesq:
    termo = st.text_input(
        "Pesquisar por nome ou telefone",
        placeholder="Ex.: João ou 912345678",
        label_visibility="collapsed",
    )
with col_filtro:
    so_com_premio = st.checkbox("Só com prémio", value=False)

filtrados = clientes.copy()
if termo.strip():
    t = termo.strip().lower()
    filtrados = filtrados[
        filtrados["nome"].str.lower().str.contains(t, na=False)
        | filtrados["telefone"].astype(str).str.contains(t, na=False)
    ]
if so_com_premio:
    filtrados = filtrados[filtrados["pontos"] >= PONTOS_PARA_PREMIO]

st.caption(f"{len(filtrados)} cliente(s) encontrado(s)")
st.divider()

# --- Ranking Top 10 ---
st.markdown("### 🏆 Top 10 por visitas")
top10 = clientes.head(10).copy()
top10_display = top10[["nome", "telefone", "total_visitas", "pontos", "total_gasto"]].copy()
top10_display.columns = ["Cliente", "Telefone", "Visitas", "Pontos", "Total gasto ()"]
top10_display["Total gasto ()"] = top10_display["Total gasto ()"].map(lambda v: f"{float(v or 0):.2f}")
top10_display.index = range(1, len(top10_display) + 1)
st.dataframe(top10_display, use_container_width=True)

st.divider()

# --- Lista detalhada + ações por cliente ---
st.markdown("### 📋 Lista de clientes")

if filtrados.empty:
    st.info("Nenhum cliente corresponde aos filtros.")
    st.stop()

for _, c in filtrados.iterrows():
    cid = int(c["id"])
    nome = c["nome"]
    tel = c["telefone"]
    pontos = int(c["pontos"] or 0)
    visitas = int(c["total_visitas"] or 0)
    gasto = float(c["total_gasto"] or 0)
    tem_premio = pontos >= PONTOS_PARA_PREMIO

    header = (
        f"👤 **{nome}** · 📱 {tel} · ✂️ {visitas} visitas · "
        f"🎯 {pontos} pts · 💶 {gasto:.2f}"
        + (" · 🎁 PRÉMIO!" if tem_premio else "")
    )

    with st.expander(header, expanded=False):
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("🎯 Pontos", pontos)
        col_b.metric("✂️ Visitas", visitas)
        col_c.metric("💶 Gasto", f"{gasto:.2f}")

        st.markdown("---")

        # Resgate de prémio
        st.markdown(f"#### 🎁 Resgate de prémio")
        st.caption(f"Prémio: **{DESCRICAO_PREMIO}** · Custo: **{PONTOS_PARA_PREMIO} pontos**")

        if not tem_premio:
            faltam = PONTOS_PARA_PREMIO - pontos
            st.info(f"Faltam **{faltam}** ponto(s) para o prémio.")
        else:
            st.success(f"✅ Este cliente tem prémio disponível ({pontos} pontos).")
            confirmar = st.checkbox(
                f"Confirmo o resgate de **{PONTOS_PARA_PREMIO} pontos** para **{nome}**",
                key=f"confirmar_resgate_{cid}",
            )
            if st.button(
                f"🎁 Resgatar {DESCRICAO_PREMIO}",
                key=f"btn_resgate_{cid}",
                type="primary",
                disabled=not confirmar,
            ):
                ok, msg = resgatar_premio(cid)
                if ok:
                    st.balloons()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")

        # Histórico de fidelização
        st.markdown("#### 📜 Histórico de fidelização")
        hist = historico_cliente(cid)
        if hist.empty:
            st.caption("Sem histórico ainda.")
        else:
            hist_display = hist.copy()
            hist_display.columns = ["Tipo", "Pontos", "Descrição", "Data"]
            st.dataframe(hist_display, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    f"Total: {total_clientes} clientes · "
    f"{clientes_com_premio} com prémio disponível · "
    f"Prémio: {DESCRICAO_PREMIO} ({PONTOS_PARA_PREMIO} pontos)"
)
