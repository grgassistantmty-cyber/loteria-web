import streamlit as st
from generators.gen_4x4 import render_4x4
from generators.gen_5x5 import render_5x5
from generators.gen_10dobles import render_10dobles
from generators.gen_12portada import render_12portada
from generators.gen_4x4doblesfix import render_4x4doblesfix
from generators.gen_catalogo import render_catalogo

st.set_page_config(page_title="Lotería Mexicana PRO", page_icon="🎲", layout="wide")

if "vista" not in st.session_state:
    st.session_state["vista"] = "catalogo"

def ir_a(vista):
    st.session_state["vista"] = vista
    st.rerun()

vista = st.session_state["vista"]

if vista == "catalogo":
    render_catalogo(ir_a)
elif vista == "4x4":
    render_4x4(ir_a)
elif vista == "5x5":
    render_5x5(ir_a)
elif vista == "10dobles":
    render_10dobles(ir_a)
elif vista == "12portada":
    render_12portada(ir_a)
elif vista == "4x4doblesfix":
    render_4x4doblesfix(ir_a)
else:
    render_catalogo(ir_a)
