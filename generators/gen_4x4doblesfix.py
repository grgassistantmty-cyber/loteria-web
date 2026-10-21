import streamlit as st
import io, os, random, gc
from PIL import Image
import streamlit.components.v1 as components

from utils.images import cargar_files, listar_barajas
from utils.loteria_core import get_aspecto, generar_logica_4x4, generar_hoja_4x4, imagenes_a_pdf_4x4dob
from utils.counters import registrar_entrada_generador, get_contador, inc_baraja, inc_contador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook

def render_4x4doblesfix(ir_a):
    registrar_entrada_generador("4x4doblesfix")
    
    if st.button("⬅️ Volver al Catálogo", key="back_4x4dobfix"):
        ir_a("catalogo")

    components.html(banner_top("LOTERIA 4x4 DOBLES FIX - SIN REPETIR"), height=320)

    barajas = listar_barajas()
    if not barajas:
        st.error("No se encontraron barajas"); return

    sel_baraja = st.selectbox("📁 Selecciona baraja", barajas, key="sel_4x4dobfix")
    color_entre = st.color_picker("Color", "#FF0000", key="color_4x4dobfix")

    files = cargar_files(sel_baraja, 54)
    if len(files) < 54:
        st.warning(f"Solo {len(files)} imágenes"); return

    aspecto = get_aspecto(files)

    c1, c2, c3 = st.columns(3)
    with c1: div_interno = st.slider("Div", 2, 20, 8, key="div_4x4dobfix")
    with c2: sep_v = st.slider("Sep V", 5, 50, 20, key="sepv_4x4dobfix")
    with c3: g_negro = st.slider("Borde", 2, 20, 6, key="g_4x4dobfix")

    st.info(f"👁️ Visitas 4x4doblesfix: {get_contador('visita_4x4doblesfix')}")

    if st.button("🎲 GENERAR 4x4 DOBLES FIX", type="primary", use_container_width=True, key="btn_4x4dobfix"):
        with st.spinner("Generando sin repetir..."):
            for _ in range(3): gc.collect()
            logica = generar_logica_4x4(files)
            hoja = generar_hoja_4x4(logica, color_entre, div_interno, sep_v, sep_v, g_negro, aspecto)
            st.session_state["hoja_4x4dobfix"] = hoja
            st.image(hoja, caption="4x4 Dobles Fix", use_container_width=True)
            inc_baraja(os.path.basename(sel_baraja), "4x4doblesfix")
            inc_contador("pdf_4x4doblesfix")
            buf = io.BytesIO()
            hoja.save(buf, format="PNG")
            st.download_button("⬇️ Descargar", buf.getvalue(), "4x4doblesfix.png", "image/png", use_container_width=True, key="dl_4x4dobfix")

    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
