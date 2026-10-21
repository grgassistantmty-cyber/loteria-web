import streamlit as st
import os
from utils.counters import registrar_entrada_generador, inc_baraja, inc_contador, get_contador
from utils.images import listar_barajas, cargar_files
from utils.loteria_core import generar_logica_10_cartas_54, generar_original_fijo_10, generar_con_resize_10, get_aspecto, cm_to_px
from ui.banners import banner_top, banner_facebook, copiar_clabe_component
from PIL import Image
import io

def render_10dobles(ir_a):
    registrar_entrada_generador("10dobles")
    
    if st.button("⬅️ Volver al Catálogo"):
        ir_a("catalogo")

    banner_top()
    st.title("🔥 10 Cartas - 54 Figuras - Dobles en Pos 5 y 6")
    st.caption("Lógica: 10 dups forzados en pos 5 y 6, 3x(-2) = 46 huecos, no choques")

    col1, col2 = st.columns([2,1])
    with col1:
        barajas = listar_barajas()
        if not barajas:
            st.error("No hay barajas en /barajas")
            return
        sel = st.selectbox("Elige baraja", barajas, key="baraja_10dobles")
        es_nuevo = st.checkbox("🔄 Nuevo juego (reset contadores)", value=False)

    with col2:
        st.metric("Visitas a este generador", get_contador("visita_10dobles"))
        st.metric("PDFs generados", get_contador("pdf_10dobles"))

    if not sel:
        return

    files = cargar_files(sel, 54)
    if len(files) < 54:
        st.warning(f"Solo hay {len(files)} imágenes, necesitas 54")
        return

    asp = get_aspecto(files)

    # Controles como tu app original
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1: color = st.color_picker("Color entre cartas", "#FFFFFF", key="color_10")
    with c2: div = st.slider("División interna", 0, 20, 8, key="div_10")
    with c3: sep_v = st.slider("Sep Vertical", 0, 100, 15, key="sepv_10")
    with c4: sep_h = st.slider("Sep Horizontal", 0, 100, 15, key="seph_10")

    c5, c6, c7 = st.columns(3)
    with c5: g_negro = st.slider("Borde negro", 0, 30, 10, key="g_10")
    with c6: layout = st.selectbox("Layout", ["5x2", "2x5"], key="layout_10")
    with c7: dpi = st.selectbox("DPI", [150, 300, 600], index=1)

    if st.button("🎰 GENERAR 10 CARTAS - 54 BARAJA", type="primary", use_container_width=True):
        with st.spinner("Generando lógica 10 dobles..."):
            cartas, dups = generar_logica_10_cartas_54(files, es_nuevo_juego=es_nuevo)
            if not cartas:
                st.error("No se pudo generar después de 2500 intentos. Intenta de nuevo.")
                return
            
            orig = generar_original_fijo_10(cartas, color, div, sep_v, sep_h, g_negro, asp, layout)
            st.session_state["last_10dobles_orig"] = orig
            st.session_state["last_10dobles_cartas"] = cartas
            
            st.success(f"¡Generado! Dups usados: {len(dups)}")
            st.image(orig, caption="Vista previa 5x2 - Alta resolución", use_column_width=True)
            
            inc_baraja(os.path.basename(sel), "10dobles")
            inc_contador("pdf_10dobles")
            banner_facebook()
            copiar_clabe_component()

    # Descarga
    if "last_10dobles_orig" in st.session_state:
        orig = st.session_state["last_10dobles_orig"]
        buf = io.BytesIO()
        orig.save(buf, format="PNG")
        st.download_button("📥 Descargar PNG HD", buf.getvalue(), "loteria_10dobles_54.png", "image/png", use_container_width=True)
        
        # PDF con medidas
        ancho = st.text_input("Ancho cm para PDF", "30", key="ancho_10")
        alto = st.text_input("Alto cm para PDF", "20", key="alto_10")
        if st.button("Crear PDF a medida"):
            _, final = generar_con_resize_10(st.session_state["last_10dobles_cartas"], color, div, sep_v, sep_h, g_negro, ancho, alto, dpi, asp, layout)
            buf_pdf = io.BytesIO()
            final.save(buf_pdf, format="PDF")
            st.download_button("📄 Descargar PDF", buf_pdf.getvalue(), "loteria_10dobles.pdf", "application/pdf")
