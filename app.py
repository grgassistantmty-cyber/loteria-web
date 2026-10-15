import streamlit as st
import random, io, zipfile
from PIL import Image
from datetime import datetime

RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; TOP=[0,1,2,3]; BOTTOM=[12,13,14,15]
uso_global={}

def no_chocan(a,b, la, lb):
    for i,j in zip(la,lb):
        if a[i]==b[j]: return False
    return True

def cm_to_px(cm,dpi): return int(float(cm)/2.54*int(dpi))

def get_aspecto(lista_pils):
    asp=[]
    for im in lista_pils[:10]:
        try: w,h=im.size; asp.append(h/w)
        except: pass
    return sum(asp)/len(asp) if asp else 1.42

def crear_carta_ajustada(data16_pils, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2
    base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*3)//4; ch=int(cw*aspecto)
    total_h_grid=ch*4+DIV*3; y_offset=(fh-total_h_grid)//2
    for idx in range(16):
        r=idx//4; c=idx%4; x0=c*(cw+DIV); y0=y_offset + r*(ch+DIV)
        try:
            im2=data16_pils[idx].resize((cw,ch), Image.LANCZOS)
            base.paste(im2,(x0,y0))
        except: pass
    carta.paste(base,(G,G)); return carta

def generar_logica_4_cartas_WEB(lista_pils):
    global uso_global
    if not uso_global: uso_global={i:0 for i in range(len(lista_pils))}
    for _ in range(8000):
        conteo={}; cartas_data=[[None]*16 for _ in range(4)]; pos_por_figura={}; ok=True
        base54=list(range(len(lista_pils))); random.shuffle(base54)
        huecos=[3,3,2,2]; random.shuffle(huecos)
        huecos_por_carta=[set(random.sample(range(16), h)) for h in huecos]
        idx=0
        for c in range(4):
            for pos in range(16):
                if pos in huecos_por_carta[c]: continue
                fig=base54[idx]; cartas_data[c][pos]=fig
                pos_por_figura[fig]=pos_por_figura.get(fig,set())|{pos}
                conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda_lista=list(range(len(lista_pils))); random.shuffle(segunda_lista)
        segunda_lista.sort(key=lambda x:(uso_global.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas_data[c] if f is not None])
            for pos in huecos_por_carta[c]:
                base=[f for f in segunda_lista if f not in usados and conteo.get(f,0)<2 and pos not in pos_por_figura.get(f,set())]
                if not base: base=[f for f in range(len(lista_pils)) if f not in usados and conteo.get(f,0)<2]
                if not base: ok=False; break
                eleg=base[0]; cartas_data[c][pos]=eleg
                pos_por_figura[eleg]=pos_por_figura.get(eleg,set())|{pos}
                conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok: break
        if not ok: continue
        if not no_chocan(cartas_data[0], cartas_data[1], RIGHT, LEFT): continue
        if not no_chocan(cartas_data[0], cartas_data[2], BOTTOM, TOP): continue
        if not no_chocan(cartas_data[1], cartas_data[3], BOTTOM, TOP): continue
        if not no_chocan(cartas_data[2], cartas_data[3], RIGHT, LEFT): continue
        if len(pos_por_figura) < 54: continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items(): uso_global[f]=uso_global.get(f,0)+cnt
        return cartas_data, huecos
    return None, None

def generar_sheet(cartas_data_idx, lista_pils, color_entre, div, sep_v, sep_h, g_negro, aspecto, ancho_cm=None, alto_cm=None, dpi=300):
    W_orig=3500
    cw_tmp=((W_orig-sep_v)//2 - g_negro*2 - 3*div)//4; ch_tmp=int(cw_tmp*aspecto)
    card_h_real=ch_tmp*4 + div*3 + g_negro*2; H_orig=card_h_real*2 + sep_h
    cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color_entre)
    for idx, d_idx in enumerate(cartas_data_idx):
        d_pils=[lista_pils[i] for i in d_idx]; col=idx%2; row=idx//2
        x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_ajustada(d_pils, cw, ch, div, g_negro, aspecto),(x,y))
    if ancho_cm and alto_cm:
        W_final=cm_to_px(ancho_cm, dpi); H_final=cm_to_px(alto_cm, dpi)
        final=sheet.resize((W_final, H_final), Image.LANCZOS)
        return sheet, final
    return sheet, sheet

