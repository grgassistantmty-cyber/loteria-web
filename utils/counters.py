import os, threading
from pathlib import Path
import streamlit as st
import glob

@st.cache_resource
def get_lock(): return threading.Lock()
lock = get_lock()

def get_base_path():
    p = Path("/data")
    try:
        if p.exists() and os.access(p, os.W_OK): return p
    except: pass
    return Path(".")
BASE_PATH = get_base_path()
BASE_PATH.mkdir(exist_ok=True)
CONTADOR_VISITAS = BASE_PATH / "visitas.txt"

def safe_int(s, default=0):
    try: return int(str(s).strip() or default)
    except: return default

if "visitado" not in st.session_state:
    st.session_state["visitado"]=True
    try:
        with lock:
            total = safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
            total+=1
            CONTADOR_VISITAS.write_text(str(total))
    except: total=1
else:
    try: total=safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
    except: total=1

visitas_total=total

def get_contador(nombre):
    path = BASE_PATH / f"contador_{nombre}.txt"
    if not path.exists(): return 0
    try: return safe_int(path.read_text())
    except: return 0

def inc_contador(nombre, cantidad=1):
    path = BASE_PATH / f"contador_{nombre}.txt"
    try:
        with lock:
            actual = get_contador(nombre) + cantidad
            path.write_text(str(actual))
            return actual
    except: return 0

def registrar_entrada_generador(nombre):
    key = f"entrada_registrada_{nombre}"
    if key not in st.session_state:
        inc_contador(f"visita_{nombre}")
        st.session_state[key] = True
