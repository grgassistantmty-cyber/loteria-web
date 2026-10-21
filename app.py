import streamlit as st

st.set_page_config(
    page_title="En Mantenimiento",
    page_icon="🛠️",
    layout="centered"
)

# Ocultar menú de Streamlit
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp {background-color: #0B1020;}
</style>
""", unsafe_allow_html=True)

st.image("mantenimiento.jpg", use_container_width=True)

st.markdown("""
<div style='text-align: center; padding: 20px; color: white;'>
    <h1 style='color: white; font-size: 42px; margin-bottom: 10px;'>🛠️ Estamos en Mantenimiento</h1>
    <p style='font-size: 20px; color: #D4AF37;'>
        Estamos mejorando la plataforma para ti.<br>
        ¡Tu generador de combinaciones volverá en unas horas con todo y mejoras!
    </p>
    <br>
    <div style='background: #1a223f; border-radius: 15px; padding: 20px; border: 1px solid #D4AF37;'>
        <p style='font-size: 16px; margin:0;'>⏰ Tiempo estimado: <b>Unas horas</b></p>
        <p style='font-size: 16px; margin:0;'>📱 Cualquier duda: Contáctanos por WhatsApp</p>
    </div>
    <br><br>
    <p style='font-size: 13px; color: #888;'>Gracias por tu paciencia ❤️</p>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Revisar si ya volvió", use_container_width=True):
    st.rerun()
