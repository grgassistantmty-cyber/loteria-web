import streamlit as st
st.set_page_config(page_title="Loteria Eliud PRO", layout="wide", page_icon="🎰")

from utils.counters import visitas_total, get_contador, registrar_entrada_generador
from ui.banners import banner_top, copiar_clabe_component, banner_facebook, banner_venta_offline
import streamlit.components.v1 as components

if "vista" not in st.session_state: st.session_state["vista"]="catalogo"
params=st.query_params
if "vista" in params and params["vista"] in ["catalogo","4x4","5x5","12portada","10dobles","4x4doblesfix"]:
    st.session_state["vista"]=params["vista"]

def ir_a(v): st.session_state["vista"]=v; st.query_params["vista"]=v; st.rerun()

# CATALOGO - LIGERO, NO CARGA GENERADORES
if st.session_state["vista"]=="catalogo":
    components.html(banner_top("LOTERIA ELIUD PRO - CATALOGO"), height=520)
    copiar_clabe_component()
    components.html(banner_facebook(), height=200)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎰 ENTRAR A 4x4", use_container_width=True): ir_a("4x4")
    with col2:
        if st.button("🎰 ENTRAR A 5x5", use_container_width=True): ir_a("5x5")
    with col3:
        if st.button("🎰 ENTRAR A 12 PORTADA", use_container_width=True): ir_a("12portada")
    col4, col5 = st.columns(2)
    with col4:
        if st.button("🎰 ENTRAR A 10 DOBLES", use_container_width=True): ir_a("10dobles")
    with col5:
        if st.button("🎰 ENTRAR A 4x4 DOBLES FIX", use_container_width=True): ir_a("4x4doblesfix")
    
    components.html(banner_venta_offline(), height=320)
    st.stop()

# LAZY LOADING - SOLO CARGA EL GENERADOR QUE EL USUARIO ELIGIO
if st.session_state["vista"]=="4x4":
    registrar_entrada_generador("4x4")
    from generators.gen_4x4 import render_4x4
    render_4x4(ir_a)
elif st.session_state["vista"]=="5x5":
    registrar_entrada_generador("5x5")
    from generators.gen_5x5 import render_5x5
    render_5x5(ir_a)
elif st.session_state["vista"]=="10dobles":
    registrar_entrada_generador("10dobles")
    from generators.gen_10dobles import render_10dobles
    render_10dobles(ir_a)
elif st.session_state["vista"]=="12portada":
    registrar_entrada_generador("12portada")
    from generators.gen_12portada import render_12portada
    render_12portada(ir_a)
elif st.session_state["vista"]=="4x4doblesfix":
    registrar_entrada_generador("4x4doblesfix")
    from generators.gen_4x4doblesfix import render_4x4doblesfix
    render_4x4doblesfix(ir_a)
