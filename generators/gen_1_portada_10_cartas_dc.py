import os, random, io, zipfile, gc
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

try:
    from app import BASE_PATH, EXCEL_COLORS, get_contador, inc_contador, inc_baraja, banner_top, banner_facebook, banner_venta_offline, copiar_clabe_component, instrucciones_html, ir_a, listar_barajas
except:
    BASE_PATH = Path(".")
    EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}
    def get_contador(n): return 0
    def inc_contador(n,c=1): return 0
    def inc_baraja(a,b): pass
    def banner_top(t): return f"<h1>{t}</h1>"
    def banner_facebook(): return ""
    def banner_venta_offline(): return ""
    def copiar_clabe_component(): pass
    def instrucciones_html(v=""): return ""
    def ir_a(v): st.session_state["vista"]=v; st.rerun()
    def listar_barajas():
        if not os.path.exists("barajas"): return []
        return sorted([os.path.join("barajas",d) for d in os.listdir("barajas") if os.path.isdir(os.path.join("barajas",d))])

# === FIJOS - MEJOR POSICION ===
FONT_NUM_FIJO = 151
FONT_TXT_FIJO = 91
TXT_PREF_FIJO = "PREFERIDA"
TXT_CARTAS_FIJO = "CARTAS"
OFFSET_TOP_FIJO = 100
OFFSET_BOTTOM_FIJO = 100

CARTAS_UNICAS_GLOBAL_JUEGO = set()
USADOS_POR_POSICION_HOJA = {}

def cargar_fuente(tam):
    posibles = [
        "arialbd.ttf", "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"
    ]
    for f in posibles:
        try:
            return ImageFont.truetype(f, tam)
        except:
            continue
    return ImageFont.load_default()

def cargar_imagenes(carpeta):
    if not os.path.exists(carpeta): return []
    files=[os.path.join(carpeta,f) for f in os.listdir(carpeta) if f.lower().endswith((".png",".jpg",".jpeg",".webp"))]
    files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))) or 0))
    return files

def crear_carta_imagen_rectangular(data16, card_w=600, card_h=850, div_interno=1, fast=False):
    cell_w=card_w//4; cell_h=card_h//4
    img=Image.new("RGB",(card_w,card_h), "black")
    thumb_size = cell_w-div_interno if not fast else 120
    for idx, ruta in enumerate(data16):
        try:
            im=Image.open(ruta).convert("RGB")
            if fast:
                im.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
                im = im.resize((cell_w-div_interno, cell_h-div_interno), Image.LANCZOS)
            else:
                im = im.resize((cell_w-div_interno, cell_h-div_interno), Image.LANCZOS)
        except:
            im=Image.new("RGB",(cell_w-div_interno, cell_h-div_interno),"white")
        col=idx%4; row=idx//4
        x=col*cell_w + div_interno//2; y=row*cell_h + div_interno//2
        img.paste(im,(x,y))
    return img

def posiciones_preferida_variadas_por_hoja():
    orilla=[0,1,2,3,4,7,8,11,12,13,14,15]
    random.shuffle(orilla)
    pos=[9,10]+orilla[:8]
    random.shuffle(pos)
    return pos

def buscar_equivalente_baraja(portada_path, baraja_files):
    base=os.path.splitext(os.path.basename(portada_path))[0].lower()
    for f in baraja_files:
        if os.path.splitext(os.path.basename(f))[0].lower()==base:
            return f
    return None

