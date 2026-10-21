import os, random, io, zipfile, gc
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

try:
    from app import BASE_PATH, get_contador, inc_contador, inc_baraja, banner_top, banner_facebook, banner_venta_offline, copiar_clabe_component, instrucciones_html, ir_a, listar_barajas
except:
    BASE_PATH = Path(".")
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

# === FIJO ORIGINAL COMO TU FOTO DE LA MANO ===
FONT_NUM_FIJO = 240
FONT_TXT_FIJO = 95

def cargar_fuente(tam):
    for f in ["arialbd.ttf","arial.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(f, tam)
        except: continue
    return ImageFont.load_default()

def cargar_imagenes(carpeta):
    if not os.path.exists(carpeta): return []
    files=[os.path.join(carpeta,f) for f in os.listdir(carpeta) if f.lower().endswith((".png",".jpg",".jpeg",".webp"))]
    return sorted(files)

def crear_panel_ORIGINAL_FIJO(portada_path, w, h, color_fondo):
    panel=Image.new("RGB",(w,h), color_fondo)
    draw=ImageDraw.Draw(panel)
    font_num=cargar_fuente(FONT_NUM_FIJO)
    font_txt=cargar_fuente(FONT_TXT_FIJO)
    top_h=int(h*0.18)
    bottom_h=int(h*0.18)
    middle_h=h-top_h-bottom_h
    try:
        img=Image.open(portada_path).convert("RGB")
        img=img.resize((w-8, middle_h-8), Image.LANCZOS)
        panel.paste(img,(4, top_h+4))
    except: pass
    draw.text((w//2, top_h*0.35), "1", fill="white", anchor="mm", font=font_num, stroke_width=14, stroke_fill="black")
    draw.text((w//2, top_h*0.78), "PREFERIDA", fill="white", anchor="mm", font=font_txt, stroke_width=7, stroke_fill="black")
    draw.text((w//2, h-bottom_h*0.65), "10", fill="white", anchor="mm", font=font_num, stroke_width=14, stroke_fill="black")
    draw.text((w//2, h-bottom_h*0.22), "CARTAS", fill="white", anchor="mm", font=font_txt, stroke_width=7, stroke_fill="black")
    return panel

def crear_carta_HD(data16, card_w=600, card_h=850, div=1):
    cell_w=card_w//4; cell_h=card_h//4
    img=Image.new("RGB",(card_w,card_h),"black")
    for idx,ruta in enumerate(data16):
        try: im=Image.open(ruta).convert("RGB").resize((cell_w-div, cell_h-div), Image.LANCZOS)
        except: im=Image.new("RGB",(cell_w-div, cell_h-div),"white")
        img.paste(im,( (idx%4)*cell_w+div//2, (idx//4)*cell_h+div//2 ))
    return img

def generar_10_HD(baraja_files, pref_path, color_fondo, div, sep, ori, dups):
    CW,CH=600,850
    cols,rows= (5,2) if "5x2" in ori.upper() else (2,5)
    if "10X1" in ori.upper(): cols,rows=10,1
    if "1X10" in ori.upper(): cols,rows=1,10
    W=cols*CW+(cols-1)*sep; H=rows*CH+(rows-1)*sep
    
    # BALANCEO REAL SIN REPETIR
    cartas_data=[]
    usadas=set()
    for i in range(10):
        dup=dups[i] if i < len(dups) else random.choice(baraja_files)
        disponibles=[f for f in baraja_files if f not in usadas and f!=dup]
        if len(disponibles)<15: disponibles=baraja_files
        sample=random.sample(disponibles,15)
        usadas.update(sample)
        usadas.add(dup)
        data=[dup]+sample
        random.shuffle(data)
        cartas_data.append(data[:16])

    tablero=Image.new("RGB",(W,H), color_fondo)
    for idx,data16 in enumerate(cartas_data):
        card_img=crear_carta_HD(data16, CW, CH, div)
        tablero.paste(card_img,( (idx%cols)*(CW+sep), (idx//cols)*(CH+sep) ))

    panel=crear_panel_ORIGINAL_FIJO(pref_path, CW, H, color_fondo)
    sheet=Image.new("RGB",(CW+sep+W,H), color_fondo)
    sheet.paste(panel,(0,0))
    sheet.paste(tablero,(CW+sep,0))
    return sheet

def crear_pdf_tabloide(lista_imgs):
    pdf_buffer=io.BytesIO()
    paginas=[]
    for im in lista_imgs:
        target_w,target_h=2200,3400
        pagina=Image.new("RGB",(target_w,target_h),"white")
        im_copy=im.copy()
        im_copy.thumbnail((target_w-100, target_h-100), Image.LANCZOS)
        pagina.paste(im_copy, ((target_w-im_copy.width)//2, (target_h-im_copy.height)//2))
        paginas.append(pagina)
    if paginas:
        paginas[0].save(pdf_buffer, format="PDF", save_all=True, append_images=paginas[1:], resolution=200)
    pdf_buffer.seek(0)
    return pdf_buffer

def render():
    st.markdown(banner_top("1 PREFERIDA + 10 CARTAS - 1 JUEGO ORIGINAL"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    if "entrada_registrada_10portada" not in st.session_state:
        inc_contador("visita_10portada"); st.session_state["entrada_registrada_10portada"]=True
    st.markdown(instrucciones_html("1 PREFERIDA + 10 CARTAS - ORIGINAL FIJO 1 JUEGO"), unsafe_allow_html=True)

    barajas_paths=listar_barajas()
    portadas_root="portadas"
    portadas_list=sorted([d for d in os.listdir(portadas_root) if os.path.isdir(os.path.join(portadas_root,d))]) if os.path.exists(portadas_root) else []

    c1,c2,c3=st.columns(3)
    with c1:
        baraja_sel=st.selectbox("📁 BARAJA:", [os.path.basename(p) for p in barajas_paths])
        baraja_path=os.path.join("barajas",baraja_sel)
    with c2:
        portada_sel=st.selectbox("🎨 PORTADAS:", portadas_list) if portadas_list else ""
        portada_path_root=os.path.join(portadas_root,portada_sel) if portadas_list else portadas_root
    with c3:
        ori=st.selectbox("ORIENTACION:", ["5x2 HORIZONTAL","2x5 VERTICAL"], index=0)

    c4,c5=st.columns(2)
    with c4: div_int=st.number_input("Div interno",0,20,1)
    with c5: sep=st.number_input("Separacion",0,200,30)
    color_hex=st.color_picker("Color fondo", "#FF00FF")

    files_baraja=cargar_imagenes(baraja_path)
    files_portada=cargar_imagenes(portada_path_root)
    st.info(f"Baraja: {len(files_baraja)} | Portadas: {len(files_portada)} | ORIGINAL FIJO")

    # === VISTA PREVIA REAL 1 HOJA ===
    if st.button("👁️ VISTA PREVIA REAL (1 HOJA)", use_container_width=True):
        if not files_baraja or not files_portada:
            st.error("Faltan imagenes"); return
        pref=random.choice(files_portada)
        dups_demo=random.sample(files_baraja[:54], 10)
        with st.spinner("Generando 1 hoja real con balanceo..."):
            sheet=generar_10_HD(files_baraja[:54], pref, color_hex, div_int, sep, ori, dups_demo)
        st.image(sheet, use_container_width=True)
        st.success("Vista previa REAL - así sale sin repetir")

    # === GENERAR 54 HOJAS ===
    if st.button("🎰 GENERAR 1 JUEGO COMPLETO (54 HOJAS)", type="primary", use_container_width=True):
        if len(files_baraja)<54 or len(files_portada)<54:
            st.error("Necesitas minimo 54 y 54"); return
        inc_contador("10portada"); inc_baraja(baraja_sel,"10portada")
        progress=st.progress(0); status=st.empty()
        portadas_juego=files_portada[:54]; random.shuffle(portadas_juego)
        baraja_54=files_baraja[:54]; random.shuffle(baraja_54)
        extras=random.sample(baraja_54,6); todas=baraja_54+extras; random.shuffle(todas)
        grupos=[todas[i*10:(i+1)*10] for i in range(5)] + [todas[50:]]
        while len(grupos)<9: grupos.append(random.sample(baraja_54,10))
        lista_imgs=[]
        for hoja in range(54):
            bloque=hoja//6
            dups=grupos[bloque] if bloque < len(grupos) else random.sample(baraja_54,10)
            pref=portadas_juego[hoja]
            progress.progress((hoja+1)/54)
            status.text(f"Hoja {hoja+1}/54 - REAL")
            sheet=generar_10_HD(files_baraja[:54], pref, color_hex, div_int, sep, ori, dups)
            lista_imgs.append(sheet.copy())
            del sheet; gc.collect()
        st.session_state["juego_imgs"]=lista_imgs
        st.session_state["juego_baraja"]=baraja_sel
        status.success("¡54 hojas reales listas!")
        progress.empty()

    if "juego_imgs" in st.session_state and st.session_state["juego_imgs"]:
        st.divider()
        st.subheader("📥 DESCARGAS - 1 JUEGO 54 HOJAS")
        col1,col2=st.columns(2)
        with col1:
            if st.button("📕 CREAR PDF TABLOIDE", use_container_width=True, key="pdf_btn"):
                with st.spinner("Creando PDF tabloide..."):
                    pdf_buf=crear_pdf_tabloide(st.session_state["juego_imgs"])
                    st.session_state["pdf_buf"]=pdf_buf.getvalue()
                st.success("PDF tabloide listo")
            if "pdf_buf" in st.session_state:
                st.download_button("⬇️ DESCARGAR 1 JUEGO PDF TABLOIDE", st.session_state["pdf_buf"], file_name=f"{st.session_state['juego_baraja']}_1_JUEGO_TABLOIDE.pdf", mime="application/pdf", use_container_width=True, key="dl_pdf")
        with col2:
            if st.button("🖼️ CREAR ZIP 54 JPG", use_container_width=True, key="zip_btn"):
                with st.spinner("Empaquetando JPGs..."):
                    zip_buf=io.BytesIO()
                    with zipfile.ZipFile(zip_buf,"w",zipfile.ZIP_DEFLATED) as zf:
                        for i,img in enumerate(st.session_state["juego_imgs"]):
                            b=io.BytesIO(); img.save(b, format="JPEG", quality=90); zf.writestr(f"HOJA_{i+1:02d}.jpg", b.getvalue())
                    st.session_state["zip_buf"]=zip_buf.getvalue()
                st.success("ZIP listo")
            if "zip_buf" in st.session_state:
                st.download_button("⬇️ DESCARGAR 54 PLANILLAS JPG ZIP", st.session_state["zip_buf"], file_name=f"{st.session_state['juego_baraja']}_54_JPG.zip", mime="application/zip", use_container_width=True, key="dl_zip")

    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
