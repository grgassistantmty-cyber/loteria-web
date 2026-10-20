import streamlit as st
import threading

_lock = threading.Lock()

def get_lock(): return _lock

def init_contadores():
    for k in ["visita_5x5","visita_10dobles","visita_12portada","visita_4x4doblesfix","visita_pocitos30",
              "5x5","10dobles","12portada","4x4doblesfix","pocitos30"]:
        if k not in st.session_state: st.session_state[k]=0
        if f"uso_global_{k}" not in st.session_state: st.session_state[f"uso_global_{k}"]={}
    if "uso_global_10" not in st.session_state: st.session_state["uso_global_10"]={}
    if "uso_como_dup_10" not in st.session_state: st.session_state["uso_como_dup_10"]={}
    if "hash_10" not in st.session_state: st.session_state["hash_10"]=set()

def get_contador(k): return st.session_state.get(k,0)
def inc_contador(k, v=1): st.session_state[k]=st.session_state.get(k,0)+v
def registrar_entrada_generador(gen_id): inc_contador(f"visita_{gen_id}",1)
def ir_a(pagina): st.session_state["pagina"]=pagina; st.rerun()
def inc_baraja(nombre, gen): 
    key=f"baraja_{nombre}_{gen}"
    st.session_state[key]=st.session_state.get(key,0)+1
