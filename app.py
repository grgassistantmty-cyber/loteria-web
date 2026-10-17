import os, random, io, zipfile, threading, datetime
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title="Loteria Eliud PRO", layout="wide", page_icon="🎰")

@st.cache_resource
def get_lock(): return threading.Lock()
lock = get_lock()

contador_file = "/data/visitas.txt"
try:
    os.makedirs("/data", exist_ok=True)
    open(os.path.join("/data","_test.txt"),"w").write("ok")
except:
    contador_file = "visitas_local.txt"

if "visitado" not in st.session_state:
    st.session_state["visitado"]=True
    try:
        with lock:
            total=int(open(contador_file,"r").read().strip() or 0) if os.path.exists(contador_file) else 0
            total+=1; open(contador_file,"w").write(str(total))
    except: total=1
else:
    try: total=int(open(contador_file,"r").read().strip() or 0)
    except: total=1
visitas_total=total

def get_contador(nombre):
    path = f"/data/contador_{nombre}.txt" if "/data" in contador_file else f"contador_{nombre}.txt"
    if not os.path.exists(path): return 0
    try: return int(open(path,"r").read().strip() or 0)
    except: return 0
def inc_contador(nombre, cantidad=1):
    path = f"/data/contador_{nombre}.txt" if "/data" in contador_file else f"contador_{nombre}.txt"
    try:
        with lock:
            actual = get_contador(nombre); actual += cantidad
            open(path,"w").write(str(actual)); return actual
    except: return 0
def registrar_entrada_generador(nombre):
    key = f"entrada_registrada_{nombre}"
    if key not in st.session_state:
        inc_contador(f"visita_{nombre}"); st.session_state[key] = True

if "vista" not in st.session_state: st.session_state["vista"]="catalogo"
if "uso_global_4x4" not in st.session_state: st.session_state["uso_global_4x4"]={}
if "uso_global_5x5" not in st.session_state: st.session_state["uso_global_5x5"]={}
params=st.query_params
if "vista" in params and params["vista"] in ["catalogo","4x4","5x5","12portada"]: st.session_state["vista"]=params["vista"]
def ir_a(v): st.session_state["vista"]=v; st.query_params["vista"]=v; st.rerun()

EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}

def copiar_clabe_component():
    components.html("""
    <div style="text-align:center; margin-top:10px">
        <input id="clabe" value="728969000164073671" style="position:absolute; left:-9999px;">
        <button onclick="navigator.clipboard.writeText(document.getElementById('clabe').value); document.getElementById('msg').innerHTML='✅ ¡Copiada! Ya puedes pegar en tu app del banco';" 
        style="background:gold; color:black; border:none; padding:12px 22px; border-radius:25px; font-weight:bold; cursor:pointer; font-size:17px; box-shadow: 2px 2px 5px #999;">
        📋 COPIAR CLABE - PICA AQUÍ
        </button>
        <div id="msg" style="color:green; font-weight:bold; margin-top:8px; font-size:16px;"></div>
    </div>
    """, height=90)

def banner_top(titulo):
    return f"""
    <style>
    .banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}}
    .ws{{background:#25D366;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px}}
    .fb{{background:#1877F2;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px;margin-top:10px}}
    .contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px;font-size:18px}}
    .contador2{{background:#111;color:#ffd700;padding:8px 14px;border-radius:10px;font-weight:bold;display:inline-block;margin-top:8px;font-size:14px;border:1px solid gold}}
    .apoyo{{background:linear-gradient(180deg,#fffbe6,#ffe27a);border:3px solid #ffb700;padding:18px;border-radius:14px;margin-top:16px;color:#222;text-align:center;line-height:1.7}}
    </style>
    <div class="banner">
    <h1>🎰 {titulo} 🎰</h1>
    <h3>Creado por: Eliud Monsivais - WhatsApp 8115566250</h3>
    <a class="ws" href="https://wa.me/528115566250">📲 WHATSAPP 8115566250</a><br>
    <a class="fb" href="https://www.facebook.com/groups/1646464953556819" target="_blank">🔵 UNIRME AL GRUPO DE FACEBOOK</a><br>
    <span class="contador">👁️ Visitas: {visitas_total}</span><br>
    <span class="contador2">📊 USOS | 4x4: 👀{get_contador('visita_4x4')}/🎰{get_contador('4x4')} | 5x5: 👀{get_contador('visita_5x5')}/🎰{get_contador('5x5')} | 12: 👀{get_contador('visita_12portada')}/🎰{get_contador('12portada')}</span>
    <div class="apoyo">
    💖 <b style="font-size:20px">¿TE GUSTÓ MI TRABAJO? ¡APÓYAME VOLUNTARIAMENTE!</b> 💖<br>
    Esta página es <b>100% GRATIS para ti</b>, pero a mí me cuesta <b>pagar el servidor cada mes</b> para que esté prendida 24 horas.<br>
    Si te sirvió y quieres apoyarme con <b>$5, $10, $20, $50, $100 pesitos</b>, lo que nazca de tu corazón ❤️, te lo agradezco muchísimo 🙏<br><br>
    <b>BANCO: SPIN by OXXO (OXXO)</b><br>
    <span style="font-size:22px; letter-spacing:1px; background:black; color:gold; padding:8px 14px; border-radius:8px; display:inline-block; margin:6px 0;">CLABE: 728969000164073671</span><br>
    A nombre de: <b>Eliud Monsivais</b><br>
    Puedes transferir desde BBVA, Banorte, Azteca o depositar en OXXO.<br>
    ¡DIOS TE BENDIGA Y GRACIAS POR TU APOYO!
    </div>
    </div><br>
    """

