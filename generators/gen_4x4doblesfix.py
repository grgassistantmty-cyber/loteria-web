import streamlit as st
import os
from utils.counters import registrar_entrada_generador, inc_baraja, inc_contador, get_contador
from utils.images import listar_barajas, cargar_files
from utils.loteria_core import generar_ciclo_54_dobles_4x4dob, generar_original_fijo_4x4dob, generar_con_resize_4x4dob, imagenes_a_pdf_4x4dob, get_aspecto, CICLO_FIJO_4x4DOB
from ui.banners import banner_top, banner_facebook, copiar_clabe_component
import io

def render_4x4doblesfix(ir_a):
    registrar_entrada_generador("4x4doblesfix")
    
    if st.button("⬅️ Volver al Catálogo"):
        ir_a("catalogo")

    banner_top()
    st.title("♻️ 4x4 Dobles FIX - Ciclo 54")
    st.caption(f"Lógica: Ciclo fijo de {CICLO_FIJO_4x4DOB} hojas, 54 figuras + 2 repetidas = 56 dobles, dobles en pos 5 y 6")

    col1, col2 = st.columns([2,1])
    with col1:
        barajas = listar_barajas()
        if not barajas:
            st.error("No hay barajas")
            return
        sel = st.selectbox("Elige baraja", barajas, key="baraja_4x4dob")
    with col2:
        st.metric("Visitas", get_contador("visita_4x4doblesfix"))
        st.metric("PDFs", get_contador("pdf_4x4doblesfix"))

    if not sel:
        return

    files = cargar_files(sel, 54)
    if len(files) < 54:
        st.warning(f"Necesitas 54, tienes {len(files)}")
        return

    asp = get_aspecto(files)

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1: color = st.color_picker("Color", "#000000", key="color_4x4dob")
    with c2: div = st.slider("Div", 0, 20, 8, key="div_4x4dob")
    with c3: sep_v = st.slider("Sep V", 0, 100, 15, key="sepv_4x4dob")
    with c4: sep_h = st.slider("Sep H", 0, 100, 15, key="seph_4x4dob")

    c5, c6 = st.columns(2)
    with c5: g_negro = st.slider("Borde negro", 0, 30, 10, key="g_4x4dob")
    with c6: layout = st.selectbox("Layout", ["2x2", "1x4"], key="layout_4x4dob")

    if st.button(f"🎰 GENERAR CICLO COMPLETO DE {CICLO_FIJO_4x4DOB} HOJAS", type="primary", use_container_width=True):
        with st.spinner(f"Generando ciclo de {CICLO_FIJO_4x4DOB} hojas..."):
            hojas, dobles_ciclo, repetidas = generar_ciclo_54_dobles_4x4dob(files)
            
            st.session_state["hojas_4x4dob"] = hojas
            st.session_state["dobles_ciclo"] = dobles_ciclo
            
            # Mostrar primera hoja como preview
            first_sheet = generar_original_fijo_4x4dob(hojas[0], color, div, sep_v, sep_h, g_negro, asp, layout)
            st.success(f"Ciclo generado: {len(hojas)} hojas | Dobles del ciclo: {len(dobles_ciclo)} | Repetidas: {repetidas}")
            st.image(first_sheet, caption=f"Hoja 1 de {CICLO_FIJO_4x4DOB} - Preview", use_column_width=True)
            
            # Mostrar las 14 miniaturas
            st.write("Vista rápida del ciclo completo:")
            cols = st.columns(4)
            for i, hoja_data in enumerate(hojas):
                sheet = generar_original_fijo_4x4dob(hoja_data, color, div, sep_v, sep_h, g_negro, asp, layout)
                with cols[i % 4]:
                    st.image(sheet, caption=f"Hoja {i+1}", use_column_width=True)
            
            inc_baraja(os.path.basename(sel), "4x4doblesfix")
            inc_contador("pdf_4x4doblesfix")

    # Descargas
    if "hojas_4x4dob" in st.session_state:
        hojas = st.session_state["hojas_4x4dob"]
        
        # Generar todos los PNGs para PDF
        if st.button("📄 Crear PDF con las 14 hojas", use_container_width=True):
            with st.spinner("Creando PDF..."):
                imgs = []
                for hoja_data in hojas:
                    sheet = generar_original_fijo_4x4dob(hoja_data, color, div, sep_v, sep_h, g_negro, asp, layout)
                    imgs.append(sheet)
                
                pdf_bytes = imagenes_a_pdf_4x4dob(imgs)
                if pdf_bytes:
                    st.download_button("📥 Descargar PDF 14 Hojas", pdf_bytes, "ciclo_54_14hojas.pdf", "application/pdf", use_container_width=True)
        
        # Descargar ciclo como ZIP de PNGs
        if st.button("📦 Crear ZIP con 14 PNGs", use_container_width=True):
            import zipfile
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for i, hoja_data in enumerate(hojas):
                    sheet = generar_original_fijo_4x4dob(hoja_data, color, div, sep_v, sep_h, g_negro, asp, layout)
                    img_buf = io.BytesIO()
                    sheet.save(img_buf, format="PNG")
                    zf.writestr(f"hoja_{i+1:02d}.png", img_buf.getvalue())
            st.download_button("📥 Descargar ZIP", zip_buf.getvalue(), "ciclo_54_14pngs.zip", "application/zip", use_container_width=True)
