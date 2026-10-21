import streamlit as st
import io, os, random, gc
from PIL import Image
import streamlit.components.v1 as components

from utils.helpers import (
    cargar_files, listar_barajas, cm_to_px, get_aspecto,
    crear_carta_4x4, generar_logica_4x4, generar_hoja_4x4,
    imagenes_a_pdf_4x4dob
)
from utils.counters import registrar_entrada_generador, get_contador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook, banner_venta_offline

def render_4x4(ir_a):
    # Botón volver
    if st.button("⬅️ Volver al Catálogo", key="back_4x4_final"):
        ir_a("catalogo")

    components.html(banner_top("LOTERIA 4x4 - 4 CARTAS POR HOJA"), height=320)

    # Selección baraja
    barajas = listar_barajas()
    if not barajas:
        st.error("No se encontraron barajas en /barajas"); return

    col_baraja, col_color = st.columns([3,1])
    with col_baraja:
        sel_baraja = st.selectbox("📁 Selecciona baraja (54 imágenes)", barajas, key="sel_4x4_final")
    with col_color:
        color_entre = st.color_picker("Color entre cartas", "#FF0000", key="color_4x4_final")

    files = cargar_files(sel_baraja, 54)
    if len(files) < 54:
        st.warning(f"Solo {len(files)} imágenes encontradas, se necesitan 54"); return

    st.success(f"Baraja cargada: {sel_baraja} | {len(files)} figuras")
    aspecto = get_aspecto(files)

    # Sliders idénticos a tu app original
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        div_interno = st.slider("Div interno", 2, 20, 8, key="div_4x4_final")
    with c2:
        sep_v = st.slider("Sep vertical", 5, 50, 20, key="sepv_4x4_final")
    with c3:
        sep_h = st.slider("Sep horizontal", 5, 50, 20, key="seph_4x4_final")
    with c4:
        g_negro = st.slider("Borde negro", 2, 20, 6, key="g_4x4_final")

    # Contador visitas
    st.info(f"👁️ Visitas a 4x4: {get_contador('4x4')}")

    # Botones generar
    col_gen1, col_gen2 = st.columns(2)
    with col_gen1:
        generar_btn = st.button("🎲 GENERAR 4 CARTAS 4x4", type="primary", use_container_width=True, key="btn_gen_4x4_final")
    with col_gen2:
        pdf_btn = st.button("📄 GENERAR PDF 4x4", use_container_width=True, key="btn_pdf_4x4_final")

    if generar_btn:
        with st.spinner("Generando lógica 4x4 con validación..."):
            for _ in range(3): gc.collect()
            logica = generar_logica_4x4(files)
            if not logica:
                st.error("No se pudo generar lógica sin choques, intenta de nuevo"); return

            hoja = generar_hoja_4x4(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, final_size=None, W_orig=1800)
            st.session_state["hoja_4x4_final"] = hoja
            st.session_state["logica_4x4_final"] = logica

            st.image(hoja, caption="Hoja 4x4 Generada - 4 cartas", use_container_width=True)

            # Descargas
            buf_png = io.BytesIO()
            hoja.save(buf_png, format="PNG")
            st.download_button(
                "⬇️ Descargar PNG 4x4 (1800px)", 
                buf_png.getvalue(), 
                "loteria_4x4_1800.png", 
                "image/png",
                key="dl_png_4x4_final",
                use_container_width=True
            )

            # Contador local
            st.session_state["cartas_4x4_count"] = st.session_state.get("cartas_4x4_count", 0) + 4
            st.success(f"✅ {st.session_state['cartas_4x4_count']} cartas 4x4 generadas en total en esta sesión")

            del hoja; gc.collect()

    # Mostrar si ya existe
    if "hoja_4x4_final" in st.session_state and not generar_btn:
        st.image(st.session_state["hoja_4x4_final"], caption="Última hoja generada", use_container_width=True)

    if pdf_btn and "hoja_4x4_final" in st.session_state:
        with st.spinner("Generando PDF..."):
            pdf_bytes = imagenes_a_pdf_4x4dob([st.session_state["hoja_4x4_final"]])
            if pdf_bytes:
                st.download_button(
                    "⬇️ Descargar PDF 4x4", 
                    pdf_bytes, 
                    "loteria_4x4.pdf", 
                    "application/pdf",
                    key="dl_pdf_4x4_final",
                    use_container_width=True
                )

    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
    components.html(banner_venta_offline(), height=320)
