import os, random, datetime, io, zipfile
from PIL import Image
import streamlit as st

RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; TOP=[0,1,2,3]; BOTTOM=[12,13,14,15]

EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}

def listar(dir_root):
    return sorted([d for d in os.listdir(dir_root) if os.path.isdir(os.path.join(dir_root,d))]) if os.path.isdir(dir_root) else []

def cargar_imagenes(carpeta):
    if not carpeta or not os.path.isdir(carpeta): return []
    files=[os.path.join(carpeta,f) for f in os.listdir(carpeta) if f.lower().endswith((".png",".jpg",".jpeg",".webp",".jfif"))]
    files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))) or 0) if any(c.isdigit() for c in os.path.basename(x)) else os.path.basename(x))
    return files

def no_chocan(a,b, la, lb):
    for i,j in zip(la,lb):
        if a[i]==b[j]: return False
    return True

def crear_carta_imagen(data16, card_w=1000, div_interno=8, sample_aspect=1.45):
    try:
        with Image.open(data16[0]) as im: w,h = im.size; sample_aspect = h / w
    except: pass
    cell_w = card_w // 4; cell_h = int(cell_w * sample_aspect)
    img = Image.new("RGB", (card_w, cell_h*4), "black")
    target_w = cell_w - div_interno; target_h = cell_h - div_interno
    for idx, ruta in enumerate(data16):
        try:
            im = Image.open(ruta).convert("RGB")
            iw, ih = im.size; scale = max(target_w / iw, target_h / ih)
            nw, nh = int(iw*scale), int(ih*scale)
            im = im.resize((nw, nh), Image.LANCZOS)
            left = (nw - target_w)//2; top = (nh - target_h)//2
            im = im.crop((left, top, left+target_w, top+target_h))
        except: im = Image.new("RGB", (target_w, target_h), "white")
        col = idx % 4; row = idx // 4
        x = col * cell_w + div_interno//2; y = row * cell_h + div_interno//2
        img.paste(im, (x, y))
    return img

def generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_cover_path, favorita_baraja_path, color_entre, div_interno, sep_entre):
    try:
        with Image.open(baraja_files[0]) as s: asp = s.size[1]/s.size[0]
    except: asp = 1.45
    card_w=1000; card_h=int(card_w*asp)
    grid_pos = [(2,0),(3,0),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(1,3),(2,3),(3,3)]
    vecinos={}
    for i,(r,c) in enumerate(grid_pos):
        lst=[]
        for j,(r2,c2) in enumerate(grid_pos):
            if i==j: continue
            if r==r2 and c==c2+1: lst.append((j, RIGHT, LEFT))
            if r==r2 and c==c2-1: lst.append((j, LEFT, RIGHT))
            if c==c2 and r==r2+1: lst.append((j, BOTTOM, TOP))
            if c==c2 and r==r2-1: lst.append((j, TOP, BOTTOM))
        vecinos[i]=lst
    otros = [f for f in baraja_files if f!= favorita_baraja_path][:53]
    for intento_global in range(2000):
        posiciones_fav = random.sample(range(16), 12)
        random.shuffle(otros); pool=[]
        for f in otros[:21]: pool.extend([f]*4)
        for f in otros[21:]: pool.extend([f]*3)
        random.shuffle(pool)
        pool_idx=0; cartas_data=[]; ok=True
        for idx_carta in range(12):
            fav_pos = posiciones_fav[idx_carta]; carta_ok=False
            for retry in range(40):
                top=[None]*16; top[fav_pos]=favorita_baraja_path
                usados=set([favorita_baraja_path]); temp_pool_idx=pool_idx; temp_pool=pool[:]; fail=False
                for pos in range(16):
                    if top[pos] is not None: continue
                    encontrado=False
                    for k in range(temp_pool_idx, len(temp_pool)):
                        if temp_pool[k] not in usados:
                            top[pos]=temp_pool[k]; usados.add(temp_pool[k])
                            temp_pool[k], temp_pool[temp_pool_idx] = temp_pool[temp_pool_idx], temp_pool[k]
                            temp_pool_idx+=1; encontrado=True; break
                    if not encontrado: fail=True; break
                if fail: continue
                choque=False
                for j, la, lb in vecinos[idx_carta]:
                    if j < len(cartas_data):
                        if not no_chocan(cartas_data[j], top, la, lb): choque=True; break
                if choque: continue
                pool=temp_pool; pool_idx=temp_pool_idx; cartas_data.append(top); carta_ok=True; break
            if not carta_ok: ok=False; break
        if not ok: continue
        W = 4*card_w + 3*sep_entre; H = 4*card_h + 3*sep_entre
        sheet=Image.new("RGB",(W,H), color_entre)
        try:
            imc=Image.open(portada_cover_path).convert("RGB")
            tw=2*card_w+sep_entre; th=2*card_h+sep_entre; sc=max(tw/imc.size[0], th/imc.size[1])
            imc=imc.resize((int(imc.size[0]*sc), int(imc.size[1]*sc)), Image.LANCZOS)
            imc=imc.crop(((imc.size[0]-tw)//2, (imc.size[1]-th)//2, (imc.size[0]-tw)//2+tw, (imc.size[1]-th)//2+th))
        except: imc=Image.new("RGB",(2*card_w+sep_entre, 2*card_h+sep_entre),"gold")
        sheet.paste(imc,(0,0))
        for idx, data16 in enumerate(cartas_data):
            r,c = grid_pos[idx]
            if r<2 and c<2: continue
            x=c*(card_w+sep_entre); y=r*(card_h+sep_entre)
            card_img=crear_carta_imagen(data16, card_w=card_w, div_interno=div_interno, sample_aspect=asp)
            sheet.paste(card_img,(x,y))
        return sheet
    return None

def limpiar_nombre(path_img, idx):
    raw = os.path.splitext(os.path.basename(path_img))[0]
    clean = raw.replace("_"," ").replace("-"," ").strip().upper()
    clean = ' '.join([w for w in clean.split() if not w.isdigit()]).strip()
    if not clean: clean = f"CARTA {idx}"
    return clean

def render():
    from app import banner_top, banner_facebook, copiar_clabe_component, instrucciones_html, get_contador, inc_contador, inc_baraja, registrar_entrada_generador, ir_a, listar_barajas, cm_to_px, get_aspecto
    import os

    registrar_entrada_generador("12portada")
    
    if st.button("⬅️ Volver al Catalogo"):
        ir_a("catalogo")

    st.markdown(banner_top("12 CARTAS + PORTADA - TABLOIDE"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    st.markdown(instrucciones_html("12portada"), unsafe_allow_html=True)

    BARAJAS_ROOT = "barajas"
    PORTADAS_ROOT = "portadas"

    col_ctrl, col_prev = st.columns([1,1.5])

    with col_ctrl:
        st.subheader("📁 BARAJAS")
        barajas_inc = listar(BARAJAS_ROOT) or []
        portadas_inc = listar(PORTADAS_ROOT) or []
        
        if barajas_inc:
            baraja_sel = st.selectbox("Baraja incluida:", barajas_inc, key="b12")
            baraja_path = os.path.join(BARAJAS_ROOT, baraja_sel)
        else:
            baraja_path = st.text_input("Ruta baraja (54 imgs)", key="bp12")
        
        if portadas_inc:
            portada_sel = st.selectbox("Portada incluida:", portadas_inc, key="p12")
            portada_path = os.path.join(PORTADAS_ROOT, portada_sel)
        else:
            portada_path = st.text_input("Ruta portadas", key="pp12")

        st.subheader("🎨 AJUSTES")
        color_opt = st.selectbox("Color fondo (Excel)", [f"{k:02d} - {v}" for k,v in EXCEL_COLORS.items()], index=2, key="col12")
        num = int(color_opt.split("-")[0].strip())
        color_hex = EXCEL_COLORS.get(num, "#FF0000")
        color_hex = st.color_picker("Color picker", color_hex, key="cp12")
        
        div = st.slider("Div interna", 1, 30, 8, key="div12")
        sep = st.slider("Sep entre cartas", 0, 300, 40, key="sep12")

        st.subheader("🎯 MODO")
        modo = st.radio("Modo", ["Solo 1 hoja", "Todas las 54 hojas"], key="modo12")
        num_fav = st.number_input("Numero favorita (1-54)", 1, 54, 46, key="nfav12")

        baraja_files = cargar_imagenes(baraja_path) if baraja_path else []
        portada_files = cargar_imagenes(portada_path) if portada_path else []
        st.write(f"Baraja: {len(baraja_files)} imgs | Portadas: {len(portada_files)}")

    with col_prev:
        st.subheader("👁️ VISTA PREVIA")
        if st.button("👁 Generar Vista Previa", use_container_width=True):
            if len(baraja_files)<54 or not portada_files:
                st.error(f"Necesitas 54 baraja y al menos 1 portada. Tienes {len(baraja_files)} y {len(portada_files)}")
            else:
                idx = max(0,min(num_fav-1, min(len(baraja_files),len(portada_files))-1))
                with st.spinner("Generando tabloide pulido..."):
                    sheet = generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_files[idx], baraja_files[idx], color_hex, div, sep)
                if sheet:
                    st.image(sheet, caption=f"Preview: {os.path.basename(baraja_files[idx])} - Portada {idx+1}")
                    st.session_state["sheet_12portada"] = sheet
                    st.session_state["sheet_12portada_name"] = limpiar_nombre(baraja_files[idx], idx+1)
                else:
                    st.error("No se pudo generar, intenta de nuevo")

        if "sheet_12portada" in st.session_state:
            sheet = st.session_state["sheet_12portada"]
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=95)
            st.download_button("📥 Descargar JPG", buf.getvalue(), f"{st.session_state['sheet_12portada_name']}.jpg", "image/jpeg", use_container_width=True)

            # PDF Tabloide
            if st.button("📄 Generar PDF Tabloide 33x51", use_container_width=True):
                TAB_W, TAB_H = 3300, 5100
                sr = sheet.size[0]/sheet.size[1]; tr = TAB_W/TAB_H
                if sr > tr: nw = TAB_W-150; nh = int(nw/sr)
                else: nh = TAB_H-150; nw = int(nh*sr)
                sheet_r = sheet.resize((nw, nh), Image.LANCZOS)
                tabloide = Image.new("RGB", (TAB_W, TAB_H), "white")
                tabloide.paste(sheet_r, ((TAB_W-nw)//2, (TAB_H-nh)//2))
                buf_pdf = io.BytesIO()
                tabloide.save(buf_pdf, format="PDF", resolution=300)
                st.download_button("📥 Descargar PDF Tabloide", buf_pdf.getvalue(), f"{st.session_state['sheet_12portada_name']}.pdf", "application/pdf", use_container_width=True)
                inc_contador("12portada")
                inc_baraja(os.path.basename(baraja_path), "12portada")

        st.markdown("---")
        if st.button("🖼️ EXPORTAR TODAS A ZIP JPG", use_container_width=True) and modo=="Todas las 54 hojas":
            if len(baraja_files)<54 or not portada_files:
                st.error("Faltan imagenes")
            else:
                n = min(len(baraja_files), len(portada_files), 54)
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w") as z:
                    for i in range(n):
                        sheet = generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_files[i], baraja_files[i], color_hex, div, sep)
                        if sheet:
                            img_buf = io.BytesIO()
                            sheet.save(img_buf, format="JPEG", quality=95)
                            z.writestr(f"{i+1:02d} - {limpiar_nombre(baraja_files[i], i+1)}.jpg", img_buf.getvalue())
                st.download_button("📥 Descargar ZIP 54 JPGs", zip_buf.getvalue(), "tabloide_12portada_54.zip", "application/zip", use_container_width=True)
