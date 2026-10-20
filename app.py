import streamlit as st
import importlib.util
import os
import sys

# Asegura que /app esté en path
sys.path.append("/app")

# === IMPORTS QUE SI EXISTEN ===
from utils.config import init_session
from utils.banners import banner_top

st.set_page_config(page_title="Lotería Profesional", layout="wide", initial_sidebar_state="collapsed")

init_session()
banner_top()

# === RUTAS DE VISTAS ===
VISTAS = {
    "catalogo": "vistas/vista_catalogo.py",
    "4x4": "vistas/vista_4x4.py",
    "5x5": "vistas/vista_5x5.py",
    "10dobles": "vistas/vista_10dobles.py",
    "12portada": "vistas/vista_12portada.py",
    "4x4doblesfix": "vistas/vista_4x4doblesfix.py",
}

def load_and_render(ruta):
    if not os.path.exists(ruta):
        st.error(f"No existe: {ruta}")
        st.write("Archivos en vistas:", os.listdir("vistas") if os.path.exists("vistas") else "no existe vistas/")
        return
    spec = importlib.util.spec_from_file_location("vista", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

# Vista actual
vista_actual = st.session_state.get("vista_actual", "catalogo")
ruta = VISTAS.get(vista_actual, VISTAS["catalogo"])

load_and_render(ruta)
