import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from config.empresa import EMPRESA
from components.carousel import render_carousel

cores = EMPRESA["cores"]
ouro = cores["secundaria"]

# CSS global — força dourado no botão primary e no título
st.markdown(f
<style>
    .titulo-hero {{
        font-size: 2rem;
        font-weight: bold;
        color: {ouro} !important;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }}
    .subtitulo {{
        text-align: center;
        color: {cores["texto_secundario"]};
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }}

    /* Botão primary — força dourado (várias versões do Streamlit) */
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="stBaseButton-primary"],
    div.stButton > button[data-testid="baseButton-primary"],
    .stButton > button[kind="primary"] {{
        background-color: {ouro} !important;
        color: #000000 !important;
        border: 1px solid {ouro} !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid="stBaseButton-primary"]:hover,
    div.stButton > button[data-testid="baseButton-primary"]:hover {{
        background-color: #e6c84a !important;
        border-color: #e6c84a !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4) !important;
    }}
</style>
, unsafe_allow_html=True)

# Título e subtítulo com estilo inline (mais robusto que classes)
st.markdown(
    f'<div style="font-size:5rem; font-weight:bold; color:{ouro}; '
    f'text-align:center; margin-bottom:0.5rem; letter-spacing:1px;">2SD.Barber</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div style="text-align:center; color:{cores["texto_secundario"]}; '
    f'font-size:1.1rem; margin-bottom:2rem;">Estilo e precisão em cada corte</div>',
    unsafe_allow_html=True,
)

#render_carousel(EMPRESA["carousel_imagens"], altura=200)

st.markdown('<br>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("✂️ Fazer marcação", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Marcar.py")

st.markdown('<br>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('### 🕐 Horário')
    st.write("Seg–Sáb: 09h–19h")
    st.write("Domingo: **Sob consulta**")
with c2:
    st.markdown('### 📍 Onde estamos')
    st.write(EMPRESA['morada']['rua'])
    st.write(f"{EMPRESA['morada']['codigo_postal']} {EMPRESA['morada']['cidade']}")
with c3:
    st.markdown('### 🎁 Fidelização')
    st.write("1 corte = 1 ponto")
    st.write("5 pontos = **corte grátis**")
    if st.button("Ver os meus pontos", use_container_width=True):
        st.switch_page("pages/5_Consultar_Pontos.py")

st.divider()
st.markdown(f'''
<div style="text-align:center;color:#888;padding:1rem 0">
    <p>📞 {EMPRESA['contacto']['telefone']} · 📷 {EMPRESA['contacto']['instagram']}</p>
    <p style="font-size:0.85rem">© 2026 2SD.Barber</p>
</div>
''', unsafe_allow_html=True)