def banner_facebook():
    return """
    <div style="background:#e7f3ff; border:3px solid #1877F2; border-radius:14px; padding:18px; text-align:center; margin-bottom:15px">
    <h3 style="color:#1877F2; margin:0">🔵 ¡ÚNETE A MI GRUPO DE FACEBOOK!</h3>
    <p style="color:black; font-size:17px; margin:8px 0">Aquí subo <b>barajas nuevas GRATIS</b>, doy tips y te ayudo si tienes dudas.!</p>
    <a href="https://www.facebook.com/groups/1646464953556819" target="_blank" style="background:#1877F2; color:white; padding:14px 32px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; font-size:19px">👉 ENTRAR AL GRUPO AHORA</a>
    </div>
    """

def instrucciones_html(vista="general"):
    if vista=="catalogo":
        return """
        <div style="background:#fffbe6;border:3px dashed #ffaa00;padding:20px;border-radius:14px;color:black; font-size:18px">
        <h2 style="text-align:center">📋 CÓMO USAR - EXPLICACIÓN FÁCIL PARA TODAS</h2>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid green; margin-bottom:10px">
        <b>1) 4x4 - 16 figuras por carta:</b> Lotería NORMAL de toda la vida. 16 imágenes por carta, 4 cartas por hoja, salen las 54. <b>LA MÁS USADA.</b></div>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid blue; margin-bottom:10px">
        <b>2) 5x5 - 25 figuras por carta:</b> Lotería GRANDE, 25 imágenes por carta, se ve más grande. Ideal para personas que no ven bien.</div>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid #cc0000;">
        <b>3) 12 CARTAS CON PORTADA:</b> Hoja tamaño TABLOIDE con 12 cartas + portada con tu imagen favorita en grande.</div>
        <br><span style="background:yellow; padding:6px 12px; border-radius:6px; font-weight:bold; font-size:19px">👉 ABAJO PICA EL BOTÓN VERDE "ENTRAR"</span>
        </div><br>
        """
    else:
        return f"""
        <div style="background:#fffbe6;border:2px solid #ffaa00;padding:20px;border-radius:14px;color:black; font-size:17px">
        <h2>💡 ¿PARA QUÉ SIRVE CADA BOTÓN? - {vista}</h2>
        <b>📁 Origen / Baraja:</b> Aquí eliges qué dibujos usar. Puedes usar las que ya tengo (Integrada) o subir tu propia baraja.<br>
        <b>📤 Sube tu propia baraja:</b> Si tienes tus propios dibujos, súbelos en ZIP (las 54 fotos en un zip) o súbelas sueltas una por una. ¡Tiene que ser 54 fotos!<br>
        <b>🎨 Div / División:</b> Es el grosor de la línea blanca que separa los dibujitos DENTRO de la carta. Si lo subes, se ven más separaditos.<br>
        <b>↔️ Sep V / Sep H:</b> Es el espacio ENTRE carta y carta. Vertical y Horizontal. Si lo subes, dejas más aire entre las 4 cartas.<br>
        <b>⬛ Marco:</b> Es el borde negrito alrededor de cada carta. Déjalo en 2 si no sabes.<br>
        <b>🎨 Color:</b> Color de fondo de la hoja. Elige el que combine con tu baraja.<br>
        <b>📏 Ancho / Alto / DPI:</b> Tamaño para imprimir. Déjalo en 21x35 y 300 DPI, ya sale bonito para imprenta.<br><br>
        <div style="background:#e8ffe8; padding:12px; border-radius:10px; border:2px solid green">
        <b>PASO 1:</b> Elige baraja o sube la tuya<br>
        <b>PASO 2:</b> Dale a <b>👁️ VISTA PREVIA</b> para ver cómo queda sin descargar<br>
        <b>PASO 3:</b> Si te gusta, dale a <b>🎰 GENERAR</b> y espera al 100%<br>
        <b>PASO 4:</b> Descarga PDF y ZIP abajo
        </div>
        </div><br>
        """

