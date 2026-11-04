import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from auth import esta_logado, fazer_logout, is_admin
import database  # Importa o módulo em vez de funções específicas
from database import init_db
from config.empresa import EMPRESA

# --- INÍCIO DO BLOCO DE AUTO-CORREÇÃO ---
# Força o recarregamento do módulo 'database' se a função 'processar_referral' não for encontrada.
# Isto resolve o problema de cache de módulos no Streamlit Cloud.
if not hasattr(database, "processar_referral"):
    import importlib
    database = importlib.reload(database)
    print("Módulo 'database' recarregado à força.")
# --- FIM DO BLOCO DE AUTO-CORREÇÃO ---

st.set_page_config(
    page_title="2SD.Barber",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown('''
<style>
@media (max-width: 768px) {
    .row-widget.stHorizontal {
        flex-direction: column !important;
    }
    .row-widget.stHorizontal > div {
        width: 100% !important;
        margin-bottom: 1rem;
    }
    .stButton > button {
        min-height: 3rem;
        font-size: 16px !important;
    }
}
</style>
''', unsafe_allow_html=True)

st.markdown("""
<style>
/* Aplica apenas a ecrãs de telemóvel (largura até 768px) */
@media (max-width: 768px) {
    /* Força as colunas horizontais a empilharem na vertical */
    .row-widget.stHorizontal {
        flex-direction: column !important;
    }
    /* Dá espaçamento entre as colunas empilhadas */
    .row-widget.stHorizontal > div {
        width: 100% !important;
        margin-bottom: 1rem;
    }
    /* Aumenta a área de toque dos botões */
    .stButton > button {
        min-height: 3rem;
        font-size: 16px !important;
    }
}
</style>
""", unsafe_allow_html=True)
# =========================================================
# INICIALIZAR BD (necessário no Streamlit Cloud)
# =========================================================
@st.cache_resource(show_spinner=False)
def _init_db_once():
    """Inicializa a BD uma única vez por processo, crucial para o Cloud."""
    init_db()


_init_db_once()


# =========================================================
# DEFINIÇÃO DAS PÁGINAS
# =========================================================
login_page = None

if esta_logado() and is_admin():
    # --- Admin logado ---
    paginas = [
        st.Page("pages/11_Admin_Agenda.py", title="📅 Agenda", default=True),
        st.Page("pages/12_Admin_Servicos.py", title="✂️ Serviços"),
        st.Page("pages/13_Admin_Clientes.py", title="👥 Clientes"),
        st.Page("pages/14_Admin_Horarios.py", title="🕐 Horários"),
        st.Page("pages/15_Admin_Lembretes.py", title="📨 Lembretes"),
        st.Page("pages/16_Admin_Despesas.py", title="💸 Despesas"),
    ]

    todas_paginas = paginas
else:
    # --- Público (não logado) ---
    paginas = [
        st.Page("pages/home.py", title="🏠 Início", default=True),
        st.Page("pages/2_Marcar.py", title="✂️ Marcar", url_path="marcar"),
        st.Page("pages/3_Preçario.py", title="💰 Preçário", url_path="precario"),
        st.Page("pages/4_Localização.py", title="📍 Onde estamos", url_path="localizacao"),
        st.Page("pages/5_Consultar_Pontos.py", title="🎁 Os meus pontos", url_path="pontos"),
        st.Page("pages/6_Galeria.py", title="📸 Galeria", url_path="galeria"),
    ]
    # Página de login — registada mas NÃO aparece na sidebar
    login_page = st.Page("pages/10_Admin_Login.py", title="🔐 Login")
    todas_paginas = paginas + [login_page]

# =========================================================
# NAVEGAÇÃO
# =========================================================
pg = st.navigation(todas_paginas, position="hidden")

# =========================================================
# LOGO (aceita png, jpg, jpeg, webp)
# =========================================================
ASSETS_DIR = Path(__file__).parent / "assets"


def _encontrar_logo():
    for nome in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp"):
        p = ASSETS_DIR / nome
        if p.exists():
            return p
    return None


LOGO_PATH = _encontrar_logo()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if LOGO_PATH:
        st.image(str(LOGO_PATH), width=140)
        st.divider()

    st.markdown("### ✂️ 2SD.Barber")

    for p in paginas:
        st.page_link(p, label=p.title)

    st.divider()

    if esta_logado():
        st.caption(f"👤 {st.session_state.user_nome}")
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
            st.rerun()
    else:
        if st.button("🔐 Área reservada", use_container_width=True):
            st.switch_page(login_page)
    st.divider()
    contacto = EMPRESA["contacto"]
    st.markdown(f'''
    <div style="text-align:center; font-size:0.85rem; color:#888;">
        <p style="margin:0.3rem 0;">📞 {contacto["telefone"]}</p>
        <p style="margin:0.3rem 0;">
            <a href="https://instagram.com/{contacto["instagram"].lstrip("@")}" 
               target="_blank" style="color:#D4AF37; text-decoration:none;">
               📷 {contacto["instagram"]}
            </a>
        </p>
        <p style="margin:0.3rem 0;">✉️ {contacto["email"]}</p>
    </div>
    ''', unsafe_allow_html=True)

pg.run()
