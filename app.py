import os, random, io, zipfile, threading, datetime, gc, glob, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title="Loteria Eliud PRO", layout="wide", page_icon="🎰")

@st.cache_resource
def get_lock(): return threading.Lock()
lock = get_lock()

def get_base_path():
    p = Path("/data")
    try:
        if p.exists() and os.access(p, os.W_OK): return p
    except: pass
    return Path(".")
BASE_PATH = get_base_path()
BASE_PATH.mkdir(exist_ok=True)
CONTADOR_VISITAS = BASE_PATH / "visitas.txt"

def safe_int(s, default=0):
    try: return int(str(s).strip() or default)
    except: return default

if "visitado" not in st.session_state:
    st.session_state["visitado"]=True
    try:
        with lock:
            total = safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
            total+=1
            CONTADOR_VISITAS.write_text(str(total))
    except: total=1
else:
    try: total=safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
    except: total=1
visitas_total=total

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

def get_ranking_barajas(top=10):
    ranking=[]
    generadores = ["12portada","10portada","4x4","5x5","10dobles","4x4doblesfix","visita_12portada","visita_10portada"]
    for f in BASE_PATH.glob("contador_baraja_*.txt"):
        name=f.name
        if any(name.endswith(f"_{g}.txt") for g in generadores):
            continue
        try:
            val=safe_int(f.read_text())
            if val==0: continue
            baraja_name=name.replace("contador_baraja_","").replace(".txt","")
            ranking.append((baraja_name,val))
        except: pass
    ranking=sorted(ranking, key=lambda x: x[1], reverse=True)[:top]
    return ranking

def mostrar_ranking_html():
    rank=get_ranking_barajas(10)
    if not rank:
        return '<div style="background:#111;color:#888;border:1px solid #333;padding:12px;border-radius:10px;text-align:center">Aún no hay barajas usadas - ¡Sé el primero! 🎰</div>'
    html='<div style="background:#111;color:gold;border:2px solid gold;padding:14px;border-radius:12px;margin:14px 0"><h3 style="margin:0 0 10px 0;text-align:center">🏆 TOP 10 BARAJAS MAS USADAS</h3>'
    medallas=["🥇","🥈","🥉"]
    for i,(nom,usos) in enumerate(rank,1):
        medal=medallas[i-1] if i<=3 else f"{i}."
        html+=f'<div style="padding:8px;border-bottom:1px solid #333;display:flex;justify-content:space-between"><span>{medal} <b>{nom}</b></span><span style="background:gold;color:black;padding:2px 10px;border-radius:12px;font-weight:bold">🎰 {usos}</span></div>'
    html+='</div>'
    return html

def registrar_entrada_generador(nombre):
    key = f"entrada_registrada_{nombre}"
    if key not in st.session_state:
        inc_contador(f"visita_{nombre}")
        st.session_state[key] = True

if "vista" not in st.session_state: st.session_state["vista"]="catalogo"
if "uso_global_4x4" not in st.session_state: st.session_state["uso_global_4x4"]={}
if "uso_global_5x5" not in st.session_state: st.session_state["uso_global_5x5"]={}
if "uso_global_10" not in st.session_state: st.session_state["uso_global_10"]={}
if "uso_como_dup_10" not in st.session_state: st.session_state["uso_como_dup_10"]={}
if "hash_10" not in st.session_state: st.session_state["hash_10"]=set()

params=st.query_params
if "vista" in params and params["vista"] in ["catalogo","4x4","5x5","12portada","10portada","10dobles","4x4doblesfix"]:
    st.session_state["vista"]=params["vista"]

def ir_a(v): st.session_state["vista"]=v; st.query_params["vista"]=v; st.rerun()

EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}

def copiar_clabe_component():
    components.html("""<div style="text-align:center; margin-top:10px"><input id="clabe" value="728969000164073671" style="position:absolute; left:-9999px;"><button onclick="navigator.clipboard.writeText(document.getElementById('clabe').value); document.getElementById('msg').innerHTML='✅ ¡Copiada!';" style="background:gold; color:black; border:none; padding:12px 22px; border-radius:25px; font-weight:bold; cursor:pointer; font-size:17px;">📋 COPIAR CLABE - PICA AQUÍ</button><div id="msg" style="color:green; font-weight:bold; margin-top:8px;"></div></div>""", height=90)

