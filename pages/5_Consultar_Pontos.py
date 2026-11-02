import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from config.empresa import EMPRESA
from database import (
    buscar_cliente_por_telefone, historico_cliente,
    PONTOS_PARA_PREMIO, DESCRICAO_PREMIO,
)

st.title("🎁 Os meus pontos")
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
