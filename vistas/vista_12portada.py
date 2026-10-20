import streamlit as st, os, tempfile
from utils.config import registrar_entrada_generador, ir_a
from utils.banners import banner_top, banner_facebook
from utils.barajas import listar_barajas, cargar_files, cargar_zip_temporal, cargar_imagenes_sueltas, get_lock
from generadores.core_12portada import generar_tabloide_12_con_portada_PULIDO

def render():
    registrar_entrada_generador("12portada")
    if st.button("⬅️ Volver"): ir_a("catalogo")
    st.markdown(banner_top("TABLOIDE 12 + PORTADA - FAVORITA FIJA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","ZIP"], key="m12p")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="s12p")
            files=cargar_files([p for p in barajas if os.path.basename(p)==sel][0])
        else:
            up=st.file_uploader("ZIP 54", type=["zip"], key="z12p")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54)
        portada=st.file_uploader("Portada COVER", type=["jpg","png"], key="port12")
        favorita=st.file_uploader("Favorita (la que se repite 12 veces)", type=["jpg","png"], key="fav12")
        div=st.number_input("Div", value=4, key="d12"); sep=st.number_input("Sep", value=20, key="sep12")
        color=st.color_picker("Color", "#000000", key="c12")
    with col2:
        if files and portada and favorita:
            tmp=tempfile.mkdtemp()
            p_cover=os.path.join(tmp, portada.name); open(p_cover,"wb").write(portada.getbuffer())
            p_fav=os.path.join(tmp, favorita.name); open(p_fav,"wb").write(favorita.getbuffer())
            if st.button("🎰 GENERAR 12+PORTADA", type="primary", use_container_width=True):
                with get_lock():
                    sheet=generar_tabloide_12_con_portada_PULIDO(files, p_cover, p_fav, color, div, sep)
                    if sheet: st.session_state["12p"]=sheet
            if "12p" in st.session_state:
                st.image(st.session_state["12p"], use_container_width=True)
