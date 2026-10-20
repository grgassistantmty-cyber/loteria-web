import random
from PIL import Image, ImageDraw
import streamlit as st
from utils.barajas import no_chocan

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
    from utils.barajas import cm_to_px
    orig=generar_original_fijo_10(cartas_data, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, layout)
    W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
    final=orig.resize((W_final, H_final), Image.LANCZOS)
    return orig, final
