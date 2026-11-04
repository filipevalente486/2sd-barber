import streamlit as st
from pathlib import Path
from config.empresa import EMPRESA

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _encontrar_logo():
    for nome in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp"):
        p = ASSETS_DIR / nome
        if p.exists():
            return p
    return None


def render_header(titulo, subtitulo=""):
    logo = _encontrar_logo()
    insta = EMPRESA["contacto"]["instagram"].lstrip("@")
    cor_ouro = EMPRESA["cores"]["secundaria"]
    cor_sub = EMPRESA["cores"]["texto_secundario"]

    col_logo, col_titulo, col_insta = st.columns([1, 3, 1])

    with col_logo:
        if logo:
            st.image(str(logo), width=70)

    with col_titulo:
        html = (
            f'<div style="text-align:center;">'
            f'<div style="color:{cor_ouro}; font-size:1.8rem; font-weight:bold; '
            f'line-height:1.2;">{titulo}</div>'
        )
        if subtitulo:
            html += (
                f'<div style="color:{cor_sub}; font-size:0.9rem; margin-top:0.2rem;">'
                f'{subtitulo}</div>'
            )
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with col_insta:
        st.markdown(
            f'<div style="text-align:right; padding-top:0.6rem;">'
            f'<a href="https://instagram.com/{insta}" target="_blank" '
            f'style="color:{cor_ouro}; text-decoration:none; font-size:0.9rem; '
            f'font-weight:600;">📷 {EMPRESA["contacto"]["instagram"]}</a></div>',
            unsafe_allow_html=True,
        )

    st.divider()