import streamlit as st
import io, gc
from PIL import Image
import streamlit.components.v1 as components

from utils.helpers import (
    cargar_files, listar_barajas, get_aspecto,
    crear_carta_5x5, generar_logica_5x5, generar_hoja_5x5,
    imagenes_a_pdf_4x4dob
)
from utils.counters import get_contador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook, banner_venta_offline

def render_5x5(ir_a):
    if st.button("⬅️ Volver al Catálogo", key="back_5x5_final"):
        ir_a("catalogo")

    components.html(banner_top("LOTERIA 5x5 - 4 CARTAS POR HOJA"), height=320)

    barajas = listar_barajas()
    if not barajas:
        st.error("No se encontraron barajas en /barajas")
        return

    col_baraja, col_color = st.columns([3,1])
    with col_baraja:
        sel_baraja = st.selectbox("📁 Selecciona baraja (54 imagenes)", barajas, key="sel_5x5_final")
    with col_color:
        color_entre = st.color_picker("Color entre cartas", "#00FF00", key="color_5x5_final")

    files = cargar_files(sel_baraja, 54)
    if len(files) < 54:
        st.warning(f"Solo {len(files)} imagenes, se necesitan 54")
        return

    st.success(f"Baraja cargada: {sel_baraja} | {len(files)} figuras")
    aspecto = get_aspecto(files)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        div_interno = st.slider("Div interno", 2, 20, 8, key="div_5x5_final")
    with c2:
        sep_v = st.slider("Sep vertical", 5, 50, 20, key="sepv_5x5_final")
    with c3:
        sep_h = st.slider("Sep horizontal", 5, 50, 20, key="seph_5x5_final")
    with c4:
        g_negro = st.slider("Borde negro", 2, 20, 6, key="g_5x5_final")

    st.info(f"Visitas a 5x5: {get_contador('5x5')}")

    col_gen1, col_gen2 = st.columns(2)
    with col_gen1:
        generar_btn = st.button("🎲 GENERAR 4 CARTAS 5x5", type="primary", use_container_width=True, key="btn_gen_5x5_final")
    with col_gen2:
        pdf_btn = st.button("📄 GENERAR PDF 5x5", use_container_width=True, key="btn_pdf_5x5_final")

    if generar_btn:
        with st.spinner("Generando logica 5x5..."):
            gc.collect()
            logica = generar_logica_5x5(files)
            hoja = generar_hoja_5x5(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, W_orig=2000)
            st.session_state["hoja_5x5_final"] = hoja
            st.image(hoja, caption="Hoja 5x5 Generada", use_container_width=True)

            buf_png = io.BytesIO()
            hoja.save(buf_png, format="PNG")
            st.download_button(
                "⬇️ Descargar PNG 5x5",
                buf_png.getvalue(),
                "loteria_5x5.png",
                "image/png",
                key="dl_png_5x5_final",
                use_container_width=True
            )
            st.session_state["cartas_5x5_count"] = st.session_state.get("cartas_5x5_count", 0) + 4
            st.success(f"{st.session_state['cartas_5x5_count']} cartas 5x5 generadas")

    if "hoja_5x5_final" in st.session_state and not generar_btn:
        st.image(st.session_state["hoja_5x5_final"], caption="Ultima hoja", use_container_width=True)

    if pdf_btn and "hoja_5x5_final" in st.session_state:
        pdf_bytes = imagenes_a_pdf_4x4dob([st.session_state["hoja_5x5_final"]])
        if pdf_bytes:
            st.download_button("⬇️ Descargar PDF 5x5", pdf_bytes, "loteria_5x5.pdf", "application/pdf", key="dl_pdf_5x5_final", use_container_width=True)

    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
    components.html(banner_venta_offline(), height=320)
