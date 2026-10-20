import streamlit as st
import importlib.util
from pathlib import Path

st.set_page_config(page_title="Loteria Eliud PRO", layout="wide", page_icon="🎰")

# Inicializa contadores base
from utils.config import init_session

init_session()

VISTAS = {
    "catalogo": "vistas/vista_catalogo.py",
    "4x4": "vistas/vista_4x4.py",
    "5x5": "vistas/vista_5x5.py",
    "10dobles": "vistas/vista_10dobles.py",
    "12portada": "vistas/vista_12portada.py",
    "4x4doblesfix": "vistas/vista_4x4doblesfix.py",
}

def load_and_render(ruta):
    spec = importlib.util.spec_from_file_location("mod", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "render"):
        mod.render()
    else:
        st.error(f"{ruta} no tiene render()")

vista = st.session_state.get("vista", "catalogo")
params = st.query_params
if "vista" in params and params["vista"] in VISTAS:
    vista = params["vista"]
    st.session_state["vista"] = vista

ruta = VISTAS.get(vista, VISTAS["catalogo"])
load_and_render(ruta)
