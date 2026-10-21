import streamlit as st
import io, os, gc
from PIL import Image
import streamlit.components.v1 as components

from utils.images import listar_barajas, cargar_files
from utils.loteria_core import get_aspecto, generar_logica_5x5, generar_hoja_5x5, imagenes_a_pdf_4x4dob
from utils.counters import registrar_entrada_generador, get_contador, inc_baraja, inc_contador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook, banner_venta_offline

def render_5x5(ir_a):
    registrar_entrada_generador("5x5")
    if st.button("⬅️ Volver al Catálogo", key="back_5x5"):
        ir_a("catalogo")

    components.html(banner_top("LOTERIA 5x5 - 25 FIGURAS"), height=320)

    barajas = listar_barajas()
    if not barajas:
        st.error("No se encontraron barajas"); return

    col_baraja, col_color = st.columns([3,1])
    with col_baraja:
        sel_baraja = st.selectbox("📁 Selecciona baraja", barajas, key="sel_5x5")
    with col_color:
        color_entre = st.color_picker("Color entre", "#FF0000", key="color_5x5")

    files = cargar_files(sel_baraja, 54)
    if len(files) < 54:
        st.warning(f"Solo {len(files)} imágenes"); return

    aspecto = get_aspecto(files)

    c1, c2, c3, c4 = st.columns(4)
    with c1: div_interno = st.slider("Div interno", 2, 20, 8, key="div_5x5")
    with c2: sep_v = st.slider("Sep vertical", 5, 50, 20, key="sepv_5x5")
    with c3: sep_h = st.slider("Sep horizontal", 5, 50, 20, key="seph_5x5")
    with c4: g_negro = st.slider("Borde negro", 2, 20, 6, key="g_5x5")

    st.info(f"👁️ Visitas 5x5: {get_contador('visita_5x5')}")

    if st.button("🎲 GENERAR 5x5", type="primary", use_container_width=True, key="btn_gen_5x5"):
        with st.spinner("Generando 5x5..."):
            for _ in range(2): gc.collect()
            logica = generar_logica_5x5(files)
            hoja = generar_hoja_5x5(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto)
            st.session_state["hoja_5x5"] = hoja
            st.image(hoja, caption="Hoja 5x5", use_container_width=True)
            inc_baraja(os.path.basename(sel_baraja), "5x5")
            inc_contador("pdf_5x5")
            buf = io.BytesIO()
            hoja.save(buf, format="PNG")
            st.download_button("⬇️ Descargar PNG", buf.getvalue(), "loteria_5x5.png", "image/png", use_container_width=True, key="dl_5x5")

    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
    components.html(banner_venta_offline(), height=320)
