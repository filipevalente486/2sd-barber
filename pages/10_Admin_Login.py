import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from auth import verificar_login, fazer_login, esta_logado
from config.empresa import EMPRESA

cores = EMPRESA["cores"]

# Se já estiver logado, redirecionar
if esta_logado():
    st.success(f"✅ Já está autenticado como **{st.session_state.user_nome}**.")
    st.info("Use o menu lateral para aceder às páginas de administração.")
    st.stop()

st.markdown(f"""
<style>
    .login-hero {{
        text-align: center;
        padding: 2rem 0 1.5rem 0;
    }}
    .login-hero h1 {{
        color: {cores["secundaria"]};
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
    }}
    .login-hero p {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="login-hero">
    <h1>🔐 Área Reservada</h1>
    <p>Acesso restrito à equipa 2SD.Barber</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.2, 1])

with col2:
    with st.form("form_login", clear_on_submit=False):
        username = st.text_input("👤 Utilizador", placeholder="admin")
        password = st.text_input("🔑 Palavra-passe", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Entrar", use_container_width=True, type="primary")

        if submit:
            if not username.strip() or not password:
                st.error("Preencha o utilizador e a palavra-passe.")
            else:
                user = verificar_login(username, password)
                if user:
                    fazer_login(user)
                    st.success(f"✅ Bem-vindo, **{user['nome']}**!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas ou conta inativa.")

    st.caption("💡 Credenciais por defeito: `admin` / `admin123` — altere após o primeiro login.")
