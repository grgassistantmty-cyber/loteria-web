import random
from PIL import Image
from utils.barajas import no_chocan, RIGHT4, LEFT4, TOP4, BOTTOM4
import streamlit as st

def crear_carta_4x4(data16, cw_card, ch_card, div, g, asp):
    carta=Image.new("RGB",(cw_card,ch_card),"black")
    fw=cw_card-g*2; fh=ch_card-g*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-div*3)//4; ch=int(cw*asp); th=ch*4+div*3; y0=(fh-th)//2
    for i in range(min(16,len(data16))):
        r=i//4; c=i%4; x=c*(cw+div); y=y0+r*(ch+div)
        try:
            with Image.open(data16[i]) as im:
                base.paste(im.convert("RGB").resize((cw,ch), Image.LANCZOS),(x,y))
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
    from PIL import Image
    cw_tmp=((W_orig-sep_v)//2 - g*2 - 3*div)//4; ch_tmp=int(cw_tmp*asp); card_h=ch_tmp*4+div*3+g*2
    H_orig=card_h*2+sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color)
    for idx,d16 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_4x4(d16,cw,ch,div,g,asp),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet
