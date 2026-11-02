import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import date, datetime, timedelta
from auth import esta_logado
from config.empresa import EMPRESA, DIAS_SEMANA
from database import (
    listar_horarios,
    guardar_horario,
    listar_dias_bloqueados,
    adicionar_dia_bloqueado,
    remover_dia_bloqueado,
)

cores = EMPRESA["cores"]

if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

st.markdown(f"""
<style>
    .hor-titulo {{
        color: {cores["secundaria"]};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .hor-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hor-titulo">🕐 Horários</div>', unsafe_allow_html=True)
st.markdown('<div class="hor-sub">Horário semanal e dias bloqueados</div>', unsafe_allow_html=True)

st.divider()


def _time_from_str(s):
    return datetime.strptime(s, "%H:%M").time()


def _str_from_time(t):
    return t.strftime("%H:%M")


# --- Horário semanal ---
st.markdown("### 📅 Horário semanal")

horarios = {h[0]: (h[1], h[2], bool(h[3])) for h in listar_horarios()}
for dia in range(7):
    if dia not in horarios:
        horarios[dia] = ("09:00", "19:00", dia != 6)

with st.form("form_horarios"):
    linhas = []
    for dia in range(7):
        nome = DIAS_SEMANA[dia]
        abre, fecha, ativo = horarios[dia]
        col_dia, col_abre, col_fecha, col_ativo = st.columns([2, 2, 2, 1])
        with col_dia:
            st.markdown(f"**{nome}**")
        with col_abre:
            nova_abre = st.time_input(
                "Abre", value=_time_from_str(abre), key=f"abre_{dia}",
                label_visibility="collapsed",
            )
        with col_fecha:
            nova_fecha = st.time_input(
                "Fecha", value=_time_from_str(fecha), key=f"fecha_{dia}",
                label_visibility="collapsed",
            )
        with col_ativo:
            novo_ativo = st.checkbox(
                "Aberto", value=ativo, key=f"ativo_{dia}",
                label_visibility="collapsed",
            )
        linhas.append((dia, nova_abre, nova_fecha, novo_ativo))

    guardar = st.form_submit_button("💾 Guardar horários", use_container_width=True, type="primary")

    if guardar:
        erros = []
        for dia, nova_abre, nova_fecha, novo_ativo in linhas:
            if novo_ativo and nova_fecha <= nova_abre:
                erros.append(f"{DIAS_SEMANA[dia]}: hora de fecho tem de ser depois da abertura.")
        if erros:
            for e in erros:
                st.error(e)
        else:
            for dia, nova_abre, nova_fecha, novo_ativo in linhas:
                guardar_horario(
                    dia,
                    _str_from_time(nova_abre),
                    _str_from_time(nova_fecha),
                    novo_ativo,
                )
            st.success("✅ Horários atualizados.")
            st.rerun()

st.caption("💡 Domingo — desative para 'sob consulta' (não aparece em Marcar).")
st.divider()

# --- Dias bloqueados ---
st.markdown("### 🚫 Dias bloqueados")
st.caption("Férias, feriados ou fechos pontuais. Estes dias **não** aparecem disponíveis em Marcar.")

bloqueados = listar_dias_bloqueados()

if bloqueados:
    for data_str, motivo in bloqueados:
        col_a, col_b, col_c = st.columns([1, 2, 1])
        try:
            data_fmt = datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            data_fmt = data_str
        with col_a:
            st.markdown(f"**{data_fmt}**")
        with col_b:
            st.caption(motivo or "Sem motivo indicado")
        with col_c:
            if st.button("🗑️ Remover", key=f"rem_{data_str}", use_container_width=True):
                remover_dia_bloqueado(data_str)
                st.success(f"Dia {data_fmt} removido.")
                st.rerun()
else:
    st.info("Sem dias bloqueados.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### ➕ Adicionar dia bloqueado")

with st.form("form_add_bloqueado", clear_on_submit=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        nova_data = st.date_input(
            "Data",
            value=date.today() + timedelta(days=1),
            min_value=date.today(),
        )
    with col2:
        novo_motivo = st.text_input("Motivo", placeholder="Ex.: Férias, Feriado, Formação...")
    adicionar = st.form_submit_button("➕ Bloquear dia", use_container_width=True, type="primary")

    if adicionar:
        data_str = nova_data.strftime("%Y-%m-%d")
        adicionar_dia_bloqueado(data_str, novo_motivo.strip() or "Sem motivo")
        st.success(f"✅ {nova_data.strftime('%d/%m/%Y')} bloqueado.")
        st.rerun()

st.divider()
st.caption(
    f"{sum(1 for h in horarios.values() if h[2])} dias ativos por semana · "
    f"{len(bloqueados)} dia(s) bloqueado(s)"
)
