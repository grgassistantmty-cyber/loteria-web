import random
from PIL import Image, ImageDraw
import streamlit as st
from utils.barajas import no_chocan, RIGHT5, LEFT5, TOP5, BOTTOM5

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