def listar_barajas():
    if not os.path.exists("barajas"): return []
    return sorted([os.path.join("barajas",d) for d in os.listdir("barajas") if os.path.isdir(os.path.join("barajas",d)) and d.lower().startswith("baraja")])

def cargar_files(path, limite=54):
    exts=(".png",".jpg",".jpeg",".webp",".jfif")
    if not path or not os.path.exists(path): return []
    files=[os.path.join(path,f) for f in os.listdir(path) if f.lower().endswith(exts)]
    files.sort(); return files[:limite]

def cargar_zip_temporal(uploaded_zip, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp): os.remove(os.path.join(carpeta_tmp,f))
        with zipfile.ZipFile(uploaded_zip) as zz:
            for name in zz.namelist():
                if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                    open(os.path.join(carpeta_tmp, os.path.basename(name)),"wb").write(zz.read(name))
        return cargar_files(carpeta_tmp, limite)
    except: return []

def cargar_imagenes_sueltas(uploaded_files, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp): os.remove(os.path.join(carpeta_tmp,f))
        for uf in uploaded_files[:limite]:
            open(os.path.join(carpeta_tmp, uf.name),"wb").write(uf.getbuffer())
        return cargar_files(carpeta_tmp, limite)
    except: return []

def cm_to_px(cm,dpi): return int(float(cm)/2.54*int(dpi))
def get_aspecto(files):
    asp=[]
    for p in files[:10]:
        try:
            with Image.open(p) as im: asp.append(im.size[1]/im.size[0])
        except: pass
    return sum(asp)/len(asp) if asp else 1.42
def no_chocan(a,b,la,lb):
    for i,j in zip(la,lb):
        if a[i]==b[j]: return False
    return True

RIGHT4=[3,7,11,15]; LEFT4=[0,4,8,12]; TOP4=[0,1,2,3]; BOTTOM4=[12,13,14,15]
RIGHT5=[4,9,14,19,24]; LEFT5=[0,5,10,15,20]; TOP5=[0,1,2,3,4]; BOTTOM5=[20,21,22,23,24]

def crear_carta_4x4(data16, cw_card, ch_card, div, g, asp):
    carta=Image.new("RGB",(cw_card,ch_card),"black")
    fw=cw_card-g*2; fh=ch_card-g*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-div*3)//4; ch=int(cw*asp); th=ch*4+div*3; y0=(fh-th)//2
    for i in range(min(16,len(data16))):
        r=i//4; c=i%4; x=c*(cw+div); y=y0+r*(ch+div)
        try: im=Image.open(data16[i]).convert("RGB").resize((cw,ch), Image.LANCZOS); base.paste(im,(x,y))
        except: pass
    carta.paste(base,(g,g)); return carta

