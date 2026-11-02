import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
from config.empresa import EMPRESA, DIAS_SEMANA
from database import (
    listar_servicos, gerar_slots_disponiveis,
    buscar_clientes_por_nome, criar_ou_atualizar_cliente, criar_marcacao,
)

# Ler serviço pré-selecionado via URL (?servico=ID)
pre_servico_id = None
try:
    qp = st.query_params.get("servico")
    if qp:
        pre_servico_id = int(qp)
        st.query_params.clear()
except Exception:
    pre_servico_id = None

st.title("✂️ Fazer marcação")

servicos = listar_servicos()
if servicos.empty:
    st.warning("Sem serviços configurados.")
    st.stop()

opcoes = {
    row["id"]: f"{row['nome']} — {row['duracao_min']} min — {row['preco']:.2f}€"
    for _, row in servicos.iterrows()
}

idx_default = 0
if pre_servico_id is not None and pre_servico_id in opcoes:
    idx_default = list(opcoes.keys()).index(pre_servico_id)

# ---------- 3 COLUNAS: Serviço | Dia | Hora ----------
col_serv, col_dia, col_hora = st.columns(3)

with col_serv:
    st.markdown("#### 1️⃣ Serviço")
    servico_id = st.selectbox(
        "Serviço",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
        index=idx_default,
        label_visibility="collapsed",
    )
    servico = servicos[servicos["id"] == servico_id].iloc[0]

    if pre_servico_id is not None and pre_servico_id in opcoes:
        st.success(f"✅ {servico['nome']}")

with col_dia:
    st.markdown("#### 2️⃣ Dia")
    hoje = date.today()
    datas = [hoje + timedelta(days=i) for i in range(30)]
    data_escolhida = st.selectbox(
        "Data",
        options=datas,
        format_func=lambda d: f"{DIAS_SEMANA[d.weekday()]}, {d.strftime('%d/%m/%Y')}",
        index=1,
        label_visibility="collapsed",
    )

# Calcular slots (precisa do serviço + dia escolhidos)
data_str = data_escolhida.strftime("%Y-%m-%d")
slots, motivo = gerar_slots_disponiveis(data_str, int(servico["duracao_min"]))

with col_hora:
    st.markdown("#### 3️⃣ Hora")
    if not slots:
        st.warning(f"⚠️ {motivo}")
        hora_escolhida = None
    else:
        hora_escolhida = st.selectbox("Hora", slots, label_visibility="collapsed")
        st.caption(f"⏱️ {servico['duracao_min']} minutos")

if not slots:
    st.info("Contacte-nos: " + EMPRESA['contacto']['telefone'])
    st.stop()

st.divider()

# ---------- 2 COLUNAS: Nome | Telefone ----------
st.markdown("#### 4️⃣ Os seus dados")
col_nome, col_tel = st.columns(2)

with col_nome:
    nome_input = st.text_input("Nome *", placeholder="Ex.: João Silva")
    telefone_default = ""
    if nome_input.strip():
        matches = buscar_clientes_por_nome(nome_input)
        if not matches.empty:
            telefone_default = matches.iloc[0]["telefone"]
            st.info(f"👋 Bem-vindo de volta, **{matches.iloc[0]['nome']}**!")

with col_tel:
    telefone_input = st.text_input(
        "Telefone *",
        value=telefone_default,
        placeholder="Ex.: 912345678",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Confirmar ----------
if st.button("✅ Confirmar marcação", use_container_width=True, type="primary"):
    erros = []
    if not nome_input.strip():
        erros.append("Indique o nome.")
    if not telefone_input.strip() or len(telefone_input.strip()) < 9:
        erros.append("Telefone inválido.")

    if erros:
        for e in erros:
            st.error(e)
    else:
        cliente_id = criar_ou_atualizar_cliente(nome_input.strip(), telefone_input.strip())
        marcacao_id = criar_marcacao(
            servico_id, cliente_id, data_str, hora_escolhida,
            int(servico["duracao_min"]),
        )

        st.balloons()
        st.success(f"✅ Marcação #{marcacao_id} confirmada!")
        st.markdown(f'''
        | | |
        |---|---|
        | **Serviço** | {servico['nome']} |
        | **Data** | {DIAS_SEMANA[data_escolhida.weekday()]}, {data_escolhida.strftime('%d/%m/%Y')} |
        | **Hora** | {hora_escolhida} |
        | **Preço** | {servico['preco']:.2f}€ |
        ''')

        mensagem = EMPRESA["mensagem_whatsapp"].format(
            nome=nome_input.strip(), servico=servico["nome"],
            data=data_escolhida.strftime('%d/%m/%Y'), hora=hora_escolhida,
        )
        link_wa = f"https://wa.me/{EMPRESA['contacto']['whatsapp']}?text={quote(mensagem)}"
        st.markdown(f'[📱 Confirmar via WhatsApp]({link_wa})')