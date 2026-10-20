import os, json, streamlit as st
from datetime import datetime

# === CONFIG GLOBAL ===
DPI = 300
MARGEN_CM = 0.5
EXCEL_COLORS = ["#FF0000", "#00B050", "#0070C0", "#FFC000", "#7030A0"]

def init_session():
    if "vista_actual" not in st.session_state:
        st.session_state["vista_actual"] = "catalogo"
    if "baraja_seleccionada" not in st.session_state:
        st.session_state["baraja_seleccionada"] = None
    if "ultimo_generado" not in st.session_state:
        st.session_state["ultimo_generado"] = None

def ir_a(vista):
    st.session_state["vista_actual"] = vista
    st.rerun()

def contador_visitas():
    path = "/tmp/visitas.json"
    try:
        if os.path.exists(path):
            with open(path, "r") as f: 
                data=json.load(f)
        else: 
            data={"total":0}
        data["total"]+=1
        with open(path,"w") as f: 
            json.dump(data,f)
        return data["total"]
    except: 
        return 0

def get_visitas():
    return contador_visitas()

def ranking_barajas():
    return []

# Para que no falle si tu app.py importa otras cosas
def __getattr__(name):
    # si piden cualquier otra cosa, regresa función dummy
    def dummy(*args, **kwargs):
        return None
    return dummy
