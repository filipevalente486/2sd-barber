import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import date, timedelta
from auth import esta_logado
from config.empresa import EMPRESA, DIAS_SEMANA
from database import (
    listar_marcacoes_por_data,
    concluir_marcacao,
    cancelar_marcacao,
    PONTOS_POR_VISITA,
    PONTOS_PARA_PREMIO,
)

cores = EMPRESA["cores"]

# --- Proteção: só admin logado ---
if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

# --- Header ---
st.markdown(f"""
<style>
    .agenda-titulo {{
        color: {cores["secundaria"]};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .agenda-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
    .marcacao-card {{
        background: {cores["fundo"]};
        border: 1px solid #2a2a2a;
        border-left: 4px solid {cores["secundaria"]};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }}
    .marcacao-hora {{
        color: {cores["secundaria"]};
        font-size: 1.3rem;
        font-weight: bold;
    }}
    .marcacao-estado {{
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }}
    .estado-pendente {{ background: #444; color: #fff; }}
    .estado-concluida {{ background: #1a5c1a; color: #8fff8f; }}
    .estado-cancelada {{ background: #5c1a1a; color: #ff8f8f; }}
    .dia-header {{
        color: {cores["secundaria"]};
        font-size: 1.15rem;
        font-weight: 600;
        padding: 0.3rem 0;
    }}
    .dia-resumo {{
        color: #888;
        font-size: 0.85rem;
        font-weight: 400;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="agenda-titulo">📅 Agenda</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="agenda-sub">Bem-vindo, {st.session_state.user_nome} · Gerir marcações</div>',
    unsafe_allow_html=True,
)

# --- Estado inicial ---
hoje = date.today()
if "agenda_data" not in st.session_state:
    st.session_state.agenda_data = hoje
if "date_picker_agenda" not in st.session_state:
    st.session_state.date_picker_agenda = st.session_state.agenda_data
if "agenda_vista" not in st.session_state:
    st.session_state.agenda_vista = "📅 Dia"


# --- Helpers de navegação ---
def _semana_inicio(d: date) -> date:
    """Segunda-feira da semana que contém d."""
    return d - timedelta(days=d.weekday())


def _prev_day():
    nova = st.session_state.agenda_data - timedelta(days=1)
    st.session_state.agenda_data = nova
    st.session_state.date_picker_agenda = nova


def _next_day():
    nova = st.session_state.agenda_data + timedelta(days=1)
    st.session_state.agenda_data = nova
    st.session_state.date_picker_agenda = nova


def _go_today():
    st.session_state.agenda_data = hoje
    st.session_state.date_picker_agenda = hoje


def _sync_from_picker():
    st.session_state.agenda_data = st.session_state.date_picker_agenda


def _prev_week():
    nova = st.session_state.agenda_data - timedelta(days=7)
    st.session_state.agenda_data = nova
    st.session_state.date_picker_agenda = nova


def _next_week():
    nova = st.session_state.agenda_data + timedelta(days=7)
    st.session_state.agenda_data = nova
    st.session_state.date_picker_agenda = nova


def _go_current_week():
    st.session_state.agenda_data = hoje
    st.session_state.date_picker_agenda = hoje


# --- Toggle de vista ---
vista = st.radio(
    "Vista",
    ["📅 Dia", "📆 Semana"],
    horizontal=True,
    key="agenda_vista",
    label_visibility="collapsed",
)

st.divider()


# =========================================================
# FUNÇÃO REUTILIZÁVEL — renderiza as marcações de um dia
# =========================================================
def _render_dia(marcacoes, data_obj, compacto=False):
    if marcacoes.empty:
        st.caption("📭 Sem marcações.")
        return

    for _, m in marcacoes.iterrows():
        estado = m["estado"]
        estado_class = f"estado-{estado}"
        estado_label = {
            "pendente": "⏳ Pendente",
            "concluida": "✅ Concluída",
            "cancelada": "❌ Cancelada",
        }.get(estado, estado)

        st.markdown(f"""
        <div class="marcacao-card">
            <span class="marcacao-hora">🕐 {m['hora']}</span>
            <span class="marcacao-estado {estado_class}">{estado_label}</span>
            <div style="color:{cores['texto']}; font-size:1.05rem; margin-top:0.4rem; font-weight:600;">
                {m['cliente']}
            </div>
            <div style="color:{cores['texto_secundario']}; font-size:0.9rem;">
                ✂️ {m['servico']} · ⏱️ {int(m['duracao_min'])} min · 💶 {float(m['preco'] or 0):.2f}€
            </div>
            <div style="color:#888; font-size:0.85rem; margin-top:0.3rem;">
                📱 {m['telefone']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if estado == "pendente" and not compacto:
            b1, b2, b3 = st.columns([1, 1, 3])
            with b1:
                if st.button(
                    "✅ Concluir",
                    key=f"concluir_{m['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    resultado = concluir_marcacao(int(m["id"]))
                    if resultado:
                        st.success(
                            f"✅ Marcação concluída! "
                            f"+{resultado['pontos_ganhos']} ponto(s) → "
                            f"saldo: {resultado['novo_saldo']}"
                        )
                        if resultado["premio_disponivel"]:
                            st.balloons()
                            st.info(
                                f"🎁 {m['cliente']} tem prémio disponível "
                                f"({PONTOS_PARA_PREMIO} pontos)!"
                            )
                        st.rerun()
                    else:
                        st.error("Não foi possível concluir.")
            with b2:
                if st.button(
                    "❌ Cancelar",
                    key=f"cancelar_{m['id']}",
                    use_container_width=True,
                ):
                    cancelar_marcacao(int(m["id"]))
                    st.warning(f"❌ Marcação de {m['cliente']} cancelada.")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# VISTA DIA
# =========================================================
if vista == "📅 Dia":
    col_nav1, col_data, col_nav2 = st.columns([1, 2, 1])

    with col_nav1:
        st.button("◀ Dia anterior", use_container_width=True, on_click=_prev_day)

    with col_data:
        st.date_input(
            "Data",
            label_visibility="collapsed",
            key="date_picker_agenda",
            on_change=_sync_from_picker,
        )

    with col_nav2:
        st.button("Dia seguinte ▶", use_container_width=True, on_click=_next_day)

    st.button("📌 Ir para hoje", on_click=_go_today)

    data_obj = st.session_state.agenda_data
    data_str = data_obj.strftime("%Y-%m-%d")
    dia_semana = DIAS_SEMANA[data_obj.weekday()]

    st.divider()

    marcacoes = listar_marcacoes_por_data(data_str)

    total = len(marcacoes) if not marcacoes.empty else 0
    pendentes = len(marcacoes[marcacoes["estado"] == "pendente"]) if total else 0
    concluidas = len(marcacoes[marcacoes["estado"] == "concluida"]) if total else 0
    receita = marcacoes[marcacoes["estado"] != "cancelada"]["preco"].sum() if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total", total)
    c2.metric("⏳ Pendentes", pendentes)
    c3.metric("✅ Concluídas", concluidas)
    c4.metric("💶 Receita", f"{receita:.2f}€")

    st.markdown(f"### {dia_semana}, {data_obj.strftime('%d/%m/%Y')}")
    st.divider()

    _render_dia(marcacoes, data_obj)


# =========================================================
# VISTA SEMANA
# =========================================================
else:
    col_nav1, col_label, col_nav2 = st.columns([1, 2, 1])

    week_start = _semana_inicio(st.session_state.agenda_data)
    week_end = week_start + timedelta(days=6)

    with col_nav1:
        st.button("◀ Semana anterior", use_container_width=True, on_click=_prev_week)

    with col_label:
        st.markdown(
            f"<div style='text-align:center; color:{cores['secundaria']}; "
            f"font-size:1.2rem; font-weight:600; padding-top:0.4rem;'>"
            f"📆 {week_start.strftime('%d/%m')} → {week_end.strftime('%d/%m/%Y')}"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_nav2:
        st.button("Semana seguinte ▶", use_container_width=True, on_click=_next_week)

    st.button("📌 Semana atual", on_click=_go_current_week)

    st.divider()

    # --- Recolher todos os dias da semana ---
    dias_semana = []
    total_semana = pendentes_semana = concluidas_semana = 0
    receita_semana = 0.0

    for i in range(7):
        dia = week_start + timedelta(days=i)
        data_str = dia.strftime("%Y-%m-%d")
        marcacoes = listar_marcacoes_por_data(data_str)
        n = len(marcacoes) if not marcacoes.empty else 0
        dias_semana.append((dia, data_str, marcacoes, n))

        if n > 0:
            total_semana += n
            pendentes_semana += len(marcacoes[marcacoes["estado"] == "pendente"])
            concluidas_semana += len(marcacoes[marcacoes["estado"] == "concluida"])
            receita_semana += marcacoes[marcacoes["estado"] != "cancelada"]["preco"].sum()

    # --- Métricas da semana ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total", total_semana)
    c2.metric("⏳ Pendentes", pendentes_semana)
    c3.metric("✅ Concluídas", concluidas_semana)
    c4.metric("💶 Receita", f"{receita_semana:.2f}€")

    st.divider()

    if total_semana == 0:
        st.info("📭 Sem marcações nesta semana.")
    else:
        for dia, data_str, marcacoes, n in dias_semana:
            dia_nome = DIAS_SEMANA[dia.weekday()]
            data_fmt = dia.strftime("%d/%m/%Y")
            e_hoje = " · 🟢 HOJE" if dia == hoje else ""

            if n == 0:
                header = f"**{dia_nome}, {data_fmt}**{e_hoje} · *sem marcações*"
                with st.expander(header, expanded=False):
                    st.caption("📭 Sem marcações.")
            else:
                receita_dia = marcacoes[marcacoes["estado"] != "cancelada"]["preco"].sum()
                pend_dia = len(marcacoes[marcacoes["estado"] == "pendente"])
                header = (
                    f"**{dia_nome}, {data_fmt}**{e_hoje} · "
                    f"{n} marcação(ões) · {pend_dia} pendente(s) · "
                    f"{receita_dia:.2f}€"
                )
                with st.expander(header, expanded=(dia == hoje)):
                    _render_dia(marcacoes, dia, compacto=False)