def banner_top(titulo):
    return f"""<style>.banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}} .ws{{background:#25D366;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px}} .fb{{background:#1877F2;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px;margin-top:10px}} .contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px;font-size:18px}} .contador2{{background:#111;color:#ffd700;padding:8px 14px;border-radius:10px;font-weight:bold;display:inline-block;margin-top:8px;font-size:14px;border:1px solid gold}} .apoyo{{background:linear-gradient(180deg,#fffbe6,#ffe27a);border:3px solid #ffb700;padding:18px;border-radius:14px;margin-top:16px;color:#222;text-align:center;line-height:1.7}}</style><div class="banner"><h1>🎰 {titulo} 🎰</h1><h3>Creado por: Eliud Monsivais - WhatsApp 8115566250</h3><a class="ws" href="https://wa.me/528115566250">📲 WHATSAPP 8115566250</a><br><a class="fb" href="https://www.facebook.com/groups/1646464953556819" target="_blank">🔵 UNIRME AL GRUPO DE FACEBOOK</a><br><span class="contador">👁️ Visitas: {visitas_total}</span><br><span class="contador2">📊 USOS | 4x4: 👀{get_contador('visita_4x4')}/🎰{get_contador('4x4')} | 5x5: 👀{get_contador('visita_5x5')}/🎰{get_contador('5x5')} | 10C: 👀{get_contador('visita_10dobles')}/🎰{get_contador('10dobles')} | 12P: 👀{get_contador('visita_12portada')}/🎰{get_contador('12portada')} | 10P-DC: 👀{get_contador('visita_10portada')}/🎰{get_contador('10portada')} | 4x4DOB FIX: 👀{get_contador('visita_4x4doblesfix')}/🎰{get_contador('4x4doblesfix')}</span><div class="apoyo">💖 <b style="font-size:20px">¿TE GUSTÓ MI TRABAJO? ¡APÓYAME VOLUNTARIAMENTE!</b> 💖<br>Esta página es <b>100% GRATIS</b>, pero a mí me cuesta <b>pagar el servidor cada mes</b>.<br>Si te sirvió y quieres apoyarme con <b>$5, $10, $20, $50, $100 pesitos</b>, te lo agradezco muchísimo 🙏<br><b>BANCO: SPIN by OXXO</b><br><span style="font-size:22px; background:black; color:gold; padding:8px 14px; border-radius:8px;">CLABE: 728969000164073671</span><br>A nombre de: <b>Eliud Monsivais</b><br></div></div><br>"""

def banner_facebook(): return """<div style="background:#e7f3ff; border:3px solid #1877F2; border-radius:14px; padding:18px; text-align:center; margin-bottom:15px"><h3 style="color:#1877F2; margin:0">🔵 ¡ÚNETE A MI GRUPO DE FACEBOOK!</h3><p style="color:black; font-size:17px;">Aquí subo <b>barajas nuevas GRATIS</b> y te ayudo con dudas.</p><a href="https://www.facebook.com/groups/1646464953556819" target="_blank" style="background:#1877F2; color:white; padding:14px 32px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; font-size:19px">👉 ENTRAR AL GRUPO</a></div>"""

def banner_venta_offline(): return """<div style="background:linear-gradient(90deg,#000,#4b0000); border:3px solid gold; border-radius:16px; padding:20px; text-align:center; color:white; margin:20px 0"><h2 style="color:gold; margin:0">💻 ¿QUIERES USARLO SIN INTERNET Y SIN LÍMITES?</h2><p style="font-size:18px; line-height:1.6; margin:12px 0">Si te interesa alguno de los generadores para usarlo desde la <b>comodidad de tu casa, sin necesidad de internet</b>,<br> sin límite de juegos y sin límite de PDFs, con todas tus barajas guardadas...<br><br><b style="color:#25D366; font-size:20px">¡CONTÁCTANOS POR WHATSAPP O POR EL GRUPO DE FACEBOOK QUE ESTÁ ARRIBA!</b></p><a href="https://wa.me/528115566250" style="background:#25D366; color:white; padding:14px 32px; border-radius:30px; text-decoration:none; font-weight:bold; font-size:20px; display:inline-block">📲 PEDIR INFORMES DE VERSIÓN SIN LÍMITES</a></div>"""

