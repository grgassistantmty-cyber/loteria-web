import os, random, io, zipfile, time, threading
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Loteria Eliud PRO - Catalogo", layout="wide", page_icon="🎰")

@st.cache_resource
def get_lock(): return threading.Lock()
lock = get_lock()
contador_file = "/data/visitas.txt"
os.makedirs("/data", exist_ok=True)
if "visitado" not in st.session_state:
    st.session_state["visitado"] = True
    try:
        with lock:
            total = int(open(contador_file,"r").read().strip() or 0) if os.path.exists(contador_file) else 0
            total += 1
            open(contador_file,"w").write(str(total))
    except: total = 1
else:
    try: total = int(open(contador_file,"r").read().strip() or 0)
    except: total = 1
visitas_total = total

if "uso_global_4x4" not in st.session_state: st.session_state["uso_global_4x4"] = {}
if "uso_global_5x5" not in st.session_state: st.session_state["uso_global_5x5"] = {}
if "vista" not in st.session_state: st.session_state["vista"] = "catalogo"

def listar_barajas():
    if not os.path.exists("barajas"): return []
    return sorted([os.path.join("barajas",d) for d in os.listdir("barajas") if os.path.isdir(os.path.join("barajas",d)) and d.lower().startswith("baraja")])
def cargar_files(path, limite=54):
    exts=(".png",".jpg",".jpeg",".webp",".jfif")
    files=[os.path.join(path,f) for f in os.listdir(path) if f.lower().endswith(exts)]
    files.sort(); return files[:limite]
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
    uso = st.session_state["uso_global_4x4"]
    if not uso: uso = {f:0 for f in baraja}
    st.session_state["uso_global_4x4"] = uso
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

RIGHT5=[4,9,14,19,24]; LEFT5=[0,5,10,15,20]; TOP5=[0,1,2,3,4]; BOTTOM5=[20,21,22,23,24]
def crear_carta_5x5(data25, card_w, card_h, div_interno, g_negro, aspecto):
    G=g_negro; DIV=div_interno
    carta=Image.new("RGB",(card_w, card_h),"black")
    fw=card_w-G*2; fh=card_h-G*2; base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-DIV*4)//5; ch=int(cw*aspecto); th=ch*5+DIV*4; y0=(fh-th)//2
    for idx in range(min(25,len(data25))):
        r=idx//5; c=idx%5; x0=c*(cw+DIV); y0f=y0 + r*(ch+DIV)
        try: im=Image.open(data25[idx]).convert("RGB").resize((cw,ch), Image.LANCZOS); base.paste(im,(x0,y0f))
        except: pass
    carta.paste(base,(G,G)); return carta