def generar_logica_4x4(baraja):
    uso=st.session_state["uso_global_4x4"]
    if not uso: uso={f:0 for f in baraja}; st.session_state["uso_global_4x4"]=uso
    for _ in range(3000):
        conteo={}; cartas=[[None]*16 for _ in range(4)]; pos_fig={}; ok=True
        base54=baraja.copy(); random.shuffle(base54)
        huecos=[3,3,2,2]; random.shuffle(huecos)
        huecos_carta=[set(random.sample(range(16),h)) for h in huecos]
        idx=0
        for c in range(4):
            for pos in range(16):
                if pos in huecos_carta[c]: continue
                fig=base54[idx]; cartas[c][pos]=fig; pos_fig[fig]=pos_fig.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda=baraja.copy(); random.shuffle(segunda); segunda.sort(key=lambda x:(uso.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas[c] if f])
            for pos in huecos_carta[c]:
                cand=[f for f in segunda if f not in usados and conteo.get(f,0)<2 and pos not in pos_fig.get(f,set())]
                if not cand: cand=[f for f in baraja if f not in usados and conteo.get(f,0)<2]
                if not cand: ok=False; break
                eleg=cand[0]; cartas[c][pos]=eleg; pos_fig[eleg]=pos_fig.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok: break
        if not ok: continue
        if not no_chocan(cartas[0],cartas[1],RIGHT4,LEFT4): continue
        if not no_chocan(cartas[0],cartas[2],BOTTOM4,TOP4): continue
        if not no_chocan(cartas[1],cartas[3],BOTTOM4,TOP4): continue
        if not no_chocan(cartas[2],cartas[3],RIGHT4,LEFT4): continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items(): uso[f]=uso.get(f,0)+cnt
        st.session_state["uso_global_4x4"]=uso; return cartas
    return None

def generar_hoja_4x4(cartas_data, color, div, sep_v, sep_h, g, asp, final_size=None, W_orig=2500):
    cw_tmp=((W_orig-sep_v)//2 - g*2 - 3*div)//4; ch_tmp=int(cw_tmp*asp); card_h=ch_tmp*4+div*3+g*2
    H_orig=card_h*2+sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color)
    for idx,d16 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_4x4(d16,cw,ch,div,g,asp),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet

def crear_carta_5x5(data25, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno; carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*4)//5; ch=int(cw*aspecto); th=ch*5+DIV*4; y0=(fh-th)//2
    for idx in range(min(25,len(data25))):
        r=idx//5; c=idx%5; x0=c*(cw+DIV); y0f=y0 + r*(ch+DIV)
        try: im=Image.open(data25[idx]).convert("RGB").resize((cw,ch), Image.LANCZOS); base.paste(im,(x0,y0f))
        except: pass
    carta.paste(base,(G,G)); return carta

def generar_logica_5x5(baraja_files):
    uso=st.session_state["uso_global_5x5"]
    if not uso: uso={f:0 for f in baraja_files}; st.session_state["uso_global_5x5"]=uso
    for _ in range(5000):
        conteo={}; cartas_data=[[None]*25 for _ in range(4)]; pos_por_figura={}; ok=True
        base54=baraja_files.copy(); random.shuffle(base54)
        huecos=[11,11,12,12]; random.shuffle(huecos)
        huecos_por_carta=[set(random.sample(range(25), huecos[c])) for c in range(4)]
        idx=0
        for c in range(4):
            for pos in range(25):
                if pos in huecos_por_carta[c]: continue
                fig=base54[idx]; cartas_data[c][pos]=fig; pos_por_figura[fig]=pos_por_figura.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda_lista=baraja_files.copy(); random.shuffle(segunda_lista); segunda_lista.sort(key=lambda x:(uso.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas_data[c] if f is not None])
            for pos in huecos_por_carta[c]:
                base=[f for f in segunda_lista if f not in usados and conteo.get(f,0)<2 and pos not in pos_por_figura.get(f,set())]
                if not base: base=[f for f in baraja_files if f not in usados and conteo.get(f,0)<2]
                if not base: ok=False; break
                eleg=base[0]; cartas_data[c][pos]=eleg; pos_por_figura[eleg]=pos_por_figura.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok: break
        if not ok: continue
        if not no_chocan(cartas_data[0], cartas_data[1], RIGHT5, LEFT5): continue
        if not no_chocan(cartas_data[0], cartas_data[2], BOTTOM5, TOP5): continue
        if not no_chocan(cartas_data[1], cartas_data[3], BOTTOM5, TOP5): continue
        if not no_chocan(cartas_data[2], cartas_data[3], RIGHT5, LEFT5): continue
        if len(pos_por_figura) < 54: continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items(): uso[f]=uso.get(f,0)+cnt
        st.session_state["uso_global_5x5"]=uso; return cartas_data
    return None

