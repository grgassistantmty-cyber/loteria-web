import threading
from pathlib import Path
import streamlit as st
st.set_page_config(page_title="Loteria Eliud PRO", layout="wide", page_icon="🎰")

@st.cache_resource
def get_lock(): return threading.Lock()
lock = get_lock()

# tus contadores y session_state igual que original
if "vista" not in st.session_state: st.session_state["vista"]="catalogo"
if "uso_global_4x4" not in st.session_state: st.session_state["uso_global_4x4"]={}
if "uso_global_5x5" not in st.session_state: st.session_state["uso_global_5x5"]={}
if "uso_global_10" not in st.session_state: st.session_state["uso_global_10"]={}
if "uso_como_dup_10" not in st.session_state: st.session_state["uso_como_dup_10"]={}
if "hash_10" not in st.session_state: st.session_state["hash_10"]=set()

def ir_a(v): st.session_state["vista"]=v; st.query_params["vista"]=v; st.rerun()

# ROUTER
if st.session_state.vista=="catalogo":
    from generators.gen_catalogo import render_catalogo
    render_catalogo(ir_a, lock)
elif st.session_state.vista=="4x4":
    from generators.gen_4x4 import render_4x4
    render_4x4(ir_a, lock)
elif st.session_state.vista=="5x5":
    from generators.gen_5x5 import render_5x5
    render_5x5(ir_a, lock)
elif st.session_state.vista=="10dobles":
    from generators.gen_10dobles import render_10dobles
    render_10dobles(ir_a, lock)
elif st.session_state.vista=="12portada":
    from generators.gen_12portada import render_12portada
    render_12portada(ir_a, lock)
elif st.session_state.vista=="4x4doblesfix":
    from generators.gen_4x4doblesfix import render_4x4doblesfix
    render_4x4doblesfix(ir_a, lock)
