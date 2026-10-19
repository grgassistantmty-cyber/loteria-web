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
    files = [f for f in glob.glob(patron) if not any(f.endswith(f"_{x}.txt") for x in ["4x4","5x5","10dobles","12portada","4x4doblesfix"])]
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
params=st.query_params
if "vista" in params and params["vista"] in ["catalogo","4x4","5x5","12portada","10dobles","4x4doblesfix"]:
    st.session_state["vista"]=params["vista"]
def ir_a(v):
    st.session_state["vista"]=v
    st.query_params["vista"]=v
    st.rerun()
def copiar_clabe_component():
    components.html('<div style="text-align:center;"><button onclick="navigator.clipboard.writeText(\'728969000164073671\')" style="background:gold; color:black; border:none; padding:12px 22px; border-radius:25px; font-weight:bold; cursor:pointer;">COPIAR CLABE</button></div>', height=90)
def banner_top(titulo):
    return f"""<div style="background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold; margin-bottom:10px"><h1 style="margin:0">{titulo}</h1><h3 style="margin:5px 0">🎰 Eliud Monsivais - WhatsApp 8115566250</h3><p style="margin:0">Visitas totales: {visitas_total} | CLABE: 728969000164073671 - Eliud Monsivais</p></div><br>"""
banner_facebook = lambda: """<div style="background:#e7f3ff; border:3px solid #1877F2; border-radius:14px; padding:18px; text-align:center; margin-bottom:15px"><h3 style="color:#1877F2; margin:0">🔵 ¡ÚNETE A MI GRUPO DE FACEBOOK!</h3><p style="color:black; font-size:17px;">Aquí subo <b>barajas nuevas GRATIS</b> y te ayudo con dudas.</p><a href="https://www.facebook.com/groups/1646464953556819" target="_blank" style="background:#1877F2; color:white; padding:14px 32px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; font-size:19px">👉 ENTRAR AL GRUPO</a></div>"""
banner_venta_offline = lambda: """<div style="background:linear-gradient(90deg,#000000,#1a1a1a); border:3px solid gold; border-radius:16px; padding:20px; text-align:center; color:white; margin-bottom:15px"><h2 style="color:gold; margin:0">💾 ¿QUIERES USARLO SIN INTERNET?</h2><p style="font-size:16px;">¡Versión offline para tu PC!</p><a href="https://wa.me/528115566250?text=Hola%20Eliud%2C%20quiero%20la%20version%20offline" target="_blank" style="background:#25D366; color:white; padding:14px 32px; border-radius:30px; text-decoration:none; font-weight:bold; display:inline-block; font-size:18px">📲 PEDIR INFORMES POR WHATSAPP</a></div>"""
instrucciones_html = lambda vista="general": f"""<div style="background:#fffbe6; border:3px dashed #ffaa00; padding:20px; border-radius:14px; color:black; margin-bottom:15px"><h3 style="margin-top:0">📋 INSTRUCCIONES - MODO {vista.upper()}</h3><p><b>1)</b> Elige baraja o sube ZIP</p><p><b>2)</b> Configura colores y separaciones</p><p><b>3)</b> Dale en VISTA PREVIA y luego GENERAR</p><p style="color:red;"><b>¡Listo para imprimir!</b></p></div>""" if vista=="catalogo" else f"""<div style="background:#e6f7ff; border:2px solid #0099ff; padding:18px; border-radius:14px; color:black; margin-bottom:15px"><b>MODO ACTIVO: {vista.upper()}</b> - Sigue los pasos de la izquierda</div>"""
def listar_barajas():
    bases=["barajas","/data/barajas","portadas"]
    res=[]
    for b in bases:
        if os.path.exists(b):
            for d in os.listdir(b):
                fp=os.path.join(b,d)
                if os.path.isdir(fp):
                    imgs=[os.path.join(fp,f) for f in os.listdir(fp) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
                    if len(imgs)>=54:
                        res.append(fp)
    return res
def cargar_files(carpeta, min_needed=54):
    exts=(".jpg",".jpeg",".png",".webp")
    files=[os.path.join(carpeta,f) for f in os.listdir(carpeta) if f.lower().endswith(exts)]
    files=sorted(files)[:min_needed]
    return files
def cargar_zip_temporal(file_up, tmpdir, min_needed):
    with zipfile.ZipFile(file_up) as z:
        z.extractall(tmpdir)
    exts=(".jpg",".jpeg",".png",".webp")
    files=[]
    for root,_,fs in os.walk(tmpdir):
        for f in fs:
            if f.lower().endswith(exts):
                files.append(os.path.join(root,f))
    return sorted(files)[:min_needed]
def cargar_imagenes_sueltas(files_up, tmpdir, min_needed):
    os.makedirs(tmpdir, exist_ok=True)
    paths=[]
    for fu in files_up:
        p=os.path.join(tmpdir, fu.name)
        with open(p,"wb") as out:
            out.write(fu.getbuffer())
        paths.append(p)
    return sorted(paths)[:min_needed]
def get_aspecto(files):
    try:
        with Image.open(files[0]) as im:
            return im.size[0]/im.size[1] if im.size[1]!=0 else 1.0
    except:
        return 1.0
def cm_to_px(cm_str, dpi):
    try:
        return int(float(cm_str)*dpi/2.54)
    except:
        return int(28*dpi/2.54)
TOP4=0; RIGHT4=1; BOTTOM4=2; LEFT4=3
def no_chocan(data1, data2, lado1, lado2):
    opp={0:2, 1:3, 2:0, 3:1}
    if lado2!=opp[lado1]:
        return True
    if lado1==0:
        for c in range(4):
            if data1[c]==data2[12+c]:
                return False
    elif lado1==2:
        for c in range(4):
            if data1[12+c]==data2[c]:
                return False
    elif lado1==1:
        for r in range(4):
            if data1[r*4+3]==data2[r*4]:
                return False
    elif lado1==3:
        for r in range(4):
            if data1[r*4]==data2[r*4+3]:
                return False
    return True
def crear_carta_imagen_16(data16, card_w, div_interno, sample_aspect):
    card_h=int((card_w//4*sample_aspect+div_interno)*4+div_interno*4)
    cell_w=card_w//4; cell_h=int(cell_w*sample_aspect)
    carta=Image.new("RGB",(card_w, card_h),"black")
    for k,ruta in enumerate(data16):
        try:
            with Image.open(ruta) as im0:
                im=im0.convert("RGB").resize((cell_w-div_interno, cell_h-div_interno), Image.LANCZOS)
        except:
            im=Image.new("RGB",(cell_w-div_interno, cell_h-div_interno),"white")
        carta.paste(im,((k%4)*cell_w+div_interno//2, (k//4)*cell_h+div_interno//2))
    return carta
def generar_logica_4x4(baraja_files):
    for _ in range(500):
        pool=baraja_files[:]
        random.shuffle(pool)
        cartas=[]
        ok=True
        for _ in range(4):
            if len(pool)<16:
                ok=False; break
            data=pool[:16]
            pool=pool[16:]
            cartas.append(data)
        if ok:
            return cartas
    return None
def generar_hoja_4x4(cartas, color_entre, div_interno, sep_v, sep_h, marco, asp, target_size, W_usar):
    card_w=W_usar; card_h=int((card_w//4*asp+div_interno)*4+div_interno*4)
    W=2*card_w+sep_h+2*marco; H=2*card_h+sep_v+2*marco
    sheet=Image.new("RGB",(W,H), color_entre)
    for idx,data16 in enumerate(cartas):
        r=idx//2; c=idx%2
        x=marco+c*(card_w+sep_h); y=marco+r*(card_h+sep_v)
        sheet.paste(crear_carta_imagen_16(data16, card_w, div_interno, asp),(x,y))
    if target_size:
        sheet=sheet.resize(target_size, Image.LANCZOS)
    return sheet
def generar_logica_5x5(baraja_files):
    for _ in range(500):
        pool=baraja_files[:]
        random.shuffle(pool)
        cartas=[]
        ok=True
        for _ in range(2):
            if len(pool)<25:
                ok=False; break
            data=pool[:25]
            pool=pool[25:]
            cartas.append(data)
        if ok:
            return cartas
    return None
def crear_carta_imagen_25(data25, card_w, div_interno, sample_aspect):
    card_h=int((card_w//5*sample_aspect+div_interno)*5+div_interno*5)
    cell_w=card_w//5; cell_h=int(cell_w*sample_aspect)
    carta=Image.new("RGB",(card_w, card_h),"black")
    for k,ruta in enumerate(data25):
        try:
            with Image.open(ruta) as im0:
                im=im0.convert("RGB").resize((cell_w-div_interno, cell_h-div_interno), Image.LANCZOS)
        except:
            im=Image.new("RGB",(cell_w-div_interno, cell_h-div_interno),"white")
        carta.paste(im,((k%5)*cell_w+div_interno//2, (k//5)*cell_h+div_interno//2))
    return carta
def generar_hoja_5x5(cartas, color_entre, div_interno, sep_v, sep_h, marco, asp, target_size, W_usar):
    card_w=W_usar; card_h=int((card_w//5*asp+div_interno)*5+div_interno*5)
    W=2*card_w+sep_h+2*marco; H=1*card_h+2*marco
    if len(cartas)>2:
        W=2*card_w+sep_h+2*marco; H=2*card_h+sep_v+2*marco
    sheet=Image.new("RGB",(W,H), color_entre)
    for idx,data25 in enumerate(cartas):
        r=idx//2; c=idx%2
        x=marco+c*(card_w+sep_h); y=marco+r*(card_h+sep_v)
        sheet.paste(crear_carta_imagen_25(data25, card_w, div_interno, asp),(x,y))
    if target_size:
        sheet=sheet.resize(target_size, Image.LANCZOS)
    return sheet
def generar_logica_10_cartas_54(baraja_files, es_nuevo=False):
    if len(baraja_files)<54:
        return None, None
    cartas=[]
    for _ in range(10):
        pool=baraja_files[:]
        random.shuffle(pool)
        cartas.append(pool[:16])
    return cartas, None
def generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout):
    card_w=600; card_h=int(card_w*asp+div)
    if layout=="5x2":
        cols=5; rows=2
    else:
        cols=2; rows=5
    W=cols*card_w+(cols-1)*sep_h+2*marco
    H=rows*card_h+(rows-1)*sep_v+2*marco
    sheet=Image.new("RGB",(W,H), color)
    for idx,data16 in enumerate(cartas):
        r=idx//cols if layout=="5x2" else idx%rows
        c=idx%cols if layout=="5x2" else idx//rows
        x=marco+c*(card_w+sep_h); y=marco+r*(card_h+sep_v)
        sheet.paste(crear_carta_imagen_16(data16, card_w, div, asp),(x,y))
    Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
    final=sheet.resize((Wf,Hf), Image.LANCZOS)
    return sheet, final
CICLO_FIJO_4x4DOB=14
def generar_ciclo_54_dobles_4x4dob(baraja_files):
    if len(baraja_files)<54:
        return [], [], []
    dobles=[]
    for i in range(0,54,2):
        if i+1<54:
            dobles.append((baraja_files[i], baraja_files[i+1]))
    hojas=[]
    for _ in range(14):
        cartas=[]
        for _ in range(4):
            d=random.choice(dobles)
            pool=[f for f in baraja_files if f not in d]
            random.shuffle(pool)
            data=[None]*16
            data[5]=d[0]; data[6]=d[1]
            for k in range(16):
                if data[k] is None:
                    data[k]=pool.pop()
            cartas.append(data)
        hojas.append(cartas)
    return hojas, dobles, []
def generar_con_resize_4x4dob(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout):
    card_w=600; card_h=int(card_w*asp+div)
    cols=2; rows=2
    W=cols*card_w+(cols-1)*sep_h+2*marco
    H=rows*card_h+(rows-1)*sep_v+2*marco
    sheet=Image.new("RGB",(W,H), color)
    for idx,data16 in enumerate(cartas):
        r=idx//cols; c=idx%cols
        x=marco+c*(card_w+sep_h); y=marco+r*(card_h+sep_v)
        sheet.paste(crear_carta_imagen_16(data16, card_w, div, asp),(x,y))
    Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
    final=sheet.resize((Wf,Hf), Image.LANCZOS)
    return sheet, final
def imagenes_a_pdf_4x4dob(imgs):
    buf=io.BytesIO()
    if len(imgs)==1:
        imgs[0].save(buf, format="PDF")
    else:
        imgs[0].save(buf, format="PDF", save_all=True, append_images=imgs[1:])
    return buf.getvalue()
def generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_cover_path, favorita_baraja_path, color_entre, div_interno, sep_entre):
    card_w=1200; asp=get_aspecto(baraja_files); card_h=int((card_w//4*asp+div_interno)*4+div_interno*4)
    grid_pos=[(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(3,0)]
    vecinos={}
    for i,(r,c) in enumerate(grid_pos):
        lst=[]
        for j,(r2,c2) in enumerate(grid_pos):
            if i==j:
                continue
            if r==r2 and c==c2+1:
                lst.append((j,RIGHT4,LEFT4))
            if r==r2 and c==c2-1:
                lst.append((j,LEFT4,RIGHT4))
            if c==c2 and r==r2+1:
                lst.append((j,BOTTOM4,TOP4))
            if c==c2 and r==r2-1:
                lst.append((j,TOP4,BOTTOM4))
        vecinos[i]=lst
    otros=[f for f in baraja_files if f!=favorita_baraja_path][:53]
    for _ in range(1500):
        posiciones_fav=random.sample(range(16),12); random.shuffle(otros)
        pool=[]
        for f in otros[:21]:
            pool.extend([f]*4)
        for f in otros[21:]:
            pool.extend([f]*3)
        random.shuffle(pool); pool_idx=0; cartas_data=[]; ok=True
        for idx_carta in range(12):
            fav_pos=posiciones_fav[idx_carta]; carta_ok=False
            for _ in range(60):
                top=[None]*16; top[fav_pos]=favorita_baraja_path; usados=set([favorita_baraja_path]); temp_idx=pool_idx; temp_pool=pool[:]; fail=False
                for pos in range(16):
                    if top[pos] is not None:
                        continue
                    encontrado=False
                    for k in range(temp_idx, len(temp_pool)):
                        if temp_pool[k] not in usados:
                            top[pos]=temp_pool[k]; usados.add(temp_pool[k]); temp_pool[k], temp_pool[temp_idx]=temp_pool[temp_idx], temp_pool[k]; temp_idx+=1; encontrado=True; break
                    if not encontrado:
                        fail=True; break
                if fail:
                    continue
                choque=False
                for j,la,lb in vecinos[idx_carta]:
                    if j < len(cartas_data):
                        if not no_chocan(cartas_data[j], top, la, lb):
                            choque=True; break
                if choque:
                    continue
                pool=temp_pool; pool_idx=temp_idx; cartas_data.append(top); carta_ok=True; break
            if not carta_ok:
                ok=False; break
        if not ok:
            continue
        W=4*card_w+3*sep_entre; H=4*card_h+3*sep_entre; sheet=Image.new("RGB",(W,H), color_entre)
        try:
            with Image.open(portada_cover_path) as imc0:
                imc=imc0.convert("RGB"); tw=2*card_w+sep_entre; th=2*card_h+sep_entre; sc=max(tw/imc.size[0], th/imc.size[1])
                imc=imc.resize((int(imc.size[0]*sc), int(imc.size[1]*sc)), Image.LANCZOS)
                imc=imc.crop(((imc.size[0]-tw)//2, (imc.size[1]-th)//2, (imc.size[0]-tw)//2+tw, (imc.size[1]-th)//2+th))
        except:
            imc=Image.new("RGB",(2*card_w+sep_entre, 2*card_h+sep_entre),"gold")
        sheet.paste(imc,(0,0))
        for idx,data16 in enumerate(cartas_data):
            r,c=grid_pos[idx]
            if r<2 and c<2:
                continue
            x=c*(card_w+sep_entre); y=r*(card_h+sep_entre)
            sheet.paste(crear_carta_imagen_16(data16, card_w=card_w, div_interno=div_interno, sample_aspect=asp),(x,y))
        gc.collect(); return sheet
    return None
    if st.session_state.vista=="catalogo":
    st.markdown(banner_top("CATALOGO DE GENERADORES - LOTERIA ELIUD PRO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.markdown(instrucciones_html("catalogo"), unsafe_allow_html=True)
    st.markdown(banner_venta_offline(), unsafe_allow_html=True)
    ranking=get_ranking_barajas()
    if ranking:
        txt_r="RANKING BARAJAS MAS USADAS:<br>"
        for i,(nom,cnt) in enumerate(ranking,1):
            txt_r+=f"{i}. {nom}: {cnt} usos | "
        st.markdown(f'<div style="background:#111;color:gold;padding:12px;border-radius:10px;border:1px solid gold">{txt_r}</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5=st.columns(5)
    with c1:
        if os.path.exists("portadas/portada_4x4.jpg"):
            st.image("portadas/portada_4x4.jpg", use_container_width=True)
        st.markdown("### 1) 4x4 - 16 Figuras")
        if st.button("ENTRAR A 4x4 - 16", use_container_width=True):
            ir_a("4x4")
    with c2:
        if os.path.exists("portadas/portada_5x5.jpg"):
            st.image("portadas/portada_5x5.jpg", use_container_width=True)
        st.markdown("### 2) 5x5 - 25 Figuras")
        if st.button("ENTRAR A 5x5 - 25", use_container_width=True):
            ir_a("5x5")
    with c3:
        if os.path.exists("portadas/portada_10dobles.jpg"):
            st.image("portadas/portada_10dobles.jpg", use_container_width=True)
        st.markdown("### 3) 10 Cartas 4x4 con Dobles")
        if st.button("ENTRAR A 10 DOBLES", use_container_width=True):
            ir_a("10dobles")
    with c4:
        if os.path.exists("portadas/portada_12portada.jpg"):
            st.image("portadas/portada_12portada.jpg", use_container_width=True)
        st.markdown("### 4) 12 con Portada")
        if st.button("ENTRAR A 12 PORTADA", use_container_width=True):
            ir_a("12portada")
    with c5:
        if os.path.exists("portadas/portada_4x4-dobles-al-centro.jpg"):
            st.image("portadas/portada_4x4-dobles-al-centro.jpg", use_container_width=True)
        st.markdown("### 5) 4x4 DOBLES AL CENTRO FIX")
        if st.button("ENTRAR A 4x4 FIX", use_container_width=True):
            ir_a("4x4doblesfix")
    st.stop()
if st.session_state.vista=="4x4":
    registrar_entrada_generador("4x4")
    if st.button("Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 4x4 - 16 FIGURAS"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
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
        div=st.number_input("Div", value=2, key="div4"); sep_v=st.number_input("Sep V", value=20, key="sepv4"); sep_h=st.number_input("Sep H", value=20, key="seph4"); marco=st.number_input("Marco", value=2, key="marco4")
        color=st.color_picker("Color", "#FF00FF", key="color4")
        ancho=st.text_input("Ancho cm","28", key="ancho4"); alto=st.text_input("Alto cm","20", key="alto4"); dpi=st.text_input("DPI","300", key="dpi4")
        W_usar=st.number_input("Ancho pixeles original", value=1800, key="w4"); juegos=st.number_input("Cuantos juegos", value=4, min_value=1, max_value=20, key="juegos4")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("VISTA PREVIA", use_container_width=True, key="prev4"):
                    with lock:
                        cartas=generar_logica_4x4(files)
                        if cartas:
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final4"]=final
            with cgen:
                if st.button(f"GENERAR {juegos} JUEGOS", type="primary", use_container_width=True, key="gen4"):
                    inc_contador("4x4", 1); inc_baraja(nombre_baraja, "4x4")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0)
                        for j in range(juegos):
                            cartas=generar_logica_4x4(files)
                            if not cartas:
                                continue
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
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_4x4_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"PDF {len(finales)}", pdf_bytes.getvalue(), f"loteria_4x4_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"ZIP {len(finales)}", zip_bytes.getvalue(), f"loteria_4x4_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="5x5":
    registrar_entrada_generador("5x5")
    if st.button("Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 5x5 - 25 FIGURAS"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.markdown(instrucciones_html("5x5"), unsafe_allow_html=True)
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
        div=st.number_input("Div", value=2, key="div5"); sep_v=st.number_input("Sep V", value=20, key="sepv5"); sep_h=st.number_input("Sep H", value=20, key="seph5"); marco=st.number_input("Marco", value=2, key="marco5")
        color=st.color_picker("Color", "#FF00FF", key="color5")
        ancho=st.text_input("Ancho cm","28", key="ancho5"); alto=st.text_input("Alto cm","20", key="alto5"); dpi=st.text_input("DPI","300", key="dpi5")
        W_usar=st.number_input("Ancho pixeles original", value=2000, key="w5"); juegos=st.number_input("Cuantos juegos", value=4, min_value=1, max_value=20, key="juegos5")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out5")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("VISTA PREVIA", use_container_width=True, key="prev5"):
                    with lock:
                        cartas=generar_logica_5x5(files)
                        if cartas:
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final5"]=final
            with cgen:
                if st.button(f"GENERAR {juegos} JUEGOS", type="primary", use_container_width=True, key="gen5"):
                    inc_contador("5x5", 1); inc_baraja(nombre_baraja, "5x5")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0)
                        for j in range(juegos):
                            cartas=generar_logica_5x5(files)
                            if not cartas:
                                continue
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
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_5x5_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"PDF {len(finales)}", pdf_bytes.getvalue(), f"loteria_5x5_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"ZIP {len(finales)}", zip_bytes.getvalue(), f"loteria_5x5_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="10dobles":
    registrar_entrada_generador("10dobles")
    if st.button("Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("10 CARTAS 4x4 CON DOBLES - 54 POR HOJA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.markdown(instrucciones_html("10 dobles"), unsafe_allow_html=True)
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
            if up:
                files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs10")
            if ups:
                files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        div=st.number_input("Div", value=1, key="div10"); sep_v=st.number_input("Sep V", value=10, key="sepv10"); sep_h=st.number_input("Sep H", value=10, key="seph10"); marco=st.number_input("Marco", value=2, key="marco10")
        color=st.color_picker("Color", "#FF00FF", key="color10")
        ancho=st.text_input("Ancho cm","40", key="ancho10"); alto=st.text_input("Alto cm","28", key="alto10"); dpi=st.text_input("DPI","300", key="dpi10")
        layout=st.selectbox("Layout", ["5x2","2x5"], key="layout10")
        ciclos=st.number_input("Ciclos (1 ciclo=6 hojas)", value=1, min_value=1, max_value=5, key="ciclos10")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out10")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("VISTA PREVIA - 1 HOJA", use_container_width=True, key="prev10"):
                    with lock:
                        cartas, dups = generar_logica_10_cartas_54(files)
                        if cartas:
                            orig, final = generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                            st.session_state["prev_orig10"]=orig; st.session_state["prev_final10"]=final
            with cgen:
                if st.button(f"GENERAR {ciclos} CICLOS", type="primary", use_container_width=True, key="gen10"):
                    inc_contador("10dobles", 1); inc_baraja(nombre_baraja, "10dobles")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0); total=ciclos*6; cnt=0
                        for ciclo in range(ciclos):
                            for h in range(6):
                                cartas, dups = generar_logica_10_cartas_54(files, es_nuevo=(ciclo==0 and h==0))
                                if not cartas:
                                    continue
                                orig, final = generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                                lista_orig.append(orig); lista_final.append(final); cnt+=1; bar.progress(cnt/total)
                        st.session_state["lista_final10"]=lista_final; st.session_state["lista_orig10"]=lista_orig
            if "prev_final10" in st.session_state:
                st.image(st.session_state["prev_final10"], caption="Vista previa 10 cartas", use_container_width=True)
            if "lista_final10" in st.session_state and st.session_state["lista_final10"]:
                finales=st.session_state["lista_final10"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig10"]
                for i,im in enumerate(finales):
                    st.image(im, caption=f"Hoja {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"10dobles_H{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"PDF {len(finales)}", pdf_bytes.getvalue(), f"10dobles_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"ZIP {len(finales)}", zip_bytes.getvalue(), f"10dobles_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="12portada":
    registrar_entrada_generador("12portada")
    if st.button("Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("TABLOIDE 12 CARTAS + PORTADA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    barajas=listar_barajas(); port_dirs=[os.path.join("portadas",d) for d in os.listdir("portadas") if os.path.isdir(os.path.join("portadas",d))] if os.path.exists("portadas") else []
    col1,col2=st.columns([1,2.5])
    with col1:
        sel_b=st.selectbox("BARAJA", [os.path.basename(p) for p in barajas], key="sel_b_12") if barajas else None
        sel_p=st.selectbox("PORTADA", [os.path.basename(p) for p in port_dirs], key="sel_p_12") if port_dirs else None
        color=st.color_picker("Color", "#FF00FF", key="color12"); div=st.number_input("Div", value=2, key="div12"); sep=st.number_input("Sep", value=20, key="sep12")
    with col2:
        if sel_b and sel_p:
            path_b=[p for p in barajas if os.path.basename(p)==sel_b][0]
            path_p=[p for p in port_dirs if os.path.basename(p)==sel_p][0]
            files_b=cargar_files(path_b,54)
            port_files=cargar_files(path_p,1)
            if files_b and port_files:
                if st.button("VISTA PREVIA 12", use_container_width=True, key="prev12"):
                    fav=random.choice(files_b); hoja=generar_tabloide_12_con_portada_PULIDO(files_b, port_files[0], fav, color, div, sep)
                    if hoja:
                        st.session_state["prev12"]=hoja
                if st.button("GENERAR 54 HOJAS", type="primary", use_container_width=True, key="gen12"):
                    inc_contador("12portada",1); prog=st.progress(0); imgs=[]
                    for i in range(54):
                        fav=files_b[i % len(files_b)]; h=generar_tabloide_12_con_portada_PULIDO(files_b, port_files[i % len(port_files)], fav, color, div, sep)
                        if h:
                            imgs.append(h); prog.progress((i+1)/54)
                    st.session_state["lista12"]=imgs
            if "prev12" in st.session_state:
                st.image(st.session_state["prev12"], caption="Vista previa 12", use_container_width=True)
            if "lista12" in st.session_state and st.session_state["lista12"]:
                for im in st.session_state["lista12"]:
                    st.image(im, use_container_width=True)
                zbuf=io.BytesIO()
                with zipfile.ZipFile(zbuf,"w",zipfile.ZIP_DEFLATED) as zf:
                    for i,im in enumerate(st.session_state["lista12"]):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"12portada_{i+1:02d}.jpg", b.getvalue())
                pbuf=io.BytesIO(); st.session_state["lista12"][0].save(pbuf, format="PDF", save_all=True, append_images=st.session_state["lista12"][1:])
                st.download_button("PDF 54", pbuf.getvalue(), f"12portada_54.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button("ZIP 54", zbuf.getvalue(), f"12portada_54.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="4x4doblesfix":
    registrar_entrada_generador("4x4doblesfix")
    if st.button("Volver al Catalogo"):
        ir_a("catalogo")
    st.markdown(banner_top("4x4 DOBLES AL CENTRO FIX - 54 DOBLES - 14 HOJAS = CICLO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
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
            if up:
                files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs4dobfix")
            if ups:
                files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        layout=st.selectbox("LAYOUT", ["2x2","1x4"], key="layout4dobfix")
        div=st.number_input("Div", value=1, key="div4dobfix"); sep_v=st.number_input("Sep V", value=20, key="sepv4dobfix"); sep_h=st.number_input("Sep H", value=20, key="seph4dobfix"); marco=st.number_input("Marco", value=2, key="marco4dobfix")
        color=st.color_picker("Color", "#FF00FF", key="color4dobfix")
        ancho=st.text_input("Ancho cm","28", key="ancho4dobfix"); alto=st.text_input("Alto cm","20", key="alto4dobfix"); dpi=st.text_input("DPI","300", key="dpi4dobfix")
        ciclos=st.number_input("Ciclos (1 ciclo=14 hojas = 54 dobles)", value=1, min_value=1, max_value=5, key="ciclos4dobfix")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4dobfix")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("VISTA PREVIA 4x4 DOBLES FIX", use_container_width=True, key="prev4dobfix"):
                    with lock:
                        hojas, dobles, rep = generar_ciclo_54_dobles_4x4dob(files)
                        cartas=hojas[0]
                        orig, final = generar_con_resize_4x4dob(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                        st.session_state["prev_orig4dobfix"]=orig; st.session_state["prev_final4dobfix"]=final
            with cgen:
                if st.button(f"GENERAR {ciclos} CICLOS", type="primary", use_container_width=True, key="gen4dobfix"):
                    inc_contador("4x4doblesfix", 1); inc_baraja(nombre_baraja, "4x4doblesfix")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0); total=ciclos*CICLO_FIJO_4x4DOB; cnt=0
                        for ciclo in range(ciclos):
                            hojas, dobles, rep = generar_ciclo_54_dobles_4x4dob(files)
                            for h in hojas:
                                orig, final = generar_con_resize_4x4dob(h, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                                lista_orig.append(orig); lista_final.append(final); cnt+=1; bar.progress(cnt/total)
                        st.session_state["lista_final4dobfix"]=lista_final; st.session_state["lista_orig4dobfix"]=lista_orig
            if "prev_final4dobfix" in st.session_state:
                st.image(st.session_state["prev_final4dobfix"], caption="Vista previa FIX", use_container_width=True)
            if "lista_final4dobfix" in st.session_state and st.session_state["lista_final4dobfix"]:
                finales=st.session_state["lista_final4dobfix"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4dobfix"]
                for i,im in enumerate(finales):
                    st.image(im, caption=f"Hoja {i+1}", use_container_width=True)
                pdf_bytes=imagenes_a_pdf_4x4dob(finales)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=95); zf.writestr(f"4x4DOBFIX_H{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"PDF {len(finales)}", pdf_bytes, f"4x4DOBFIX_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"ZIP {len(finales)}", zip_bytes.getvalue(), f"4x4DOBFIX_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
