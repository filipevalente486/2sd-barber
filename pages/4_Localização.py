import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import quote
from config.empresa import EMPRESA, DIAS_SEMANA

cores = EMPRESA["cores"]
contacto = EMPRESA["contacto"]
morada = EMPRESA["morada"]
horario = EMPRESA["horario_funcionamento"]

st.markdown(f"""
<style>
    .local-hero {{
        text-align: center;
        padding: 0.5rem 0 2rem 0;
    }}
    .local-hero h1 {{
        color: {cores["secundaria"]};
        font-size: 2.4rem;
        margin-bottom: 0.3rem;
    }}
    .local-hero p {{
        color: {cores["texto_secundario"]};
        font-size: 1rem;
    }}
    .info-card {{
        background: {cores["fundo"]};
        border: 1px solid #2a2a2a;
        border-left: 4px solid {cores["secundaria"]};
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }}
    .info-card h3 {{
        color: {cores["secundaria"]};
        font-size: 1.05rem;
        margin: 0 0 0.6rem 0;
    }}
    .info-card p {{
        color: {cores["texto"]};
        margin: 0.2rem 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    .info-card a {{
        color: {cores["secundaria"]};
        text-decoration: none;
    }}
    .info-card a:hover {{
        text-decoration: underline;
    }}
    .horario-linha {{
        display: flex;
        justify-content: space-between;
        color: {cores["texto"]};
        font-size: 0.92rem;
        padding: 0.25rem 0;
        border-bottom: 1px dashed #2a2a2a;
    }}
    .horario-linha:last-child {{
        border-bottom: none;
    }}
    .horario-dia {{
        color: {cores["texto_secundario"]};
    }}
    .horario-fechado {{
        color: #666;
        font-style: italic;
    }}
    .btn-row {{
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 0.8rem;
    }}
    .btn-acao {{
        display: inline-block;
        padding: 0.55rem 1.1rem;
        background: {cores["secundaria"]};
        color: #000;
        font-weight: 600;
        border-radius: 8px;
        text-decoration: none !important;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }}
    .btn-acao:hover {{
        background: #e6c84a;
        transform: translateY(-2px);
    }}
    .btn-acao.secundario {{
        background: transparent;
        color: {cores["secundaria"]};
        border: 1px solid {cores["secundaria"]};
    }}
    .btn-acao.secundario:hover {{
        background: {cores["secundaria"]};
        color: #000;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="local-hero">
    <h1>📍 Onde estamos</h1>
    <p>Venha visitar-nos</p>
</div>
""", unsafe_allow_html=True)

col_esq, col_dir = st.columns([1, 1.3], gap="large")

# ----- Coluna esquerda: informação -----
with col_esq:
    morada_completa = f"{morada['rua']}<br>{morada['codigo_postal']} {morada['cidade']}"
    st.markdown(f"""
    <div class="info-card">
        <h3>🏠 Morada</h3>
        <p>{morada_completa}</p>
    </div>
    """, unsafe_allow_html=True)

    tel_limpo = contacto["telefone"].replace(" ", "")
    wa_num = contacto["whatsapp"]
    wa_msg = quote("Olá! Gostaria de mais informações.")
    st.markdown(f"""
    <div class="info-card">
        <h3>📞 Contactos</h3>
        <p>📱 <a href="tel:{tel_limpo}">{contacto['telefone']}</a></p>
        <p>✉️ <a href="mailto:{contacto['email']}">{contacto['email']}</a></p>
        <p>📷 <a href="https://instagram.com/{contacto['instagram'].lstrip('@')}" target="_blank">{contacto['instagram']}</a></p>
        <div class="btn-row">
            <a class="btn-acao" href="tel:{tel_limpo}">📞 Ligar</a>
            <a class="btn-acao secundario" href="https://wa.me/{wa_num}?text={wa_msg}" target="_blank">💬 WhatsApp</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    notas = EMPRESA.get("notas_horario", {})
    linhas = []
    for dia_num in range(7):
        nome = DIAS_SEMANA[dia_num]
        h = horario.get(dia_num)
        nota = notas.get(dia_num)
        if h is None:
            texto = nota if nota else "Fechado"
            linhas.append(f'<div class="horario-linha"><span class="horario-dia">{nome}</span><span class="horario-fechado">{texto}</span></div>')
        else:
            linhas.append(f'<div class="horario-linha"><span class="horario-dia">{nome}</span><span>{h[0]} – {h[1]}</span></div>')

    st.markdown(f"""
    <div class="info-card">
        <h3>🕐 Horário</h3>
        {''.join(linhas)}
    </div>
    """, unsafe_allow_html=True)

# ----- Coluna direita: mapa -----
with col_dir:
    st.markdown("""
    <div class="info-card" style="border-left-color:#2a2a2a;">
        <h3>🗺️ Mapa</h3>
    """, unsafe_allow_html=True)

    endereco_query = quote(f"{morada['rua']}, {morada['codigo_postal']} {morada['cidade']}")
    maps_embed = f"https://maps.google.com/maps?q={endereco_query}&t=&z=15&ie=UTF8&iwloc=&output=embed"

    components.html(
        f'<iframe src="{maps_embed}" width="100%" height="420" '
        f'style="border:0; border-radius:8px;" allowfullscreen="" loading="lazy" '
        f'referrerpolicy="no-referrer-when-downgrade"></iframe>',
        height=430,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:1rem;">
        <a class="btn-acao" href="{morada['google_maps_url']}" target="_blank">
            🧭 Abrir no Google Maps
        </a>
    </div>
    """, unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✂️ Fazer marcação", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Marcar.py")
