import streamlit as st, os, tempfile, datetime, io
from utils.config import registrar_entrada_generador, ir_a, inc_contador
from utils.banners import banner_top, banner_facebook, copiar_clabe_component, instrucciones_html
from utils.barajas import listar_barajas, cargar_files, cargar_zip_temporal, cargar_imagenes_sueltas, get_lock
from generadores.core_pocitos30 import generar_tabloide_pil, generar_pdf_bytes_pocitos

def render():
    registrar_entrada_generador("pocitos30")
    if st.button("⬅️ Volver"): ir_a("catalogo")
    st.markdown(banner_top("POCITOS 30 - 12 COMODINES RANDOM - MITADES ORIGINALES"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.markdown(instrucciones_html("POCITOS 30: 30 pozos, 5x6. 12 comodines random por juego. Mitades M1/M2 intactas."), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","ZIP","Fotos"], key="mP30")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sP30")
            files=cargar_files([p for p in barajas if os.path.basename(p)==sel][0])
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54", type=["zip"], key="zP30")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54)
        else:
            ups=st.file_uploader("54 fotos", type=["jpg","png","webp"], accept_multiple_files=True, key="iP30")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54)
        num=st.number_input("No. Tabloides (cada tabloide = 6 juegos)", value=1, min_value=1, max_value=100, key="nP30")
    with col2:
        if files:
            c1,c2=st.columns(2)
            with c1:
                if st.button("👁️ VISTA PREVIA 1 JUEGO (30 pozos)", use_container_width=True):
                    with get_lock():
                        img=generar_tabloide_pil(files, tempfile.mkdtemp())
                        st.session_state["prevP30"]=img
            with c2:
                if st.button("🎰 GENERAR PDF POCITOS 30", type="primary", use_container_width=True):
                    with get_lock():
                        inc_contador("pocitos30",1)
                        pdf=generar_pdf_bytes_pocitos(files, num)
                        st.session_state["pdfP30"]=pdf
            if "prevP30" in st.session_state:
                st.image(st.session_state["prevP30"], caption="Preview 1 juego - 30 pozos con mitades", use_container_width=True)
            if "pdfP30" in st.session_state:
                fecha=datetime.datetime.now().strftime("%Y%m%d_%H%M")
                st.download_button(f"📄 PDF POCITOS 30 - {num} tabloides = {num*6} juegos", st.session_state["pdfP30"], f"POCITOS30_{num}tab_{fecha}.pdf", "application/pdf", use_container_width=True, type="primary")
