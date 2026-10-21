import os, random, io, zipfile, threading, datetime, gc, glob, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import streamlit as st

EXCEL_COLORS = {1:"#000000",2:"#FFFFFF",3:"#FF0000",4:"#00FF00",5:"#0000FF",6:"#FFFF00",7:"#FF00FF",8:"#00FFFF",9:"#800000",10:"#008000",11:"#000080",12:"#808000",13:"#800080",14:"#008080",15:"#C0C0C0",16:"#808080",17:"#9999FF",18:"#993366",19:"#FFFFCC",20:"#CCFFFF",21:"#660066",22:"#FF8080",23:"#0066CC",24:"#CCCCFF",25:"#000080",26:"#FF00FF",27:"#FFFF00",28:"#00FFFF",29:"#800080",30:"#800000",31:"#008080",32:"#0000FF",33:"#00CCFF",34:"#CCFFCC",35:"#FFFF99",36:"#99CCFF",37:"#FF99CC",38:"#CC99FF",39:"#FFCC99",40:"#3366FF",41:"#33CCCC",42:"#99CC00",43:"#FFCC00",44:"#FF9900",45:"#FF6600",46:"#666699",47:"#969696",48:"#003366",49:"#339966",50:"#003300",51:"#333300",52:"#993300",53:"#993366",54:"#333399",55:"#333333",56:"#000000"}

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