def generar_logica_5x5(baraja_files):
    uso = st.session_state["uso_global_5x5"]
    if not uso: uso={f:0 for f in baraja_files}
    st.session_state["uso_global_5x5"]=uso
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
                if not base: base=[f for f in baraja_files if f not in usados and conteo.get(f,0)<2 and pos not in pos_por_figura.get(f,set())]
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
    cw_tmp=((W_orig-sep_v)//2 - g_negro*2 - 4*div_interno)//5; ch_tmp=int(cw_tmp*aspecto); card_h_real=ch_tmp*5 + div_interno*4 + g_negro*2; H_orig=card_h_real*2 + sep_h
    cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2; sheet=Image.new("RGB",(W_orig, H_orig), color_entre)
    for idx,d25 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta_5x5(d25, cw, ch, div_interno, g_negro, aspecto),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet

# CATALOGO
if st.session_state.vista == "catalogo":
    st.markdown(f"""<style>.banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}}.contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px}}</style><div class="banner"><h1>🎰 CATALOGO LOTERIA ELIUD PRO 🎰</h1><h3>Elige tu juego - Visitas: {visitas_total}</h3></div><br>""", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if os.path.exists("portadas/portada_4x4.jpg"): st.image("portadas/portada_4x4.jpg", use_column_width=True)
        st.markdown("### 4x4 - 16 imgs - Huecos 3,3,2,2 - 54 Garantizadas")
        if st.button("🎰 ENTRAR A 4x4", use_container_width=True, type="primary"): st.session_state.vista="4x4"; st.rerun()
    with c2:
        if os.path.exists("portadas/portada_5x5.jpg"): st.image("portadas/portada_5x5.jpg", use_column_width=True)
        st.markdown("### 5x5 - 25 imgs - 11,11,12,12 ROTADO - 54+46 - NUEVO")
        if st.button("🎰 ENTRAR A 5x5", use_container_width=True): st.session_state.vista="5x5"; st.rerun()
    st.stop()

if st.session_state.vista == "4x4":
    if st.button("⬅️ Volver al Catalogo"): st.session_state.vista="catalogo"; st.rerun()
    st.markdown(f"""<div style="background:linear-gradient(90deg,#cc0000,#000);padding:12px;border-radius:12px;color:white;text-align:center;border:2px solid gold"><h2>🎰 GENERADOR 4 CARTAS 4X4 🎰 - Visitas: {visitas_total}</h2></div><br>""", unsafe_allow_html=True)
    barajas=listar_barajas()
    col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Origen", ["Integrada","ZIP"], key="modo4")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel4")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel)
        elif modo=="ZIP":
            z=st.file_uploader("ZIP 54", type=["zip"], key="zip4")
            if z:
                tmp="/tmp/baraja4"; os.makedirs(tmp, exist_ok=True)
                with zipfile.ZipFile(z) as zz:
                    for name in zz.namelist():
                        if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                            open(os.path.join(tmp, os.path.basename(name)),"wb").write(zz.read(name))
                files=cargar_files(tmp)
        div=st.number_input("Div", value=1, key="div4"); sep_v=st.number_input("Sep V", value=20, key="sepv4"); sep_h=st.number_input("Sep H", value=20, key="seph4"); marco=st.number_input("Marco", value=2, key="marco4")
        color=st.color_picker("Color", "#FF00FF", key="color4")
        ancho=st.text_input("Ancho cm","21", key="ancho4"); alto=st.text_input("Alto cm","35", key="alto4"); dpi=st.text_input("DPI","300", key="dpi4")
        W_usar=2500; juegos=st.number_input("Juegos", value=2, min_value=1, max_value=10, key="j4")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4")
        if st.button("🔄 Resetear memoria 4x4"): st.session_state["uso_global_4x4"]={}; st.success("Reseteada")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👀 VER 1 PREVIEW 4x4", use_container_width=True, key="prev4"):
                    with lock:
                        cartas=generar_logica_4x4(files)
                        if cartas:
                            orig=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_4x4(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["orig4"]=orig; st.session_state["final4"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS 4x4", type="primary", use_container_width=True, key="gen4"):
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
            if "orig4" in st.session_state:
                st.image(st.session_state["orig4"], caption="ORIGINAL 4x4", use_column_width=True)
                st.image(st.session_state["final4"], caption="RESIZE 4x4", use_column_width=True)
            if "lista_final4" in st.session_state and st.session_state["lista_final4"]:
                finales=st.session_state["lista_final4"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4"]
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_{i+1:02d}.jpg", b.getvalue())
                d1,d2=st.columns(2)
                with d1: st.download_button(f"⬇️ PDF {len(finales)} 4x4", pdf_bytes.getvalue(), f"loteria_4x4_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                with d2: st.download_button(f"⬇️ ZIP {len(finales)} 4x4", zip_bytes.getvalue(), f"loteria_4x4_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()

if st.session_state.vista == "5x5":
    if st.button("⬅️ Volver al Catalogo"): st.session_state.vista="catalogo"; st.rerun()
    st.markdown(f"""<div style="background:linear-gradient(90deg,#0033cc,#000);padding:12px;border-radius:12px;color:white;text-align:center;border:2px solid gold"><h2>🎰 GENERADOR 5x5 4 CARTAS - 54+46 ROTADO 11,11,12,12 🎰 - Visitas: {visitas_total}</h2></div><br>""", unsafe_allow_html=True)
    barajas=listar_barajas()
    col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Origen", ["Integrada","ZIP"], key="modo5")
        files=None
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel5")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel)
        elif modo=="ZIP":
            z=st.file_uploader("ZIP 54", type=["zip"], key="zip5")
            if z:
                tmp="/tmp/baraja5"; os.makedirs(tmp, exist_ok=True)
                with zipfile.ZipFile(z) as zz:
                    for name in zz.namelist():
                        if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                            open(os.path.join(tmp, os.path.basename(name)),"wb").write(zz.read(name))
                files=cargar_files(tmp)
        div=st.number_input("Div", value=1, key="div5"); sep_v=st.number_input("Sep V", value=20, key="sepv5"); sep_h=st.number_input("Sep H", value=20, key="seph5"); marco=st.number_input("Marco", value=2, key="marco5")
        color=st.color_picker("Color", "#FF00FF", key="color5")
        ancho=st.text_input("Ancho cm","21", key="ancho5"); alto=st.text_input("Alto cm","35", key="alto5"); dpi=st.text_input("DPI","300", key="dpi5")
        W_usar=3500; juegos=st.number_input("Juegos", value=1, min_value=1, max_value=10, key="j5")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out5")
        if st.button("🔄 Resetear memoria 5x5"): st.session_state["uso_global_5x5"]={}; st.success("Reseteada")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👀 VER 1 PREVIEW 5x5 4C", use_container_width=True, key="prev5"):
                    with lock:
                        cartas=generar_logica_5x5(files)
                        if cartas:
                            orig=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["orig5"]=orig; st.session_state["final5"]=final; st.session_state["cartas5"]=cartas
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS 5x5", type="primary", use_container_width=True, key="gen5"):
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
            if "orig5" in st.session_state:
                st.markdown(f"54 unicas: {len(set(sum(st.session_state.get('cartas5', [[]]),[])))}")
                st.image(st.session_state["orig5"], caption="ORIGINAL 5x5 3500", use_column_width=True)
                st.image(st.session_state["final5"], caption="RESIZE 5x5", use_column_width=True)
            if "lista_final5" in st.session_state and st.session_state["lista_final5"]:
                finales=st.session_state["lista_final5"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig5"]
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_5x5_{i+1:02d}.jpg", b.getvalue())
                d1,d2=st.columns(2)
                with d1: st.download_button(f"⬇️ PDF {len(finales)} 5x5", pdf_bytes.getvalue(), f"loteria_5x5_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                with d2: st.download_button(f"⬇️ ZIP {len(finales)} 5x5", zip_bytes.getvalue(), f"loteria_5x5_{len(finales)}.zip", "application/zip", use_container_width=True)
