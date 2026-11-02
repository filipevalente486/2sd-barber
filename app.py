import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from auth import esta_logado, fazer_logout, is_admin

st.set_page_config(
    page_title="2SD.Barber",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

    # Só as páginas visíveis (login fica de fora)
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

pg.run()