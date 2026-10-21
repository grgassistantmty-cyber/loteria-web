import streamlit as st
from collections import defaultdict

def _init_counters():
    if "contadores" not in st.session_state:
        st.session_state["contadores"] = defaultdict(int)
    if "barajas_count" not in st.session_state:
        st.session_state["barajas_count"] = defaultdict(int)

def registrar_entrada_generador(nombre):
    _init_counters()
    key = f"visita_{nombre}"
    st.session_state["contadores"][key] += 1

def get_contador(nombre):
    _init_counters()
    return st.session_state["contadores"].get(nombre, 0)

def inc_contador(nombre):
    _init_counters()
    st.session_state["contadores"][nombre] += 1
    return st.session_state["contadores"][nombre]

def inc_baraja(nombre_baraja, generador):
    _init_counters()
    key = f"{generador}_{nombre_baraja}"
    st.session_state["barajas_count"][key] += 1
    inc_contador(f"pdf_{generador}")
    return st.session_state["barajas_count"][key]

# alias por si algún archivo viejo lo llama diferente
def registrar_entrada(nombre):
    return registrar_entrada_generador(nombre)
