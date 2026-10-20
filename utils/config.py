import os, glob, threading
from pathlib import Path
import streamlit as st

@st.cache_resource
def get_lock():
    return threading.Lock()
lock = get_lock()

def get_base_path():
    p = Path("/data")
    try:
        if p.exists() and os.access(p, os.W_OK):
            return p
    except:
        pass
    return Path(".")
BASE_PATH = get_base_path()
BASE_PATH.mkdir(exist_ok=True)
CONTADOR_VISITAS = BASE_PATH / "visitas.txt"

def safe_int(s, default=0):
    try: return int(str(s).strip() or default)
    except: return default

def init_session():
    if "visitado" not in st.session_state:
        st.session_state["visitado"]=True
        try:
            with lock:
                total = safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
                total+=1
                CONTADOR_VISITAS.write_text(str(total))
        except: pass
    if "vista" not in st.session_state: st.session_state["vista"]="catalogo"
    if "uso_global_4x4" not in st.session_state: st.session_state["uso_global_4x4"]={}
    if "uso_global_5x5" not in st.session_state: st.session_state["uso_global_5x5"]={}
    if "uso_global_10" not in st.session_state: st.session_state["uso_global_10"]={}
    if "uso_como_dup_10" not in st.session_state: st.session_state["uso_como_dup_10"]={}
    if "hash_10" not in st.session_state: st.session_state["hash_10"]=set()

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

def inc_baraja(baraja_nombre, generador):
    safe = "".join(c if c.isalnum() else "_" for c in baraja_nombre)[:50]
    path_total = BASE_PATH / f"contador_baraja_{safe}.txt"
    path_gen = BASE_PATH / f"contador_baraja_{safe}_{generador}.txt"
    try:
        with lock:
            a = safe_int(path_total.read_text() if path_total.exists() else 0)
            path_total.write_text(str(a+1))
            b = safe_int(path_gen.read_text() if path_gen.exists() else 0)
            path_gen.write_text(str(b+1))
    except: pass

def get_ranking_barajas():
    patron = str(BASE_PATH / "contador_baraja_*.txt")
    files = [f for f in glob.glob(patron) if not any(f.endswith(f"_{x}.txt") for x in ["4x4","5x5","10dobles","12portada","4x4doblesfix"])]
    ranking=[]
    for fp in files:
        try:
            nombre = os.path.basename(fp).replace("contador_baraja_","").replace(".txt","").replace("_"," ")
            cnt = safe_int(open(fp,"r", encoding="utf-8", errors="ignore").read())
            ranking.append((nombre,cnt))
        except: pass
    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking[:15]

def registrar_entrada_generador(nombre):
    key = f"entrada_registrada_{nombre}"
    if key not in st.session_state:
        inc_contador(f"visita_{nombre}")
        st.session_state[key] = True

def ir_a(v):
    st.session_state["vista"]=v
    st.query_params["vista"]=v
    st.rerun()

def get_visitas_total():
    try: return safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
    except: return 1

EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}