def generar_hoja_5x5(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, final_size=None, W_orig=3500):
    cw_tmp=((W_orig-sep_v)//2 - g_negro*2 - 4*div_interno)//5; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*5 + div_interno*4 + g_negro*2
    H_orig=card_h_real*2 + sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d25 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_5x5(d25, cw, ch, div_interno, g_negro, aspecto),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet

def crear_carta_imagen_16(data16, card_w=1000, div_interno=8, sample_aspect=1.45):
    cell_w=card_w//4; cell_h=int(cell_w*sample_aspect)
    img=Image.new("RGB",(card_w, cell_h*4),"black")
    target_w=cell_w-div_interno; target_h=cell_h-div_interno
    for idx,ruta in enumerate(data16):
        try:
            im=Image.open(ruta).convert("RGB")
            iw,ih=im.size; scale=max(target_w/iw, target_h/ih)
            nw,nh=int(iw*scale), int(ih*scale)
            im=im.resize((nw,nh), Image.LANCZOS)
            left=(nw-target_w)//2; top=(nh-target_h)//2
            im=im.crop((left,top,left+target_w,top+target_h))
        except: im=Image.new("RGB",(target_w,target_h),"white")
        col=idx%4; row=idx//4; x=col*cell_w+div_interno//2; y=row*cell_h+div_interno//2
        img.paste(im,(x,y))
    return img

def generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_cover_path, favorita_baraja_path, color_entre, div_interno, sep_entre):
    try:
        with Image.open(baraja_files[0]) as s: asp=s.size[1]/s.size[0]
    except: asp=1.45
    card_w=1000; card_h=int(card_w*asp)
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
    for _ in range(2000):
        posiciones_fav=random.sample(range(16),12)
        random.shuffle(otros); pool=[]
        for f in otros[:21]: pool.extend([f]*4)
        for f in otros[21:]: pool.extend([f]*3)
        random.shuffle(pool)
        pool_idx=0; cartas_data=[]; ok=True
        for idx_carta in range(12):
            fav_pos=posiciones_fav[idx_carta]; carta_ok=False
            for _ in range(60):
                top=[None]*16; top[fav_pos]=favorita_baraja_path
                usados=set([favorita_baraja_path]); temp_idx=pool_idx; temp_pool=pool[:]; fail=False
                for pos in range(16):
                    if top[pos] is not None: continue
                    encontrado=False
                    for k in range(temp_idx, len(temp_pool)):
                        if temp_pool[k] not in usados:
                            top[pos]=temp_pool[k]; usados.add(temp_pool[k])
                            temp_pool[k], temp_pool[temp_idx]=temp_pool[temp_idx], temp_pool[k]
                            temp_idx+=1; encontrado=True; break
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
            imc=Image.open(portada_cover_path).convert("RGB")
            tw=2*card_w+sep_entre; th=2*card_h+sep_entre; sc=max(tw/imc.size[0], th/imc.size[1])
            imc=imc.resize((int(imc.size[0]*sc), int(imc.size[1]*sc)), Image.LANCZOS)
            imc=imc.crop(((imc.size[0]-tw)//2, (imc.size[1]-th)//2, (imc.size[0]-tw)//2+tw, (imc.size[1]-th)//2+th))
        except: imc=Image.new("RGB",(2*card_w+sep_entre, 2*card_h+sep_entre),"gold")
        sheet.paste(imc,(0,0))
        for idx,data16 in enumerate(cartas_data):
            r,c=grid_pos[idx]
            if r<2 and c<2: continue
            x=c*(card_w+sep_entre); y=r*(card_h+sep_entre)
            sheet.paste(crear_carta_imagen_16(data16, card_w=card_w, div_interno=div_interno, sample_aspect=asp),(x,y))
        return sheet
    return None

def limpiar_nombre(path_img, idx):
    raw=os.path.splitext(os.path.basename(path_img))[0]
    clean=raw.replace("_"," ").replace("-"," ").strip().upper()
    clean=' '.join([w for w in clean.split() if not w.isdigit()]).strip()
    if not clean: clean=f"CARTA {idx}"
    return clean

# CATALOGO
if st.session_state.vista=="catalogo":
    st.markdown(banner_top("CATALOGO LOTERIA ELIUD PRO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.markdown(instrucciones_html("catalogo"), unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        if os.path.exists("portadas/portada_4x4.jpg"): st.image("portadas/portada_4x4.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 4x4 sencillas (sin dobles)")
        st.info("Planillas de 4 cartas 4x4 sencillas sin dobles y siempre las 54 por hoja.")
        st.caption(f"👀 {get_contador('visita_4x4')} visitas | 🎰 {get_contador('4x4')} usos")
        if st.button("🎰 ENTRAR A 4x4", use_container_width=True, type="primary"): ir_a("4x4")
    with c2:
        if os.path.exists("portadas/portada_5x5.jpg"): st.image("portadas/portada_5x5.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 5x5 sencillas (sin dobles)")
        st.info("Planillas de 4 cartas 5x5 sencillas, ideal para letra grande.")
        st.caption(f"👀 {get_contador('visita_5x5')} visitas | 🎰 {get_contador('5x5')} usos")
        if st.button("🎰 ENTRAR A 5x5", use_container_width=True): ir_a("5x5")
    with c3:
        if os.path.exists("portadas/1-portada-12-cartas.jpg"): st.image("portadas/1-portada-12-cartas.jpg", use_container_width=True)
        st.markdown("### 12 CARTAS CON 1 PORTADA")
        st.info("1 hoja TABLOIDE con 12 cartas + portada con 1 imagen preferida en grande.")
        st.caption(f"👀 {get_contador('visita_12portada')} visitas | 🎰 {get_contador('12portada')} usos")
        if st.button("🎰 ENTRAR A 12 CON PORTADA", use_container_width=True): ir_a("12portada")
    st.stop()

# ===== 4x4 CON VISTA PREVIA Y SUBIDA =====
if st.session_state.vista=="4x4":
    registrar_entrada_generador("4x4")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 4 CARTAS 4X4"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_4x4')} visitas | 🎰 {get_contador('4x4')} usos")
    st.markdown(instrucciones_html("4x4"), unsafe_allow_html=True)
    barajas=listar_barajas()
    col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("¿De dónde sacar baraja?", ["Integrada","Subir ZIP (54 fotos)","Subir Fotos Sueltas (54)"], key="modo4")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel4")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel)
        elif "ZIP" in modo:
            up=st.file_uploader("Sube tu ZIP con 54 imágenes", type=["zip"], key="zip4")
            if up: files=cargar_zip_temporal(up, "/tmp/baraja4", 54); st.success(f"✅ {len(files)} imágenes cargadas")
        else:
            ups=st.file_uploader("Sube tus 54 fotos (puedes seleccionar varias)", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs4")
            if ups: files=cargar_imagenes_sueltas(ups, "/tmp/baraja4s", 54); st.success(f"✅ {len(files)} imágenes cargadas")
        if files: st.caption(f"Tienes {len(files)} imágenes listas")
        div=st.number_input("Div - Separación dentro de carta", value=1, key="div4")
        sep_v=st.number_input("Sep V - Separación vertical entre cartas", value=20, key="sepv4")
        sep_h=st.number_input("Sep H - Separación horizontal entre cartas", value=20, key="seph4")
        marco=st.number_input("Marco - Borde negro", value=2, key="marco4")
        color=st.color_picker("Color de fondo", "#FF00FF", key="color4")
        ancho=st.text_input("Ancho cm","21", key="ancho4"); alto=st.text_input("Alto cm","35", key="alto4"); dpi=st.text_input("DPI","300", key="dpi4")
        W_usar=2500; juegos=st.number_input("Cuántos juegos?", value=2, min_value=1, max_value=10, key="j4")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA - Ver 1 juego", use_container_width=True, key="prev4"):
                    with lock:
                        cartas=generar_logica_4x4(files)
                        if cartas:
                            orig=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_orig4"]=orig; st.session_state["prev_final4"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS 4x4", type="primary", use_container_width=True, key="gen4"):
                    inc_contador("4x4", 1); inc_contador("4x4_juegos", juegos)
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
                st.markdown("### 👁️ VISTA PREVIA")
                st.image(st.session_state["prev_final4"], caption="Vista previa - Así se va a imprimir", use_container_width=True)
            if "lista_final4" in st.session_state and st.session_state["lista_final4"]:
                finales=st.session_state["lista_final4"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4"]
                st.markdown(f"### ✅ {len(finales)} Juegos Generados")
                for i,im in enumerate(finales): st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)} 4x4", pdf_bytes.getvalue(), f"loteria_4x4_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)} 4x4", zip_bytes.getvalue(), f"loteria_4x4_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()

