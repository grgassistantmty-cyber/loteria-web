import streamlit as st

def banner_top(texto=""):
    if texto == "":
        texto = "Lotería Mexicana - Generador Profesional"
    return f"""
    <div style='background:linear-gradient(90deg,#111,#333);padding:14px;border-radius:10px;text-align:center;color:white;font-weight:bold;border:1px solid #00FF88'>
    {texto}
    </div>
    """

def banner_facebook():
    return """
    <div style='background:#1877F2;padding:10px;border-radius:8px;text-align:center;color:white;margin:10px 0'>
    📘 Síguenos en Facebook - Lotería Profesional
    </div>
    """

def copiar_clabe_component():
    st.markdown("""
    <div style='background:#222;padding:10px;border-radius:8px;text-align:center;color:#00FF88'>
    CLABE: 012180015849123456
    </div>
    """, unsafe_allow_html=True)

def banner_venta_offline():
    return "<div></div>"

def instrucciones_html():
    return "<div></div>"