# --- UI ---
st.set_page_config(page_title="Loteria 4 Cartas WEB", layout="wide")
st.title("Loteria 4 Cartas - WEB 3,3,2,2 ROTADOS")

zip_file=st.file_uploader("Sube tu baraja en ZIP (54 imgs)", type="zip")

if zip_file:
    with zipfile.ZipFile(zip_file) as z:
        pils=[]; names=[]
        for name in sorted(z.namelist()):
            if name.lower().endswith((".png",".jpg",".jpeg",".webp",".jfif")):
                try:
                    pils.append(Image.open(io.BytesIO(z.read(name))).convert("RGB"))
                    names.append(name)
                except: pass
        pils=pils[:54]
        st.success(f"Baraja cargada: {len(pils)} imagenes")

        # NUEVO - PREVIEW MINI 54 CARTAS
        st.subheader(f"Preview de las {len(pils)} cartas subidas:")
        cols = st.columns(9)
        for i, im in enumerate(pils):
            with cols[i % 9]:
                st.image(im, caption=f"{i+1}", use_container_width=True)

        c1,c2,c3,c4=st.columns(4)
        with c1: color=st.color_picker("Color entre cartas", "#FF00FF")
        with c2: div=st.number_input("Div interno",0,30,1)
        with c3: sep_v=st.number_input("Sep V",0,500,200)
        with c4: sep_h=st.number_input("Sep H",0,500,200)
        c5,c6,c7,c8=st.columns(4)
        with c5: g_marco=st.number_input("Marco negro",0,30,0)
        with c6: ancho=st.number_input("Ancho cm", value=21.0)
        with c7: alto=st.number_input("Alto cm", value=35.0)
        with c8: dpi=st.number_input("DPI", value=300)
        ciclos=st.number_input("Cuantas hojas generar",1,14,1)

        if st.button("GENERAR PREVIEW ROTADO"):
            uso_global={}
            cartas, huecos = generar_logica_4_cartas_WEB(pils)
            if cartas:
                aspecto=get_aspecto(pils)
                orig, final = generar_sheet(cartas, pils, color, div, sep_v, sep_h, g_marco, aspecto, ancho, alto, dpi)
                st.info(f"Huecos rotados esta hoja: {huecos} - Carta1={huecos[0]} repetidas, Carta2={huecos[1]} etc")
                colA, colB = st.columns(2)
                with colA: st.image(orig.resize((500, int(500*orig.size[1]/orig.size[0]))), caption="ORIGINAL 3500")
                with colB: st.image(final.resize((500, int(500*final.size[1]/final.size[0]))), caption=f"RESIZE {ancho}x{alto}cm {dpi}dpi")
                buf=io.BytesIO(); final.save(buf, format="JPEG", quality=95, dpi=(dpi,dpi))
                st.download_button("Descargar JPG", buf.getvalue(), file_name=f"loteria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            else:
                st.error("No se pudo, intenta de nuevo")

        if st.button(f"GENERAR {ciclos} HOJAS EN ZIP"):
            uso_global={}; aspecto=get_aspecto(pils)
            zip_out=io.BytesIO()
            with zipfile.ZipFile(zip_out, 'w') as zout:
                for h in range(1, ciclos+1):
                    cartas, huecos = generar_logica_4_cartas_WEB(pils)
                    if cartas:
                        _, final = generar_sheet(cartas, pils, color, div, sep_v, sep_h, g_marco, aspecto, ancho, alto, dpi)
                        buf=io.BytesIO(); final.save(buf, format="JPEG", quality=95, dpi=(dpi,dpi))
                        zout.writestr(f"loteria_H{h:02d}_huecos_{''.join(map(str,huecos))}.jpg", buf.getvalue())
            st.download_button("Descargar ZIP con todas", zip_out.getvalue(), file_name=f"loterias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")