# ===== 5x5 CON VISTA PREVIA Y SUBIDA =====
if st.session_state.vista=="5x5":
    registrar_entrada_generador("5x5")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 5x5 4 CARTAS"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_5x5')} visitas | 🎰 {get_contador('5x5')} usos")
    st.markdown(instrucciones_html("5x5 GRANDE"), unsafe_allow_html=True)
    barajas=listar_barajas()
    col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("¿De dónde sacar baraja?", ["Integrada","Subir ZIP (54 fotos)","Subir Fotos Sueltas (54)"], key="modo5")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel5")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel)
        elif "ZIP" in modo:
            up=st.file_uploader("Sube tu ZIP con 54 imágenes", type=["zip"], key="zip5")
            if up: files=cargar_zip_temporal(up, "/tmp/baraja5", 54); st.success(f"✅ {len(files)} imágenes")
        else:
            ups=st.file_uploader("Sube tus 54 fotos", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs5")
            if ups: files=cargar_imagenes_sueltas(ups, "/tmp/baraja5s", 54); st.success(f"✅ {len(files)} imágenes")
        div=st.number_input("Div - Separación dentro de carta", value=1, key="div5")
        sep_v=st.number_input("Sep V - Separación vertical", value=20, key="sepv5")
        sep_h=st.number_input("Sep H - Separación horizontal", value=20, key="seph5")
        marco=st.number_input("Marco - Borde negro", value=2, key="marco5")
        color=st.color_picker("Color de fondo", "#FF00FF", key="color5")
        ancho=st.text_input("Ancho cm","21", key="ancho5"); alto=st.text_input("Alto cm","35", key="alto5"); dpi=st.text_input("DPI","300", key="dpi5")
        W_usar=3500; juegos=st.number_input("Cuántos juegos?", value=1, min_value=1, max_value=10, key="j5")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out5")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA - Ver 1 juego", use_container_width=True, key="prev5"):
                    with lock:
                        cartas=generar_logica_5x5(files)
                        if cartas:
                            orig=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final5"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS 5x5", type="primary", use_container_width=True, key="gen5"):
                    inc_contador("5x5", 1); inc_contador("5x5_juegos", juegos)
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
                st.markdown("### 👁️ VISTA PREVIA")
                st.image(st.session_state["prev_final5"], caption="Vista previa", use_container_width=True)
            if "lista_final5" in st.session_state and st.session_state["lista_final5"]:
                finales=st.session_state["lista_final5"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig5"]
                st.markdown(f"### ✅ {len(finales)} Juegos")
                for i,im in enumerate(finales): st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_5x5_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)} 5x5", pdf_bytes.getvalue(), f"loteria_5x5_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)} 5x5", zip_bytes.getvalue(), f"loteria_5x5_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()

