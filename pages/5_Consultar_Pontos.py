import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from urllib.parse import quote
from config.empresa import EMPRESA
from database import (
    buscar_cliente_por_telefone, historico_cliente,
    PONTOS_PARA_PREMIO, DESCRICAO_PREMIO,
    PONTOS_REFERRAL, obter_codigo_referral,
)
from components.header import render_header

render_header("🎁 Os meus pontos", "Consulte o seu saldo")

st.info(f"Cada corte vale 1 ponto. Aos {PONTOS_PARA_PREMIO} pontos, ganha **{DESCRICAO_PREMIO}**!")

telefone = st.text_input("O seu telefone", placeholder="912345678")

if st.button("🔍 Consultar", use_container_width=True):
    if not telefone.strip():
        st.error("Indique o telefone.")
    else:
        cliente = buscar_cliente_por_telefone(telefone.strip())
        if cliente is None:
            st.warning("Sem cliente com este telefone. Faça a primeira marcação!")
        else:
            pontos = int(cliente["pontos"])
            c1, c2, c3 = st.columns(3)
            c1.metric("🎯 Pontos", pontos)
            c2.metric("✂️ Cortes", int(cliente["total_visitas"]))
            c3.metric("💶 Gasto", f"{cliente['total_gasto']:.2f}€")

            st.markdown(f'### Olá, **{cliente["nome"]}**!')

            st.progress(min(pontos / PONTOS_PARA_PREMIO, 1.0))

            if pontos >= PONTOS_PARA_PREMIO:
                st.success(f"🎉 Parabéns! Pode resgatar **{DESCRICAO_PREMIO}**.")
            else:
                faltam = PONTOS_PARA_PREMIO - pontos
                st.info(f"Faltam **{faltam}** ponto(s).")

            st.divider()
            st.subheader("📜 Histórico")
            hist = historico_cliente(int(cliente["id"]))
            if hist.empty:
                st.info("Sem histórico ainda.")
            else:
                st.dataframe(hist, hide_index=True, use_container_width=True)

            # --- Campanha "Traz o teu amigo" ---
            st.divider()
            st.subheader("🎁 Traz o teu amigo")

            codigo = obter_codigo_referral(int(cliente["id"]))
            app_url = EMPRESA.get("app_url", "https://2sd-barber.streamlit.app")
            link_convite = f"{app_url}/marcar?ref={codigo}"

            st.markdown(
                f"Partilha o teu link com um amigo. Quando ele fizer a **primeira marcação** "
                f"e **comparecer**, ganhas **{PONTOS_REFERRAL} pontos**!"
            )

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("**O teu código:**")
                st.markdown(
                    f"<div style='background:#1a1a1a; border:1px solid #D4AF37; "
                    f"border-radius:8px; padding:0.6rem 1rem; text-align:center; "
                    f"font-size:1.2rem; font-weight:bold; color:#D4AF37;'>"
                    f"{codigo}</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown("**O teu link de convite:**")
                st.code(link_convite, language=None)

            mensagem = f"Boas! 👋 Recomendo a 2SD.Barber. Marca aqui: {link_convite}"
            link_wa = f"https://wa.me/?text={quote(mensagem)}"
            st.markdown(
                f'<a href="{link_wa}" target="_blank" style="display:inline-block; '
                f'background:#D4AF37; color:#000; padding:0.6rem 1.2rem; border-radius:8px; '
                f'text-decoration:none; font-weight:600; margin-top:0.5rem;">'
                f'📱 Partilhar no WhatsApp</a>',
                unsafe_allow_html=True,
            )