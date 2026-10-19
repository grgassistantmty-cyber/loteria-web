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
def get_ranking_barajas():
    patron = str(BASE_PATH / "contador_baraja_*.txt")
    files = [f for f in glob.glob(patron) if not any(f.endswith(f"_{x}.txt") for x in ["4x4","5x5","10dobles","12portada","4x4doblesfix"])]
    ranking=[]
    for fp in files:
        try:
            nombre = os.path.basename(fp).replace("contador_baraja_","").replace(".txt","").replace("_"," ")
            cnt = safe_int(open(fp,"r", encoding="utf-8", errors="ignore").read())
            ranking.append((nombre,cnt))
        except: pass
    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking[:15]
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
if "vista" in params and params["vista"] in ["catalogo","4x4","5x5","12portada","10dobles","4x4doblesfix"]:
    st.session_state["vista"]=params["vista"]
def ir_a(v): st.session_state["vista"]=v; st.query_params["vista"]=v; st.rerun()
EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}

# === GENERADOR 6 - 1-PORT-10-CART-DC - INDEPENDIENTE ===
CARTAS_UNICAS_GLOBAL_1P10 = set()
USADOS_POS_1P10 = {}

def crear_carta_1p10(data16, card_w=600, card_h=850, div_interno=1):
    from PIL import Image
    cell_w=card_w//4; cell_h=card_h//4
    img=Image.new("RGB",(card_w,card_h), "black")
    for idx, ruta in enumerate(data16):
        try:
            im=Image.open(ruta).convert("RGB").resize((cell_w-div_interno, cell_h-div_interno), Image.LANCZOS)
        except:
            im=Image.new("RGB",(cell_w-div_interno, cell_h-div_interno),"white")
        col=idx%4; row=idx//4
        img.paste(im,(col*cell_w + div_interno//2, row*cell_h + div_interno//2))
    return img

def pos_pref_variadas_1p10():
    import random
    orilla=[0,1,2,3,4,7,8,11,12,13,14,15]
    random.shuffle(orilla)
    pos=[9,10]+orilla[:8]
    random.shuffle(pos)
    return pos

def buscar_eq_1p10(portada_path, baraja_files):
    import os
    base=os.path.splitext(os.path.basename(portada_path))[0].lower()
    for ff in baraja_files:
        if os.path.splitext(os.path.basename(ff))[0].lower()==base:
            return ff
    return None

def crear_panel_1p10(portada_path, w, h, color_fondo, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom):
    from PIL import Image, ImageDraw, ImageFont
    panel=Image.new("RGB",(w,h), color_fondo)
    draw=ImageDraw.Draw(panel)
    try:
        font_num=ImageFont.truetype("arialbd.ttf", font_num_size)
        font_txt=ImageFont.truetype("arialbd.ttf", font_txt_size)
    except:
        font_num=ImageFont.load_default()
        font_txt=ImageFont.load_default()
    top_h=int(h*0.14); bottom_h=int(h*0.14)
    middle_h=h-top_h-bottom_h
    try:
        with Image.open(portada_path) as orig:
            img=orig.convert("RGB")
            w_target=w-8
            ratio=w_target / img.width
            h_target=int(img.height * ratio)
            if h_target > middle_h-16:
                h_target=middle_h-16
                ratio2=h_target / orig.height
                w_target=int(orig.width * ratio2)
                w_target=min(w_target, w-8)
            img=img.resize((w_target, h_target), Image.LANCZOS)
            panel.paste(img,((w - w_target)//2, top_h + (middle_h - h_target)//2))
    except:
        pass
    draw.text((w//2, top_h*0.28 + offset_top), "1", fill="white", anchor="mm", font=font_num, stroke_width=3, stroke_fill="black")
    draw.text((w//2, top_h*0.72 + offset_top), txt_pref, fill="white", anchor="mm", font=font_txt, stroke_width=2, stroke_fill="black")
    draw.text((w//2, h-bottom_h + bottom_h*0.28 - offset_bottom), "10", fill="white", anchor="mm", font=font_num, stroke_width=3, stroke_fill="black")
    draw.text((w//2, h-bottom_h + bottom_h*0.72 - offset_bottom), txt_cartas, fill="white", anchor="mm", font=font_txt, stroke_width=2, stroke_fill="black")
    return panel

def generar_1p10_balanceado(baraja_files, preferida_portada_path, color_entre, div_interno, sep_entre, orientacion, dups_de_esta_hoja, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom):
    global CARTAS_UNICAS_GLOBAL_1P10, USADOS_POS_1P10
    import random, os
    from PIL import Image
    CW,CH=600,850
    ori=orientacion.upper()
    if "10X1" in ori: cols,rows=10,1
    elif "1X10" in ori: cols,rows=1,10
    elif "5X2" in ori: cols,rows=5,2
    else: cols,rows=2,5
    W=cols*CW+(cols-1)*sep_entre; H=rows*CH+(rows-1)*sep_entre
    pref_baraja=buscar_eq_1p10(preferida_portada_path, baraja_files) or random.choice(baraja_files)
    pref_name=os.path.splitext(os.path.basename(pref_baraja))[0].lower()
    baraja_filtrada=[ff for ff in baraja_files if os.path.splitext(os.path.basename(ff))[0].lower()!=pref_name] or baraja_files
    dups_filtrados=[d for d in dups_de_esta_hoja if os.path.splitext(os.path.basename(d))[0].lower()!=pref_name]
    while len(dups_filtrados)<10:
        cand=[ff for ff in baraja_filtrada if ff not in dups_filtrados]
        if not cand: break
        dups_filtrados.append(random.choice(cand))
    posiciones_preferida=pos_pref_variadas_1p10()
    dups_nombres=[os.path.splitext(os.path.basename(d))[0].lower() for d in dups_filtrados]
    USADOS_POS_1P10={i:set() for i in range(16)}
    plan_extra={i:[] for i in range(10)}
    for idx_origen in range(10):
        destinos=[j for j in range(10) if j!=idx_origen]
        random.shuffle(destinos)
        for dest in destinos:
            if len(plan_extra[dest])<1:
                plan_extra[dest].append(dups_filtrados[idx_origen]); break
    conteo_hoja={nom:2 for nom in dups_nombres}
    cartas_data=[]
    for idx_carta in range(10):
        dup=dups_filtrados[idx_carta]; dup_name=dups_nombres[idx_carta]
        while True:
            top=[None]*16; top[5]=dup; top[6]=dup
            top[posiciones_preferida[idx_carta]]=pref_baraja
            usados=set([dup, pref_baraja]); usados_nombres=set([dup_name, pref_name])
            for extra_path in plan_extra[idx_carta]:
                extra_nom=os.path.splitext(os.path.basename(extra_path))[0].lower()
                if extra_nom in usados_nombres: continue
                libres=[p for p in range(16) if top[p] is None and p not in (5,6,9,10)]
                random.shuffle(libres)
                for p in libres:
                    if extra_path not in USADOS_POS_1P10[p] and conteo_hoja.get(extra_nom,0)<3:
                        top[p]=extra_path; usados.add(extra_path); usados_nombres.add(extra_nom); break
            ok=True
            for pos in range(16):
                if top[pos] is not None: continue
                candidatos=[ff for ff in baraja_filtrada if ff not in usados and os.path.splitext(os.path.basename(ff))[0].lower() not in usados_nombres and ff not in USADOS_POS_1P10[pos] and conteo_hoja.get(os.path.splitext(os.path.basename(ff))[0].lower(),0)<3]
                if not candidatos: candidatos=[ff for ff in baraja_filtrada if ff not in usados]
                if not candidatos: ok=False; break
                elegido=random.choice(candidatos); top[pos]=elegido; usados.add(elegido); usados_nombres.add(os.path.splitext(os.path.basename(elegido))[0].lower())
            if not ok: continue
            nombres_top=[os.path.splitext(os.path.basename(ff))[0].lower() for ff in top]
            if len(set(nombres_top))!=15: continue
            firma=frozenset(nombres_top)
            if firma in CARTAS_UNICAS_GLOBAL_1P10: continue
            CARTAS_UNICAS_GLOBAL_1P10.add(firma)
            for p,ff in enumerate(top): USADOS_POS_1P10[p].add(ff)
            for n in set(nombres_top):
                if n!=dup_name: conteo_hoja[n]=conteo_hoja.get(n,0)+1
            cartas_data.append(top); break
    tablero=Image.new("RGB",(W,H), color_entre)
    for idx,data16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols
        tablero.paste(crear_carta_1p10(data16, CW, CH, div_interno),(col*(CW+sep_entre), row*(CH+sep_entre)))
    panel=crear_panel_1p10(preferida_portada_path, CW, H, color_entre, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom)
    sheet_final=Image.new("RGB",(CW+sep_entre+W, H), color_entre)
    sheet_final.paste(panel,(0,0)); sheet_final.paste(tablero,(CW+sep_entre,0))
    return sheet_final, conteo_hoja, cartas_data
def pagina_1port_10cart_dc():
    import streamlit as st, io, zipfile, random, os
    from pathlib import Path
    st.markdown("## GENERADOR 6 - 1 Portada + 10 Cartas Doble Centro")
    st.markdown('<div style="background:#fffbe6;border:3px solid #FF00FF;padding:15px;border-radius:10px;color:black">Logica independiente: doble al centro pos 5,6 - 15 diferentes por carta - sin repetidos por posicion - preferida variada - panel izq 600</div><br>', unsafe_allow_html=True)
    if st.button("Reiniciar contadores 1P10DC"):
        CARTAS_UNICAS_GLOBAL_1P10.clear()
        st.success("Reiniciado")
    col1,col2,col3 = st.columns(3)
    barajas = listar_barajas() if 'listar_barajas' in globals() else []
    portadas = listar_portadas_files() if 'listar_portadas_files' in globals() else []
    with col1:
        sel_baraja = st.selectbox("Baraja", barajas, key="sel_baraja_1p10")
        up_zip_baraja = st.file_uploader("Subir baraja ZIP", type=["zip"], key="up_baraja_1p10")
        up_imgs_baraja = st.file_uploader("Subir imagenes sueltas", accept_multiple_files=True, type=["png","jpg","jpeg","webp"], key="up_imgs_baraja_1p10")
    with col2:
        sel_portada = st.selectbox("Portada carpeta", portadas, key="sel_portada_1p10")
        up_zip_portada = st.file_uploader("Subir portadas ZIP", type=["zip"], key="up_portada_1p10")
    with col3:
        ori = st.selectbox("Orientacion", ["2x5 VERTICAL","5x2 HORIZONTAL","HORIZONTAL (10x1)","VERTICAL (1x10)"], index=1, key="ori_1p10")
        color_fondo = st.color_picker("Color fondo", "#FF00FF", key="color_1p10")
        div = st.slider("Divisor interno", 0, 20, 1, key="div_1p10")
        sep = st.slider("Separacion", 0, 200, 50, key="sep_1p10")
    c4,c5 = st.columns(2)
    with c4:
        font_num = st.slider("Tam Num 1 y 10", 20, 200, 72, key="fontnum_1p10")
        txt_pref = st.text_input("Texto arriba", "PREFERIDA", key="txtpref_1p10")
        offset_top = st.slider("Offset top", -100, 100, 0, key="offtop_1p10")
    with c5:
        font_txt = st.slider("Tam Texto", 10, 120, 48, key="fonttxt_1p10")
        txt_cartas = st.text_input("Texto abajo", "CARTAS", key="txtcartas_1p10")
        offset_bottom = st.slider("Offset bottom", -100, 100, 0, key="offbot_1p10")
    tmp_baraja = Path("tmp_baraja_1p10"); tmp_baraja.mkdir(exist_ok=True)
    baraja_files = []
    if up_zip_baraja:
        for ff in tmp_baraja.glob("*"): 
            try: ff.unlink()
            except: pass
        with zipfile.ZipFile(up_zip_baraja) as zz:
            for name in zz.namelist():
                if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                    (tmp_baraja / os.path.basename(name)).write_bytes(zz.read(name))
        baraja_files = cargar_files(str(tmp_baraja)) if 'cargar_files' in globals() else []
    elif up_imgs_baraja:
        for ff in tmp_baraja.glob("*"): 
            try: ff.unlink()
            except: pass
        for uf in up_imgs_baraja:
            (tmp_baraja / uf.name).write_bytes(uf.getbuffer())
        baraja_files = cargar_files(str(tmp_baraja)) if 'cargar_files' in globals() else []
    else:
        baraja_files = cargar_files(sel_baraja) if 'cargar_files' in globals() else []
    tmp_portada = Path("tmp_portada_1p10"); tmp_portada.mkdir(exist_ok=True)
    portada_files = []
    if up_zip_portada:
        for ff in tmp_portada.glob("*"): 
            try: ff.unlink()
            except: pass
        with zipfile.ZipFile(up_zip_portada) as zz:
            for name in zz.namelist():
                if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                    (tmp_portada / os.path.basename(name)).write_bytes(zz.read(name))
        portada_files = cargar_files(str(tmp_portada)) if 'cargar_files' in globals() else []
    else:
        portada_files = cargar_files(sel_portada) if 'cargar_files' in globals() else []
    if not baraja_files:
        st.warning("No hay baraja")
        return
    if not portada_files:
        st.warning("No hay portadas")
        return
    sel_portada_file = st.selectbox("Elige portada preferida", portada_files, format_func=lambda x: os.path.basename(str(x)), key="pref_file_1p10")
    if st.button("VISTA PREVIA", type="primary", key="preview_1p10"):
        dups = random.sample(baraja_files, min(10, len(baraja_files)))
        sheet, conteo, _ = generar_1p10_balanceado([str(x) for x in baraja_files], str(sel_portada_file), color_fondo, div, sep, ori, [str(x) for x in dups], font_num, font_txt, txt_pref.upper(), txt_cartas.upper(), offset_top, offset_bottom)
        st.session_state["last_sheet_1p10"]=sheet
        st.image(sheet, caption="Vista previa", use_container_width=True)
    if "last_sheet_1p10" in st.session_state:
        sheet = st.session_state["last_sheet_1p10"]
        buf = io.BytesIO()
        sheet.save(buf, format="JPEG", quality=95)
        st.download_button("Descargar JPG", buf.getvalue(), file_name="1-port-10-cart-dc.jpg", mime="image/jpeg", key="dl_jpg_1p10")
        buf_pdf = io.BytesIO()
        sheet.convert("RGB").save(buf_pdf, format="PDF")
        st.download_button("Descargar PDF", buf_pdf.getvalue(), file_name="1-port-10-cart-dc.pdf", mime="application/pdf", key="dl_pdf_1p10")
    num_hojas = st.number_input("Cuantas hojas", 1, 20, 1, key="numhojas_1p10")
    if st.button("GENERAR ZIP", key="gen_full_1p10"):
        sheets=[]
        for h in range(num_hojas):
            dups = random.sample(baraja_files, min(10, len(baraja_files)))
            sheet, conteo, _ = generar_1p10_balanceado([str(x) for x in baraja_files], str(random.choice(portada_files)), color_fondo, div, sep, ori, [str(x) for x in dups], font_num, font_txt, txt_pref.upper(), txt_cartas.upper(), offset_top, offset_bottom)
            sheets.append(sheet)
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i,s in enumerate(sheets):
                b=io.BytesIO()
                s.save(b, format="JPEG", quality=95)
                zf.writestr(f"hoja_{i+1}.jpg", b.getvalue())
        st.download_button("Descargar ZIP", zip_buf.getvalue(), file_name="1-port-10-cart-dc.zip", mime="application/zip", key="dl_zip_1p10")

def copiar_clabe_component():
    components.html("""<div style="text-align:center; margin-top:10px"><input id="clabe" value="728969000164073671" style="position:absolute; left:-9999px;"><button onclick="navigator.clipboard.writeText(document.getElementById('clabe').value); document.getElementById('msg').innerHTML='✅ ¡Copiada!';" style="background:gold; color:black; border:none; padding:12px 22px; border-radius:25px; font-weight:bold; cursor:pointer; font-size:17px;">📋 COPIAR CLABE - PICA AQUÍ</button><div id="msg" style="color:green; font-weight:bold; margin-top:8px;"></div></div>""", height=90)
def banner_top(titulo):
    return f"""<style>.banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}} .ws{{background:#25D366;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px}} .fb{{background:#1877F2;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px;margin-top:10px}} .contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px;font-size:18px}} .contador2{{background:#111;color:#ffd700;padding:8px 14px;border-radius:10px;font-weight:bold;display:inline-block;margin-top:8px;font-size:14px;border:1px solid gold}} .apoyo{{background:linear-gradient(180deg,#fffbe6,#ffe27a);border:3px solid #ffb700;padding:18px;border-radius:14px;margin-top:16px;color:#222;text-align:center;line-height:1.7}}</style><div class="banner"><h1>🎰 {titulo} 🎰</h1><h3>Creado por: Eliud Monsivais - WhatsApp 8115566250</h3><a class="ws" href="https://wa.me/528115566250">📲 WHATSAPP 8115566250</a><br><a class="fb" href="https://www.facebook.com/groups/1646464953556819" target="_blank">🔵 UNIRME AL GRUPO DE FACEBOOK</a><br><span class="contador">👁️ Visitas: {visitas_total}</span><br><span class="contador2">📊 USOS | 4x4: 👀{get_contador('visita_4x4')}/🎰{get_contador('4x4')} | 5x5: 👀{get_contador('visita_5x5')}/🎰{get_contador('5x5')} | 10C: 👀{get_contador('visita_10dobles')}/🎰{get_contador('10dobles')} | 12: 👀{get_contador('visita_12portada')}/🎰{get_contador('12portada')} | 4x4DOB FIX: 👀{get_contador('visita_4x4doblesfix')}/🎰{get_contador('4x4doblesfix')}</span><div class="apoyo">💖 <b style="font-size:20px">¿TE GUSTÓ MI TRABAJO? ¡APÓYAME VOLUNTARIAMENTE!</b> 💖<br>Esta página es <b>100% GRATIS</b>, pero a mí me cuesta <b>pagar el servidor cada mes</b>.<br>Si te sirvió y quieres apoyarme con <b>$5, $10, $20, $50, $100 pesitos</b>, te lo agradezco muchísimo 🙏<br><b>BANCO: SPIN by OXXO</b><br><span style="font-size:22px; background:black; color:gold; padding:8px 14px; border-radius:8px;">CLABE: 728969000164073671</span><br>A nombre de: <b>Eliud Monsivais</b><br></div></div><br>"""
def banner_facebook(): return """<div style="background:#e7f3ff; border:3px solid #1877F2; border-radius:14px; padding:18px; text-align:center; margin-bottom:15px"><h3 style="color:#1877F2; margin:0">🔵 ¡ÚNETE A MI GRUPO DE FACEBOOK!</h3><p style="color:black; font-size:17px;">Aquí subo <b>barajas nuevas GRATIS</b> y te ayudo con dudas.</p><a href="https://www.facebook.com/groups/1646464953556819" target="_blank" style="background:#1877F2; color:white; padding:14px 32px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; font-size:19px">👉 ENTRAR AL GRUPO</a></div>"""
def banner_venta_offline(): return """<div style="background:linear-gradient(90deg,#000,#4b0000); border:3px solid gold; border-radius:16px; padding:20px; text-align:center; color:white; margin:20px 0"><h2 style="color:gold; margin:0">💻 ¿QUIERES USARLO SIN INTERNET Y SIN LÍMITES?</h2><p style="font-size:18px; line-height:1.6; margin:12px 0">Si te interesa alguno de los generadores para usarlo desde la <b>comodidad de tu casa, sin necesidad de internet</b>,<br> sin límite de juegos y sin límite de PDFs, con todas tus barajas guardadas...<br><br><b style="color:#25D366; font-size:20px">¡CONTÁCTANOS POR WHATSAPP O POR EL GRUPO DE FACEBOOK QUE ESTÁ ARRIBA!</b></p><a href="https://wa.me/528115566250" style="background:#25D366; color:white; padding:14px 32px; border-radius:30px; text-decoration:none; font-weight:bold; font-size:20px; display:inline-block">📲 PEDIR INFORMES DE VERSIÓN SIN LÍMITES</a></div>"""
def instrucciones_html(vista="general"):
    if vista=="catalogo": return """<div style="background:#fffbe6;border:3px dashed #ffaa00;padding:20px;border-radius:14px;color:black; font-size:18px"><h2 style="text-align:center">📋 CÓMO USAR</h2><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid green; margin-bottom:10px"><b>1) 4x4 - 16 figuras:</b> 4 cartas por hoja.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid blue; margin-bottom:10px"><b>2) 5x5 - 25 figuras:</b> 4 cartas por hoja.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid gold;"><b>3) 10 Cartas 4x4 con Dobles - 54 por Hoja (3x -2):</b> 10 cartas por hoja, layout 5x2 / 2x5, ciclos 6 hojas.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid #cc0000;"><b>4) 12 CON PORTADA:</b> Tabloide 12 cartas + portada.</div><div style="background:white; padding:12px; border-radius:10px; border-left:6px solid purple;"><b>5) 4x4 DOBLES AL CENTRO FIX - 54 DOBLES:</b> 4 cartas por hoja, dobles en pos 6 y 7, 14 hojas = ciclo completo, sin huecos rosas, marco parejo 4 lados, con PDF.</div></div><br>"""
    else: return f"""<div style="background:#fffbe6;border:2px solid #ffaa00;padding:18px;border-radius:14px;color:black; font-size:17px"><h3>💡 PARA QUÉ ES CADA COSA - {vista}</h3><b>📁 Baraja:</b> Elige tus dibujos.<br><b>🎨 Div:</b> Grosor línea blanca DENTRO de la carta.<br><b>↔️ Sep V / Sep H:</b> Espacio ENTRE las cartas.<br><b>⬛ Marco:</b> Borde negro.<br><b>🎨 Color:</b> Fondo hoja.<br><br><b>👁️ Primero VISTA PREVIA, luego GENERAR y DESCARGAR</b></div><br>"""
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
        for f in os.listdir(carpeta_tmp):
            try: os.remove(os.path.join(carpeta_tmp,f))
            except: pass
        with zipfile.ZipFile(uploaded_zip) as zz:
            for name in zz.namelist():
                if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                    open(os.path.join(carpeta_tmp, os.path.basename(name)),"wb").write(zz.read(name))
        return cargar_files(carpeta_tmp, limite)
    except: return []
def cargar_imagenes_sueltas(uploaded_files, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp):
            try: os.remove(os.path.join(carpeta_tmp,f))
            except: pass
        for uf in uploaded_files[:limite]:
            open(os.path.join(carpeta_tmp, uf.name),"wb").write(uf.getbuffer())
        return cargar_files(carpeta_tmp, limite)
    except: return []
def cm_to_px(cm,dpi):
    try: return int(float(cm)/2.54*int(dpi))
    except: return 800
def get_aspecto(files):
    asp=[]
    for p in files[:10]:
        try:
            with Image.open(p) as im: asp.append(im.size[1]/im.size[0])
        except: pass
    return sum(asp)/len(asp) if asp else 1.42
def no_chocan(a,b,la,lb):
    for i,j in zip(la,lb):
        if a[i] is None or b[j] is None: continue
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
        try:
            with Image.open(data16[i]) as im: base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x,y))
        except: pass
    carta.paste(base,(g,g)); return carta
def generar_logica_4x4(baraja):
    uso=st.session_state["uso_global_4x4"]
    if not uso: uso={f:0 for f in baraja}; st.session_state["uso_global_4x4"]=uso
    for _ in range(2500):
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
def generar_hoja_4x4(cartas_data, color, div, sep_v, sep_h, g, asp, final_size=None, W_orig=1800):
    cw_tmp=((W_orig-sep_v)//2 - g*2 - 3*div)//4; ch_tmp=int(cw_tmp*asp); card_h=ch_tmp*4+div*3+g*2
    H_orig=card_h*2+sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color)
    for idx,d16 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_4x4(d16,cw,ch,div,g,asp),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet
def crear_carta_5x5(data25, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*4)//5; ch=int(cw*aspecto); th=ch*5+DIV*4; y0=(fh-th)//2
    for idx in range(min(25,len(data25))):
        r=idx//5; c=idx%5; x0=c*(cw+DIV); y0f=y0 + r*(ch+DIV)
        try:
            with Image.open(data25[idx]) as im: base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x0,y0f))
        except: pass
    carta.paste(base,(G,G)); return carta
def generar_logica_5x5(baraja_files):
    uso=st.session_state["uso_global_5x5"]
    if not uso: uso={f:0 for f in baraja_files}; st.session_state["uso_global_5x5"]=uso
    for _ in range(2500):
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
def generar_hoja_5x5(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, final_size=None, W_orig=2000):
    cw_tmp=((W_orig-sep_v)//2 - g_negro*2 - 4*div_interno)//5; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*5 + div_interno*4 + g_negro*2
    H_orig=card_h_real*2 + sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d25 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_5x5(d25, cw, ch, div_interno, g_negro, aspecto),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
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
            with Image.open(data16[idx]) as im: im2=im.convert("RGB").resize((cw,ch), Image.LANCZOS); celda.paste(im2,(0,0))
        except: pass
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
        for idx in range(10): cartas_data[idx][5]=dups_10[idx]; cartas_data[idx][6]=dups_10[idx]
        ok=True
        for i,d in enumerate(dups_10):
            posibles=[c for c in range(10) if c!=i]; random.shuffle(posibles); colocado=False
            for dest in posibles:
                if d in cartas_data[dest]: continue
                libres=[p for p in range(16) if cartas_data[dest][p] is None and p not in PROHIBIDAS]; random.shuffle(libres)
                for p in libres:
                    cartas_data[dest][p]=d
                    if dest>0 and dest%5!=0 and not no_chocan(cartas_data[dest-1], cartas_data[dest], RIGHT, LEFT): cartas_data[dest][p]=None; continue
                    if dest>=5 and not no_chocan(cartas_data[dest-5], cartas_data[dest], BOTTOM, TOP): cartas_data[dest][p]=None; continue
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
                    if cidx>0 and cidx%5!=0 and not no_chocan(cartas_data[cidx-1], cartas_data[cidx], RIGHT, LEFT): cartas_data[cidx][pos]=None; continue
                    if cidx>=5 and not no_chocan(cartas_data[cidx-5], cartas_data[cidx], BOTTOM, TOP): cartas_data[cidx][pos]=None; continue
                    ch=tuple(sorted([x for x in cartas_data[cidx] if x]))
                    if len(ch)==16 and ch in cartas_hash: cartas_data[cidx][pos]=None; continue
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
            with Image.open(data16[idx]) as im: im2=im.convert("RGB").resize((cw,ch), Image.LANCZOS); celda.paste(im2,(0,0))
        except: pass
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
            for i, pos in enumerate(pos_libres[:14]): top[pos]=restantes[i]
            for pos in range(16):
                if top[pos] is None: top[pos]=random.choice(restantes)
            cartas_data_hoja.append(top)
        hojas.append(cartas_data_hoja)
    return hojas, dobles_ciclo, repetidas
def generar_original_fijo_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout="2x2"):
    CARD_W = 1100; fw = CARD_W - g_negro*2; cw_cell = (fw - div_interno*3)//4; ch_cell = int(cw_cell * aspecto); CARD_H = ch_cell*4 + div_interno*3 + g_negro*2
    if layout=="1x4":
        W_orig = CARD_W*4 + sep_v*3; H_orig = CARD_H; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
        for idx,d16 in enumerate(cartas_data): x=idx*(CARD_W+sep_v); y=0; sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
    else:
        W_orig = CARD_W*2 + sep_v; H_orig = CARD_H*2 + sep_h; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
        for idx,d16 in enumerate(cartas_data): col=idx%2; row=idx//2; x=col*(CARD_W+sep_v); y=row*(CARD_H+sep_h); sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
    return sheet
def generar_con_resize_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, ancho_cm, alto_cm, dpi, aspecto, layout="2x2"):
    orig=generar_original_fijo_4x4dob(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
def imagenes_a_pdf_4x4dob(imagenes_pil):
    if not imagenes_pil: return None
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
        except: im=Image.new("RGB",(target_w,target_h),"white")
        col=idx%4; row=idx//4; x=col*cell_w+div_interno//2; y=row*cell_h+div_interno//2; img.paste(im,(x,y))
    return img
def generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_cover_path, favorita_baraja_path, color_entre, div_interno, sep_entre):
    try:
        with Image.open(baraja_files[0]) as s: asp=s.size[1]/s.size[0]
    except: asp=1.45
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
        except: imc=Image.new("RGB",(2*card_w+sep_entre, 2*card_h+sep_entre),"gold")
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
if st.session_state.vista=="catalogo":
    st.markdown(banner_top("CATALOGO LOTERIA ELIUD PRO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    st.markdown(instrucciones_html("catalogo"), unsafe_allow_html=True)
    ranking = get_ranking_barajas()
    if ranking:
        st.markdown("### 🏆 RANKING BARAJAS MÁS USADAS")
        html_rank = "<div style='background:white;border:2px solid gold;border-radius:12px;padding:12px;color:black'>"
        for i,(nom,cnt) in enumerate(ranking,1): html_rank += f"<div style='padding:6px;border-bottom:1px solid #eee'><b>{i}. {nom}</b> - {cnt} usos</div>"
        html_rank += "</div><br>"
        st.markdown(html_rank, unsafe_allow_html=True)
    st.markdown(banner_venta_offline(), unsafe_allow_html=True)
    c1,c2,c3,c4,c5=st.columns(5)
    with c1:
        if os.path.exists("portadas/portada_4x4.jpg"): st.image("portadas/portada_4x4.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 4x4 sencillas")
        st.caption(f"👀 {get_contador('visita_4x4')} | 🎰 {get_contador('4x4')}")
        if st.button("🎰 ENTRAR A 4x4", use_container_width=True, type="primary"): ir_a("4x4")
    with c2:
        if os.path.exists("portadas/portada_5x5.jpg"): st.image("portadas/portada_5x5.jpg", use_container_width=True)
        st.markdown("### 4 Cartas 5x5 sencillas")
        st.caption(f"👀 {get_contador('visita_5x5')} | 🎰 {get_contador('5x5')}")
        if st.button("🎰 ENTRAR A 5x5", use_container_width=True): ir_a("5x5")
    with c3:
        if os.path.exists("portadas/portada_10-4x4-dobles.jpg"): st.image("portadas/portada_10-4x4-dobles.jpg", use_container_width=True)
        st.markdown("### 10 Cartas 4x4 con Dobles - 54 por Hoja")
        st.caption(f"👀 {get_contador('visita_10dobles')} | 🎰 {get_contador('10dobles')}")
        if st.button("🎰 ENTRAR A 10 CARTAS DOBLES", use_container_width=True): ir_a("10dobles")
    with c4:
        if os.path.exists("portadas/1-portada-12-cartas.jpg"): st.image("portadas/1-portada-12-cartas.jpg", use_container_width=True)
        st.markdown("### 12 CARTAS CON 1 PORTADA")
        st.caption(f"👀 {get_contador('visita_12portada')} | 🎰 {get_contador('12portada')}")
        if st.button("🎰 ENTRAR A 12 CON PORTADA", use_container_width=True): ir_a("12portada")
    with c5:
        if os.path.exists("portadas/portada_4x4-dobles-al-centro.jpg"): st.image("portadas/portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        elif os.path.exists("portada_4x4-dobles-al-centro.jpg"): st.image("portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        st.markdown("### 🆕 4x4 DOBLES AL CENTRO - 54 DOBLES FIX")
        st.caption(f"👀 {get_contador('visita_4x4doblesfix')} | 🎰 {get_contador('4x4doblesfix')}")
        st.markdown("<span style='background:purple;color:white;padding:4px 8px;border-radius:10px;font-size:12px'>NUEVO - SIN HUECOS - PDF</span>", unsafe_allow_html=True)
        if st.button("🎰 ENTRAR A 4x4 DOBLES FIX", use_container_width=True, type="primary"): ir_a("4x4doblesfix")
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
if st.session_state.vista=="5x5":
    registrar_entrada_generador("5x5")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
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
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs5")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
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
            if "prev_final5" in st.session_state: st.image(st.session_state["prev_final5"], caption="Vista previa", use_container_width=True)
            if "lista_final5" in st.session_state and st.session_state["lista_final5"]:
                finales=st.session_state["lista_final5"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig5"]
                for i,im in enumerate(finales): st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_5x5_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"loteria_5x5_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"loteria_5x5_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="10dobles":
    registrar_entrada_generador("10dobles")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("10 Cartas 4x4 con Dobles - 54 por Hoja (3x -2)"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_10dobles')} | 🎰 {get_contador('10dobles')}")
    st.markdown(instrucciones_html("10 Cartas 4x4 con Dobles - 54 por Hoja (3x -2)"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo10")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel10")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip10")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs10")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        layout=st.selectbox("LAYOUT", ["5x2","2x5"], key="layout10")
        div=st.number_input("Div", value=1, key="div10"); sep_v=st.number_input("Sep V", value=40, key="sepv10"); sep_h=st.number_input("Sep H", value=40, key="seph10"); marco=st.number_input("Marco", value=4, key="marco10")
        color=st.color_picker("Color", "#FF00FF", key="color10")
        ancho=st.text_input("Ancho cm","54", key="ancho10"); alto=st.text_input("Alto cm","35", key="alto10"); dpi=st.text_input("DPI","300", key="dpi10")
        ciclos=st.number_input("Ciclos (1 ciclo=6 hojas)", value=1, min_value=1, max_value=10, key="ciclos10")
        st.info(f"💡 1 ciclo = 6 hojas para completar las 54 dobles. Aquí limitado a {ciclos} ciclo(s). ¿Necesitas más? Versión COMPLETA sin límites para PC disponible por WhatsApp.")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out10")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA 10C FULL", use_container_width=True, key="prev10"):
                    with lock:
                        st.session_state["uso_global_10"]={}; st.session_state["uso_como_dup_10"]={}; st.session_state["hash_10"]=set()
                        cartas,dups=generar_logica_10_cartas_54(files, es_nuevo_juego=True)
                        if cartas:
                            orig, final = generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                            st.session_state["prev_orig10"]=orig; st.session_state["prev_final10"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {ciclos} CICLOS - 54xHOJA", type="primary", use_container_width=True, key="gen10"):
                    inc_contador("10dobles", 1); inc_baraja(nombre_baraja, "10dobles")
                    with lock:
                        lista_final=[]; lista_orig=[]; st.session_state["uso_global_10"]={}; st.session_state["uso_como_dup_10"]={}; st.session_state["hash_10"]=set()
                        bar=st.progress(0); total_h = ciclos*6; cnt=0
                        for ciclo in range(1, ciclos+1):
                            st.session_state["uso_global_10"]={}; st.session_state["uso_como_dup_10"]={}; st.session_state["hash_10"]=set()
                            for h in range(1,7):
                                cartas,dups=generar_logica_10_cartas_54(files, es_nuevo_juego=(h==1))
                                if not cartas: continue
                                orig, final = generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                                lista_orig.append(orig); lista_final.append(final); cnt+=1; bar.progress(cnt/total_h)
                        st.session_state["lista_final10"]=lista_final; st.session_state["lista_orig10"]=lista_orig
            if "prev_final10" in st.session_state: st.image(st.session_state["prev_final10"], caption=f"Vista previa {layout} - 10C FULL 54xHOJA", use_container_width=True)
            if "lista_final10" in st.session_state and st.session_state["lista_final10"]:
                finales=st.session_state["lista_final10"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig10"]
                for i,im in enumerate(finales): st.image(im, caption=f"Hoja {i+1} - 10 Cartas", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=95); zf.writestr(f"10C_FULL_{layout}_H{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"10C_FULL_{layout}_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"10C_FULL_{layout}_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="12portada":
    registrar_entrada_generador("12portada")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 12 CARTAS CON PORTADA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_12portada')} | 🎰 {get_contador('12portada')}")
    st.markdown(instrucciones_html("12 CON PORTADA"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo_baraja=st.radio("Fuente", ["INCLUIDAS","IMPORTADAS ZIP"], key="fuente12")
        baraja_files=[]; portada_files=[]; baraja_nombre="baraja"; portada_nombre="portada"; nombre_baraja="Baraja_Personalizada"
        if modo_baraja=="INCLUIDAS":
            if barajas:
                sel_b=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel_b_12")
                path_b=[p for p in barajas if os.path.basename(p)==sel_b][0]
                baraja_files=cargar_files(path_b,54); baraja_nombre=sel_b; nombre_baraja=sel_b
            if os.path.exists("portadas"):
                port_dirs=[os.path.join("portadas",d) for d in os.listdir("portadas") if os.path.isdir(os.path.join("portadas",d))]
                if port_dirs:
                    sel_p=st.selectbox("Portada", [os.path.basename(p) for p in port_dirs], key="sel_p_12")
                    path_p=[p for p in port_dirs if os.path.basename(p)==sel_p][0]
                    portada_files=cargar_files(path_p,54); portada_nombre=sel_p
        else:
            zb=st.file_uploader("ZIP Baraja 54", type=["zip"], key="zip_b_12")
            if zb: baraja_files=cargar_zip_temporal(zb, tempfile.mkdtemp(), 54); nombre_baraja=zb.name
            zp=st.file_uploader("ZIP Portada 54", type=["zip"], key="zip_p_12")
            if zp: portada_files=cargar_zip_temporal(zp, tempfile.mkdtemp(), 54)
        modo_gen=st.radio("Modo", ["UNA - Solo 1 hoja","TODAS - 54 hojas"], key="modo_gen_12")
        st.info("💡 En modo GRATIS puedes generar 1 hoja o las 54 de un jalón. Si necesitas hacer cientos sin internet, tenemos la versión COMPLETA para computadora. ¡Pregunta por WhatsApp!")
        num_fav=st.number_input("Número favorita (1-54)", value=46, min_value=1, max_value=54, key="num_fav_12")
        lista_excel=[f"{k:02d} - {v}" for k,v in EXCEL_COLORS.items()]
        sel_excel=st.selectbox("Color Excel", lista_excel, index=2, key="excel_12")
        hex_excel=EXCEL_COLORS.get(int(sel_excel.split("-")[0].strip()), "#FF0000")
        color_entre=st.color_picker("Color HEX", hex_excel, key="color_12")
        div_interno=st.number_input("Div. interna", value=8, key="div_12")
        sep_entre=st.number_input("Sep. entre cartas", value=40, key="sep_12")
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
            with cgen:
                if st.button("🖼 EXPORTAR TABLOIDE", type="primary", use_container_width=True, key="gen12"):
                    inc_contador("12portada", 1); inc_baraja(nombre_baraja, "12portada")
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
            if "orig12" in st.session_state: st.image(st.session_state["final12"], caption="Vista previa - Alta Calidad Final", use_container_width=True)
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
                with d1: st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"TABLOIDE_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                with d2: st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"TABLOIDE_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="4x4doblesfix":
    registrar_entrada_generador("4x4doblesfix")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("🆕 4x4 DOBLES AL CENTRO - 54 DOBLES FIX"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_4x4doblesfix')} | 🎰 {get_contador('4x4doblesfix')}")
    st.markdown(instrucciones_html("4x4 DOBLES AL CENTRO FIX - 54 DOBLES"), unsafe_allow_html=True)
    if os.path.exists("portadas/portada_4x4-dobles-al-centro.jpg"): st.image("portadas/portada_4x4-dobles-al-centro.jpg", use_container_width=False)
    elif os.path.exists("portada_4x4-dobles-al-centro.jpg"): st.image("portada_4x4-dobles-al-centro.jpg", use_container_width=False)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo4dobfix")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel4dobfix")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip4dobfix")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        elif vista == "1port10cartdc":
    registrar_entrada_generador("1port10cartdc")
    pagina_1port_10cart_dc()

else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs4dobfix")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        st.divider()
        layout=st.selectbox("LAYOUT", ["2x2","1x4"], key="layout4dobfix")
        div=st.number_input("Div", value=1, key="div4dobfix"); sep_v=st.number_input("Sep V", value=80, key="sepv4dobfix"); sep_h=st.number_input("Sep H", value=80, key="seph4dobfix"); marco=st.number_input("Marco", value=6, key="marco4dobfix")
        color=st.color_picker("Color entre cartas", "#FF00FF", key="color4dobfix")
        ancho=st.text_input("Ancho cm (resize)","21", key="ancho4dobfix"); alto=st.text_input("Alto cm (resize)","28", key="alto4dobfix"); dpi=st.text_input("DPI","300", key="dpi4dobfix")
        st.info("💡 Limitado a 1 ciclo = 14 hojas. 54 dobles garantizadas + 2 repetidas. Fix sin huecos rosas, marco parejo 4 lados. Con PDF + JPG + info_54_dobles.txt")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4dobfix")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA - 2 PREVIEWS", use_container_width=True, key="prev4dobfix"):
                    with lock:
                        hojas_ciclo, dobles, repetidas = generar_ciclo_54_dobles_4x4dob(files)
                        primera = hojas_ciclo[0]
                        orig, final = generar_con_resize_4x4dob(primera, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                        st.session_state["prev_orig4dobfix"]=orig; st.session_state["prev_final4dobfix"]=final
                        st.session_state["hojas4dobfix"]=hojas_ciclo; st.session_state["dobles4dobfix"]=dobles; st.session_state["repetidas4dobfix"]=repetidas
            with cgen:
                if st.button(f"🎰 GENERAR CICLO 14 HOJAS + PDF", type="primary", use_container_width=True, key="gen4dobfix"):
                    inc_contador("4x4doblesfix", 1); inc_baraja(nombre_baraja, "4x4doblesfix")
                    with lock:
                        hojas_ciclo, dobles, repetidas = generar_ciclo_54_dobles_4x4dob(files)
                        originales=[]; resizes=[]; bar=st.progress(0)
                        for idx, hoja in enumerate(hojas_ciclo,1):
                            o,f = generar_con_resize_4x4dob(hoja, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                            originales.append(o); resizes.append(f); bar.progress(idx/len(hojas_ciclo))
                        st.session_state["lista_orig4dobfix"]=originales; st.session_state["lista_final4dobfix"]=resizes
                        st.session_state["hojas4dobfix"]=hojas_ciclo; st.session_state["dobles4dobfix"]=dobles; st.session_state["repetidas4dobfix"]=repetidas
            if "prev_final4dobfix" in st.session_state:
                c1p,c2p=st.columns(2)
                with c1p: st.image(st.session_state["prev_orig4dobfix"], caption=f"1- ORIGINAL FIJO {st.session_state['prev_orig4dobfix'].size}", use_container_width=True)
                with c2p: st.image(st.session_state["prev_final4dobfix"], caption=f"2- RESIZE {st.session_state['prev_final4dobfix'].size}", use_container_width=True)
            if "lista_final4dobfix" in st.session_state and st.session_state["lista_final4dobfix"]:
                finales = st.session_state["lista_final4dobfix"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4dobfix"]
                for i,im in enumerate(finales): st.image(im, caption=f"Hoja {i+1}/14", use_container_width=True)
                pdf_orig = imagenes_a_pdf_4x4dob(st.session_state["lista_orig4dobfix"])
                pdf_res = imagenes_a_pdf_4x4dob(st.session_state["lista_final4dobfix"])
                lista_nombres = [os.path.basename(f) for f in st.session_state["dobles4dobfix"]]; rep_nombres = [os.path.basename(f) for f in st.session_state["repetidas4dobfix"]]
                unicas = sorted(set(lista_nombres)); fecha=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                info_text = f"""LOTERIA 4x4 DOBLES FIX - 54 DOBLES
Fecha: {fecha}
Layout: {layout}
Div {div} SepV {sep_v} SepH {sep_h} Marco {marco} Color {color}
Resize: {ancho}x{alto}cm {dpi}DPI - Sin huecos, marco parejo

REPETIDAS:
{chr(10).join([f"- {r}" for r in rep_nombres])}

56 DOBLES:
{chr(10).join([f"{i+1:02d}. {n}" for i,n in enumerate(lista_nombres)])}

54 UNICAS:
{chr(10).join([f"- {n}" for n in unicas])}
Total: {len(unicas)}/54
"""
                zip_buf=io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i,(o,r) in enumerate(zip(st.session_state["lista_orig4dobfix"], st.session_state["lista_final4dobfix"]),1):
                        bo=io.BytesIO(); o.save(bo, format="JPEG", quality=95); zf.writestr(f"JPG_ORIGINAL_H{i:02d}.jpg", bo.getvalue())
                        br=io.BytesIO(); r.save(br, format="JPEG", quality=95, dpi=(int(dpi),int(dpi))); zf.writestr(f"JPG_RESIZE_H{i:02d}.jpg", br.getvalue())
                    zf.writestr(f"PDF_ORIGINAL_{layout}_{fecha}.pdf", pdf_orig)
                    zf.writestr(f"PDF_RESIZE_{layout}_{fecha}.pdf", pdf_res)
                    zf.writestr("info_54_dobles.txt", info_text)
                c1d,c2d,c3d=st.columns(3)
                with c1d: st.download_button(f"📦 ZIP TODO", zip_buf.getvalue(), f"4x4DOBLES_FIX_{layout}_{fecha}.zip", "application/zip", use_container_width=True, type="primary")
                with c2d: st.download_button(f"📄 PDF ORIGINAL", pdf_orig, f"ORIGINAL_{layout}_{fecha}.pdf", "application/pdf", use_container_width=True)
                with c3d: st.download_button(f"📄 PDF RESIZE", pdf_res, f"RESIZE_{layout}_{fecha}.pdf", "application/pdf", use_container_width=True)
    st.stop()
