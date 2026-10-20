import streamlit as st
from utils.config import get_contador, ir_a
from utils.banners import banner_top, banner_facebook, copiar_clabe_component

GENERADORES = [
    {"id": "5x5", "titulo": "5x5 TRADICIONAL", "desc": "25 pozos - Clásico", "emoji": "🎯", "color": "#00FF88"},
    {"id": "10dobles", "titulo": "10 TABLOIDES DOBLES", "desc": "10 juegos dobles", "emoji": "🎲", "color": "#FFAA00"},
    {"id": "12portada", "titulo": "12 + PORTADA", "desc": "12 juegos + portada", "emoji": "🖼️", "color": "#00AAFF"},
    {"id": "4x4doblesfix", "titulo": "4x4 DOBLES FIX", "desc": "4x4 con fix", "emoji": "🔧", "color": "#FF00FF"},
    {"id": "pocitos30", "titulo": "POCITOS 30 - MITADES", "desc": "30 pozos con mitades M1/M2", "emoji": "💎", "color": "#FFFF00", "badge": "NUEVO"},
]

st.markdown(banner_top("CATALOGO DE GENERADORES - BINGO"), unsafe_allow_html=True)
st.markdown(banner_facebook(), unsafe_allow_html=True)
copiar_clabe_component()

st.markdown(f"### {len(GENERADORES)} generadores disponibles")
cols = st.columns(3)
for i, gen in enumerate(GENERADORES):
    col = cols[i % 3]
    with col:
        visitas = get_contador(f"visita_{gen['id']}")
        usos = get_contador(gen['id'])
        badge = f"<span style='background:red;color:white;padding:2px 6px;border-radius:4px;font-size:10px'>{gen.get('badge','')}</span>" if gen.get("badge") else ""
        st.markdown(f"""
        <div style="border:2px solid {gen['color']}; border-radius:12px; padding:16px; margin-bottom:12px; background:#111">
            <div style="font-size:24px">{gen['emoji']} {badge}</div>
            <div style="font-weight:bold; color:white; margin:8px 0">{gen['titulo']}</div>
            <div style="color:#aaa; font-size:12px">{gen['desc']}</div>
            <div style="color:#666; font-size:10px; margin-top:8px">👀 {visitas} | 🎰 {usos}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Entrar {gen['id']}", key=f"btn_{gen['id']}", use_container_width=True):
            ir_a(gen['id'])
