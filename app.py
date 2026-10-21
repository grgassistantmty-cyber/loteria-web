import streamlit as st

st.set_page_config(
    page_title="En Mantenimiento",
    page_icon="🛠️",
    layout="centered"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp {background-color: #0B1020;}
.whatsapp-btn {
    display: inline-block;
    background-color: #25D366;
    color: white !important;
    padding: 14px 28px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: bold;
    font-size: 18px;
    margin-top: 15px;
    transition: 0.3s;
}
.whatsapp-btn:hover {
    background-color: #128C7E;
    transform: scale(1.05);
}
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
        <p style='font-size: 16px; margin:0;'>Gracias por tu paciencia ❤️</p>
    </div>
    <br>
    <a href="https://wa.me/528115566250?text=Hola!%20Vi%20que%20la%20app%20esta%20en%20mantenimiento" target="_blank" class="whatsapp-btn">
        📱 Contáctanos: 811 556 6250
    </a>
    <br><br>
    <p style='font-size: 13px; color: #888;'>Click en el botón para ir directo a WhatsApp</p>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Revisar si ya volvió", use_container_width=True):
    st.rerun()