def instrucciones_html(vista="general"):
    if vista=="catalogo": return """<div style="background:#fffbe6;border:3px dashed #ffaa00;padding:20px;border-radius:14px;color:black; font-size:18px"><h2 style="text-align:center">📋 CÓMO USAR</h2><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid gold;"><b>1) 12 CON PORTADA:</b> Tabloide 12 cartas + portada.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid #cc0000; margin-top:8px"><b>2) 10 CON PORTADA DOBLES POZO H:</b> 10 cartas + portada, dobles en pozo horizontal 5 y 6, panel ancho carta.</div></div><br>"""
    else: return f"""<div style="background:#fffbe6;border:2px solid #ffaa00;padding:18px;border-radius:14px;color:black; font-size:17px"><h3>💡 PARA QUÉ ES CADA COSA - {vista}</h3><b>📁 Baraja:</b> Elige tus dibujos.<br><b>🎨 Div:</b> Grosor línea blanca DENTRO de la carta.<br><b>↔️ Sep:</b> Espacio ENTRE las cartas.<br><b>🎨 Color:</b> Fondo hoja.<br><br><b>👁️ Primero VISTA PREVIA, luego GENERAR y DESCARGAR</b></div><br>"""

def listar_barajas():
    if not os.path.exists("barajas"): return []
    return sorted([os.path.join("barajas",d) for d in os.listdir("barajas") if os.path.isdir(os.path.join("barajas",d))])

# --- CATALOGO ---
if st.session_state.vista=="catalogo":
    st.markdown(banner_top("LOTERIA ELIUD PRO - CATALOGO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.markdown(instrucciones_html("catalogo"), unsafe_allow_html=True)
    
    # AQUI ESTA EL RANKING NUEVO AMORSH
    st.markdown(mostrar_ranking_html(), unsafe_allow_html=True)
    
    st.markdown("### 🎰 ELIGE TU GENERADOR")
    miniaturas = {
        "12portada": "miniaturas/miniatura-1-portada-12-cartas-sd.jpg",
        "10portada": "miniaturas/miniatura-1-portada-10-cartas-dc.jpg",
    }
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### 📌 12 CARTAS + PORTADA (SD)")
        thumb = miniaturas["12portada"]
        if os.path.exists(thumb):
            st.image(thumb, caption="Tabloide 12 + Portada", use_container_width=True)
        else:
            st.warning(f"Falta {thumb}")
        if st.button("🎰 ENTRAR A 12 + PORTADA", use_container_width=True, type="primary", key="btn12"):
            ir_a("12portada")
        st.caption(f"👀{get_contador('visita_12portada')} | 🎰{get_contador('12portada')}")

    with c2:
        st.markdown("#### 📌 10 CARTAS DOBLES POZO H (DC)")
        thumb2 = miniaturas["10portada"]
        if os.path.exists(thumb2):
            st.image(thumb2, caption="10 + Portada Dobles Pozo", use_container_width=True)
        else:
            st.warning(f"Falta {thumb2}")
        if st.button("🎰 ENTRAR A 10 DOBLES POZO H", use_container_width=True, type="primary", key="btn10p"):
            ir_a("10portada")
        st.caption(f"👀{get_contador('visita_10portada')} | 🎰{get_contador('10portada')} - NUEVO desde 0")

    st.markdown("---")
    st.info("Más generadores próximamente...")
    st.stop()

# --- ROUTER ---
if st.session_state.vista=="12portada":
    try:
        import generators.gen_1_portada_12_cartas as gen12
        gen12.render()
    except Exception as e:
        st.error(f"Error cargando generators/gen_1_portada_12_cartas.py: {e}")
        import traceback; st.code(traceback.format_exc())
        if st.button("⬅️ Volver"): ir_a("catalogo")
    st.stop()

if st.session_state.vista=="10portada":
    try:
        import generators.gen_1_portada_10_cartas_dc as gen10
        gen10.render()
    except Exception as e:
        st.error(f"Error cargando generators/gen_1_portada_10_cartas_dc.py: {e}")
        st.info("Asegúrate que el archivo se llame exactamente gen_1_portada_10_cartas_dc.py en generators/ y que tenga def render()")
        import traceback; st.code(traceback.format_exc())
        if st.button("⬅️ Volver al Catalogo", key="vol10"): ir_a("catalogo")
    st.stop()

if st.session_state.vista in ["4x4","5x5","10dobles","4x4doblesfix"]:
    st.markdown(banner_top(f"GENERADOR {st.session_state.vista.upper()}"), unsafe_allow_html=True)
    st.warning("Este generador aún no está migrado. Está en construcción.")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.stop()
