import streamlit as st
import io, os, gc
from PIL import Image
import streamlit.components.v1 as components

from utils.images import listar_barajas, cargar_files, listar_portadas
from utils.loteria_core import get_aspecto, generar_logica_12portada, generar_hoja_12portada, imagenes_a_pdf_4x4dob
from utils.counters import registrar_entrada_generador, get_contador, inc_baraja, inc_contador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook

def render_12portada(ir_a):
    registrar_entrada_generador("12portada")
    if st.button("⬅️ Volver al Catálogo", key="back_12port"):
        ir_a("catalogo")

    components.html(banner_top("TABLOIDE 12 + PORTADA 2x2"), height=320)
    st.caption("12 cartas + portada gigante, favorita repetida")

    barajas = listar_barajas()
    portadas = listar_portadas()
    if not barajas:
        st.error("No hay barajas"); return

    sel_baraja = st.selectbox("📁 Baraja", barajas, key="sel_12port")
    sel_portada = st.selectbox("🖼️ Portada", portadas, key="sel_port_12port") if portadas else None
    color_entre = st.color_picker("Color", "#FF0000", key="color_12port")

    files = cargar_files(sel_baraja, 54)
    if len(files) < 54:
        st.warning("Faltan imágenes"); return

    aspecto = get_aspecto(files)
    c1, c2, c3 = st.columns(3)
    with c1: div_interno = st.slider("Div", 2, 20, 8, key="div_12port")
    with c2: sep_v = st.slider("Sep V", 5, 50, 20, key="sepv_12port")
    with c3: g_negro = st.slider("Borde", 2, 20, 6, key="g_12port")

    st.info(f"👁️ Visitas 12portada: {get_contador('visita_12portada')}")

    if st.button("🎲 GENERAR 12 + PORTADA", type="primary", use_container_width=True, key="btn_12port"):
        with st.spinner("Generando tabloide..."):
            logica = generar_logica_12portada(files)
            hoja = generar_hoja_12portada(logica, color_entre, div_interno, sep_v, sep_v, g_negro, aspecto, sel_portada)
            st.session_state["hoja_12port"] = hoja
            st.image(hoja, caption="Tabloide 12+Portada", use_container_width=True)
            inc_baraja(os.path.basename(sel_baraja), "12portada")
            inc_contador("pdf_12portada")
            buf = io.BytesIO()
            hoja.save(buf, format="PNG")
            st.download_button("⬇️ Descargar", buf.getvalue(), "12portada.png", "image/png", use_container_width=True, key="dl_12port")

    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
