"""
Autenticação da 2SD.Barber.
"""
import bcrypt
import streamlit as st
from database import get_conn, init_db


def verificar_login(username, password):
    init_db()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role, nome, ativo FROM utilizadores WHERE username = ?",
            (username.strip(),)
        ).fetchone()
    if not row:
        return None
    if not bool(row[5]):
        return None
    if bcrypt.checkpw(password.encode(), row[2].encode()):
        return {"id": row[0], "username": row[1], "role": row[3], "nome": row[4]}
    return None


def fazer_login(user):
    st.session_state.user_id = int(user["id"])
    st.session_state.username = user["username"]
    st.session_state.user_nome = user["nome"]
    st.session_state.role = user["role"]


def fazer_logout():
    for k in ["user_id", "username", "user_nome", "role"]:
        st.session_state.pop(k, None)


def esta_logado():
    return "user_id" in st.session_state


def is_admin():
    return st.session_state.get("role") == "admin"
