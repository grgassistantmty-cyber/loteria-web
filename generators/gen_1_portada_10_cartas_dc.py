import os, random, io, zipfile, gc
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

try:
    from app import BASE_PATH, EXCEL_COLORS, get_contador, inc_contador, inc_baraja, banner_top, banner_facebook, banner_venta_offline, copiar_clabe_component, instrucciones_html, ir_a, listar_barajas
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

# === FIJOS - TU MEJOR POSICION ===
FONT_NUM_FIJO = 151
FONT_TXT_FIJO = 91
TXT_PREF_FIJO = "PREFERIDA"
TXT_CARTAS_FIJO = "CARTAS"
OFFSET_TOP_FIJO = 100
OFFSET_BOTTOM_FIJO = 100

CARTAS_UNICAS_GLOBAL_JUEGO = set()
USADOS_POR_POSICION_HOJA = {}

def cargar_fuente(tam):
    posibles = ["arialbd.ttf","arial.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]
    for f in posibles:
        try: return ImageFont.truetype(f, tam)
        except: continue
    return ImageFont.load_default()

def cargar_imagenes(carpeta):
    if not os.path.exists(carpeta): return []
    files=[os.path.join(carpeta,f) for f in os.listdir(carpeta) if f.lower().endswith((".png",".jpg",".jpeg",".webp"))]
    files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))) or 0))
    return files

