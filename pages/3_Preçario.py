import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from config.empresa import EMPRESA
from database import listar_servicos

cores = EMPRESA["cores"]

st.markdown(f"""
<style>
    .preco-hero {{
        text-align: center;
        padding: 0.5rem 0 1.5rem 0;
    }}
    .preco-hero h1 {{
        color: {cores["secundaria"]};
        font-size: 2.4rem;
        margin-bottom: 0.2rem;
    }}
    .preco-hero p {{
        color: {cores["texto_secundario"]};
        font-size: 1rem;
    }}
    .card-link {{
        text-decoration: none !important;
        display: block;
        cursor: pointer;
    }}
    .servico-card {{
        background: {cores["fundo"]};
        border: 1px solid #2a2a2a;
        border-top: 4px solid {cores["secundaria"]};
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
        height: 175px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
    }}
    .card-link:hover .servico-card {{
        border-color: {cores["secundaria"]};
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(212,175,55,0.25);
    }}
    .servico-topo {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.5rem;
    }}
    .servico-nome {{
        color: {cores["texto"]};
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.25;
    }}
    .servico-preco {{
        color: {cores["secundaria"]};
        font-size: 1.5rem;
        font-weight: bold;
        white-space: nowrap;
    }}
    .servico-desc {{
        color: {cores["texto_secundario"]};
        font-size: 0.85rem;
        line-height: 1.35;
        margin: 0.5rem 0;
        flex: 1;
    }}
    .servico-meta {{
        color: #888;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .servico-cta {{
        color: {cores["secundaria"]};
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .nota-final {{
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        padding: 1rem 0 0 0;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="preco-hero">
    <h1>💰 Preçário</h1>
    <p>Clique num serviço para marcar diretamente</p>
</div>
""", unsafe_allow_html=True)

servicos = listar_servicos()
if servicos.empty:
    st.warning("Sem serviços configurados.")
    st.stop()

servicos = servicos.reset_index(drop=True)

COLS = 3
for linha_inicio in range(0, len(servicos), COLS):
    cols = st.columns(COLS, gap="medium")
    bloco = servicos.iloc[linha_inicio:linha_inicio + COLS]
    for idx, (_, row) in enumerate(bloco.iterrows()):
        sid = int(row["id"])
        nome = row["nome"]
        desc = row["descricao"] or ""
        dur = int(row["duracao_min"])
        preco = float(row["preco"]) if row["preco"] is not None else 0.0

        link = f"/marcar?servico={sid}"
        with cols[idx]:
            st.markdown(f"""
            <a class="card-link" href="{link}" target="_self">
                <div class="servico-card">
                    <div>
                        <div class="servico-topo">
                            <div class="servico-nome">{nome}</div>
                            <div class="servico-preco">{preco:.2f}€</div>
                        </div>
                        <div class="servico-desc">{desc}</div>
                    </div>
                    <div class="servico-meta">
                        <span>⏱️ {dur} min</span>
                        <span class="servico-cta">Marcar →</span>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✂️ Ver todos os serviços", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Marcar.py")

st.markdown("""
<div class="nota-final">
    Preços com IVA incluído · Pagamento em numerário ou MBWay
</div>
""", unsafe_allow_html=True)
