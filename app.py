import streamlit as st, importlib, os, glob
from utils.config import init_contadores

st.set_page_config(page_title="BINGO GENERADORES", layout="wide", initial_sidebar_state="collapsed")
init_contadores()

if "pagina" not in st.session_state: st.session_state["pagina"]="catalogo"
pagina = st.session_state["pagina"]

vistas_disponibles = {}
for path in glob.glob("vistas/vista_*.py"):
    nombre = os.path.basename(path).replace("vista_","").replace(".py","")
    vistas_disponibles[nombre] = f"vistas.vista_{nombre}"

if pagina == "catalogo":
    from vistas.catalogo import render
    render()
elif pagina in vistas_disponibles:
    modulo = importlib.import_module(vistas_disponibles[pagina])
    modulo.render()
else:
    st.session_state["pagina"]="catalogo"
    st.rerun()