def crear_carta_imagen_rectangular(data16, card_w=600, card_h=850, div_interno=1, fast=False):
    cell_w=card_w//4; cell_h=card_h//4
    img=Image.new("RGB",(card_w,card_h), "black")
    for idx, ruta in enumerate(data16):
        try:
            im=Image.open(ruta).convert("RGB")
            if fast: im.thumbnail((150,150), Image.LANCZOS)
            im=im.resize((cell_w-div_interno, cell_h-div_interno), Image.LANCZOS)
        except:
            im=Image.new("RGB",(cell_w-div_interno, cell_h-div_interno),"white")
        col=idx%4; row=idx//4
        img.paste(im,(col*cell_w + div_interno//2, row*cell_h + div_interno//2))
    return img

def posiciones_preferida_variadas_por_hoja():
    orilla=[0,1,2,3,4,7,8,11,12,13,14,15]
    random.shuffle(orilla)
    return [9,10]+orilla[:8]

def buscar_equivalente_baraja(portada_path, baraja_files):
    base=os.path.splitext(os.path.basename(portada_path))[0].lower()
    for f in baraja_files:
        if os.path.splitext(os.path.basename(f))[0].lower()==base: return f
    return None

def crear_panel_con_texto_editable(portada_path, w, h, color_fondo, font_num_size, font_txt_size, txt_pref, txt_cartas, offset_top, offset_bottom):
    panel=Image.new("RGB",(w,h), color_fondo)
    draw=ImageDraw.Draw(panel)
    font_num=cargar_fuente(font_num_size); font_txt=cargar_fuente(font_txt_size)
    top_h=int(h*0.14); bottom_h=int(h*0.14); middle_h=h-top_h-bottom_h
    try:
        img_pref=Image.open(portada_path).convert("RGB")
        img_pref.thumbnail((600,750), Image.LANCZOS)
        w_target=w-8; ratio=w_target/img_pref.width; h_target=int(img_pref.height*ratio)
        if h_target>middle_h-16:
            h_target=middle_h-16; w_target=int(img_pref.width*h_target/img_pref.height)
            w_target=min(w_target,w-8); img_pref=img_pref.resize((w_target,h_target), Image.LANCZOS)
        else: img_pref=img_pref.resize((w_target,h_target), Image.LANCZOS)
        panel.paste(img_pref,((w-w_target)//2, top_h+(middle_h-h_target)//2))
    except: pass
    draw.text((w//2, top_h*0.28+offset_top), "1", fill="white", anchor="mm", font=font_num, stroke_width=6, stroke_fill="black")
    draw.text((w//2, top_h*0.72+offset_top), txt_pref, fill="white", anchor="mm", font=font_txt, stroke_width=4, stroke_fill="black")
    draw.text((w//2, h-bottom_h+bottom_h*0.28-offset_bottom), "10", fill="white", anchor="mm", font=font_num, stroke_width=6, stroke_fill="black")
    draw.text((w//2, h-bottom_h+bottom_h*0.72-offset_bottom), txt_cartas, fill="white", anchor="mm", font=font_txt, stroke_width=4, stroke_fill="black")
    return panel

def generar_10_balanceado_FAST_PREVIEW(baraja_files, preferida_portada_path, color_entre, div_interno, sep_entre):
    CW,CH=300,425; cols,rows=5,2
    W=cols*CW+(cols-1)*sep_entre; H=rows*CH+(rows-1)*sep_entre
    cartas_data=[random.sample(baraja_files,16) for _ in range(10)]
    tablero=Image.new("RGB",(W,H), color_entre)
    for idx,data16 in enumerate(cartas_data):
        card_img=crear_carta_imagen_rectangular(data16, CW, CH, div_interno, fast=True)
        tablero.paste(card_img,( (idx%cols)*(CW+sep_entre), (idx//cols)*(CH+sep_entre) ))
    panel=crear_panel_con_texto_editable(preferida_portada_path, CW, H, color_entre, 80, 50, TXT_PREF_FIJO, TXT_CARTAS_FIJO, 50, 50)
    sheet=Image.new("RGB",(CW+sep_entre+W,H), color_entre); sheet.paste(panel,(0,0)); sheet.paste(tablero,(CW+sep_entre,0))
    return sheet

def generar_10_balanceado(baraja_files, preferida_portada_path, color_entre, div_interno, sep_entre, orientacion, dups_de_esta_hoja):
    global CARTAS_UNICAS_GLOBAL_JUEGO, USADOS_POR_POSICION_HOJA
    CW,CH=600,850
    ori=orientacion.upper()
    if "10X1" in ori: cols,rows=10,1
    elif "1X10" in ori: cols,rows=1,10
    elif "5X2" in ori: cols,rows=5,2
    else: cols,rows=2,5
    W=cols*CW+(cols-1)*sep_entre; H=rows*CH+(rows-1)*sep_entre
    pref_baraja=buscar_equivalente_baraja(preferida_portada_path, baraja_files) or random.choice(baraja_files)
    pref_name=os.path.splitext(os.path.basename(pref_baraja))[0].lower()
    baraja_filtrada=[f for f in baraja_files if os.path.splitext(os.path.basename(f))[0].lower()!=pref_name] or baraja_files
    dups_filtrados=[d for d in dups_de_esta_hoja if os.path.splitext(os.path.basename(d))[0].lower()!=pref_name]
    while len(dups_filtrados)<10: dups_filtrados.append(random.choice(baraja_filtrada))
    posiciones_preferida=posiciones_preferida_variadas_por_hoja()
    dups_nombres=[os.path.splitext(os.path.basename(d))[0].lower() for d in dups_filtrados]
    cartas_data=[]; USADOS_POR_POSICION_HOJA={i:set() for i in range(16)}; conteo_hoja={nom:2 for nom in dups_nombres}
    for idx_carta in range(10):
        dup=dups_filtrados[idx_carta]; dup_name=dups_nombres[idx_carta]
        top=[None]*16; top[5]=dup; top[6]=dup; top[posiciones_preferida[idx_carta % len(posiciones_preferida)]]=pref_baraja
        usados=set([dup,pref_baraja]); usados_nombres=set([dup_name,pref_name])
        for pos in range(16):
            if top[pos] is not None: continue
            cand=[f for f in baraja_filtrada if f not in usados and os.path.splitext(os.path.basename(f))[0].lower() not in usados_nombres]
            if not cand: cand=baraja_filtrada
            elegido=random.choice(cand); top[pos]=elegido; usados.add(elegido); usados_nombres.add(os.path.splitext(os.path.basename(elegido))[0].lower())
        cartas_data.append(top)
    tablero=Image.new("RGB",(W,H), color_entre)
    for idx,data16 in enumerate(cartas_data):
        card_img=crear_carta_imagen_rectangular(data16, CW, CH, div_interno)
        tablero.paste(card_img,( (idx%cols)*(CW+sep_entre), (idx//cols)*(CH+sep_entre) ))
    panel=crear_panel_con_texto_editable(preferida_portada_path, CW, H, color_entre, FONT_NUM_FIJO, FONT_TXT_FIJO, TXT_PREF_FIJO, TXT_CARTAS_FIJO, OFFSET_TOP_FIJO, OFFSET_BOTTOM_FIJO)
    sheet=Image.new("RGB",(CW+sep_entre+W,H), color_entre); sheet.paste(panel,(0,0)); sheet.paste(tablero,(CW+sep_entre,0))
    return sheet

def crear_pdf_tabloide(lista_imgs):
    # PDF tabloide 11x17 pulgadas usando solo Pillow (sin reportlab para no instalar)
    if not lista_imgs: return None
    # Convertir a RGB y guardar como PDF multipagina
    pdf_buffer = io.BytesIO()
    # Tamaño tabloide 11x17 a 200dpi = 2200x3400 para PDF
    imgs_rgb = []
    for im in lista_imgs:
        # Ajustar a tabloide
        target_w, target_h = 2200, 3400
        # Crear pagina tabloide blanca
        pagina = Image.new("RGB", (target_w, target_h), "white")
        # Escalar imagen manteniendo aspecto
        im_copy = im.copy()
        im_copy.thumbnail((target_w-100, target_h-100), Image.LANCZOS)
        x = (target_w - im_copy.width)//2
        y = (target_h - im_copy.height)//2
        pagina.paste(im_copy, (x,y))
        imgs_rgb.append(pagina)
    imgs_rgb[0].save(pdf_buffer, format="PDF", save_all=True, append_images=imgs_rgb[1:], resolution=200)
    pdf_buffer.seek(0)
    return pdf_buffer

def render():
    global CARTAS_UNICAS_GLOBAL_JUEGO
    st.markdown(banner_top("1 PREFERIDA + 10 CARTAS - 1 JUEGO"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True)
    copiar_clabe_component()
    if "entrada_registrada_10portada" not in st.session_state:
        inc_contador("visita_10portada"); st.session_state["entrada_registrada_10portada"]=True
    st.markdown(instrucciones_html("1 PREFERIDA + 10 CARTAS - LIMITADO 1 JUEGO"), unsafe_allow_html=True)
    barajas_paths = listar_barajas()
    if not barajas_paths:
        st.error("No hay barajas"); return
    portadas_root="portadas"
    portadas_list=sorted([d for d in os.listdir(portadas_root) if os.path.isdir(os.path.join(portadas_root,d))]) if os.path.exists(portadas_root) else []
    c1,c2,c3=st.columns(3)
    with c1:
        baraja_sel=st.selectbox("📁 BARAJA:", [os.path.basename(p) for p in barajas_paths])
        baraja_path=os.path.join("barajas",baraja_sel)
    with c2:
        portada_sel=st.selectbox("🎨 PORTADAS:", portadas_list) if portadas_list else "portadas"
        portada_path_root=os.path.join(portadas_root,portada_sel) if portadas_list else portadas_root
    with c3:
        ori=st.selectbox("ORIENTACION:", ["5x2 HORIZONTAL","2x5 VERTICAL"], index=0)
    c4,c5=st.columns(2)
    with c4: div_int=st.number_input("Div interno",0,20,1)
    with c5: sep=st.number_input("Separacion",0,200,30)
    color_hex=st.color_picker("Color fondo", "#FF00FF")

    files_baraja=cargar_imagenes(baraja_path); files_portada=cargar_imagenes(portada_path_root)
    st.info(f"Baraja: {len(files_baraja)} | Portadas: {len(files_portada)} | LIMITADO 1 JUEGO (54 hojas) | FIJO 151/91")

    if st.button("👁️ VISTA PREVIA RÁPIDA", use_container_width=True):
        pref=random.choice(files_portada)
        sheet=generar_10_balanceado_FAST_PREVIEW(files_baraja, pref, color_hex, div_int, sep)
        st.image(sheet, use_container_width=True)
        st.session_state["preview_ok"]=True
        st.session_state["pref_preview"]=pref

    if st.button("🎰 GENERAR 1 JUEGO COMPLETO (54 HOJAS)", type="primary", use_container_width=True):
        if len(files_baraja)<54 or len(files_portada)<54:
            st.error("Faltan 54 imgs"); return
        inc_contador("10portada"); inc_baraja(baraja_sel,"10portada")
        progress=st.progress(0); status=st.empty()
        CARTAS_UNICAS_GLOBAL_JUEGO=set()
        portadas_juego=files_portada[:54][:]; random.shuffle(portadas_juego)
        baraja_54=files_baraja[:54][:]; random.shuffle(baraja_54)
        extras=random.sample(baraja_54,6); todas=baraja_54+extras; random.shuffle(todas)
        grupos=[]; restantes=todas[:]
        for g in range(9):
            sel=random.sample(restantes,10) if len(restantes)>=10 else random.sample(files_baraja[:54],10)
            grupos.append(sel)
            for f in sel:
                if f in restantes: restantes.remove(f)
            if len(restantes)<10: restantes=files_baraja[:54][:]

        lista_imgs=[]
        for hoja in range(54):
            bloque=hoja//6; idx_in=hoja%6
            dups=grupos[bloque] if bloque < len(grupos) else random.sample(files_baraja[:54],10)
            pref=portadas_juego[hoja]
            progress.progress((hoja+1)/54); status.text(f"Generando hoja {hoja+1}/54")
            sheet=generar_10_balanceado(files_baraja[:54], pref, color_hex, div_int, sep, ori, dups)
            lista_imgs.append(sheet.copy())
            del sheet; gc.collect()

        st.session_state["juego_imgs"]=lista_imgs
        st.session_state["juego_baraja"]=baraja_sel
        status.success("¡54 hojas generadas! Ahora puedes descargar PDF o JPG")
        progress.empty()

    if "juego_imgs" in st.session_state and st.session_state["juego_imgs"]:
        st.divider()
        st.subheader("📥 DESCARGAS - 1 JUEGO")
        col1,col2=st.columns(2)
        with col1:
            if st.button("📕 GENERAR PDF TABLOIDE (54 páginas)", use_container_width=True):
                with st.spinner("Creando PDF tabloide 11x17..."):
                    pdf_buf=crear_pdf_tabloide(st.session_state["juego_imgs"])
                    st.session_state["pdf_buf"]=pdf_buf.getvalue()
                st.success("PDF listo")
            if "pdf_buf" in st.session_state:
                st.download_button("⬇️ DESCARGAR PDF TABLOIDE", st.session_state["pdf_buf"], file_name=f"{st.session_state['juego_baraja']}_1_JUEGO_TABLOIDE.pdf", mime="application/pdf", use_container_width=True)
        with col2:
            if st.button("🖼️ GENERAR ZIP 54 JPG", use_container_width=True):
                with st.spinner("Empaquetando 54 JPG..."):
                    zip_buf=io.BytesIO()
                    with zipfile.ZipFile(zip_buf,"w",zipfile.ZIP_DEFLATED) as zf:
                        for i,img in enumerate(st.session_state["juego_imgs"]):
                            b=io.BytesIO(); img.save(b, format="JPEG", quality=90); zf.writestr(f"HOJA_{i+1:02d}.jpg", b.getvalue())
                    st.session_state["zip_buf"]=zip_buf.getvalue()
                st.success("ZIP listo")
            if "zip_buf" in st.session_state:
                st.download_button("⬇️ DESCARGAR ZIP 54 JPG", st.session_state["zip_buf"], file_name=f"{st.session_state['juego_baraja']}_54_JPG.zip", mime="application/zip", use_container_width=True)

    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
