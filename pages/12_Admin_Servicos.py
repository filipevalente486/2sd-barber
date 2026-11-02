import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from auth import esta_logado
from config.empresa import EMPRESA
from database import get_conn, EMPRESA_ID

cores = EMPRESA["cores"]

if not esta_logado():
    st.error("🔒 Acesso restrito. Faça login para continuar.")
    if st.button("Ir para o login", type="primary"):
        st.switch_page("pages/10_Admin_Login.py")
    st.stop()

st.markdown(f"""
<style>
    .serv-titulo {{
        color: {cores["secundaria"]};
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }}
    .serv-sub {{
        color: {cores["texto_secundario"]};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="serv-titulo">✂️ Serviços</div>', unsafe_allow_html=True)
st.markdown('<div class="serv-sub">Adicionar, editar e gerir os serviços da barbearia</div>', unsafe_allow_html=True)

st.divider()


# --- Carregar serviços ---
def _carregar_servicos():
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, nome, descricao, duracao_min, preco, ativo, ordem "
            "FROM servicos WHERE empresa_id = ? ORDER BY ordem, id",
            (EMPRESA_ID,),
        ).fetchall()


servicos = _carregar_servicos()

# --- Formulário: novo serviço ---
with st.expander("➕ Adicionar novo serviço", expanded=False):
    with st.form("form_novo_servico", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            novo_nome = st.text_input("Nome *", placeholder="Ex.: Corte Degradê")
        with col2:
            nova_ordem = st.number_input("Ordem", min_value=0, max_value=999, value=len(servicos), step=1)

        nova_desc = st.text_area("Descrição", placeholder="Breve descrição do serviço", height=80)

        col3, col4 = st.columns(2)
        with col3:
            nova_duracao = st.number_input("Duração (min) *", min_value=5, max_value=240, value=30, step=5)
        with col4:
            novo_preco = st.number_input("Preço (€) *", min_value=0.0, max_value=999.99, value=10.0, step=0.5, format="%.2f")

        criar = st.form_submit_button("➕ Adicionar serviço", use_container_width=True, type="primary")

        if criar:
            if not novo_nome.strip():
                st.error("O nome é obrigatório.")
            elif nova_duracao < 5:
                st.error("Duração mínima de 5 minutos.")
            elif novo_preco < 0:
                st.error("Preço não pode ser negativo.")
            else:
                with get_conn() as conn:
                    conn.execute(
                        "INSERT INTO servicos (empresa_id, nome, descricao, duracao_min, preco, ativo, ordem) "
                        "VALUES (?, ?, ?, ?, ?, 1, ?)",
                        (EMPRESA_ID, novo_nome.strip(), nova_desc.strip() or None,
                         int(nova_duracao), float(novo_preco), int(nova_ordem)),
                    )
                    conn.commit()
                st.success(f"✅ Serviço **{novo_nome.strip()}** adicionado.")
                st.rerun()

# --- Lista / edição dos serviços existentes ---
st.markdown("### 📋 Serviços existentes")

if not servicos:
    st.info("Ainda não há serviços. Adicione o primeiro acima.")
    st.stop()

for s in servicos:
    sid, nome, desc, duracao, preco, ativo, ordem = s
    estado_label = "🟢 Ativo" if ativo else "⚪ Inativo"
    cor = cores["secundaria"] if ativo else "#666"

    with st.container():
        header = f"**{nome}** · {duracao} min · {preco:.2f}€ · {estado_label} · ordem {ordem}"
        with st.expander(header, expanded=False):
            with st.form(f"form_edit_{sid}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    ed_nome = st.text_input("Nome", value=nome, key=f"nome_{sid}")
                with col2:
                    ed_ordem = st.number_input(
                        "Ordem", min_value=0, max_value=999, value=int(ordem), step=1,
                        key=f"ordem_{sid}",
                    )

                ed_desc = st.text_area(
                    "Descrição", value=desc or "", height=70, key=f"desc_{sid}",
                )

                col3, col4 = st.columns(2)
                with col3:
                    ed_duracao = st.number_input(
                        "Duração (min)", min_value=5, max_value=240,
                        value=int(duracao), step=5, key=f"dur_{sid}",
                    )
                with col4:
                    ed_preco = st.number_input(
                        "Preço (€)", min_value=0.0, max_value=999.99,
                        value=float(preco), step=0.5, format="%.2f",
                        key=f"preco_{sid}",
                    )

                guardar = st.form_submit_button("💾 Guardar alterações", use_container_width=True, type="primary")

                if guardar:
                    if not ed_nome.strip():
                        st.error("O nome é obrigatório.")
                    else:
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE servicos SET nome = ?, descricao = ?, duracao_min = ?, "
                                "preco = ?, ordem = ? WHERE id = ? AND empresa_id = ?",
                                (ed_nome.strip(), ed_desc.strip() or None,
                                 int(ed_duracao), float(ed_preco), int(ed_ordem),
                                 sid, EMPRESA_ID),
                            )
                            conn.commit()
                        st.success("✅ Serviço atualizado.")
                        st.rerun()

            # Ações fora do form: ativar/desativar
            b1, b2 = st.columns([1, 3])
            with b1:
                if ativo:
                    if st.button("⚪ Desativar", key=f"desativar_{sid}", use_container_width=True):
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE servicos SET ativo = 0 WHERE id = ? AND empresa_id = ?",
                                (sid, EMPRESA_ID),
                            )
                            conn.commit()
                        st.warning(f"⚪ **{nome}** desativado (não aparece em Marcar/Preçário).")
                        st.rerun()
                else:
                    if st.button("🟢 Ativar", key=f"ativar_{sid}", use_container_width=True):
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE servicos SET ativo = 1 WHERE id = ? AND empresa_id = ?",
                                (sid, EMPRESA_ID),
                            )
                            conn.commit()
                        st.success(f"🟢 **{nome}** reativado.")
                        st.rerun()

st.divider()
st.caption(f"Total: {len(servicos)} serviços · {sum(1 for s in servicos if s[5])} ativos")
