import streamlit as st
import io, os, gc
from PIL import Image
import streamlit.components.v1 as components

from utils.images import listar_barajas, cargar_files
from utils.loteria_core import get_aspecto, generar_logica_10dobles, generar_hoja_10dobles, imagenes_a_pdf_4x4dob
from utils.counters import registrar_entrada_generador, get_contador, inc_baraja, inc_contador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook

def render_10dobles(ir_a):
    registrar_entrada_generador("10dobles")
    if st.button("⬅️ Volver al Catálogo", key="back_10dob"):
        ir_a("catalogo")

    components.html(banner_top("LOTERIA 10 DOBLES - 54 BARAJA"), height=320)
    st.caption("54 figuras, dobles en pos 5 y 6")

    barajas = listar_barajas()
    if not barajas:
        st.error("No hay barajas"); return

    sel_baraja = st.selectbox("📁 Selecciona baraja", barajas, key="sel_10dob")
    color_entre = st.color_picker("Color", "#FF0000", key="color_10dob")

    files = cargar_files(sel_baraja, 54)
    if len(files) < 54:
        st.warning(f"Faltan imágenes: {len(files)}"); return

    aspecto = get_aspecto(files)
    c1, c2, c3 = st.columns(3)
    with c1: div_interno = st.slider("Div", 2, 20, 8, key="div_10dob")
    with c2: sep_v = st.slider("Sep V", 5, 50, 20, key="sepv_10dob")
    with c3: g_negro = st.slider("Borde", 2, 20, 6, key="g_10dob")

    st.info(f"👁️ Visitas 10dobles: {get_contador('visita_10dobles')}")

    if st.button("🎲 GENERAR 10 DOBLES", type="primary", use_container_width=True, key="btn_10dob"):
        with st.spinner("Generando..."):
            logica = generar_logica_10dobles(files)
            hoja = generar_hoja_10dobles(logica, color_entre, div_interno, sep_v, sep_v, g_negro, aspecto)
            st.session_state["hoja_10dob"] = hoja
            st.image(hoja, caption="10 Dobles", use_container_width=True)
            inc_baraja(os.path.basename(sel_baraja), "10dobles")
            inc_contador("pdf_10dobles")
            buf = io.BytesIO()
            hoja.save(buf, format="PNG")
            st.download_button("⬇️ Descargar", buf.getvalue(), "10dobles.png", "image/png", use_container_width=True, key="dl_10dob")

    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
