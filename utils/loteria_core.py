from PIL import Image, ImageDraw
import random
import os

# Para que no marque error de importación
def get_aspecto(files):
    try:
        if not files:
            return (1,1)
        with Image.open(files[0]) as im:
            return im.size
    except:
        return (500, 700)

def _load_img(path, size=(300,420)):
    try:
        img = Image.open(path).convert("RGB")
        return img.resize(size)
    except:
        return Image.new("RGB", size, "white")

def generar_logica_5x5(files):
    # 25 figuras aleatorias
    return random.sample(files, min(25, len(files))) if len(files) >= 25 else files

def generar_hoja_5x5(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto):
    # crea una hoja 5x5 simple
    cols, rows = 5, 5
    w, h = 2480, 3508  # A4
    hoja = Image.new("RGB", (w, h), color_entre)
    draw = ImageDraw.Draw(hoja)
    # fondo blanco con borde
    margin = 50
    cw = (w - margin*2 - sep_h*(cols-1)) // cols
    ch = (h - margin*2 - sep_v*(rows-1)) // rows
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= len(logica): break
            x = margin + c*(cw+sep_h)
            y = margin + r*(ch+sep_v)
            img = _load_img(logica[idx], (cw-div_interno*2, ch-div_interno*2))
            hoja.paste(img, (x+div_interno, y+div_interno))
            # borde negro
            draw.rectangle([x, y, x+cw, y+ch], outline="black", width=g_negro)
            idx+=1
    return hoja

# --- 10 DOBLES --- ESTA ES LA QUE TE MARCA ERROR
def generar_logica_10dobles(files):
    # 54 figuras, dobles en pos 5 y 6 (index 4 y 5)
    if len(files) < 54:
        return files
    base = random.sample(files, 52) # 52 únicas
    duplicada = random.choice(base)
    logica = base[:4] + [duplicada, duplicada] + base[4:] # inserta doble en 5 y 6
    return logica[:54]

def generar_hoja_10dobles(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto):
    # reutiliza la de 5x5 pero con 6x9 para 54 figuras aprox
    # simplificado: 6 columnas x 9 filas = 54
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

def generar_logica_12portada(files):
    return random.sample(files, min(12, len(files)))

def generar_hoja_12portada(logica, color_entre, div_interno, sep_v, sep_h, g_negro, aspecto, sel_portada=None):
    # 12 + portada gigante
    w, h = 2480, 3508
    hoja = Image.new("RGB", (w, h), color_entre)
    draw = ImageDraw.Draw(hoja)
    margin = 50
    # portada arriba grande
    port_h = h // 3
    if sel_portada:
        # sel_portada viene como "portadas01/archivo.jpg"
        base = "portadas" if os.path.exists("portadas") else "PORTADAS"
        p_path = os.path.join(base, sel_portada)
        if os.path.exists(p_path):
            p_img = _load_img(p_path, (w-margin*2, port_h-margin))
            hoja.paste(p_img, (margin, margin))
    # 12 abajo 4x3
    cols, rows = 4, 3
    top = port_h + margin + 20
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

# --- FUNCIONES QUE USAN LOS OTROS GENERADORES ---
def generar_logica_4x4(files):
    return [random.sample(files, 16) for _ in range(4)]

def generar_hoja_4x4(logica, *args, **kwargs):
    # logica es lista de 4 tablas de 16
    # para no romper, solo genera 1 hoja con la primera tabla
    files = logica[0] if isinstance(logica[0], list) else logica
    return generar_hoja_5x5(files[:16], "#FF0000", 8, 20, 20, 6, (1,1))

def generar_logica_4x4dobles(files):
    return generar_logica_4x4(files)

def generar_hoja_4x4dobles(logica, *args, **kwargs):
    return generar_hoja_4x4(logica, *args, **kwargs)

def imagenes_a_pdf_4x4dob(imagenes):
    return imagenes[0] if imagenes else None
