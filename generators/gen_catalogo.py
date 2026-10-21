import streamlit as st
from ui.banners import banner_top
import streamlit.components.v1 as components

def render_catalogo(ir_a):
    components.html(banner_top("CATALOGO PRINCIPAL"), height=320)
    
    st.title("📚 Catálogo de Loterías")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 4x4 - 4 por hoja", use_container_width=True):
            ir_a("4x4")
        if st.button("🎲 5x5", use_container_width=True):
            ir_a("5x5")
    with col2:
        if st.button("🎲 10 Dobles", use_container_width=True):
            ir_a("10dobles")
        if st.button("🖼️ 12 + Portada", use_container_width=True):
            ir_a("12portada")
        if st.button("🎲 4x4 Dobles Fix", use_container_width=True):
            ir_a("4x4doblesfix")
