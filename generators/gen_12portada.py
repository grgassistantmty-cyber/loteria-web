import streamlit as st
import os
from utils.counters import registrar_entrada_generador, inc_baraja, inc_contador, get_contador
from utils.images import listar_barajas, cargar_files
from utils.loteria_core import generar_tabloide_12_con_portada_PULIDO, get_aspecto
from ui.banners import banner_top, banner_facebook, copiar_clabe_component
from PIL import Image
import io
import glob

def listar_portadas():
    if not os.path.exists("portadas"):
        return []
    exts = (".png", ".jpg", ".jpeg", ".webp", ".jfif")
    files = [os.path.join("portadas", f) for f in os.listdir("portadas") if f.lower().endswith(exts)]
    files.sort()
    return files

def render_12portada(ir_a):
    registrar_entrada_generador("12portada")
    
    if st.button("⬅️ Volver al Catálogo"):
        ir_a("catalogo")

    banner_top()
    st.title("🖼️ Tabloide 12 con Portada - PULIDO")
    st.caption("Lógica: 4x4 grid = 16 slots, 4 para portada 2x2, 12 cartas, 1 favorita repetida en pos random")

    col1, col2 = st.columns([2,1])
    with col1:
        barajas = listar_barajas()
        portadas = listar_portadas()
        if not barajas:
            st.error("No hay barajas en /barajas")
            return
        sel_baraja = st.selectbox("Elige baraja", barajas, key="baraja_12p")
        sel_portada = st.selectbox("Elige portada (imagen grande 2x2)", portadas, key="portada_12p") if portadas else None
        if not sel_portada:
            st.warning("Sube una imagen a /portadas para usar como cover 2x2")

    with col2:
        st.metric("Visitas", get_contador("visita_12portada"))
        st.metric("PDFs", get_contador("pdf_12portada"))

    if not sel_baraja or not sel_portada:
        return

    files = cargar_files(sel_baraja, 54)
    asp = get_aspecto(files)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: color = st.color_picker("Color entre cartas", "#000000", key="color_12p")
    with c2: div = st.slider("División interna", 0, 20, 8, key="div_12p")
    with c3: sep = st.slider("Separación", 0, 100, 20, key="sep_12p")

    # Elegir favorita
    st.write("Elige la imagen favorita que se repetirá 12 veces:")
    cols = st.columns(6)
    fav_idx = st.session_state.get("fav_idx_12p", 0)
    for i, f in enumerate(files[:18]):
        with cols[i % 6]:
            try:
                st.image(f, width=80)
                if st.button(f"Fav {i}", key=f"favbtn_{i}"):
                    st.session_state["fav_idx_12p"] = i
                    fav_idx = i
            except:
                pass
    
    favorita_path = files[fav_idx] if files else None
    if favorita_path:
        st.info(f"Favorita: {os.path.basename(favorita_path)}")

    if st.button("🎰 GENERAR TABLOIDE 12 + PORTADA", type="primary", use_container_width=True):
        if not favorita_path:
            st.error("Elige favorita")
            return
        with st.spinner("Generando PULIDO 12+portada (puede tardar 30s)..."):
            sheet = generar_tabloide_12_con_portada_PULIDO(files, sel_portada, favorita_path, color, div, sep)
            if not sheet:
                st.error("No se pudo después de 1500 intentos. Intenta de nuevo.")
                return
            
            st.session_state["last_12p"] = sheet
            st.success("¡Tabloide generado!")
            st.image(sheet, caption="Tabloide 4x4 con portada 2x2", use_column_width=True)
            
            inc_baraja(os.path.basename(sel_baraja), "12portada")
            inc_contador("pdf_12portada")
            banner_facebook()
            copiar_clabe_component()

    if "last_12p" in st.session_state:
        buf = io.BytesIO()
        st.session_state["last_12p"].save(buf, format="PNG")
        st.download_button("📥 Descargar PNG HD", buf.getvalue(), "tabloide_12_portada.png", "image/png", use_container_width=True)
