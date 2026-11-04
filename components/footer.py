import streamlit as st
from config.empresa import EMPRESA


def render_footer():
    """Rodapé com contactos + Instagram, para usar no fim de qualquer página."""
    contacto = EMPRESA["contacto"]
    insta_handle = contacto["instagram"].lstrip("@")
    st.divider()
    st.markdown(f'''
    <div style="text-align:center; padding:1rem 0;">
        <p style="margin:0.3rem 0; color:#b0b0b0; font-size:0.95rem;">
            📞 <a href="tel:{contacto["telefone"].replace(" ", "")}" 
                   style="color:#D4AF37; text-decoration:none;">{contacto["telefone"]}</a>
            &nbsp;·&nbsp;
            📷 <a href="https://instagram.com/{insta_handle}" 
                   target="_blank" 
                   style="color:#D4AF37; text-decoration:none;">{contacto["instagram"]}</a>
            &nbsp;·&nbsp;
            ✉️ <a href="mailto:{contacto["email"]}" 
                   style="color:#D4AF37; text-decoration:none;">{contacto["email"]}</a>
        </p>
        <p style="font-size:0.8rem; color:#666; margin-top:0.5rem;">
            © 2026 {EMPRESA["nome"]}
        </p>
    </div>
    ''', unsafe_allow_html=True)