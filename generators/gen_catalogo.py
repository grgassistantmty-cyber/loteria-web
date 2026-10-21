import streamlit as st
from utils.counters import get_contador
from ui.banners import banner_top

def render_catalogo(ir_a):
    banner_top()
    st.title("🎲 Catálogo de Generadores - Lotería Mexicana")
    st.caption("Elige qué tipo de lotería quieres generar")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Visitas totales", get_contador("visitas_totales"))

    st.divider()

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🃏 Clásicos")
        if st.button("🎯 4x4 Clásico - 16 figuras\n54 barajas", use_container_width=True):
            ir_a("4x4")
        st.caption("El tradicional 4x4, 16 imágenes por carta")
        
        st.divider()
        
        if st.button("🔥 10 Dobles - 54 baraja\nDobles en pos 5 y 6", use_container_width=True, type="primary"):
            ir_a("10dobles")
        st.caption("54 figuras, 10 cartas, dups forzados")

    with c2:
        st.subheader("⭐ Especiales")
        if st.button("📏 5x5 Grande - 25 figuras", use_container_width=True):
            ir_a("5x5")
        st.caption("Cartas grandes de 25 imágenes")

        st.divider()

        if st.button("🖼️ Tabloide 12 + Portada\nPULIDO 2x2 cover", use_container_width=True):
            ir_a("12portada")
        st.caption("12 cartas + portada gigante 2x2, favorita repetida")

        st.divider()

        if st.button("♻️ 4x4 Dobles FIX\nCiclo 54 - 14 hojas", use_container_width=True):
            ir_a("4x4doblesfix")
        st.caption(f"Ciclo completo 14 hojas, 54+2 repetidas")

    st.divider()
    st.info("💡 Tip: Cada generador guarda visitas y PDFs por separado para tus stats.")
