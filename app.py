import os, random, io, zipfile, threading, datetime, gc, glob, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title="Loteria Eliud PRO", layout="wide", page_icon="🎰")
@st.cache_resource
def get_lock():
    return threading.Lock()
lock = get_lock()
def get_base_path():
    p = Path("/data")
    try:
        if p.exists() and os.access(p, os.W_OK):
            return p
    except:
        pass
    return Path(".")
BASE_PATH = get_base_path()
BASE_PATH.mkdir(exist_ok=True)
CONTADOR_VISITAS = BASE_PATH / "visitas.txt"
def safe_int(s, default=0):
    try:
        return int(str(s).strip() or default)
    except:
        return default
if "visitado" not in st.session_state:
    st.session_state["visitado"]=True
    try:
        with lock:
            total = safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
            total+=1
            CONTADOR_VISITAS.write_text(str(total))
    except:
        total=1
else:
    try:
        total=safe_int(CONTADOR_VISITAS.read_text() if CONTADOR_VISITAS.exists() else 0)
    except:
        total=1
visitas_total=total
def get_contador(nombre):
    path = BASE_PATH / f"contador_{nombre}.txt"
    if not path.exists():
        return 0
    try:
        return safe_int(path.read_text())
    except:
        return 0
def inc_contador(nombre, cantidad=1):
    path = BASE_PATH / f"contador_{nombre}.txt"
    try:
        with lock:
            actual = get_contador(nombre) + cantidad
            path.write_text(str(actual))
            return actual
    except:
        return 0
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
    except:
        pass
def get_ranking_barajas():
    patron = str(BASE_PATH / "contador_baraja_*.txt")
    files = [f for f in glob.glob(patron) if not any(f.endswith(f"_{x}.txt") for x in ["4x4","5x5","10dobles","12portada","4x4doblesfix","10panel"])]
    ranking=[]
    for fp in files:
        try:
            nombre = os.path.basename(fp).replace("contador_baraja_","").replace(".txt","").replace("_"," ")
            cnt = safe_int(open(fp,"r", encoding="utf-8", errors="ignore").read())
            ranking.append((nombre,cnt))
        except:
            pass
    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking[:15]
def registrar_entrada_generador(nombre):
    key = f"entrada_registrada_{nombre}"
    if key not in st.session_state:
        inc_contador(f"visita_{nombre}")
        st.session_state[key] = True
if "vista" not in st.session_state:
    st.session_state["vista"]="catalogo"
if "uso_global_4x4" not in st.session_state:
    st.session_state["uso_global_4x4"]={}
if "uso_global_5x5" not in st.session_state:
    st.session_state["uso_global_5x5"]={}
if "uso_global_10" not in st.session_state:
    st.session_state["uso_global_10"]={}
if "uso_como_dup_10" not in st.session_state:
    st.session_state["uso_como_dup_10"]={}
if "hash_10" not in st.session_state:
    st.session_state["hash_10"]=set()
if "uso_global_10panel" not in st.session_state:
    st.session_state["uso_global_10panel"]={}
if "uso_como_dup_10panel" not in st.session_state:
    st.session_state["uso_como_dup_10panel"]={}
if "hash_10panel" not in st.session_state:
    st.session_state["hash_10panel"]=set()
params=st.query_params
if "vista" in params and params["vista"] in ["catalogo","4x4","5x5","12portada","10dobles","4x4doblesfix","10panel"]:
    st.session_state["vista"]=params["vista"]
def ir_a(v):
    st.session_state["vista"]=v; st.query_params["vista"]=v; st.rerun()
EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}
def copiar_clabe_component():
    components.html("""<div style="text-align:center; margin-top:10px"><input id="clabe" value="728969000164073671" style="position:absolute; left:-9999px;"><button onclick="navigator.clipboard.writeText(document.getElementById('clabe').value); document.getElementById('msg').innerHTML='✅ ¡Copiada!';" style="background:gold; color:black; border:none; padding:12px 22px; border-radius:25px; font-weight:bold; cursor:pointer; font-size:17px;">📋 COPIAR CLABE - PICA AQUÍ</button><div id="msg" style="color:green; font-weight:bold; margin-top:8px;"></div></div>""", height=90)
def banner_top(titulo):
    return f"""<style>.banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}} .ws{{background:#25D366;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px}} .fb{{background:#1877F2;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px;margin-top:10px}} .contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px;font-size:18px}} .contador2{{background:#111;color:#ffd700;padding:8px 14px;border-radius:10px;font-weight:bold;display:inline-block;margin-top:8px;font-size:14px;border:1px solid gold}} .apoyo{{background:linear-gradient(180deg,#fffbe6,#ffe27a);border:3px solid #ffb700;padding:18px;border-radius:14px;margin-top:16px;color:#222;text-align:center;line-height:1.7}}</style><div class="banner"><h1>🎰 {titulo} 🎰</h1><h3>Creado por: Eliud Monsivais - WhatsApp 8115566250</h3><a class="ws" href="https://wa.me/528115566250">📲 WHATSAPP 8115566250</a><br><a class="fb" href="https://www.facebook.com/groups/1646464953556819" target="_blank">🔵 UNIRME AL GRUPO DE FACEBOOK</a><br><span class="contador">👁️ Visitas: {visitas_total}</span><br><span class="contador2">📊 USOS | 4x4: 👀{get_contador('visita_4x4')}/🎰{get_contador('4x4')} | 5x5: 👀{get_contador('visita_5x5')}/🎰{get_contador('5x5')} | 10C: 👀{get_contador('visita_10dobles')}/🎰{get_contador('10dobles')} | 12: 👀{get_contador('visita_12portada')}/🎰{get_contador('12portada')} | 4x4DOB FIX: 👀{get_contador('visita_4x4doblesfix')}/🎰{get_contador('4x4doblesfix')} | 10PANEL: 👀{get_contador('visita_10panel')}/🎰{get_contador('10panel')}</span><div class="apoyo">💖 <b style="font-size:20px">¿TE GUSTÓ MI TRABAJO? ¡APÓYAME VOLUNTARIAMENTE!</b> 💖<br>Esta página es <b>100% GRATIS</b>, pero a mí me cuesta <b>pagar el servidor cada mes</b>.<br>Si te sirvió y quieres apoyarme con <b>$5, $10, $20, $50, $100 pesitos</b>, te lo agradezco muchísimo 🙏<br><b>BANCO: SPIN by OXXO</b><br><span style="font-size:22px; background:black; color:gold; padding:8px 14px; border-radius:8px;">CLABE: 728969000164073671</span><br>A nombre de: <b>Eliud Monsivais</b><br></div></div><br>"""
def banner_facebook():
    return """<div style="background:#e7f3ff; border:3px solid #1877F2; border-radius:14px; padding:18px; text-align:center; margin-bottom:15px"><h3 style="color:#1877F2; margin:0">🔵 ¡ÚNETE A MI GRUPO DE FACEBOOK!</h3><p style="color:black; font-size:17px;">Aquí subo <b>barajas nuevas GRATIS</b> y te ayudo con dudas.</p><a href="https://www.facebook.com/groups/1646464953556819" target="_blank" style="background:#1877F2; color:white; padding:14px 32px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; font-size:19px">👉 ENTRAR AL GRUPO</a></div>"""
def banner_venta_offline():
    return """<div style="background:linear-gradient(90deg,#000,#4b0000); border:3px solid gold; border-radius:16px; padding:20px; text-align:center; color:white; margin:20px 0"><h2 style="color:gold; margin:0">💻 ¿QUIERES USARLO SIN INTERNET Y SIN LÍMITES?</h2><p style="font-size:18px; line-height:1.6; margin:12px 0">Si te interesa alguno de los generadores para usarlo desde la <b>comodidad de tu casa, sin necesidad de internet</b>,<br> sin límite de juegos y sin límite de PDFs, con todas tus barajas guardadas...<br><br><b style="color:#25D366; font-size:20px">¡CONTÁCTANOS POR WHATSAPP O POR EL GRUPO DE FACEBOOK QUE ESTÁ ARRIBA!</b></p><a href="https://wa.me/528115566250" style="background:#25D366; color:white; padding:14px 32px; border-radius:30px; text-decoration:none; font-weight:bold; font-size:20px; display:inline-block">📲 PEDIR INFORMES DE VERSIÓN SIN LÍMITES</a></div>"""
def instrucciones_html(vista="general"):
    if vista=="catalogo":
        return """<div style="background:#fffbe6;border:3px dashed #ffaa00;padding:20px;border-radius:14px;color:black; font-size:18px"><h2 style="text-align:center">📋 CÓMO USAR</h2><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid green; margin-bottom:10px"><b>1) 4x4 - 16 figuras:</b> 4 cartas por hoja.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid blue; margin-bottom:10px"><b>2) 5x5 - 25 figuras:</b> 4 cartas por hoja.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid gold;"><b>3) 10 Cartas 4x4 con Dobles - 54 por Hoja (3x -2):</b> 10 cartas por hoja, layout 5x2 / 2x5, ciclos 6 hojas.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid #cc0000;"><b>4) 12 CON PORTADA:</b> Tabloide 12 cartas + portada.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid purple;"><b>5) 4x4 DOBLES AL CENTRO FIX - 54 DOBLES:</b> 4 cartas por hoja, dobles en pos 6 y 7, 14 hojas = ciclo completo, sin huecos rosas, marco parejo 4 lados, con PDF.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid #FF00FF;"><b>6) 🆕 10C PANEL 600 SIN ESTIRAR:</b> 10 cartas por hoja tipo PANEL ancho carta, carta de 600px sin estirar, ideal para imprimir en hoja carta / tabloide.</div></div><br>"""
    else:
        return f"""<div style="background:#fffbe6;border:2px solid #ffaa00;padding:18px;border-radius:14px;color:black; font-size:17px"><h3>💡 PARA QUÉ ES CADA COSA - {vista}</h3><b>📁 Baraja:</b> Elige tus dibujos.<br><b>🎨 Div:</b> Grosor línea blanca DENTRO de la carta.<br><b>↔️ Sep V / Sep H:</b> Espacio ENTRE las cartas.<br><b>⬛ Marco:</b> Borde negro.<br><b>🎨 Color:</b> Fondo hoja.<br><br><b>👁️ Primero VISTA PREVIA, luego GENERAR y DESCARGAR</b></div><br>"""
