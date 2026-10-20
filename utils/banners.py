import streamlit as st
import streamlit.components.v1 as components

def banner_top():
    st.markdown("""
    <div style='background:#111;padding:10px;border-radius:10px;text-align:center;color:white'>
    Lotería Mexicana - Generador Profesional
    </div>
    """, unsafe_allow_html=True)

def banner_facebook():
    st.markdown("""
    <div style='background:#1877F2;padding:8px;border-radius:8px;text-align:center;color:white'>
    Síguenos en Facebook - Lotería Profesional
    </div>
    """, unsafe_allow_html=True)

def banner_venta_offline():
    st.markdown("""
    <div style='background:#25D366;padding:8px;border-radius:8px;text-align:center;color:white'>
    Venta Offline - WhatsApp
    </div>
    """, unsafe_allow_html=True)

def copiar_clabe_component():
    clabe = "012180015849123456"
    components.html(f"""
    <div>
    <input type="text" value="{clabe}" id="clabe" style="width:100%">
    <button onclick="navigator.clipboard.writeText('{clabe}')">Copiar CLABE</button>
    </div>
    """, height=80)

def instrucciones_html():
    return "<div>Instrucciones de impresión</div>"
