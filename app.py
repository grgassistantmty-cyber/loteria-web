import os, random, io, zipfile
from datetime import datetime
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Loteria Eliud 14 Juegos", layout="wide", page_icon="🎰")

# ===== CONTADOR DE VISITAS =====
contador_file = "visitas.txt"
if "visitado" not in st.session_state:
    st.session_state["visitado"] = True
    try:
        if os.path.exists(contador_file):
            with open(contador_file, "r") as f:
                total = int(f.read().strip() or 0)
        else:
            total = 0
        total += 1
        with open(contador_file, "w") as f:
            f.write(str(total))
    except:
        total = 1
else:
    try:
        with open(contador_file, "r") as f:
            total = int(f.read().strip() or 0)
    except:
        total = 1
visitas_total = total

# ===== BANNER CON CONTADOR =====
st.markdown(f"""
<style>.banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}}
.ws{{background:#25D366;color:white!important;padding:10px 24px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block}}
.contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px;font-size:18px}}</style>
<div class="banner"><h1>🎰 GENERADOR 4 CARTAS - 3,3,2,2 ROTADOS 🎰</h1><h3>Creado por Eliud Monsivais - WhatsApp 8115566250</h3>
<a class="ws" href="https://wa.me/528115566250">📲 WHATSAPP 8115566250</a><br>
<span class="contador">👁️ Visitas: {visitas_total} | Hoy: {datetime.now().strftime('%d/%m/%Y')}</span></div><br>
""", unsafe_allow_html=True)

RIGHT=[3,7,11,15]; LEFT=[0,4,8,12]; TOP=[0,1,2,3]; BOTTOM=[12,13,14,15]

def listar_barajas():
    if not os.path.exists("barajas"): return []
    return sorted([os.path.join("barajas",d) for d in os.listdir("barajas") if os.path.isdir(os.path.join("barajas",d)) and d.lower().startswith("baraja")])
def cargar_files(path):
    exts=(".png",".jpg",".jpeg",".webp",".jfif")
    files=[os.path.join(path,f) for f in os.listdir(path) if f.lower().endswith(exts)]
    files.sort(); return files[:54]
def cm_to_px(cm,dpi): return int(float(cm)/2.54*int(dpi))
def get_aspecto(files):
    asp=[]
    for p in files[:10]:
        try:
            with Image.open(p) as im: asp.append(im.size[1]/im.size[0])
        except: pass
    return sum(asp)/len(asp) if asp else 1.42
def crear_carta(data16, cw_card, ch_card, div, g, asp):
    carta=Image.new("RGB",(cw_card,ch_card),"black")
    fw=cw_card-g*2; fh=ch_card-g*2
    base=Image.new("RGB",(fw,fh),"black")
    cw=(fw-div*3)//4; ch=int(cw*asp)
    th=ch*4+div*3; y0=(fh-th)//2
    for i in range(min(16,len(data16))):
        r=i//4; c=i%4; x=c*(cw+div); y=y0+r*(ch+div)
        try:
            im=Image.open(data16[i]).convert("RGB").resize((cw,ch), Image.LANCZOS)
            base.paste(im,(x,y))
        except: pass
    carta.paste(base,(g,g)); return carta

uso_global={}
def no_chocan(a,b,la,lb):
    for i,j in zip(la,lb):
        if a[i]==b[j]: return False
    return True
def generar_logica(baraja):
    global uso_global
    if not uso_global: uso_global={f:0 for f in baraja}
    for _ in range(5000):
        conteo={}; cartas=[[None]*16 for _ in range(4)]; pos_fig={}; ok=True
        base54=baraja.copy(); random.shuffle(base54)
        huecos=[3,3,2,2]; random.shuffle(huecos)
        huecos_carta=[set(random.sample(range(16),h)) for h in huecos]
        idx=0
        for c in range(4):
            for pos in range(16):
                if pos in huecos_carta[c]: continue
                fig=base54[idx]; cartas[c][pos]=fig; pos_fig[fig]=pos_fig.get(fig,set())|{pos}; conteo[fig]=conteo.get(fig,0)+1; idx+=1
        segunda=baraja.copy(); random.shuffle(segunda); segunda.sort(key=lambda x:(uso_global.get(x,0), random.random()))
        for c in range(4):
            usados=set([f for f in cartas[c] if f])
            for pos in huecos_carta[c]:
                cand=[f for f in segunda if f not in usados and conteo.get(f,0)<2 and pos not in pos_fig.get(f,set())]
                if not cand: cand=[f for f in baraja if f not in usados and conteo.get(f,0)<2]
                if not cand: ok=False; break
                eleg=cand[0]; cartas[c][pos]=eleg; pos_fig[eleg]=pos_fig.get(eleg,set())|{pos}; conteo[eleg]=conteo.get(eleg,0)+1; usados.add(eleg)
            if not ok: break
        if not ok: continue
        if not no_chocan(cartas[0],cartas[1],RIGHT,LEFT): continue
        if not no_chocan(cartas[0],cartas[2],BOTTOM,TOP): continue
        if not no_chocan(cartas[1],cartas[3],BOTTOM,TOP): continue
        if not no_chocan(cartas[2],cartas[3],RIGHT,LEFT): continue
        if any(v>2 for v in conteo.values()): continue
        for f,cnt in conteo.items(): uso_global[f]=uso_global.get(f,0)+cnt
        return cartas
    return None

