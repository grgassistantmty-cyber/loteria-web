from PIL import Image, ImageDraw
import random, os

def cm_to_px(cm, dpi=300):
    return int(cm * dpi / 2.54)

def get_aspecto(files):
    try:
        if not files: return (1,1)
        with Image.open(files[0]) as im:
            return im.size
    except:
        return (500,700)

def _load_img(path, size=(300,420)):
    try:
        img = Image.open(path).convert("RGB")
        return img.resize(size)
    except:
        return Image.new("RGB", size, "white")

# ===== 4x4 =====
def generar_logica_4x4(files):
    return [random.sample(files, 16) for _ in range(4)]

def crear_carta_4x4(*args, **kwargs):
    # para compatibilidad
    return generar_hoja_4x4(*args, **kwargs)

def generar_hoja_4x4(logica, color_entre="#FF0000", div_interno=8, sep_v=20, sep_h=20, g_negro=6, aspecto=None, final_size=None, W_orig=1800):
    # logica puede ser [ [16], [16], [16], [16] ] o solo [16]
    if logica and isinstance(logica[0], list):
        files = logica[0]
    else:
        files = logica if isinstance(logica, list) else []
    
    cols, rows = 4, 4
    w, h = 1800, 2400
    if final_size:
        w, h = final_size
    hoja = Image.new("RGB", (w, h), color_entre)
    draw = ImageDraw.Draw(hoja)
    margin = 40
    cw = (w - margin*2 - sep_h*(cols-1)) // cols
    ch = (h - margin*2 - sep_v*(rows-1)) // rows
    for idx, path in enumerate(files[:16]):
        r = idx // cols
        c = idx % cols
        x = margin + c*(cw+sep_h)
        y = margin + r*(ch+sep_v)
        img = _load_img(path, (cw-div_interno*2, ch-div_interno*2))
        hoja.paste(img, (x+div_interno, y+div_interno))
        draw.rectangle([x, y, x+cw, y+ch], outline="black", width=g_negro)
    return hoja

def imagenes_a_pdf_4x4dob(imagenes):
    # dummy para que no truene, regresa bytes del primer png
    if not imagenes: return None
    import io
    buf = io.BytesIO()
    imagenes[0].save(buf, format="PDF")
    return buf.getvalue()

# ===== 5x5 =====
def generar_logica_5x5(files):
    return random.sample(files, min(25, len(files)))

def generar_hoja_5x5(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto):
    cols, rows = 5, 5
    w, h = 2480, 3508
    hoja = Image.new("RGB", (w, h), color_entre)
    draw = ImageDraw.Draw(hoja)
    margin = 50
    cw = (w - margin*2 - sep_h*(cols-1)) // cols
    ch = (h - margin*2 - sep_v*(rows-1)) // rows
    for idx, path in enumerate(logica[:25]):
        r = idx // cols
        c = idx % cols
        x = margin + c*(cw+sep_h)
        y = margin + r*(ch+sep_v)
        img = _load_img(path, (cw-div_interno*2, ch-div_interno*2))
        hoja.paste(img, (x+div_interno, y+div_interno))
        draw.rectangle([x, y, x+cw, y+ch], outline="black", width=g_negro)
    return hoja

# ===== 10 DOBLES =====
def generar_logica_10dobles(files):
    if len(files) < 54:
        return files
    base = random.sample(files, 52)
    duplicada = random.choice(base)
    logica = base[:4] + [duplicada, duplicada] + base[4:]
    return logica[:54]

def generar_hoja_10dobles(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto):
    cols, rows = 6, 9
    w, h = 2480, 3508
    hoja = Image.new("RGB", (w, h), color_entre)
    draw = ImageDraw.Draw(hoja)
    margin = 40
    cw = (w - margin*2 - sep_h*(cols-1)) // cols
    ch = (h - margin*2 - sep_v*(rows-1)) // rows
    for idx, path in enumerate(logica[:54]):
        r = idx // cols
        c = idx % cols
        x = margin + c*(cw+sep_h)
        y = margin + r*(ch+sep_v)
        img = _load_img(path, (cw-div_interno*2, ch-div_interno*2))
        hoja.paste(img, (x+div_interno, y+div_interno))
        draw.rectangle([x, y, x+cw, y+ch], outline="black", width=g_negro)
    return hoja

# ===== 12 + PORTADA =====
def generar_logica_12portada(files):
    return random.sample(files, min(12, len(files)))

def generar_hoja_12portada(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, sel_portada=None):
    w, h = 2480, 3508
    hoja = Image.new("RGB", (w, h), color_entre)
    draw = ImageDraw.Draw(hoja)
    margin = 50
    port_h = h // 3
    if sel_portada:
        base = "portadas" if os.path.exists("portadas") else "PORTADAS"
        p_path = os.path.join(base, sel_portada)
        if os.path.exists(p_path):
            p_img = _load_img(p_path, (w-margin*2, port_h-margin))
            hoja.paste(p_img, (margin, margin))
    top = port_h + margin + 20
    cols, rows = 4, 3
    cw = (w - margin*2 - sep_h*(cols-1)) // cols
    ch = (h - top - margin - sep_v*(rows-1)) // rows
    for idx, path in enumerate(logica[:12]):
        r = idx // cols
        c = idx % cols
        x = margin + c*(cw+sep_h)
        y = top + r*(ch+sep_v)
        img = _load_img(path, (cw-div_interno*2, ch-div_interno*2))
        hoja.paste(img, (x+div_interno, y+div_interno))
        draw.rectangle([x, y, x+cw, y+ch], outline="black", width=g_negro)
    return hoja

# ===== extras para gen_4x4doblesfix =====
def generar_logica_4x4dobles(files):
    return generar_logica_4x4(files)

def generar_hoja_4x4dobles(*args, **kwargs):
    return generar_hoja_4x4(*args, **kwargs)
