import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
from auth import esta_logado
from config.empresa import EMPRESA, DIAS_SEMANA
from database import (
    listar_marcacoes_por_data_com_lembrete,
    marcar_lembrete_enviado,
    desmarcar_lembrete_enviado,
)

cores = EMPRESA["cores"]

if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

st.markdown(f"""
<style>
    .lemb-titulo {{
        color: {cores["secundaria"]};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .lemb-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
    .lemb-card {{
        background: {cores["fundo"]};
        border: 1px solid #2a2a2a;
        border-left: 4px solid {cores["secundaria"]};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }}
    .lemb-card.lembrado {{
        border-left-color: #4a9d4a;
        opacity: 0.85;
    }}
    .lemb-hora {{
        color: {cores["secundaria"]};
        font-size: 1.2rem;
        font-weight: bold;
    }}
    .lemb-nome {{
        color: {cores["texto"]};
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }}
    .lemb-info {{
        color: {cores["texto_secundario"]};
        font-size: 0.88rem;
    }}
    .lemb-badge {{
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }}
    .badge-lembrado {{ background: #1a5c1a; color: #8fff8f; }}
    .badge-pendente {{ background: #5c4a1a; color: #ffd98f; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="lemb-titulo">📨 Lembretes</div>', unsafe_allow_html=True)
st.markdown('<div class="lemb-sub">Envie confirmações e lembretes via WhatsApp</div>', unsafe_allow_html=True)

hoje = date.today()
amanha = hoje + timedelta(days=1)

if "lemb_data" not in st.session_state:
    st.session_state.lemb_data = amanha

col_nav1, col_data, col_nav2 = st.columns([1, 2, 1])


def _prev_day():
    st.session_state.lemb_data -= timedelta(days=1)


def _next_day():
    st.session_state.lemb_data += timedelta(days=1)


def _go_tomorrow():
    st.session_state.lemb_data = amanha


with col_nav1:
    st.button("◀ Anterior", use_container_width=True, on_click=_prev_day)

with col_data:
    st.markdown(
        f"<div style='text-align:center; padding-top:0.4rem; color:{cores['secundaria']}; "
        f"font-size:1.1rem; font-weight:600;'>"
        f"📅 {DIAS_SEMANA[st.session_state.lemb_data.weekday()]}, "
        f"{st.session_state.lemb_data.strftime('%d/%m/%Y')}"
        f"</div>",
        unsafe_allow_html=True,
    )

with col_nav2:
    st.button("Seguinte ▶", use_container_width=True, on_click=_next_day)

st.button("📌 Ir para amanhã", on_click=_go_tomorrow)

st.divider()

data_str = st.session_state.lemb_data.strftime("%Y-%m-%d")
marcacoes = listar_marcacoes_por_data_com_lembrete(data_str)

if marcacoes.empty:
    st.info("📭 Sem marcações neste dia.")
    st.stop()

so_pendentes = st.checkbox("Mostrar só os **não lembrados**", value=False)

filtradas = marcacoes.copy()
if so_pendentes:
    filtradas = filtradas[filtradas["lembrete_enviado"] == 0]

total = len(marcacoes)
lembrados = int(marcacoes["lembrete_enviado"].sum())
pendentes = total - lembrados

c1, c2, c3 = st.columns(3)
c1.metric("📊 Total", total)
c2.metric("✅ Lembrados", lembrados)
c3.metric("⏳ Por lembrar", pendentes)

st.divider()

if filtradas.empty:
    st.success("🎉 Todos os clientes deste dia já foram lembrados!")
    st.stop()

for _, m in filtradas.iterrows():
    mid = int(m["id"])
    nome = m["cliente"]
    tel = m["telefone"]
    hora = m["hora"]
    servico = m["servico"]
    lembrado = int(m["lembrete_enviado"]) == 1

    tel_limpo = "".join(ch for ch in str(tel) if ch.isdigit())
    if not tel_limpo.startswith("351"):
        tel_limpo = "351" + tel_limpo

    data_fmt = st.session_state.lemb_data.strftime("%d/%m/%Y")
    dia_nome = DIAS_SEMANA[st.session_state.lemb_data.weekday()]

    mensagem = (
        f"Olá {nome}! 👋\n\n"
        f"Lembramos que tem marcação na 2SD.Barber:\n"
        f"📅 {dia_nome}, {data_fmt}\n"
        f"🕐 {hora}\n"
        f"✂️ {servico}\n\n"
        f"Até breve!"
    )
    link_wa = f"https://wa.me/{tel_limpo}?text={quote(mensagem)}"

    card_class = "lemb-card lembrado" if lembrado else "lemb-card"
    badge = (
        '<span class="lemb-badge badge-lembrado">✅ LEMBRADO</span>'
        if lembrado
        else '<span class="lemb-badge badge-pendente">⏳ POR LEMBRAR</span>'
    )

    st.markdown(f"""
    <div class="{card_class}">
        <span class="lemb-hora">🕐 {hora}</span>{badge}
        <div class="lemb-nome">{nome}</div>
        <div class="lemb-info">✂️ {servico} · 📱 {tel}</div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3 = st.columns([1, 1, 2])
    with b1:
        st.markdown(
            f'<a href="{link_wa}" target="_blank" style="display:block; text-align:center; '
            f'background:{cores["secundaria"]}; color:#000; padding:0.5rem; '
            f'border-radius:8px; text-decoration:none; font-weight:600;">💬 WhatsApp</a>',
            unsafe_allow_html=True,
        )
    with b2:
        if lembrado:
            if st.button("↩️ Desmarcar", key=f"desm_{mid}", use_container_width=True):
                desmarcar_lembrete_enviado(mid)
                st.rerun()
        else:
            if st.button("✅ Marcar lembrado", key=f"lemb_{mid}", use_container_width=True):
                marcar_lembrete_enviado(mid)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

st.divider()
st.caption(
    f"{pendentes} cliente(s) por lembrar · "
    f"{lembrados} já lembrado(s) · "
    f"{total} no total"
)