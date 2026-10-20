import streamlit as st, os, tempfile, datetime
from utils.config import get_contador, inc_contador, registrar_entrada_generador, ir_a
from utils.banners import banner_top, banner_facebook, copiar_clabe_component, instrucciones_html
from utils.barajas import listar_barajas, cargar_files, cargar_zip_temporal, cargar_imagenes_sueltas, get_aspecto, get_lock, cm_to_px
from generadores.core_5x5 import generar_logica_5x5, generar_hoja_5x5
from utils.barajas import cm_to_px

def render():
    registrar_entrada_generador("5x5")
    if st.button("⬅️ Volver"): ir_a("catalogo")
    st.markdown(banner_top("BINGO 5x5 - 4 CARTAS X HOJA - SIN CHOCAR"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    barajas=listar_barajas()
    col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","ZIP","Fotos"], key="modo5x5")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Elige", [os.path.basename(p) for p in barajas], key="sel5x5")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel)
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54", type=["zip"], key="zip5x5")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54)
        else:
            ups=st.file_uploader("Fotos 54", type=["jpg","png","jpeg","webp"], accept_multiple_files=True, key="img5x5")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54)
        div=st.number_input("Div", value=4, key="div5x5"); g=st.number_input("Marco negro", value=6, key="g5x5")
        sep_v=st.number_input("Sep V", value=40, key="sv5x5"); sep_h=st.number_input("Sep H", value=40, key="sh5x5")
        color=st.color_picker("Color", "#FF00FF", key="col5x5")
        if st.session_state.get("uso_global_5x5") and st.button("Reset uso 5x5"): st.session_state["uso_global_5x5"]={}
    with col2:
        if files:
            asp=get_aspecto(files)
            if st.button("🎰 GENERAR 5x5 LOGICA", type="primary", use_container_width=True):
                with get_lock():
                    data=generar_logica_5x5(files)
                    if data:
                        inc_contador("5x5",1)
                        sheet=generar_hoja_5x5(data, color, div, sep_v, sep_h, g, asp)
                        st.session_state["sheet5x5"]=sheet
                    else: st.error("No se pudo generar, intenta de nuevo")
            if "sheet5x5" in st.session_state:
                st.image(st.session_state["sheet5x5"], use_container_width=True)
                buf=st.session_state["sheet5x5"]
                import io; b=io.BytesIO(); buf.save(b, format="PNG")
                st.download_button("📥 PNG 5x5", b.getvalue(), f"5x5_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.png", "image/png", use_container_width=True)