def crear_panel_con_texto_editable(portada_path, w, h, color_fondo, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom, fast=False):
    panel=Image.new("RGB",(w,h), color_fondo)
    draw=ImageDraw.Draw(panel)
    font_num = cargar_fuente(font_num_size)
    font_txt = cargar_fuente(font_txt_size)
    top_h=int(h*0.14); bottom_h=int(h*0.14)
    middle_h=h-top_h-bottom_h
    try:
        img_pref=Image.open(portada_path).convert("RGB")
        if fast:
            img_pref.thumbnail((400, 500), Image.LANCZOS)
        elif img_pref.width > 600 or img_pref.height > 750:
            img_pref.thumbnail((600, 750), Image.LANCZOS)
        w_target=w-8
        ratio=w_target / img_pref.width
        h_target=int(img_pref.height * ratio)
        if h_target > middle_h-16:
            h_target=middle_h-16
            w_target=int(img_pref.width * h_target / img_pref.height)
            w_target=min(w_target, w-8)
            img_pref=img_pref.resize((w_target, h_target), Image.LANCZOS)
        else:
            img_pref=img_pref.resize((w_target, h_target), Image.LANCZOS)
        x=(w - w_target)//2
        y=top_h + (middle_h - h_target)//2
        panel.paste(img_pref,(x,y))
    except:
        pass
    draw.text((w//2, top_h*0.28 + offset_top), "1", fill="white", anchor="mm", font=font_num, stroke_width=6, stroke_fill="black")
    draw.text((w//2, top_h*0.72 + offset_top), txt_pref, fill="white", anchor="mm", font=font_txt, stroke_width=4, stroke_fill="black")
    draw.text((w//2, h-bottom_h + bottom_h*0.28 - offset_bottom), "10", fill="white", anchor="mm", font=font_num, stroke_width=6, stroke_fill="black")
    draw.text((w//2, h-bottom_h + bottom_h*0.72 - offset_bottom), txt_cartas, fill="white", anchor="mm", font=font_txt, stroke_width=4, stroke_fill="black")
    return panel

def generar_10_balanceado_FAST_PREVIEW(baraja_files, preferida_portada_path, color_entre, div_interno, sep_entre, orientacion):
    CW,CH=300,425
    cols,rows=5,2
    W=cols*CW+(cols-1)*sep_entre; H=rows*CH+(rows-1)*sep_entre
    pref_baraja=buscar_equivalente_baraja(preferida_portada_path, baraja_files) or random.choice(baraja_files)
    cartas_data=[]
    for _ in range(10):
        sample = random.sample(baraja_files, 16)
        cartas_data.append(sample)
    tablero=Image.new("RGB",(W,H), color_entre)
    for idx,data16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols
        card_img=crear_carta_imagen_rectangular(data16, card_w=CW, card_h=CH, div_interno=div_interno, fast=True)
        tablero.paste(card_img,(col*(CW+sep_entre), row*(CH+sep_entre)))
    panel_w=CW
    panel=crear_panel_con_texto_editable(preferida_portada_path, panel_w, H, color_entre, 80, 50, TXT_PREF_FIJO, TXT_CARTAS_FIJO, 50, 50, fast=True)
    final_W=panel_w+sep_entre+W
    sheet_final=Image.new("RGB",(final_W, H), color_entre)
    sheet_final.paste(panel,(0,0))
    sheet_final.paste(tablero,(panel_w+sep_entre,0))
    return sheet_final

def generar_10_balanceado(baraja_files, preferida_portada_path, color_entre, div_interno, sep_entre, orientacion, dups_de_esta_hoja, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom):
    global CARTAS_UNICAS_GLOBAL_JUEGO, USADOS_POR_POSICION_HOJA
    CW,CH=600,850
    ori=orientacion.upper()
    if "10X1" in ori: cols,rows=10,1
    elif "1X10" in ori: cols,rows=1,10
    elif "5X2" in ori: cols,rows=5,2
    else: cols,rows=2,5
    W=cols*CW+(cols-1)*sep_entre; H=rows*CH+(rows-1)*sep_entre
    pref_baraja=buscar_equivalente_baraja(preferida_portada_path, baraja_files)
    if pref_baraja is None: pref_baraja=random.choice(baraja_files)
    pref_name=os.path.splitext(os.path.basename(pref_baraja))[0].lower()
    conteo_hoja={}
    baraja_filtrada=[f for f in baraja_files if os.path.splitext(os.path.basename(f))[0].lower()!=pref_name]
    if not baraja_filtrada: baraja_filtrada=baraja_files
    dups_filtrados=[]
    for d in dups_de_esta_hoja:
        if os.path.splitext(os.path.basename(d))[0].lower()!=pref_name:
            dups_filtrados.append(d)
    while len(dups_filtrados)<10:
        cand=[f for f in baraja_filtrada if f not in dups_filtrados]
        if not cand: break
        dups_filtrados.append(random.choice(cand))
    posiciones_preferida=posiciones_preferida_variadas_por_hoja()
    dups_nombres=[os.path.splitext(os.path.basename(d))[0].lower() for d in dups_filtrados]
    cartas_data=[]
    USADOS_POR_POSICION_HOJA = {i:set() for i in range(16)}
    plan_extra = {i: [] for i in range(10)}
    for idx_origen in range(10):
        destinos = [j for j in range(10) if j != idx_origen]
        random.shuffle(destinos)
        for dest in destinos:
            if len(plan_extra[dest]) < 1:
                plan_extra[dest].append(dups_filtrados[idx_origen])
                break
    for nom in dups_nombres: conteo_hoja[nom]=2
    for idx_carta in range(10):
        dup=dups_filtrados[idx_carta]; dup_name=dups_nombres[idx_carta]
        intentos_carta=0
        while True:
            intentos_carta+=1
            if intentos_carta>60:
                USADOS_POR_POSICION_HOJA = {i:set() for i in range(16)}
                intentos_carta=0
            top=[None]*16; top[5]=dup; top[6]=dup
            pp=posiciones_preferida[idx_carta]; top[pp]=pref_baraja
            usados=set([dup, pref_baraja]); usados_nombres=set([dup_name, pref_name])
            for extra_path in plan_extra[idx_carta]:
                extra_nom = os.path.splitext(os.path.basename(extra_path))[0].lower()
                if extra_nom in usados_nombres: continue
                libres = [p for p in range(16) if top[p] is None and p not in (5,6,9,10)]
                random.shuffle(libres)
                for p in libres:
                    if extra_path not in USADOS_POR_POSICION_HOJA[p] and conteo_hoja.get(extra_nom,0) < 3:
                        top[p]=extra_path; usados.add(extra_path); usados_nombres.add(extra_nom)
                        break
            ok=True
            for pos in range(16):
                if top[pos] is not None: continue
                if pos in (9,10):
                    candidatos=[f for f in baraja_filtrada if f not in usados and os.path.splitext(os.path.basename(f))[0].lower() not in usados_nombres and f not in USADOS_POR_POSICION_HOJA[pos] and conteo_hoja.get(os.path.splitext(os.path.basename(f))[0].lower(),0)<2 and os.path.splitext(os.path.basename(f))[0].lower() not in dups_nombres]
                else:
                    candidatos=[f for f in baraja_filtrada if f not in usados and os.path.splitext(os.path.basename(f))[0].lower() not in usados_nombres and f not in USADOS_POR_POSICION_HOJA[pos] and conteo_hoja.get(os.path.splitext(os.path.basename(f))[0].lower(),0)<3]
                if not candidatos:
                    candidatos=[f for f in baraja_filtrada if f not in usados and os.path.splitext(os.path.basename(f))[0].lower() not in usados_nombres and conteo_hoja.get(os.path.splitext(os.path.basename(f))[0].lower(),0)<3]
                if not candidatos:
                    candidatos=[f for f in baraja_filtrada if f not in usados]
                if not candidatos:
                    ok=False; break
                elegido=random.choice(candidatos)
                top[pos]=elegido; usados.add(elegido); usados_nombres.add(os.path.splitext(os.path.basename(elegido))[0].lower())
            if not ok: continue
            nombres_top=[os.path.splitext(os.path.basename(f))[0].lower() for f in top]
            if len(set(nombres_top))!=15: continue
            firma=frozenset(nombres_top)
            if firma in CARTAS_UNICAS_GLOBAL_JUEGO: continue
            CARTAS_UNICAS_GLOBAL_JUEGO.add(firma)
            for p,f in enumerate(top):
                USADOS_POR_POSICION_HOJA[p].add(f)
            for n in set(nombres_top):
                if n==dup_name: continue
                conteo_hoja[n]=conteo_hoja.get(n,0)+1
            for extra_path in plan_extra[idx_carta]:
                extra_nom=os.path.splitext(os.path.basename(extra_path))[0].lower()
                if extra_nom in nombres_top:
                    if conteo_hoja[extra_nom] < 3:
                        conteo_hoja[extra_nom]+=1
            cartas_data.append(top)
            break
    tablero=Image.new("RGB",(W,H), color_entre)
    for idx,data16 in enumerate(cartas_data):
        col=idx%cols; row=idx//cols
        card_img=crear_carta_imagen_rectangular(data16, card_w=CW, card_h=CH, div_interno=div_interno)
        tablero.paste(card_img,(col*(CW+sep_entre), row*(CH+sep_entre)))
    panel_w=CW
    panel=crear_panel_con_texto_editable(preferida_portada_path, panel_w, H, color_entre, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom)
    final_W=panel_w+sep_entre+W
    sheet_final=Image.new("RGB",(final_W, H), color_entre)
    sheet_final.paste(panel,(0,0))
    sheet_final.paste(tablero,(panel_w+sep_entre,0))
    return sheet_final

def render():
    global CARTAS_UNICAS_GLOBAL_JUEGO
    st.markdown(banner_top("1 PREFERIDA + 10 CARTAS - DOBLES EN 6 Y 7"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    if "entrada_registrada_10portada" not in st.session_state:
        inc_contador("visita_10portada")
        st.session_state["entrada_registrada_10portada"]=True
    st.markdown(instrucciones_html("1 PREFERIDA + 10 CARTAS DOBLES 6 Y 7"), unsafe_allow_html=True)
    barajas_paths = listar_barajas()
    if not barajas_paths:
        st.error("No hay barajas")
        if st.button("⬅️ Volver"): ir_a("catalogo")
        return
    portadas_root = "portadas"
    portadas_list = sorted([d for d in os.listdir(portadas_root) if os.path.isdir(os.path.join(portadas_root,d))]) if os.path.exists(portadas_root) else []
    c1,c2,c3 = st.columns(3)
    with c1:
        baraja_sel = st.selectbox("📁 BARAJA:", [os.path.basename(p) for p in barajas_paths])
        baraja_path = os.path.join("barajas", baraja_sel)
    with c2:
        portada_sel = st.selectbox("🎨 PORTADAS:", portadas_list) if portadas_list else st.selectbox("🎨 PORTADAS:", ["portadas"])
        portada_path_root = os.path.join(portadas_root, portada_sel) if portadas_list else portadas_root
    with c3:
        ori = st.selectbox("ORIENTACION:", ["5x2 HORIZONTAL","2x5 VERTICAL"], index=0)
    c4,c5,c6 = st.columns(3)
    with c4:
        div_int = st.number_input("Div interno", 0, 20, 1)
    with c5:
        sep = st.number_input("Separacion", 0, 200, 30)
    with c6:
        color_hex = st.color_picker("Color fondo", "#FF00FF")
    with c6:
        juegos = st.number_input("Juegos de 54 hojas", 1, 10, 1)

    files_baraja = cargar_imagenes(baraja_path)
    files_portada = cargar_imagenes(portada_path_root)
    st.info(f"Baraja: {len(files_baraja)} | Portadas: {len(files_portada)} | FIJO {FONT_NUM_FIJO}/{FONT_TXT_FIJO} - Preview rápido")

    if st.button("👁️ VISTA PREVIA 1 HOJA - RÁPIDA 2 SEG", use_container_width=True):
        if len(files_baraja)<10 or len(files_portada)<1:
            st.error("Faltan imagenes")
        else:
            with st.spinner("Preview rápido..."):
                pref = random.choice(files_portada)
                sheet = generar_10_balanceado_FAST_PREVIEW(files_baraja, pref, color_hex, div_int, sep, ori)
                st.image(sheet, caption=f"Preview rápido - {os.path.basename(pref)}", use_container_width=True)
                st.caption("Este es preview rápido. El ZIP final sí usa el balanceo completo y letras 151/91 fijas")

    if st.button("🎰 GENERAR 54 HOJAS x JUEGO + ZIP - POSICION FIJA", type="primary", use_container_width=True):
        if len(files_baraja)<54 or len(files_portada)<54:
            st.error("Faltan 54 imagenes")
            return
        inc_contador("10portada")
        inc_baraja(baraja_sel, "10portada")
        progress = st.progress(0)
        status = st.empty()
        zip_buffer = io.BytesIO()
        total = juegos*54
        gen = 0
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for juego in range(1, juegos+1):
                CARTAS_UNICAS_GLOBAL_JUEGO=set()
                portadas_juego = files_portada[:54][:]
                random.shuffle(portadas_juego)
                for bloque in range(9):
                    baraja_54 = files_baraja[:54][:]
                    random.shuffle(baraja_54)
                    extras = random.sample(baraja_54,6)
                    todas_dobles = baraja_54+extras
                    random.shuffle(todas_dobles)
                    grupos=[]
                    restantes=todas_dobles[:]
                    for g in range(6):
                        if g%2==1 and grupos:
                            prev=set([os.path.splitext(os.path.basename(x))[0].lower() for x in grupos[-1]])
                            cand=[f for f in restantes if os.path.splitext(os.path.basename(f))[0].lower() not in prev]
                            sel=random.sample(cand,10) if len(cand)>=10 else random.sample(restantes,10)
                        else:
                            sel=random.sample(restantes,10) if len(restantes)>=10 else random.sample(files_baraja[:54],10)
                        grupos.append(sel)
                        for f in sel:
                            if f in restantes: restantes.remove(f)
                        if len(restantes)<10:
                            restantes=files_baraja[:54][:]
                            random.shuffle(restantes)
                    for hoja_in_bloque in range(6):
                        hoja_global=bloque*6+hoja_in_bloque+1
                        dups_hoja=grupos[hoja_in_bloque]
                        preferida_portada=portadas_juego[hoja_global-1]
                        gen+=1
                        status.text(f"Juego {juego} Hoja {hoja_global}/54 - {gen}/{total}")
                        progress.progress(gen/total)
                        sheet = generar_10_balanceado(files_baraja[:54], preferida_portada, color_hex, div_int, sep, ori, dups_hoja, FONT_NUM_FIJO, FONT_TXT_FIJO, TXT_PREF_FIJO, TXT_CARTAS_FIJO, OFFSET_TOP_FIJO, OFFSET_BOTTOM_FIJO)
                        buf=io.BytesIO()
                        sheet.save(buf, format="JPEG", quality=85, optimize=True)
                        zf.writestr(f"{baraja_sel}_J{juego}_HOJA_{hoja_global:02d}.jpg", buf.getvalue())
                        del sheet, buf
                        gc.collect()
        progress.empty()
        status.success(f"¡{total} hojas - 151/91 fijo!")
        st.download_button("📥 DESCARGAR ZIP", zip_buffer.getvalue(), file_name=f"{baraja_sel}_{portada_sel}_{juegos}juegos_FIJO.zip", mime="application/zip", use_container_width=True)
        st.markdown(banner_venta_offline(), unsafe_allow_html=True)
    if st.button("⬅️ Volver al Catalogo"):
        ir_a("catalogo")