def listar_barajas():
    if not os.path.exists("barajas"):
        return []
    return sorted([os.path.join("barajas",d) for d in os.listdir("barajas") if os.path.isdir(os.path.join("barajas",d)) and d.lower().startswith("baraja")])
def cargar_files(path, limite=54):
    exts=(".png",".jpg",".jpeg",".webp",".jfif")
    if not path or not os.path.exists(path):
        return []
    files=[os.path.join(path,f) for f in os.listdir(path) if f.lower().endswith(exts)]
    files.sort()
    return files[:limite]
def cargar_zip_temporal(uploaded_zip, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp):
            try:
                os.remove(os.path.join(carpeta_tmp,f))
            except:
                pass
        with zipfile.ZipFile(uploaded_zip) as zz:
            for name in zz.namelist():
                if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                    open(os.path.join(carpeta_tmp, os.path.basename(name)),"wb").write(zz.read(name))
        return cargar_files(carpeta_tmp, limite)
    except:
        return []
def cargar_imagenes_sueltas(uploaded_files, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp):
            try:
                os.remove(os.path.join(carpeta_tmp,f))
            except:
                pass
        for uf in uploaded_files[:limite]:
            open(os.path.join(carpeta_tmp, uf.name),"wb").write(uf.getbuffer())
        return cargar_files(carpeta_tmp, limite)
    except:
        return []
def cm_to_px(cm,dpi):
    try:
        return int(float(cm)/2.54*int(dpi))
    except:
        return 800
def get_aspecto(files):
    asp=[]
    for p in files[:10]:
        try:
            with Image.open(p) as im:
                asp.append(im.size[1]/im.size[0])
        except:
            pass
    return sum(asp)/len(asp) if asp else 1.42
def no_chocan(a,b,la,lb):
    for i,j in zip(la,lb):
        if a[i] is None or b[j] is None:
            continue
        if a[i]==b[j]:
            return False
    return True
RIGHT4=[3,7,11,15]; LEFT4=[0,4,8,12]; TOP4=[0,1,2,3]; BOTTOM4=[12,13,14,15]
RIGHT5=[4,9,14,19,24]; LEFT5=[0,5,10,15,20]; TOP5=[0,1,2,3,4]; BOTTOM5=[20,21,22,23,24]
def crear_carta_4x4(data16, cw_card, ch_card, div, g, asp):
    carta=Image.new("RGB",(cw_card,ch_card),"black")
    fw=cw_card-g*2; fh=ch_card-g*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-div*3)//4; ch=int(cw*asp); th=ch*4+div*3; y0=(fh-th)//2
    for i in range(min(16,len(data16))):
        r=i//4; c=i%4; x=c*(cw+div); y=y0+r*(ch+div)
        try:
            with Image.open(data16[i]) as im:
                base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x,y))
        except:
            pass
    carta.paste(base,(g,g)); return carta
def generar_logica_4x4(baraja):
    uso=st.session_state["uso_global_4x4"]
    if not uso:
        uso={f:0 for f in baraja}; st.session_state["uso_global_4x4"]=uso
    for _ in range(2500):
        conteo={}; cartas=[[None]*16 for _ in range(4)]; pos_fig={}; ok=True
        base54=baraja.copy(); random.shuffle(base54)
        huecos=[3,3,2,2]; random.shuffle(huecos)
        huecos_carta=[set(random.sample(range(16),h)) for h in huecos]
        idx=0
        for c in range(4):
            for pos in range(16):
                if pos in huecos_carta[c]:
                    continue
                fig=base54[idx]; cartas[c][pos]=fig; pos_fig[fig]=pos_fig.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda=baraja.copy(); random.shuffle(segunda); segunda.sort(key=lambda x:(uso.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas[c] if f])
            for pos in huecos_carta[c]:
                cand=[f for f in segunda if f not in usados and conteo.get(f,0)<2 and pos not in pos_fig.get(f,set())]
                if not cand:
                    cand=[f for f in baraja if f not in usados and conteo.get(f,0)<2]
                if not cand:
                    ok=False; break
                eleg=cand[0]; cartas[c][pos]=eleg; pos_fig[eleg]=pos_fig.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok:
                break
        if not ok:
            continue
        if not no_chocan(cartas[0],cartas[1],RIGHT4,LEFT4): continue
        if not no_chocan(cartas[0],cartas[2],BOTTOM4,TOP4): continue
        if not no_chocan(cartas[1],cartas[3],BOTTOM4,TOP4): continue
        if not no_chocan(cartas[2],cartas[3],RIGHT4,LEFT4): continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items():
            uso[f]=uso.get(f,0)+cnt
        st.session_state["uso_global_4x4"]=uso; return cartas
    return None
def generar_hoja_4x4(cartas_data, color, div, sep_v, sep_h, g, asp, final_size=None, W_orig=1800):
    cw_tmp=((W_orig-sep_v)//2 - g*2 - 3*div)//4; ch_tmp=int(cw_tmp*asp); card_h=ch_tmp*4+div*3+g*2
    H_orig=card_h*2+sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color)
    for idx,d16 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_4x4(d16,cw,ch,div,g,asp),(x,y))
    if final_size:
        sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet
def crear_carta_5x5(data25, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*4)//5; ch=int(cw*aspecto); th=ch*5+DIV*4; y0=(fh-th)//2
    for idx in range(min(25,len(data25))):
        r=idx//5; c=idx%5; x0=c*(cw+DIV); y0f=y0 + r*(ch+DIV)
        try:
            with Image.open(data25[idx]) as im:
                base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x0,y0f))
        except:
            pass
    carta.paste(base,(G,G)); return carta
def generar_logica_5x5(baraja_files):
    uso=st.session_state["uso_global_5x5"]
    if not uso:
        uso={f:0 for f in baraja_files}; st.session_state["uso_global_5x5"]=uso
    for _ in range(2500):
        conteo={}; cartas_data=[[None]*25 for _ in range(4)]; pos_por_figura={}; ok=True
        base54=baraja_files.copy(); random.shuffle(base54)
        huecos=[11,11,12,12]; random.shuffle(huecos)
        huecos_por_carta=[set(random.sample(range(25), huecos[c])) for c in range(4)]
        idx=0
        for c in range(4):
            for pos in range(25):
                if pos in huecos_por_carta[c]:
                    continue
                fig=base54[idx]; cartas_data[c][pos]=fig; pos_por_figura[fig]=pos_por_figura.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda_lista=baraja_files.copy(); random.shuffle(segunda_lista); segunda_lista.sort(key=lambda x:(uso.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas_data[c] if f is not None])
            for pos in huecos_por_carta[c]:
                base=[f for f in segunda_lista if f not in usados and conteo.get(f,0)<2 and pos not in pos_por_figura.get(f,set())]
                if not base:
                    base=[f for f in baraja_files if f not in usados and conteo.get(f,0)<2]
                if not base:
                    ok=False; break
                eleg=base[0]; cartas_data[c][pos]=eleg; pos_por_figura[eleg]=pos_por_figura.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok:
                break
        if not ok:
            continue
        if not no_chocan(cartas_data[0], cartas_data[1], RIGHT5, LEFT5): continue
        if not no_chocan(cartas_data[0], cartas_data[2], BOTTOM5, TOP5): continue
        if not no_chocan(cartas_data[1], cartas_data[3], BOTTOM5, TOP5): continue
        if not no_chocan(cartas_data[2], cartas_data[3], RIGHT5, LEFT5): continue
        if len(pos_por_figura) < 54: continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items():
            uso[f]=uso.get(f,0)+cnt
        st.session_state["uso_global_5x5"]=uso; return cartas_data
    return None
def generar_hoja_5x5(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, final_size=None, W_orig=2000):
    cw_tmp=((W_orig-sep_v)//2 - g_negro*2 - 4*div_interno)//5; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*5 + div_interno*4 + g_negro*2
    H_orig=card_h_real*2 + sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d25 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_5x5(d25, cw, ch, div_interno, g_negro, aspecto),(x,y))
    if final_size:
        sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet
