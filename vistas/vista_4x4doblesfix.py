import streamlit as st, os, tempfile, datetime, io
from utils.config import registrar_entrada_generador, ir_a, inc_contador
from utils.banners import banner_top, banner_facebook, copiar_clabe_component
from utils.barajas import listar_barajas, cargar_files, cargar_zip_temporal, cargar_imagenes_sueltas, get_aspecto, get_lock, cm_to_px
from generadores.core_4x4doblesfix import generar_ciclo_54_dobles_4x4dob, generar_con_resize_4x4dob, imagenes_a_pdf_4x4dob

def render():
    registrar_entrada_generador("4x4doblesfix")
    if st.button("⬅️ Volver"): ir_a("catalogo")
    st.markdown(banner_top("4x4 DOBLES FIX - 54 DOBLES GARANTIZADOS - 14 HOJAS"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","ZIP","Fotos"], key="m4x4")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="s4x4")
            files=cargar_files([p for p in barajas if os.path.basename(p)==sel][0])
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP", type=["zip"], key="z4x4")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54)
        else:
            ups=st.file_uploader("Fotos", type=["jpg","png"], accept_multiple_files=True, key="i4x4")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54)
        layout=st.selectbox("Layout", ["2x2","1x4"], key="lay4x4")
        div=st.number_input("Div", value=2, key="d4x4"); g=st.number_input("Marco", value=6, key="g4x4")
        sep_v=st.number_input("Sep V", value=80, key="sv4x4"); sep_h=st.number_input("Sep H", value=80, key="sh4x4")
        color=st.color_picker("Color", "#FF00FF", key="c4x4")
        ancho=st.text_input("Ancho","21", key="a4x4"); alto=st.text_input("Alto","28", key="al4x4"); dpi=st.text_input("DPI","300", key="dpi4x4")
        salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4x4")
    with col2:
        if files:
            asp=get_aspecto(files)
            if st.button("🎰 GENERAR CICLO 14 HOJAS - 54 DOBLES", type="primary", use_container_width=True):
                with get_lock():
                    hojas,dobles,rep=generar_ciclo_54_dobles_4x4dob(files)
                    st.session_state["hojas4x4"]=hojas; st.session_state["rep4x4"]=rep
                    inc_contador("4x4doblesfix",1)
            if "hojas4x4" in st.session_state:
                finales=[]
                for hoja in st.session_state["hojas4x4"]:
                    o,f=generar_con_resize_4x4dob(hoja, color, div, sep_v, sep_h, g, ancho, alto, dpi, asp, layout)
                    finales.append(f if salida=="RESIZE cm" else o)
                for i,im in enumerate(finales): st.image(im, caption=f"Hoja {i+1}/14", use_container_width=True)
                pdf=imagenes_a_pdf_4x4dob(finales)
                st.download_button("📄 PDF 14 HOJAS 54 DOBLES", pdf, f"4x4doblesfix_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf", "application/pdf", use_container_width=True, type="primary")