def generar_hoja(cartas_data, color, div, sep_v, sep_h, g, asp, final_size=None):
    W_orig=3500; cw_tmp=((W_orig-sep_v)//2 - g*2 - 3*div)//4; ch_tmp=int(cw_tmp*asp); card_h=ch_tmp*4+div*3+g*2
    H_orig=card_h*2+sep_h; cw=(W_orig-sep_v)//2; ch=(H_orig-sep_h)//2
    sheet=Image.new("RGB",(W_orig,H_orig), color)
    for idx,d16 in enumerate(cartas_data):
        col=idx%2; row=idx//2; x=col*(cw+sep_v); y=row*(ch+sep_h)
        sheet.paste(crear_carta(d16,cw,ch,div,g,asp),(x,y))
    if final_size: sheet=sheet.resize(final_size, Image.LANCZOS)
    return sheet

barajas=listar_barajas()
col1,col2=st.columns([1,2.5])
with col1:
    modo=st.radio("Origen", ["Integrada","ZIP"])
    files=None
    if modo=="Integrada" and barajas:
        sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas])
        path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
        files=cargar_files(path_sel)
    elif modo=="ZIP":
        z=st.file_uploader("ZIP 54", type=["zip"])
        if z:
            tmp="/tmp/baraja"; os.makedirs(tmp, exist_ok=True)
            for f in os.listdir(tmp):
                try: os.remove(os.path.join(tmp,f))
                except: pass
            with zipfile.ZipFile(z) as zz:
                for name in zz.namelist():
                    if name.lower().endswith((".jpg",".jpeg",".png",".webp")):
                        data=zz.read(name)
                        open(os.path.join(tmp, os.path.basename(name)),"wb").write(data)
            files=cargar_files(tmp)
    st.divider()
    div=st.number_input("Div", value=1, min_value=0, max_value=30, step=1)
    sep_v=st.number_input("Sep V", value=20, min_value=0, max_value=500, step=1)
    sep_h=st.number_input("Sep H", value=20, min_value=0, max_value=500, step=1)
    marco=st.number_input("Marco", value=2, min_value=0, max_value=30, step=1)
    color=st.color_picker("Color", "#FF00FF")
    ancho=st.text_input("Ancho cm","21"); alto=st.text_input("Alto cm","35"); dpi=st.text_input("DPI","300")
    st.divider()
    juegos=st.number_input("Cantidad de juegos (hojas)", value=1, min_value=1, max_value=100, step=1)
    tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL 3500"], horizontal=True)

if files and len(files)>=10:
    asp=get_aspecto(files)
    st.info(f"Cartas: {len(files)} | Juegos: {juegos} | Visitas: {visitas_total}")
    cprev,cgen=st.columns(2)
    with cprev:
        if st.button("👀 VER 1 PREVIEW", use_container_width=True):
            uso_global={}
            cartas=generar_logica(files)
            if cartas:
                orig=generar_hoja(cartas,color,div,sep_v,sep_h,marco,asp)
                Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                final=generar_hoja(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf))
                st.session_state["orig"]=orig; st.session_state["final"]=final
            else: st.error("No se pudo")
    with cgen:
        if st.button(f"🎰 GENERAR {juegos} JUEGOS", type="primary", use_container_width=True):
            uso_global={}
            lista_final=[]; lista_orig=[]; bar=st.progress(0)
            for j in range(juegos):
                cartas=generar_logica(files)
                if not cartas: continue
                orig=generar_hoja(cartas,color,div,sep_v,sep_h,marco,asp)
                Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                final=generar_hoja(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf))
                lista_orig.append(orig); lista_final.append(final)
                bar.progress((j+1)/juegos)
            st.session_state["lista_final"]=lista_final; st.session_state["lista_orig"]=lista_orig

if "orig" in st.session_state:
    c1,c2=st.columns(2)
    with c1: st.image(st.session_state["orig"], caption="ORIGINAL 3500", use_container_width=True)
    with c2: st.image(st.session_state["final"], caption=f"RESIZE {ancho}x{alto}", use_container_width=True)

if "lista_final" in st.session_state and st.session_state["lista_final"]:
    st.divider()
    st.subheader(f"📦 {len(st.session_state['lista_final'])} Juegos")
    cols=st.columns(3)
    for i, im in enumerate(st.session_state["lista_final"][:3]):
        cols[i%3].image(im, caption=f"Juego {i+1}", use_container_width=True)
    pdf_bytes=io.BytesIO()
    finales=st.session_state["lista_final"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig"]
    finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=95)
    zip_bytes=io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as zf:
        for i, im in enumerate(finales):
            b=io.BytesIO(); im.save(b, format="JPEG", quality=95)
            zf.writestr(f"juego_{i+1:02d}.jpg", b.getvalue())
    d1,d2=st.columns(2)
    with d1: st.download_button(f"⬇️ PDF {len(finales)} JUEGOS", pdf_bytes.getvalue(), f"loteria_{len(finales)}_juegos.pdf", "application/pdf", use_container_width=True)
    with d2: st.download_button(f"⬇️ ZIP {len(finales)} JPGs", zip_bytes.getvalue(), f"loteria_{len(finales)}_juegos.zip", "application/zip", use_container_width=True)