def poner_puntito_10(celda):
    w,h = celda.size; d = ImageDraw.Draw(celda); d.ellipse((w//2-2, h-8, w//2+2, h-4), fill="black"); return celda
def crear_carta_ajustada_10(data16, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*3)//4; ch=int(cw*aspecto); total_h_grid=ch*4+DIV*3; y_offset=(fh-total_h_grid)//2
    for idx in range(min(16,len(data16))):
        r=idx//4; c=idx%4; x0=c*(cw+DIV); y0=y_offset + r*(ch+DIV)
        celda=Image.new("RGB",(cw,ch),"black")
        try:
            with Image.open(data16[idx]) as im:
                im2=im.convert("RGB").resize((cw,ch), Image.LANCZOS); celda.paste(im2,(0,0))
        except:
            pass
        celda=poner_puntito_10(celda); base.paste(celda,(x0,y0))
    carta.paste(base,(G,G)); return carta
def generar_logica_10_cartas_54(baraja_files, es_nuevo_juego=False):
    uso_global = st.session_state["uso_global_10"]; uso_como_dup = st.session_state["uso_como_dup_10"]; cartas_hash = st.session_state["hash_10"]
    if es_nuevo_juego or not uso_global:
        uso_global={f:0 for f in baraja_files}; uso_como_dup={f:0 for f in baraja_files}; cartas_hash=set()
    RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; BOTTOM=[12,13,14,15]; TOP=[0,1,2,3]
    for _ in range(2500):
        orden_dups=sorted(baraja_files, key=lambda x: (uso_como_dup.get(x,0), random.random()))
        dups_10=orden_dups[:10]; random.shuffle(dups_10); dups_set=set(dups_10)
        lista_44=[f for f in baraja_files if f not in dups_set]; random.shuffle(lista_44)
        conteo={f:2 for f in dups_10}; cartas_data=[[None]*16 for _ in range(10)]; PROHIBIDAS={9,10}
        for idx in range(10):
            cartas_data[idx][5]=dups_10[idx]; cartas_data[idx][6]=dups_10[idx]
        ok=True
        for i,d in enumerate(dups_10):
            posibles=[c for c in range(10) if c!=i]; random.shuffle(posibles); colocado=False
            for dest in posibles:
                if d in cartas_data[dest]:
                    continue
                libres=[p for p in range(16) if cartas_data[dest][p] is None and p not in PROHIBIDAS]; random.shuffle(libres)
                for p in libres:
                    cartas_data[dest][p]=d
                    if dest>0 and dest%5!=0 and not no_chocan(cartas_data[dest-1], cartas_data[dest], RIGHT, LEFT):
                        cartas_data[dest][p]=None; continue
                    if dest>=5 and not no_chocan(cartas_data[dest-5], cartas_data[dest], BOTTOM, TOP):
                        cartas_data[dest][p]=None; continue
                    conteo[d]+=1; colocado=True; break
                if colocado:
                    break
            if not colocado:
                ok=False; break
        if not ok:
            continue
        for cidx in range(10):
            usados=set([x for x in cartas_data[cidx] if x])
            for pos in range(16):
                if cartas_data[cidx][pos] is not None:
                    continue
                base44=[f for f in lista_44 if f not in usados and conteo.get(f,0)<4]
                if not base44:
                    base44=[f for f in baraja_files if f not in usados and f not in dups_set and conteo.get(f,0)<4]
                base44=sorted(base44, key=lambda x:(conteo.get(x,0), uso_global.get(x,0), random.random())); colocado=False
                for pick in base44[:15]:
                    cartas_data[cidx][pos]=pick
                    if cidx>0 and cidx%5!=0 and not no_chocan(cartas_data[cidx-1], cartas_data[cidx], RIGHT, LEFT):
                        cartas_data[cidx][pos]=None; continue
                    if cidx>=5 and not no_chocan(cartas_data[cidx-5], cartas_data[cidx], BOTTOM, TOP):
                        cartas_data[cidx][pos]=None; continue
                    ch=tuple(sorted([x for x in cartas_data[cidx] if x]))
                    if len(ch)==16 and ch in cartas_hash:
                        cartas_data[cidx][pos]=None; continue
                    usados.add(pick); conteo[pick]=conteo.get(pick,0)+1; colocado=True; break
                if not colocado:
                    ok=False; break
            if not ok:
                break
        if not ok:
            continue
        temp_hash=set()
        for cd in cartas_data:
            hh=tuple(sorted(cd))
            if hh in cartas_hash or hh in temp_hash:
                ok=False; break
            temp_hash.add(hh)
        if not ok:
            continue
        todas=set()
        for cd in cartas_data:
            todas.update([x for x in cd if x])
        if len(todas)<54:
            continue
        for hh in temp_hash:
            cartas_hash.add(hh)
        for f,c in conteo.items():
            uso_global[f]=uso_global.get(f,0)+c
        for f in dups_10:
            uso_como_dup[f]=uso_como_dup.get(f,0)+1
        st.session_state["uso_global_10"]=uso_global; st.session_state["uso_como_dup_10"]=uso_como_dup; st.session_state["hash_10"]=cartas_hash
        return cartas_data, dups_10
    return None, None
def generar_original_fijo_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="5x2"):
    cols,rows=(5,2) if layout=="5x2" else (2,5)
    W_base=7500 if layout=="5x2" else 3200; card_w_real=W_base//cols
    cw_tmp=(card_w_real - g_negro*2 - 3*div_interno)//4; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*4 + div_interno*3 + g_negro*2
    W_orig=card_w_real*cols + sep_v*(cols-1); H_orig=card_h_real*rows + sep_h*(rows-1)
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols; x=col*(card_w_real+sep_v); y=row*(card_h_real+sep_h)
        sheet.paste(crear_carta_ajustada_10(d16, card_w_real, card_h_real, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="5x2"):
    orig=generar_original_fijo_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
# ============ 10C PANEL 600 SIN ESTIRAR ============
CARTA_PANEL_W = 600
def crear_carta_panel_600(data16, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    cw_cell = (CARTA_PANEL_W - G*2 - DIV*3)//4
    ch_cell = int(cw_cell * aspecto)
    card_h = ch_cell*4 + DIV*3 + G*2
    carta=Image.new("RGB",(CARTA_PANEL_W, card_h),"black")
    fw=CARTA_PANEL_W-G*2
    base=Image.new("RGB",(fw, card_h-G*2),"black")
    for idx in range(min(16,len(data16))):
        r=idx//4; c=idx%4; x0=c*(cw_cell+DIV); y0=r*(ch_cell+DIV)
        celda=Image.new("RGB",(cw_cell,ch_cell),"black")
        try:
            with Image.open(data16[idx]) as im:
                im2=im.convert("RGB").resize((cw_cell,ch_cell), Image.LANCZOS)
                celda.paste(im2,(0,0))
        except:
            pass
        base.paste(celda,(x0,y0))
    carta.paste(base,(G,G))
    return carta
def generar_logica_10panel_54(baraja_files, es_nuevo_juego=False):
    uso_global = st.session_state["uso_global_10panel"]
    uso_como_dup = st.session_state["uso_como_dup_10panel"]
    cartas_hash = st.session_state["hash_10panel"]
    if es_nuevo_juego or not uso_global:
        uso_global={f:0 for f in baraja_files}
        uso_como_dup={f:0 for f in baraja_files}
        cartas_hash=set()
    RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; BOTTOM=[12,13,14,15]; TOP=[0,1,2,3]
    for _ in range(2500):
        orden_dups=sorted(baraja_files, key=lambda x: (uso_como_dup.get(x,0), random.random()))
        dups_10=orden_dups[:10]; random.shuffle(dups_10); dups_set=set(dups_10)
        lista_44=[f for f in baraja_files if f not in dups_set]; random.shuffle(lista_44)
        conteo={f:2 for f in dups_10}; cartas_data=[[None]*16 for _ in range(10)]
        for idx in range(10):
            cartas_data[idx][5]=dups_10[idx]; cartas_data[idx][6]=dups_10[idx]
        ok=True
        for i,d in enumerate(dups_10):
            posibles=[c for c in range(10) if c!=i]; random.shuffle(posibles); colocado=False
            for dest in posibles:
                if d in cartas_data[dest]: continue
                libres=[p for p in range(16) if cartas_data[dest][p] is None]; random.shuffle(libres)
                for p in libres:
                    cartas_data[dest][p]=d
                    if dest>0 and dest%5!=0 and not no_chocan(cartas_data[dest-1], cartas_data[dest], RIGHT, LEFT):
                        cartas_data[dest][p]=None; continue
                    if dest>=5 and not no_chocan(cartas_data[dest-5], cartas_data[dest], BOTTOM, TOP):
                        cartas_data[dest][p]=None; continue
                    conteo[d]+=1; colocado=True; break
                if colocado: break
            if not colocado: ok=False; break
        if not ok: continue
        for cidx in range(10):
            usados=set([x for x in cartas_data[cidx] if x])
            for pos in range(16):
                if cartas_data[cidx][pos] is not None: continue
                base44=[f for f in lista_44 if f not in usados and conteo.get(f,0)<4]
                if not base44: base44=[f for f in baraja_files if f not in usados and f not in dups_set and conteo.get(f,0)<4]
                base44=sorted(base44, key=lambda x:(conteo.get(x,0), uso_global.get(x,0), random.random()))
                colocado=False
                for pick in base44[:15]:
                    cartas_data[cidx][pos]=pick
                    if cidx>0 and cidx%5!=0 and not no_chocan(cartas_data[cidx-1], cartas_data[cidx], RIGHT, LEFT):
                        cartas_data[cidx][pos]=None; continue
                    if cidx>=5 and not no_chocan(cartas_data[cidx-5], cartas_data[cidx], BOTTOM, TOP):
                        cartas_data[cidx][pos]=None; continue
                    ch=tuple(sorted([x for x in cartas_data[cidx] if x]))
                    if len(ch)==16 and ch in cartas_hash:
                        cartas_data[cidx][pos]=None; continue
                    usados.add(pick); conteo[pick]=conteo.get(pick,0)+1; colocado=True; break
                if not colocado: ok=False; break
            if not ok: break
        if not ok: continue
        temp_hash=set()
        for cd in cartas_data:
            hh=tuple(sorted(cd))
            if hh in cartas_hash or hh in temp_hash: ok=False; break
            temp_hash.add(hh)
        if not ok: continue
        todas=set()
        for cd in cartas_data: todas.update([x for x in cd if x])
        if len(todas)<54: continue
        for hh in temp_hash: cartas_hash.add(hh)
        for f,c in conteo.items(): uso_global[f]=uso_global.get(f,0)+c
        for f in dups_10: uso_como_dup[f]=uso_como_dup.get(f,0)+1
        st.session_state["uso_global_10panel"]=uso_global
        st.session_state["uso_como_dup_10panel"]=uso_como_dup
        st.session_state["hash_10panel"]=cartas_hash
        return cartas_data, dups_10
    return None, None
def generar_original_fijo_10panel(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="5x2"):
    cols,rows=(5,2) if layout=="5x2" else (2,5)
    sample_card = crear_carta_panel_600(cartas_data[0], div_interno, g_negro, aspecto)
    cw_real, ch_real = sample_card.size
    W_orig=cw_real*cols + sep_v*(cols-1)
    H_orig=ch_real*rows + sep_h*(rows-1)
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols; x=col*(cw_real+sep_v); y=row*(ch_real+sep_h)
        sheet.paste(crear_carta_panel_600(d16, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_10panel(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="5x2"):
    orig=generar_original_fijo_10panel(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
CICLO_FIJO_4x4DOB = 14
def poner_puntito_4x4dob(celda):
    w,h = celda.size; d = ImageDraw.Draw(celda); d.ellipse((w//2-2, h-8, w//2+2, h-4), fill="black"); return celda
def crear_carta_ajustada_4x4dob(data16, card_w, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno; fw = card_w - G*2; cw = (fw - DIV*3)//4; ch = int(cw*aspecto); card_h = ch*4 + DIV*3 + G*2
    carta=Image.new("RGB",(card_w, card_h),"black"); base=Image.new("RGB",(fw, card_h - G*2),"black")
    for idx in range(min(16,len(data16))):
        r=idx//4; c=idx%4; x0=c*(cw+DIV); y0=r*(ch+DIV)
        celda=Image.new("RGB",(cw,ch),"black")
        try:
            with Image.open(data16[idx]) as im:
                im2=im.convert("RGB").resize((cw,ch), Image.LANCZOS); celda.paste(im2,(0,0))
        except:
            pass
        celda=poner_puntito_4x4dob(celda); base.paste(celda,(x0,y0))
    carta.paste(base,(G,G)); return carta
def generar_ciclo_54_dobles_4x4dob(baraja_files):
    todas = baraja_files.copy(); random.shuffle(todas)
    repetidas = random.sample(todas, 2); dobles_ciclo = todas + repetidas; random.shuffle(dobles_ciclo)
    hojas = []; idx_doble = 0
    for _ in range(CICLO_FIJO_4x4DOB):
        cartas_data_hoja = []
        for _ in range(4):
            dup = dobles_ciclo[idx_doble]; idx_doble+=1
            restantes = [f for f in baraja_files if f != dup]; random.shuffle(restantes)
            top = [None]*16; top[5]=dup; top[6]=dup
            pos_libres = [i for i in range(16) if i not in [5,6]]; random.shuffle(pos_libres)
            for i, pos in enumerate(pos_libres[:14]):
                top[pos]=restantes[i]
            for pos in range(16):
                if top[pos] is None:
                    top[pos]=random.choice(restantes)
            cartas_data_hoja.append(top)
        hojas.append(cartas_data_hoja)
    return hojas, dobles_ciclo, repetidas
def generar_original_fijo_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="2x2"):
    CARD_W = 1100; fw = CARD_W - g_negro*2; cw_cell = (fw - div_interno*3)//4; ch_cell = int(cw_cell * aspecto); CARD_H = ch_cell*4 + div_interno*3 + g_negro*2
    if layout=="1x4":
        W_orig = CARD_W*4 + sep_v*3; H_orig = CARD_H; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
        for idx,d16 in enumerate(cartas_data):
            x=idx*(CARD_W+sep_v); y=0; sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
    else:
        W_orig = CARD_W*2 + sep_v; H_orig = CARD_H*2 + sep_h; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
        for idx,d16 in enumerate(cartas_data):
            col=idx%2; row=idx//2; x=col*(CARD_W+sep_v); y=row*(CARD_H+sep_h); sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="2x2"):
    orig=generar_original_fijo_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
def imagenes_a_pdf_4x4dob(imagenes_pil):
    if not imagenes_pil:
        return None
    rgb_imgs = [im.convert("RGB") for im in imagenes_pil]; buf = io.BytesIO()
    rgb_imgs[0].save(buf, format="PDF", save_all=True, append_images=rgb_imgs[1:], resolution=300)
    return buf.getvalue()
def crear_carta_imagen_16(data16, card_w=1000, div_interno=8, sample_aspect=1.45):
    cell_w=card_w//4; cell_h=int(cell_w*sample_aspect); img=Image.new("RGB",(card_w, cell_h*4),"black")
    target_w=cell_w-div_interno; target_h=cell_h-div_interno
    for idx,ruta in enumerate(data16):
        try:
            with Image.open(ruta) as im0:
                im=im0.convert("RGB"); iw,ih=im.size; scale=max(target_w/iw, target_h/ih)
                nw,nh=int(iw*scale), int(ih*scale); im=im.resize((nw,nh), Image.LANCZOS)
                left=(nw-target_w)//2; top=(nh-target_h)//2; im=im.crop((left,top,left+target_w,top+target_h))
        except:
            im=Image.new("RGB",(target_w,target_h),"white")
        col=idx%4; row=idx//4; x=col*cell_w+div_interno//2; y=row*cell_h+div_interno//2; img.paste(im,(x,y))
    return img
def generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_cover_path, favorita_baraja_path, color_entre, div_interno, sep_entre):
    try:
        with Image.open(baraja_files[0]) as s:
            asp=s.size[1]/s.size[0]
    except:
        asp=1.45
    card_w=800; card_h=int(card_w*asp)
    grid_pos=[(2,0),(3,0),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(1,3),(2,3),(3,3)]
    vecinos={}
    for i,(r,c) in enumerate(grid_pos):
        lst=[]
        for j,(r2,c2) in enumerate(grid_pos):
            if i==j: continue
            if r==r2 and c==c2+1: lst.append((j,RIGHT4,LEFT4))
            if r==r2 and c==c2-1: lst.append((j,LEFT4,RIGHT4))
            if c==c2 and r==r2+1: lst.append((j,BOTTOM4,TOP4))
            if c==c2 and r==r2-1: lst.append((j,TOP4,BOTTOM4))
        vecinos[i]=lst
    otros=[f for f in baraja_files if f!=favorita_baraja_path][:53]
    for _ in range(1500):
        posiciones_fav=random.sample(range(16),12); random.shuffle(otros); pool=[]
        for f in otros[:21]: pool.extend([f]*4)
        for f in otros[21:]: pool.extend([f]*3)
        random.shuffle(pool); pool_idx=0; cartas_data=[]; ok=True
        for idx_carta in range(12):
            fav_pos=posiciones_fav[idx_carta]; carta_ok=False
            for _ in range(60):
                top=[None]*16; top[fav_pos]=favorita_baraja_path; usados=set([favorita_baraja_path]); temp_idx=pool_idx; temp_pool=pool[:]; fail=False
                for pos in range(16):
                    if top[pos] is not None: continue
                    encontrado=False
                    for k in range(temp_idx, len(temp_pool)):
                        if temp_pool[k] not in usados:
                            top[pos]=temp_pool[k]; usados.add(temp_pool[k]); temp_pool[k], temp_pool[temp_idx]=temp_pool[temp_idx], temp_pool[k]; temp_idx+=1; encontrado=True; break
                    if not encontrado: fail=True; break
                if fail: continue
                choque=False
                for j,la,lb in vecinos[idx_carta]:
                    if j < len(cartas_data):
                        if not no_chocan(cartas_data[j], top, la, lb): choque=True; break
                if choque: continue
                pool=temp_pool; pool_idx=temp_idx; cartas_data.append(top); carta_ok=True; break
            if not carta_ok: ok=False; break
        if not ok: continue
        W=4*card_w+3*sep_entre; H=4*card_h+3*sep_entre
        sheet=Image.new("RGB",(W,H), color_entre)
        try:
            with Image.open(portada_cover_path) as imc0:
                imc=imc0.convert("RGB")
                tw=2*card_w+sep_entre; th=2*card_h+sep_entre; sc=max(tw/imc.size[0], th/imc.size[1])
                imc=imc.resize((int(imc.size[0]*sc), int(imc.size[1]*sc)), Image.LANCZOS)
                imc=imc.crop(((imc.size[0]-tw)//2, (imc.size[1]-th)//2, (imc.size[0]-tw)//2+tw, (imc.size[1]-th)//2+th))
        except:
            imc=Image.new("RGB",(2*card_w+sep_entre, 2*card_h+sep_entre),"gold")
        sheet.paste(imc,(0,0))
        for idx,data16 in enumerate(cartas_data):
            r,c=grid_pos[idx]
            if r<2 and c<2: continue
            x=c*(card_w+sep_entre); y=r*(card_h+sep_entre)
            sheet.paste(crear_carta_imagen_16(data16, card_w=card_w, div_interno=div_interno, sample_aspect=asp),(x,y))
        gc.collect(); return sheet
    return None
def limpiar_nombre(path_img, idx):
    raw=os.path.splitext(os.path.basename(path_img))[0]
    clean=raw.replace("_"," ").replace("-"," ").strip().upper()
    clean=' '.join([w for w in clean.split() if not w.isdigit()]).strip()
    if not clean: clean=f"CARTA {idx}"
    return clean

# CATALOGO 6 BOTONES
if st.session_state.vista=="catalogo":
    st.markdown(banner_top("CATALOGO LOTERIA ELIUD PRO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.markdown(instrucciones_html("catalogo"), unsafe_allow_html=True)
    ranking = get_ranking_barajas()
    if ranking:
        st.markdown("### 🏆 RANKING BARAJAS MÁS USADAS")
        html_rank = "<div style='background:white;border:2px solid gold;border-radius:12px;padding:12px;color:black'>"
        for i,(nom,cnt) in enumerate(ranking,1):
            html_rank += f"<div style='padding:6px;border-bottom:1px solid #eee'><b>{i}. {nom}</b> - {cnt} usos</div>"
        html_rank += "</div><br>"
        st.markdown(html_rank, unsafe_allow_html=True)
    st.markdown(banner_venta_offline(), unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6=st.columns(6)
    with c1:
        if os.path.exists("portadas/portada_4x4.jpg"):
            st.image("portadas/portada_4x4.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 4x4 sencillas")
        st.caption(f"👀 {get_contador('visita_4x4')} | 🎰 {get_contador('4x4')}")
        if st.button("🎰 ENTRAR A 4x4", use_container_width=True, type="primary"):
            ir_a("4x4")
    with c2:
        if os.path.exists("portadas/portada_5x5.jpg"):
            st.image("portadas/portada_5x5.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 5x5 sencillas")
        st.caption(f"👀 {get_contador('visita_5x5')} | 🎰 {get_contador('5x5')}")
        if st.button("🎰 ENTRAR A 5x5", use_container_width=True):
            ir_a("5x5")
    with c3:
        if os.path.exists("portadas/portada_10-4x4-dobles.jpg"):
            st.image("portadas/portada_10-4x4-dobles.jpg", use_container_width=True)
        st.markdown("### 10 Cartas 4x4 con Dobles - 54 por Hoja")
        st.caption(f"👀 {get_contador('visita_10dobles')} | 🎰 {get_contador('10dobles')}")
        if st.button("🎰 ENTRAR A 10 CARTAS DOBLES", use_container_width=True):
            ir_a("10dobles")
    with c4:
        if os.path.exists("portadas/1-portada-12-cartas.jpg"):
            st.image("portadas/1-portada-12-cartas.jpg", use_container_width=True)
        st.markdown("### 12 CARTAS CON 1 PORTADA")
        st.caption(f"👀 {get_contador('visita_12portada')} | 🎰 {get_contador('12portada')}")
        if st.button("🎰 ENTRAR A 12 CON PORTADA", use_container_width=True):
            ir_a("12portada")
    with c5:
        if os.path.exists("portadas/portada_4x4-dobles-al-centro.jpg"):
            st.image("portadas/portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        elif os.path.exists("portada_4x4-dobles-al-centro.jpg"):
            st.image("portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        st.markdown("### 🆕 4x4 DOBLES AL CENTRO - 54 DOBLES FIX")
        st.caption(f"👀 {get_contador('visita_4x4doblesfix')} | 🎰 {get_contador('4x4doblesfix')}")
        st.markdown("<span style='background:purple;color:white;padding:4px 8px;border-radius:10px;font-size:12px'>NUEVO - SIN HUECOS - PDF</span>", unsafe_allow_html=True)
        if st.button("🎰 ENTRAR A 4x4 DOBLES FIX", use_container_width=True, type="primary"):
            ir_a("4x4doblesfix")
    with c6:
        if os.path.exists("portadas/1-port-10-cart-dc.jpg"):
            st.image("portadas/1-port-10-cart-dc.jpg", use_container_width=True)
        else:
            st.warning("Sube portadas/1-port-10-cart-dc.jpg")
        st.markdown("### 🆕 10C PANEL 600 SIN ESTIRAR")
        st.caption(f"👀 {get_contador('visita_10panel')} | 🎰 {get_contador('10panel')}")
        st.markdown("<span style='background:#FF00FF;color:white;padding:4px 8px;border-radius:10px;font-size:12px'>NUEVO - PANEL ANCHO CARTA - 600</span>", unsafe_allow_html=True)
        if st.button("🎰 ENTRAR A 10C PANEL", use_container_width=True, type="primary"):
            ir_a("10panel")
    st.stop()

if st.session_state.vista=="4x4":
    registrar_entrada_generador("4x4")
    if st.button("⬅️ Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 4 CARTAS 4X4"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_4x4')} | 🎰 {get_contador('4x4')}")
    st.markdown(instrucciones_html("4x4"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo4")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel4")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip4")
            if up:
                files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs4")
            if ups:
                files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        div=st.number_input("Div", value=1, key="div4"); sep_v=st.number_input("Sep V", value=20, key="sepv4"); sep_h=st.number_input("Sep H", value=20, key="seph4"); marco=st.number_input("Marco", value=2, key="marco4")
        color=st.color_picker("Color", "#FF00FF", key="color4")
        ancho=st.text_input("Ancho cm","21", key="ancho4"); alto=st.text_input("Alto cm","35", key="alto4"); dpi=st.text_input("DPI","300", key="dpi4")
        W_usar=1800
        juegos=st.number_input("Juegos (máx 10)", value=1, min_value=1, max_value=10, key="j4")
        st.info("💡 ¿Necesitas más de 10 juegos de un jalón? Adquiere la versión COMPLETA para computadora sin internet y sin límites. Aquí es gratis y está limitado a 10 para que todos puedan probarlo 🙏")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA", use_container_width=True, key="prev4"):
                    with lock:
                        cartas=generar_logica_4x4(files)
                        if cartas:
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final4"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS", type="primary", use_container_width=True, key="gen4"):
                    inc_contador("4x4", 1); inc_baraja(nombre_baraja, "4x4")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0)
                        for j in range(juegos):
                            cartas=generar_logica_4x4(files)
                            if not cartas: continue
                            orig=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            lista_orig.append(orig); lista_final.append(final); bar.progress((j+1)/juegos)
                        st.session_state["lista_final4"]=lista_final; st.session_state["lista_orig4"]=lista_orig
            if "prev_final4" in st.session_state:
                st.image(st.session_state["prev_final4"], caption="Vista previa", use_container_width=True)
            if "lista_final4" in st.session_state and st.session_state["lista_final4"]:
                finales=st.session_state["lista_final4"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4"]
                for i,im in enumerate(finales):
                    st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"loteria_4x4_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"loteria_4x4_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()

if st.session_state.vista=="5x5":
    registrar_entrada_generador("5x5")
    if st.button("⬅️ Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 5x5 4 CARTAS"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_5x5')} | 🎰 {get_contador('5x5')}")
    st.markdown(instrucciones_html("5x5 GRANDE"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo5")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel5")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip5")
            if up:
                files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs5")
            if ups:
                files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        div=st.number_input("Div", value=1, key="div5"); sep_v=st.number_input("Sep V", value=20, key="sepv5"); sep_h=st.number_input("Sep H", value=20, key="seph5"); marco=st.number_input("Marco", value=2, key="marco5")
        color=st.color_picker("Color", "#FF00FF", key="color5")
        ancho=st.text_input("Ancho cm","21", key="ancho5"); alto=st.text_input("Alto cm","35", key="alto5"); dpi=st.text_input("DPI","300", key="dpi5")
        W_usar=2000
        juegos=st.number_input("Juegos (máx 10)", value=1, min_value=1, max_value=10, key="j5")
        st.info("💡 ¿Necesitas más de 10 juegos de un jalón? Adquiere la versión COMPLETA para computadora sin internet y sin límites. Aquí es gratis y está limitado a 10 para que todos puedan probarlo 🙏")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out5")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA", use_container_width=True, key="prev5"):
                    with lock:
                        cartas=generar_logica_5x5(files)
                        if cartas:
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final5"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS", type="primary", use_container_width=True, key="gen5"):
                    inc_contador("5x5", 1); inc_baraja(nombre_baraja, "5x5")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0)
                        for j in range(juegos):
                            cartas=generar_logica_5x5(files)
                            if not cartas: continue
                            orig=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            lista_orig.append(orig); lista_final.append(final); bar.progress((j+1)/juegos)
                        st.session_state["lista_final5"]=lista_final; st.session_state["lista_orig5"]=lista_orig
            if "prev_final5" in st.session_state:
                st.image(st.session_state["prev_final5"], caption="Vista previa", use_container_width=True)
            if "lista_final5" in st.session_state and st.session_state["lista_final5"]:
                finales=st.session_state["lista_final5"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig5"]
                for i,im in enumerate(finales):
                    st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
               def crear_carta_4x4(data16, cw_card, ch_card, div, g, asp):
    carta=Image.new("RGB",(cw_card,ch_card),"black")
    fw=cw_card-g*2; fh=ch_card-g*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-div*3)//4; ch=int(cw*asp); th=ch*4+div*3; y0=(fh-th)//2
    for i in range(min(16,len(data16))):
        r=i//4; c=i%4; x=c*(cw+div); y=y0+r*(ch+div)
        try:
            with Image.open(data16[i]) as im:
                base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x,y))
        except:
            pass
    carta.paste(base,(g,g)); return carta
def generar_logica_4x4(baraja):
    uso=st.session_state["uso_global_4x4"]
    if not uso:
        uso={f:0 for f in baraja}; st.session_state["uso_global_4x4"]=uso
    for _ in range(2500):
        conteo={}; cartas=[[None]*16 for _ in range(4)]; pos_fig={}; ok=True
        base54=baraja.copy(); random.shuffle(base54)
        huecos=[3,3,2,2]; random.shuffle(huecos)
        huecos_carta=[set(random.sample(range(16),h)) for h in huecos]
        idx=0
        for c in range(4):
            for pos in range(16):
                if pos in huecos_carta[c]:
                    continue
                fig=base54[idx]; cartas[c][pos]=fig; pos_fig[fig]=pos_fig.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda=baraja.copy(); random.shuffle(segunda); segunda.sort(key=lambda x:(uso.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas[c] if f])
            for pos in huecos_carta[c]:
                cand=[f for f in segunda if f not in usados and conteo.get(f,0)<2 and pos not in pos_fig.get(f,set())]
                if not cand:
                    cand=[f for f in baraja if f not in usados and conteo.get(f,0)<2]
                if not cand:
                    ok=False; break
                eleg=cand[0]; cartas[c][pos]=eleg; pos_fig[eleg]=pos_fig.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok:
                break
        if not ok:
            continue
        if not no_chocan(cartas[0],cartas[1],RIGHT4,LEFT4): continue
        if not no_chocan(cartas[0],cartas[2],BOTTOM4,TOP4): continue
        if not no_chocan(cartas[1],cartas[3],BOTTOM4,TOP4): continue
        if not no_chocan(cartas[2],cartas[3],RIGHT4,LEFT4): continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items():
            uso[f]=uso.get(f,0)+cnt
        st.session_state["uso_global_4x4"]=uso; return cartas
    return None
def generar_hoja_4x4(cartas_data, color, div, sep_v, sep_h, g, asp, final_size=None, W_orig=1800):
    cw_tmp=((W_orig-sep_v)//2 - g*2 - 3*div)//4; ch_tmp=int(cw_tmp*asp); card_h=ch_tmp*4+div*3+g*2
    H_orig=card_h*2+sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color)
    for idx,d16 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_4x4(d16,cw,ch,div,g,asp),(x,y))
    if final_size:
        sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet
def crear_carta_5x5(data25, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*4)//5; ch=int(cw*aspecto); th=ch*5+DIV*4; y0=(fh-th)//2
    for idx in range(min(25,len(data25))):
        r=idx//5; c=idx%5; x0=c*(cw+DIV); y0f=y0 + r*(ch+DIV)
        try:
            with Image.open(data25[idx]) as im:
                base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x0,y0f))
        except:
            pass
    carta.paste(base,(G,G)); return carta
def generar_logica_5x5(baraja_files):
    uso=st.session_state["uso_global_5x5"]
    if not uso:
        uso={f:0 for f in baraja_files}; st.session_state["uso_global_5x5"]=uso
    for _ in range(2500):
        conteo={}; cartas_data=[[None]*25 for _ in range(4)]; pos_por_figura={}; ok=True
        base54=baraja_files.copy(); random.shuffle(base54)
        huecos=[11,11,12,12]; random.shuffle(huecos)
        huecos_por_carta=[set(random.sample(range(25), huecos[c])) for c in range(4)]
        idx=0
        for c in range(4):
            for pos in range(25):
                if pos in huecos_por_carta[c]:
                    continue
                fig=base54[idx]; cartas_data[c][pos]=fig; pos_por_figura[fig]=pos_por_figura.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda_lista=baraja_files.copy(); random.shuffle(segunda_lista); segunda_lista.sort(key=lambda x:(uso.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas_data[c] if f is not None])
            for pos in huecos_por_carta[c]:
                base=[f for f in segunda_lista if f not in usados and conteo.get(f,0)<2 and pos not in pos_por_figura.get(f,set())]
                if not base:
                    base=[f for f in baraja_files if f not in usados and conteo.get(f,0)<2]
                if not base:
                    ok=False; break
                eleg=base[0]; cartas_data[c][pos]=eleg; pos_por_figura[eleg]=pos_por_figura.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok:
                break
        if not ok:
            continue
        if not no_chocan(cartas_data[0], cartas_data[1], RIGHT5, LEFT5): continue
        if not no_chocan(cartas_data[0], cartas_data[2], BOTTOM5, TOP5): continue
        if not no_chocan(cartas_data[1], cartas_data[3], BOTTOM5, TOP5): continue
        if not no_chocan(cartas_data[2], cartas_data[3], RIGHT5, LEFT5): continue
        if len(pos_por_figura) < 54: continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items():
            uso[f]=uso.get(f,0)+cnt
        st.session_state["uso_global_5x5"]=uso; return cartas_data
    return None
def generar_hoja_5x5(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, final_size=None, W_orig=2000):
    cw_tmp=((W_orig-sep_v)//2 - g_negro*2 - 4*div_interno)//5; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*5 + div_interno*4 + g_negro*2
    H_orig=card_h_real*2 + sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d25 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_5x5(d25, cw, ch, div_interno, g_negro, aspecto),(x,y))
    if final_size:
        sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet
def poner_puntito_10(celda):
    w,h = celda.size; d = ImageDraw.Draw(celda); d.ellipse((w//2-2, h-8, w//2+2, h-4), fill="black"); return celda
def crear_carta_ajustada_10(data16, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*3)//4; ch=int(cw*aspecto); total_h_grid=ch*4+DIV*3; y_offset=(fh-total_h_grid)//2
    for idx in range(min(16,len(data16))):
        r=idx//4; c=idx%4; x0=c*(cw+DIV); y0=y_offset + r*(ch+DIV)
        celda=Image.new("RGB",(cw,ch),"black")
        try:
            with Image.open(data16[idx]) as im:
                im2=im.convert("RGB").resize((cw,ch), Image.LANCZOS); celda.paste(im2,(0,0))
        except:
            pass
        celda=poner_puntito_10(celda); base.paste(celda,(x0,y0))
    carta.paste(base,(G,G)); return carta
def generar_logica_10_cartas_54(baraja_files, es_nuevo_juego=False):
    uso_global = st.session_state["uso_global_10"]; uso_como_dup = st.session_state["uso_como_dup_10"]; cartas_hash = st.session_state["hash_10"]
    if es_nuevo_juego or not uso_global:
        uso_global={f:0 for f in baraja_files}; uso_como_dup={f:0 for f in baraja_files}; cartas_hash=set()
    RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; BOTTOM=[12,13,14,15]; TOP=[0,1,2,3]
    for _ in range(2500):
        orden_dups=sorted(baraja_files, key=lambda x: (uso_como_dup.get(x,0), random.random()))
        dups_10=orden_dups[:10]; random.shuffle(dups_10); dups_set=set(dups_10)
        lista_44=[f for f in baraja_files if f not in dups_set]; random.shuffle(lista_44)
        conteo={f:2 for f in dups_10}; cartas_data=[[None]*16 for _ in range(10)]; PROHIBIDAS={9,10}
        for idx in range(10):
            cartas_data[idx][5]=dups_10[idx]; cartas_data[idx][6]=dups_10[idx]
        ok=True
        for i,d in enumerate(dups_10):
            posibles=[c for c in range(10) if c!=i]; random.shuffle(posibles); colocado=False
            for dest in posibles:
                if d in cartas_data[dest]: continue
                libres=[p for p in range(16) if cartas_data[dest][p] is None and p not in PROHIBIDAS]; random.shuffle(libres)
                for p in libres:
                    cartas_data[dest][p]=d
                    if dest>0 and dest%5!=0 and not no_chocan(cartas_data[dest-1], cartas_data[dest], RIGHT, LEFT):
                        cartas_data[dest][p]=None; continue
                    if dest>=5 and not no_chocan(cartas_data[dest-5], cartas_data[dest], BOTTOM, TOP):
                        cartas_data[dest][p]=None; continue
                    conteo[d]+=1; colocado=True; break
                if colocado: break
            if not colocado: ok=False; break
        if not ok: continue
        for cidx in range(10):
            usados=set([x for x in cartas_data[cidx] if x])
            for pos in range(16):
                if cartas_data[cidx][pos] is not None: continue
                base44=[f for f in lista_44 if f not in usados and conteo.get(f,0)<4]
                if not base44: base44=[f for f in baraja_files if f not in usados and f not in dups_set and conteo.get(f,0)<4]
                base44=sorted(base44, key=lambda x:(conteo.get(x,0), uso_global.get(x,0), random.random())); colocado=False
                for pick in base44[:15]:
                    cartas_data[cidx][pos]=pick
                    if cidx>0 and cidx%5!=0 and not no_chocan(cartas_data[cidx-1], cartas_data[cidx], RIGHT, LEFT):
                        cartas_data[cidx][pos]=None; continue
                    if cidx>=5 and not no_chocan(cartas_data[cidx-5], cartas_data[cidx], BOTTOM, TOP):
                        cartas_data[cidx][pos]=None; continue
                    ch=tuple(sorted([x for x in cartas_data[cidx] if x]))
                    if len(ch)==16 and ch in cartas_hash:
                        cartas_data[cidx][pos]=None; continue
                    usados.add(pick); conteo[pick]=conteo.get(pick,0)+1; colocado=True; break
                if not colocado: ok=False; break
            if not ok: break
        if not ok: continue
        temp_hash=set()
        for cd in cartas_data:
            hh=tuple(sorted(cd))
            if hh in cartas_hash or hh in temp_hash: ok=False; break
            temp_hash.add(hh)
        if not ok: continue
        todas=set()
        for cd in cartas_data: todas.update([x for x in cd if x])
        if len(todas)<54: continue
        for hh in temp_hash: cartas_hash.add(hh)
        for f,c in conteo.items(): uso_global[f]=uso_global.get(f,0)+c
        for f in dups_10: uso_como_dup[f]=uso_como_dup.get(f,0)+1
        st.session_state["uso_global_10"]=uso_global; st.session_state["uso_como_dup_10"]=uso_como_dup; st.session_state["hash_10"]=cartas_hash
        return cartas_data, dups_10
    return None, None
def generar_original_fijo_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="5x2"):
    cols,rows=(5,2) if layout=="5x2" else (2,5)
    W_base=7500 if layout=="5x2" else 3200; card_w_real=W_base//cols
    cw_tmp=(card_w_real - g_negro*2 - 3*div_interno)//4; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*4 + div_interno*3 + g_negro*2
    W_orig=card_w_real*cols + sep_v*(cols-1); H_orig=card_h_real*rows + sep_h*(rows-1)
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols; x=col*(card_w_real+sep_v); y=row*(card_h_real+sep_h)
        sheet.paste(crear_carta_ajustada_10(d16, card_w_real, card_h_real, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="5x2"):
    orig=generar_original_fijo_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final

# ===== NUEVO 10C PANEL 600 SIN ESTIRAR =====
CARTA_PANEL_W = 600
def crear_carta_panel_600(data16, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    cw_cell = (CARTA_PANEL_W - G*2 - DIV*3)//4
    ch_cell = int(cw_cell * aspecto)
    card_h = ch_cell*4 + DIV*3 + G*2
    carta=Image.new("RGB",(CARTA_PANEL_W, card_h),"black")
    fw=CARTA_PANEL_W-G*2
    base=Image.new("RGB",(fw, card_h-G*2),"black")
    for idx in range(min(16,len(data16))):
        r=idx//4; c=idx%4; x0=c*(cw_cell+DIV); y0=r*(ch_cell+DIV)
        celda=Image.new("RGB",(cw_cell,ch_cell),"black")
        try:
            with Image.open(data16[idx]) as im:
                im2=im.convert("RGB").resize((cw_cell,ch_cell), Image.LANCZOS)
                celda.paste(im2,(0,0))
        except:
            pass
        base.paste(celda,(x0,y0))
    carta.paste(base,(G,G))
    return carta
def generar_logica_10panel_54(baraja_files, es_nuevo_juego=False):
    uso_global = st.session_state["uso_global_10panel"]
    uso_como_dup = st.session_state["uso_como_dup_10panel"]
    cartas_hash = st.session_state["hash_10panel"]
    if es_nuevo_juego or not uso_global:
        uso_global={f:0 for f in baraja_files}
        uso_como_dup={f:0 for f in baraja_files}
        cartas_hash=set()
    RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; BOTTOM=[12,13,14,15]; TOP=[0,1,2,3]
    for _ in range(2500):
        orden_dups=sorted(baraja_files, key=lambda x: (uso_como_dup.get(x,0), random.random()))
        dups_10=orden_dups[:10]; random.shuffle(dups_10); dups_set=set(dups_10)
        lista_44=[f for f in baraja_files if f not in dups_set]; random.shuffle(lista_44)
        conteo={f:2 for f in dups_10}; cartas_data=[[None]*16 for _ in range(10)]
        for idx in range(10):
            cartas_data[idx][5]=dups_10[idx]
            cartas_data[idx][6]=dups_10[idx]
        ok=True
        for i,d in enumerate(dups_10):
            posibles=[c for c in range(10) if c!=i]; random.shuffle(posibles); colocado=False
            for dest in posibles:
                if d in cartas_data[dest]: continue
                libres=[p for p in range(16) if cartas_data[dest][p] is None]; random.shuffle(libres)
                for p in libres:
                    cartas_data[dest][p]=d
                    if dest>0 and dest%5!=0 and not no_chocan(cartas_data[dest-1], cartas_data[dest], RIGHT, LEFT):
                        cartas_data[dest][p]=None; continue
                    if dest>=5 and not no_chocan(cartas_data[dest-5], cartas_data[dest], BOTTOM, TOP):
                        cartas_data[dest][p]=None; continue
                    conteo[d]+=1; colocado=True; break
                if colocado: break
            if not colocado: ok=False; break
        if not ok: continue
        for cidx in range(10):
            usados=set([x for x in cartas_data[cidx] if x])
            for pos in range(16):
                if cartas_data[cidx][pos] is not None: continue
                base44=[f for f in lista_44 if f not in usados and conteo.get(f,0)<4]
                if not base44: base44=[f for f in baraja_files if f not in usados and f not in dups_set and conteo.get(f,0)<4]
                base44=sorted(base44, key=lambda x:(conteo.get(x,0), uso_global.get(x,0), random.random()))
                colocado=False
                for pick in base44[:15]:
                    cartas_data[cidx][pos]=pick
                    if cidx>0 and cidx%5!=0 and not no_chocan(cartas_data[cidx-1], cartas_data[cidx], RIGHT, LEFT):
                        cartas_data[cidx][pos]=None; continue
                    if cidx>=5 and not no_chocan(cartas_data[cidx-5], cartas_data[cidx], BOTTOM, TOP):
                        cartas_data[cidx][pos]=None; continue
                    ch=tuple(sorted([x for x in cartas_data[cidx] if x]))
                    if len(ch)==16 and ch in cartas_hash:
                        cartas_data[cidx][pos]=None; continue
                    usados.add(pick); conteo[pick]=conteo.get(pick,0)+1; colocado=True; break
                if not colocado: ok=False; break
            if not ok: break
        if not ok: continue
        temp_hash=set()
        for cd in cartas_data:
            hh=tuple(sorted(cd))
            if hh in cartas_hash or hh in temp_hash: ok=False; break
            temp_hash.add(hh)
        if not ok: continue
        todas=set()
        for cd in cartas_data: todas.update([x for x in cd if x])
        if len(todas)<54: continue
        for hh in temp_hash: cartas_hash.add(hh)
        for f,c in conteo.items(): uso_global[f]=uso_global.get(f,0)+c
        for f in dups_10: uso_como_dup[f]=uso_como_dup.get(f,0)+1
        st.session_state["uso_global_10panel"]=uso_global
        st.session_state["uso_como_dup_10panel"]=uso_como_dup
        st.session_state["hash_10panel"]=cartas_hash
        return cartas_data, dups_10
    return None, None
def generar_original_fijo_10panel(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="5x2"):
    cols,rows=(5,2) if layout=="5x2" else (2,5)
    sample_card = crear_carta_panel_600(cartas_data[0], div_interno, g_negro, aspecto)
    cw_real, ch_real = sample_card.size
    W_orig=cw_real*cols + sep_v*(cols-1)
    H_orig=ch_real*rows + sep_h*(rows-1)
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols; x=col*(cw_real+sep_v); y=row*(ch_real+sep_h)
        sheet.paste(crear_carta_panel_600(d16, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_10panel(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="5x2"):
    orig=generar_original_fijo_10panel(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
    CICLO_FIJO_4x4DOB = 14
def poner_puntito_4x4dob(celda):
    w,h = celda.size; d = ImageDraw.Draw(celda); d.ellipse((w//2-2, h-8, w//2+2, h-4), fill="black"); return celda
def crear_carta_ajustada_4x4dob(data16, card_w, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno; fw = card_w - G*2; cw = (fw - DIV*3)//4; ch = int(cw*aspecto); card_h = ch*4 + DIV*3 + G*2
    carta=Image.new("RGB",(card_w, card_h),"black"); base=Image.new("RGB",(fw, card_h - G*2),"black")
    for idx in range(min(16,len(data16))):
        r=idx//4; c=idx%4; x0=c*(cw+DIV); y0=r*(ch+DIV)
        celda=Image.new("RGB",(cw,ch),"black")
        try:
            with Image.open(data16[idx]) as im:
                im2=im.convert("RGB").resize((cw,ch), Image.LANCZOS); celda.paste(im2,(0,0))
        except:
            pass
        celda=poner_puntito_4x4dob(celda); base.paste(celda,(x0,y0))
    carta.paste(base,(G,G)); return carta
def generar_ciclo_54_dobles_4x4dob(baraja_files):
    todas = baraja_files.copy(); random.shuffle(todas)
    repetidas = random.sample(todas, 2); dobles_ciclo = todas + repetidas; random.shuffle(dobles_ciclo)
    hojas = []; idx_doble = 0
    for _ in range(CICLO_FIJO_4x4DOB):
        cartas_data_hoja = []
        for _ in range(4):
            dup = dobles_ciclo[idx_doble]; idx_doble+=1
            restantes = [f for f in baraja_files if f != dup]; random.shuffle(restantes)
            top = [None]*16; top[5]=dup; top[6]=dup
            pos_libres = [i for i in range(16) if i not in [5,6]]; random.shuffle(pos_libres)
            for i, pos in enumerate(pos_libres[:14]):
                top[pos]=restantes[i]
            for pos in range(16):
                if top[pos] is None:
                    top[pos]=random.choice(restantes)
            cartas_data_hoja.append(top)
        hojas.append(cartas_data_hoja)
    return hojas, dobles_ciclo, repetidas
def generar_original_fijo_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="2x2"):
    CARD_W = 1100; fw = CARD_W - g_negro*2; cw_cell = (fw - div_interno*3)//4; ch_cell = int(cw_cell * aspecto); CARD_H = ch_cell*4 + div_interno*3 + g_negro*2
    if layout=="1x4":
        W_orig = CARD_W*4 + sep_v*3; H_orig = CARD_H; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
        for idx,d16 in enumerate(cartas_data):
            x=idx*(CARD_W+sep_v); y=0; sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
    else:
        W_orig = CARD_W*2 + sep_v; H_orig = CARD_H*2 + sep_h; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
        for idx,d16 in enumerate(cartas_data):
            col=idx%2; row=idx//2; x=col*(CARD_W+sep_v); y=row*(CARD_H+sep_h); sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="2x2"):
    orig=generar_original_fijo_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
def imagenes_a_pdf_4x4dob(imagenes_pil):
    if not imagenes_pil:
        return None
    rgb_imgs = [im.convert("RGB") for im in imagenes_pil]; buf = io.BytesIO()
    rgb_imgs[0].save(buf, format="PDF", save_all=True, append_images=rgb_imgs[1:], resolution=300)
    return buf.getvalue()
def crear_carta_imagen_16(data16, card_w=1000, div_interno=8, sample_aspect=1.45):
    cell_w=card_w//4; cell_h=int(cell_w*sample_aspect); img=Image.new("RGB",(card_w, cell_h*4),"black")
    target_w=cell_w-div_interno; target_h=cell_h-div_interno
    for idx,ruta in enumerate(data16):
        try:
            with Image.open(ruta) as im0:
                im=im0.convert("RGB"); iw,ih=im.size; scale=max(target_w/iw, target_h/ih)
                nw,nh=int(iw*scale), int(ih*scale); im=im.resize((nw,nh), Image.LANCZOS)
                left=(nw-target_w)//2; top=(nh-target_h)//2; im=im.crop((left,top,left+target_w,top+target_h))
        except:
            im=Image.new("RGB",(target_w,target_h),"white")
        col=idx%4; row=idx//4; x=col*cell_w+div_interno//2; y=row*cell_h+div_interno//2; img.paste(im,(x,y))
    return img
def generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_cover_path, favorita_baraja_path, color_entre, div_interno, sep_entre):
    try:
        with Image.open(baraja_files[0]) as s:
            asp=s.size[1]/s.size[0]
    except:
        asp=1.45
    card_w=800; card_h=int(card_w*asp)
    grid_pos=[(2,0),(3,0),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(1,3),(2,3),(3,3)]
    vecinos={}
    for i,(r,c) in enumerate(grid_pos):
        lst=[]
        for j,(r2,c2) in enumerate(grid_pos):
            if i==j: continue
            if r==r2 and c==c2+1: lst.append((j,RIGHT4,LEFT4))
            if r==r2 and c==c2-1: lst.append((j,LEFT4,RIGHT4))
            if c==c2 and r==r2+1: lst.append((j,BOTTOM4,TOP4))
            if c==c2 and r==r2-1: lst.append((j,TOP4,BOTTOM4))
        vecinos[i]=lst
    otros=[f for f in baraja_files if f!=favorita_baraja_path][:53]
    for _ in range(1500):
        posiciones_fav=random.sample(range(16),12); random.shuffle(otros); pool=[]
        for f in otros[:21]: pool.extend([f]*4)
        for f in otros[21:]: pool.extend([f]*3)
        random.shuffle(pool); pool_idx=0; cartas_data=[]; ok=True
        for idx_carta in range(12):
            fav_pos=posiciones_fav[idx_carta]; carta_ok=False
            for _ in range(60):
                top=[None]*16; top[fav_pos]=favorita_baraja_path; usados=set([favorita_baraja_path]); temp_idx=pool_idx; temp_pool=pool[:]; fail=False
                for pos in range(16):
                    if top[pos] is not None: continue
                    encontrado=False
                    for k in range(temp_idx, len(temp_pool)):
                        if temp_pool[k] not in usados:
                            top[pos]=temp_pool[k]; usados.add(temp_pool[k]); temp_pool[k], temp_pool[temp_idx]=temp_pool[temp_idx], temp_pool[k]; temp_idx+=1; encontrado=True; break
                    if not encontrado: fail=True; break
                if fail: continue
                choque=False
                for j,la,lb in vecinos[idx_carta]:
                    if j < len(cartas_data):
                        if not no_chocan(cartas_data[j], top, la, lb): choque=True; break
                if choque: continue
                pool=temp_pool; pool_idx=temp_idx; cartas_data.append(top); carta_ok=True; break
            if not carta_ok: ok=False; break
        if not ok: continue
        W=4*card_w+3*sep_entre; H=4*card_h+3*sep_entre
        sheet=Image.new("RGB",(W,H), color_entre)
        try:
            with Image.open(portada_cover_path) as imc0:
                imc=imc0.convert("RGB")
                tw=2*card_w+sep_entre; th=2*card_h+sep_entre; sc=max(tw/imc.size[0], th/imc.size[1])
                imc=imc.resize((int(imc.size[0]*sc), int(imc.size[1]*sc)), Image.LANCZOS)
                imc=imc.crop(((imc.size[0]-tw)//2, (imc.size[1]-th)//2, (imc.size[0]-tw)//2+tw, (imc.size[1]-th)//2+th))
        except:
            imc=Image.new("RGB",(2*card_w+sep_entre, 2*card_h+sep_entre),"gold")
        sheet.paste(imc,(0,0))
        for idx,data16 in enumerate(cartas_data):
            r,c=grid_pos[idx]
            if r<2 and c<2: continue
            x=c*(card_w+sep_entre); y=r*(card_h+sep_entre)
            sheet.paste(crear_carta_imagen_16(data16, card_w=card_w, div_interno=div_interno, sample_aspect=asp),(x,y))
        gc.collect(); return sheet
    return None
def limpiar_nombre(path_img, idx):
    raw=os.path.splitext(os.path.basename(path_img))[0]
    clean=raw.replace("_"," ").replace("-"," ").strip().upper()
    clean=' '.join([w for w in clean.split() if not w.isdigit()]).strip()
    if not clean: clean=f"CARTA {idx}"
    return clean

# ========== CATALOGO CON 6 GENERADORES ==========
if st.session_state.vista=="catalogo":
    st.markdown(banner_top("CATALOGO LOTERIA ELIUD PRO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.markdown(instrucciones_html("catalogo"), unsafe_allow_html=True)
    ranking = get_ranking_barajas()
    if ranking:
        st.markdown("### 🏆 RANKING BARAJAS MÁS USADAS")
        html_rank = "<div style='background:white;border:2px solid gold;border-radius:12px;padding:12px;color:black'>"
        for i,(nom,cnt) in enumerate(ranking,1):
            html_rank += f"<div style='padding:6px;border-bottom:1px solid #eee'><b>{i}. {nom}</b> - {cnt} usos</div>"
        html_rank += "</div><br>"
        st.markdown(html_rank, unsafe_allow_html=True)
    st.markdown(banner_venta_offline(), unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6=st.columns(6)
    with c1:
        if os.path.exists("portadas/portada_4x4.jpg"):
            st.image("portadas/portada_4x4.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 4x4 sencillas")
        st.caption(f"👀 {get_contador('visita_4x4')} | 🎰 {get_contador('4x4')}")
        if st.button("🎰 ENTRAR A 4x4", use_container_width=True, type="primary"):
            ir_a("4x4")
    with c2:
        if os.path.exists("portadas/portada_5x5.jpg"):
            st.image("portadas/portada_5x5.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 5x5 sencillas")
        st.caption(f"👀 {get_contador('visita_5x5')} | 🎰 {get_contador('5x5')}")
        if st.button("🎰 ENTRAR A 5x5", use_container_width=True):
            ir_a("5x5")
    with c3:
        if os.path.exists("portadas/portada_10-4x4-dobles.jpg"):
            st.image("portadas/portada_10-4x4-dobles.jpg", use_container_width=True)
        st.markdown("### 10 Cartas 4x4 con Dobles - 54 por Hoja")
        st.caption(f"👀 {get_contador('visita_10dobles')} | 🎰 {get_contador('10dobles')}")
        if st.button("🎰 ENTRAR A 10 CARTAS DOBLES", use_container_width=True):
            ir_a("10dobles")
    with c4:
        if os.path.exists("portadas/1-portada-12-cartas.jpg"):
            st.image("portadas/1-portada-12-cartas.jpg", use_container_width=True)
        st.markdown("### 12 CARTAS CON 1 PORTADA")
        st.caption(f"👀 {get_contador('visita_12portada')} | 🎰 {get_contador('12portada')}")
        if st.button("🎰 ENTRAR A 12 CON PORTADA", use_container_width=True):
            ir_a("12portada")
    with c5:
        if os.path.exists("portadas/portada_4x4-dobles-al-centro.jpg"):
            st.image("portadas/portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        elif os.path.exists("portada_4x4-dobles-al-centro.jpg"):
            st.image("portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        st.markdown("### 🆕 4x4 DOBLES AL CENTRO - 54 DOBLES FIX")
        st.caption(f"👀 {get_contador('visita_4x4doblesfix')} | 🎰 {get_contador('4x4doblesfix')}")
        st.markdown("<span style='background:purple;color:white;padding:4px 8px;border-radius:10px;font-size:12px'>NUEVO - SIN HUECOS - PDF</span>", unsafe_allow_html=True)
        if st.button("🎰 ENTRAR A 4x4 DOBLES FIX", use_container_width=True, type="primary"):
            ir_a("4x4doblesfix")
    with c6:
        if os.path.exists("portadas/1-port-10-cart-dc.jpg"):
            st.image("portadas/1-port-10-cart-dc.jpg", use_container_width=True)
        else:
            st.warning("⚠️ Sube tu portada a portadas/1-port-10-cart-dc.jpg")
        st.markdown("### 🆕 10C PANEL 600 SIN ESTIRAR")
        st.caption(f"👀 {get_contador('visita_10panel')} | 🎰 {get_contador('10panel')}")
        st.markdown("<span style='background:#FF00FF;color:white;padding:4px 8px;border-radius:10px;font-size:12px'>NUEVO - PANEL ANCHO CARTA - 600</span>", unsafe_allow_html=True)
        if st.button("🎰 ENTRAR A 10C PANEL", use_container_width=True, type="primary"):
            ir_a("10panel")
    st.stop()

if st.session_state.vista=="4x4":
    registrar_entrada_generador("4x4")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 4 CARTAS 4X4"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_4x4')} | 🎰 {get_contador('4x4')}")
    st.markdown(instrucciones_html("4x4"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo4")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel4")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip4")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs4")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        div=st.number_input("Div", value=1, key="div4"); sep_v=st.number_input("Sep V", value=20, key="sepv4"); sep_h=st.number_input("Sep H", value=20, key="seph4"); marco=st.number_input("Marco", value=2, key="marco4")
        color=st.color_picker("Color", "#FF00FF", key="color4")
        ancho=st.text_input("Ancho cm","21", key="ancho4"); alto=st.text_input("Alto cm","35", key="alto4"); dpi=st.text_input("DPI","300", key="dpi4")
        W_usar=1800; juegos=st.number_input("Juegos (máx 10)", value=1, min_value=1, max_value=10, key="j4")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA", use_container_width=True, key="prev4"):
                    with lock:
                        cartas=generar_logica_4x4(files)
                        if cartas:
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final4"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS", type="primary", use_container_width=True, key="gen4"):
                    inc_contador("4x4", 1); inc_baraja(nombre_baraja, "4x4")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0)
                        for j in range(juegos):
                            cartas=generar_logica_4x4(files)
                            if not cartas: continue
                            orig=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            lista_orig.append(orig); lista_final.append(final); bar.progress((j+1)/juegos)
                        st.session_state["lista_final4"]=lista_final; st.session_state["lista_orig4"]=lista_orig
            if "prev_final4" in st.session_state: st.image(st.session_state["prev_final4"], caption="Vista previa", use_container_width=True)
            if "lista_final4" in st.session_state and st.session_state["lista_final4"]:
                finales=st.session_state["lista_final4"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4"]
                for i,im in enumerate(finales): st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"loteria_4x4_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"loteria_4x4_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()

if st.session_state.vista=="10panel":
    registrar_entrada_generador("10panel")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("🆕 10C PANEL 600 SIN ESTIRAR - ANCHO CARTA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_10panel')} | 🎰 {get_contador('10panel')}")
    st.markdown(instrucciones_html("10C PANEL 600 SIN ESTIRAR"), unsafe_allow_html=True)
    if os.path.exists("portadas/1-port-10-cart-dc.jpg"): st.image("portadas/1-port-10-cart-dc.jpg", width=450)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo10panel")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel10panel")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip10panel")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs10panel")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        layout=st.selectbox("LAYOUT PANEL", ["5x2","2x5"], key="layout10panel")
        div=st.number_input("Div", value=1, key="div10panel"); sep_v=st.number_input("Sep V", value=20, key="sepv10panel"); sep_h=st.number_input("Sep H", value=20, key="seph10panel"); marco=st.number_input("Marco", value=2, key="marco10panel")
        color=st.color_picker("Color", "#FFFFFF", key="color10panel")
        ancho=st.text_input("Ancho cm","54", key="ancho10panel"); alto=st.text_input("Alto cm","35", key="alto10panel"); dpi=st.text_input("DPI","300", key="dpi10panel")
        ciclos=st.number_input("Ciclos (1 ciclo=6 hojas)", value=1, min_value=1, max_value=10, key="ciclos10panel")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL 600"], horizontal=True, key="out10panel")
        st.info("📏 Carta 600px sin estirar - Ideal hoja carta. No se deforma. Nuevo generador PANEL.")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA 10C PANEL 600", use_container_width=True, key="prev10panel"):
                    with lock:
                        st.session_state["uso_global_10panel"]={}; st.session_state["uso_como_dup_10panel"]={}; st.session_state["hash_10panel"]=set()
                        cartas,dups=generar_logica_10panel_54(files, es_nuevo_juego=True)
                        if cartas:
                            orig, final = generar_con_resize_10panel(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                            st.session_state["prev_orig10panel"]=orig; st.session_state["prev_final10panel"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {ciclos} CICLOS PANEL 600", type="primary", use_container_width=True, key="gen10panel"):
                    inc_contador("10panel", 1); inc_baraja(nombre_baraja, "10panel")
                    with lock:
                        lista_final=[]; lista_orig=[]; st.session_state["uso_global_10panel"]={}; st.session_state["uso_como_dup_10panel"]={}; st.session_state["hash_10panel"]=set()
                        bar=st.progress(0); total_h = ciclos*6; cnt=0
                        for ciclo in range(1, ciclos+1):
                            st.session_state["uso_global_10panel"]={}; st.session_state["uso_como_dup_10panel"]={}; st.session_state["hash_10panel"]=set()
                            for h in range(1,7):
                                cartas,dups=generar_logica_10panel_54(files, es_nuevo_juego=(h==1))
                                if not cartas: continue
                                orig, final = generar_con_resize_10panel(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                                lista_orig.append(orig); lista_final.append(final); cnt+=1; bar.progress(cnt/total_h)
                        st.session_state["lista_final10panel"]=lista_final; st.session_state["lista_orig10panel"]=lista_orig
            if "prev_final10panel" in st.session_state:
                st.image(st.session_state["prev_final10panel"], caption=f"Vista previa PANEL 600 - {layout}", use_container_width=True)
            if "lista_final10panel" in st.session_state and st.session_state["lista_final10panel"]:
                finales=st.session_state["lista_final10panel"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig10panel"]
                for i,im in enumerate(finales): st.image(im, caption=f"Hoja {i+1} - 10C PANEL 600", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=95); zf.writestr(f"10C_PANEL_600_H{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"10C_PANEL_600_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"10C_PANEL_600_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()

# ... RESTO DE TUS VISTAS 5x5, 10dobles, 12portada, 4x4doblesfix SIGUEN IGUAL QUE LAS TENIAS, SOLO ASEGURATE DE COPIARLAS DE TU ARCHIVO ORIGINAL ABAJO DE ESTO ...
# Si quieres te mando también esas 3 vistas que faltan, pero con estas 3 partes ya tienes el 6to generador funcionando.
# IMPORTANTE: No olvides subir tu imagen a portadas/1-port-10-cart-dc.jpg
