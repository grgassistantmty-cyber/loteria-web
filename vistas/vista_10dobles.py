import streamlit as st, os, tempfile, datetime, io
from utils.config import registrar_entrada_generador, ir_a, inc_contador
from utils.banners import banner_top, banner_facebook, copiar_clabe_component
from utils.barajas import listar_barajas, cargar_files, cargar_zip_temporal, cargar_imagenes_sueltas, get_aspecto, get_lock, cm_to_px
from generadores.core_10dobles import generar_logica_10_cartas_54, generar_original_fijo_10, generar_con_resize_10

def render():
    registrar_entrada_generador("10dobles")
    if st.button("⬅️ Volver"): ir_a("catalogo")
    st.markdown(banner_top("10 CARTAS - DOBLES - SIN CHOCAR"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","ZIP","Fotos"], key="m10")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="s10")
            files=cargar_files([p for p in barajas if os.path.basename(p)==sel][0])
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP", type=["zip"], key="z10")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54)
        else:
            ups=st.file_uploader("Fotos", type=["jpg","png"], accept_multiple_files=True, key="i10")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54)
        layout=st.selectbox("Layout", ["5x2","2x5"], key="lay10")
        div=st.number_input("Div", value=2, key="d10"); g=st.number_input("Marco", value=6, key="g10")
        sep_v=st.number_input("Sep V", value=60, key="sv10"); sep_h=st.number_input("Sep H", value=60, key="sh10")
        color=st.color_picker("Color", "#FF00FF", key="c10")
        ancho=st.text_input("Ancho cm","36", key="a10"); alto=st.text_input("Alto cm","25", key="al10"); dpi=st.text_input("DPI","300", key="dpi10")
        salida=st.radio("Salida", ["RESIZE","ORIGINAL"], horizontal=True, key="out10")
    with col2:
        if files:
            asp=get_aspecto(files)
            if st.button("🎰 GENERAR 10 CARTAS", type="primary", use_container_width=True):
                with get_lock():
                    cartas,dups=generar_logica_10_cartas_54(files, es_nuevo_juego=False)
                    if cartas:
                        inc_contador("10dobles",1)
                        orig=generar_original_fijo_10(cartas, color, div, sep_v, sep_h, g, asp, layout)
                        Wf=cm_to_px(ancho,dpi); Hf=cm_to_px(alto,dpi)
                        final=orig.resize((Wf,Hf), __import__("PIL.Image").Image.LANCZOS) if salida=="RESIZE" else orig
                        st.session_state["10img"]=final; st.session_state["10orig"]=orig
            if "10img" in st.session_state:
                st.image(st.session_state["10img"], use_container_width=True)
                b=io.BytesIO(); st.session_state["10img"].save(b, format="PNG")
                st.download_button("📥 PNG 10 CARTAS", b.getvalue(), f"10dobles_{datetime.datetime.now().strftime('%Y%m%d')}.png", "image/png", use_container_width=True)