# 12 PORTADA - igual que antes
if st.session_state.vista=="12portada":
    registrar_entrada_generador("12portada")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 12 CARTAS CON PORTADA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_12portada')} | 🎰 {get_contador('12portada')}")
    st.markdown(instrucciones_html("12 CON PORTADA"), unsafe_allow_html=True)
    barajas=listar_barajas()
    col1,col2=st.columns([1,2.5])
    with col1:
        st.markdown("### 1) BARAJAS")
        modo_baraja=st.radio("Fuente", ["INCLUIDAS","IMPORTADAS ZIP"], key="fuente12")
        baraja_files=[]; portada_files=[]; baraja_nombre="baraja"; portada_nombre="portada"
        if modo_baraja=="INCLUIDAS":
            if barajas:
                sel_b=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel_b_12")
                path_b=[p for p in barajas if os.path.basename(p)==sel_b][0]
                baraja_files=cargar_files(path_b,54); baraja_nombre=sel_b
            if os.path.exists("portadas"):
                port_dirs=[os.path.join("portadas",d) for d in os.listdir("portadas") if os.path.isdir(os.path.join("portadas",d))]
                if port_dirs:
                    sel_p=st.selectbox("Portada", [os.path.basename(p) for p in port_dirs], key="sel_p_12")
                    path_p=[p for p in port_dirs if os.path.basename(p)==sel_p][0]
                    portada_files=cargar_files(path_p,54); portada_nombre=sel_p
                else:
                    port_files=cargar_files("portadas",54)
                    if port_files: portada_files=port_files; portada_nombre="portadas"
        else:
            zb=st.file_uploader("ZIP Baraja 54", type=["zip"], key="zip_b_12")
            if zb: baraja_files=cargar_zip_temporal(zb, "/tmp/baraja12", 54)
            zp=st.file_uploader("ZIP Portada 54", type=["zip"], key="zip_p_12")
            if zp: portada_files=cargar_zip_temporal(zp, "/tmp/portada12", 54)
        modo_gen=st.radio("Modo", ["UNA - Solo 1 hoja (elegir #)","TODAS - 54 hojas"], key="modo_gen_12")
        num_fav=st.number_input("Número favorita (1-54)", value=46, min_value=1, max_value=54, key="num_fav_12")
        lista_excel=[f"{k:02d} - {v}" for k,v in EXCEL_COLORS.items()]
        sel_excel=st.selectbox("Color Excel", lista_excel, index=2, key="excel_12")
        hex_excel=EXCEL_COLORS.get(int(sel_excel.split("-")[0].strip()), "#FF0000")
        color_entre=st.color_picker("Color HEX", hex_excel, key="color_12")
        div_interno=st.number_input("Div. interna - separación dentro de carta", value=8, key="div_12")
        sep_entre=st.number_input("Sep. entre cartas - espacio entre cartas", value=40, key="sep_12")
        ancho=st.text_input("Ancho cm tabloide","28", key="ancho12"); alto=st.text_input("Alto cm tabloide","43", key="alto12"); dpi=st.text_input("DPI","300", key="dpi12")
    with col2:
        if baraja_files and portada_files:
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁 VISTA PREVIA", use_container_width=True, key="prev12"):
                    with lock:
                        idx=max(0,min(num_fav-1, min(len(baraja_files),len(portada_files))-1))
                        sheet=generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_files[idx], baraja_files[idx], color_entre, div_interno, sep_entre)
                        if sheet:
                            st.session_state["orig12"]=sheet
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            st.session_state["final12"]=sheet.resize((Wf,Hf), Image.LANCZOS)
                            st.session_state["fav_actual"]=idx
            with cgen:
                if st.button("🖼 EXPORTAR TABLOIDE", type="primary", use_container_width=True, key="gen12"):
                    inc_contador("12portada", 1)
                    with lock:
                        lista_final=[]; lista_nombres=[]; bar=st.progress(0)
                        if "UNA" in modo_gen:
                            idx=max(0,min(num_fav-1, min(len(baraja_files),len(portada_files))-1))
                            lista=[(portada_files[idx], baraja_files[idx])]
                        else:
                            n=min(len(baraja_files), len(portada_files),54)
                            lista=[(portada_files[i], baraja_files[i]) for i in range(n)]
                        for i,(cover_path,fav_path) in enumerate(lista,1):
                            sheet=generar_tabloide_12_con_portada_PULIDO(baraja_files, cover_path, fav_path, color_entre, div_interno, sep_entre)
                            if not sheet: continue
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=sheet.resize((Wf,Hf), Image.LANCZOS)
                            lista_final.append(final); lista_nombres.append(limpiar_nombre(fav_path,i))
                            bar.progress(i/len(lista))
                        st.session_state["lista_final12"]=lista_final; st.session_state["lista_nombres12"]=lista_nombres
            if "orig12" in st.session_state:
                st.image(st.session_state["orig12"], caption=f"ORIGINAL Preview #{st.session_state.get('fav_actual',0)+1}", use_container_width=True)
                st.image(st.session_state["final12"], caption="RESIZE Preview", use_container_width=True)
            if "lista_final12" in st.session_state and st.session_state["lista_final12"]:
                finales=st.session_state["lista_final12"]; nombres=st.session_state["lista_nombres12"]
                for i,im in enumerate(finales): st.image(im, caption=f"{i+1:02d} - {nombres[i]}", use_container_width=True)
                pdf_bytes=io.BytesIO()
                if len(finales)==1: finales[0].save(pdf_bytes, format="PDF", resolution=300, quality=95)
                else: finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], resolution=300, quality=95)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    fecha=datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    for i,im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=95, dpi=(300,300))
                        zf.writestr(f"{i+1:02d} - {nombres[i]} - {fecha}.jpg", b.getvalue())
                d1,d2=st.columns(2)
                with d1: st.download_button(f"⬇️ PDF TABLOIDE {len(finales)} HOJAS", pdf_bytes.getvalue(), f"TABLOIDE_12_{len(finales)}_{baraja_nombre}_{portada_nombre}.pdf", "application/pdf", use_container_width=True, type="primary")
                with d2: st.download_button(f"⬇️ ZIP JPG {len(finales)} HOJAS", zip_bytes.getvalue(), f"JPG_TABLOIDE_12_{len(finales)}.zip", "application/zip", use_container_width=True)
        else: st.warning("Selecciona baraja (54) y portada (54) para activar preview")
    st.stop()
