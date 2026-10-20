import random, io
from PIL import Image, ImageDraw
from utils.barajas import cm_to_px

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
        for idx,d16 in enumerate(cartas_data):
            col=idx%2; row=idx//2; x=col*(CARD_W+sep_v); y=row*(CARD_H+sep_h); sheet.paste(crear_carta_ajustada_4x4dob(d16, CARD_W, div_interno, g_negro, aspecto),(x,y))
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
