import os, random, glob, io, tempfile
from PIL import Image
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# === TU CODIGO BUENO ORIGINAL - MITADES PERFECTAS INTACTAS ===
COMODINES_DEF = [
    [(1,2,'C'), (2,2,'C'), (12,3,'C')], [(1,3,'M1'), (6,2,'M2'), (11,2,'C')],
    [(2,3,'M1'), (6,3,'C'), (7,2,'M2')], [(7,3,'M1'), (11,3,'C'), (12,2,'M2')],
    [(16,2,'C'), (17,2,'C'), (27,3,'C')], [(16,3,'M1'),(21,2,'M2'), (26,2,'C')],
    [(17,3,'M1'),(21,3,'C'), (22,2,'M2')], [(22,3,'M1'),(26,3,'C'), (27,2,'M2')],
    [(3,2,'C'), (4,2,'C'), (14,3,'C')], [(3,3,'M1'), (8,2,'M2'), (13,2,'C')],
    [(4,3,'M1'), (8,3,'C'), (9,2,'M2')], [(9,3,'M1'), (13,3,'C'), (14,2,'M2')],
]
RESTANTES_DEF = [
    [(1,1,'C')], [(6,1,'C')], [(11,1,'C')], [(16,1,'C')], [(21,1,'C')], [(26,1,'C')],
    [(2,1,'C')], [(7,1,'C')], [(12,1,'C')], [(17,1,'C')], [(22,1,'C')], [(27,1,'C')],
    [(3,1,'C')], [(8,1,'C')], [(13,1,'C')], [(18,1,'C')], [(23,1,'C')], [(28,1,'C')],
    [(4,1,'C')], [(9,1,'C')], [(14,1,'C')], [(19,1,'C')], [(24,1,'C')], [(29,1,'C')],
    [(5,1,'C')], [(10,1,'C')], [(15,1,'C')], [(20,1,'C')], [(25,1,'C')], [(30,1,'C')],
    [(18,3,'M1'), (23,2,'M2')], [(23,3,'M1'), (28,2,'M2')], [(19,3,'M1'), (24,2,'M2')],
    [(24,3,'M1'), (29,2,'M2')], [(5,3,'M1'), (10,2,'M2')], [(10,3,'M1'), (15,2,'M2')],
    [(20,3,'M1'), (25,2,'M2')], [(25,3,'M1'), (30,2,'M2')], [(18,2,'C'), (28,3,'C')],
    [(19,2,'C'), (29,3,'C')], [(5,2,'C'), (15,3,'C')], [(20,2,'C'), (30,3,'C')],
]
ORDEN = [[1,6,11,16,21,26],[2,7,12,17,22,27],[3,8,13,18,23,28],[4,9,14,19,24,29],[5,10,15,20,25,30]]

def get_crop_image_pil(path, tipo):
    im = Image.open(path).convert("RGB")
    w,h = im.size
    if tipo == 'M1': im = im.crop((0,0,w,h//2))
    elif tipo == 'M2': im = im.crop((0,h//2,w,h))
    return im

def generar_tabloide_pil(baraja_files, tmpdir):
    """Genera 1 juego (6 cartas = 3x2 en tabloide) en PIL Image para preview"""
    # Retorna lista de 6 PIL Images (cada juego)
    baraja_temp = baraja_files[:]
    random.shuffle(baraja_temp)
    comodines_12 = baraja_temp[:12]
    resto = [x for x in baraja_files if x not in comodines_12]
    random.shuffle(resto)
    restantes_42 = resto[:42]
    mapa = {}
    for idx, tercia in enumerate(COMODINES_DEF):
        fig = comodines_12[idx]
        for pozo,secc,tipo in tercia: mapa[(pozo,secc)] = (fig, tipo)
    for idx, grupo in enumerate(RESTANTES_DEF):
        fig = restantes_42[idx]
        for pozo,secc,tipo in grupo: mapa[(pozo,secc)] = (fig, tipo)
    
    # Crear imagen grande de 30 pozos (1 carta de pocitos = 5x6)
    W,H = 1000, 1200
    juego_img = Image.new("RGB",(W,H),"white")
    cell_w, cell_h = W//5, H//6
    for col_idx in range(5):
        for r in range(6):
            pozo_num = ORDEN[col_idx][r]
            x = col_idx*cell_w; y = (5-r)*cell_h
            g_w, s_w, s_h = int(cell_w*0.50), int(cell_w*0.50), cell_h//2
            # sección 1 completa
            if (pozo_num,1) in mapa:
                p1,t1 = mapa[(pozo_num,1)]
                im1 = get_crop_image_pil(p1,t1).resize((g_w, cell_h), Image.LANCZOS)
                juego_img.paste(im1,(x,y))
            # sección 2 mitad arriba
            if (pozo_num,2) in mapa:
                p2,t2 = mapa[(pozo_num,2)]
                im2 = get_crop_image_pil(p2,t2).resize((s_w, s_h), Image.LANCZOS)
                juego_img.paste(im2,(x+g_w, y+s_h))
            # sección 3 mitad abajo
            if (pozo_num,3) in mapa:
                p3,t3 = mapa[(pozo_num,3)]
                im3 = get_crop_image_pil(p3,t3).resize((s_w, s_h), Image.LANCZOS)
                juego_img.paste(im3,(x+g_w, y))
    return juego_img

def generar_pdf_bytes_pocitos(baraja_files, num_tabloides=1):
    PAGE_W, PAGE_H = landscape((11*72, 17*72))
    J_COLS, J_ROWS = 3,2
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H))
    
    tmpdir = tempfile.mkdtemp()
    
    for tab in range(num_tabloides):
        margen, sep = 0.15*inch, 0.28*inch
        area_w = PAGE_W - margen*2 - sep*(J_COLS-1)
        area_h = PAGE_H - margen*2 - sep*(J_ROWS-1)
        juego_w, juego_h = area_w/J_COLS, area_h/J_ROWS
        
        for jr in range(J_ROWS):
            for jc in range(J_COLS):
                baraja_temp = baraja_files[:]
                random.shuffle(baraja_temp)
                comodines_12 = baraja_temp[:12]
                resto = [x for x in baraja_files if x not in comodines_12]
                random.shuffle(resto)
                restantes_42 = resto[:42]
                mapa = {}
                for idx, tercia in enumerate(COMODINES_DEF):
                    fig = comodines_12[idx]
                    for pozo,secc,tipo in tercia: mapa[(pozo,secc)] = (fig, tipo)
                for idx, grupo in enumerate(RESTANTES_DEF):
                    fig = restantes_42[idx]
                    for pozo,secc,tipo in grupo: mapa[(pozo,secc)] = (fig, tipo)

                for col_idx in range(5):
                    for r in range(6):
                        pozo_num = ORDEN[col_idx][r]
                        j_x = margen + jc*(juego_w+sep)
                        j_y = margen + (J_ROWS-1-jr)*(juego_h+sep)
                        cell_w, cell_h = juego_w/5, juego_h/6
                        x = j_x + col_idx*cell_w; y = j_y + (5-r)*cell_h
                        g_w, s_w, s_h = cell_w*0.50, cell_w*0.50, cell_h/2
                        
                        p1,t1 = mapa[(pozo_num,1)]
                        im1 = get_crop_image_pil(p1,t1)
                        tmp1 = os.path.join(tmpdir, f"t1_{tab}_{jc}_{jr}_{pozo_num}.jpg")
                        im1.save(tmp1)
                        c.drawImage(ImageReader(tmp1), x, y, g_w, cell_h, preserveAspectRatio=False)
                        os.remove(tmp1)
                        
                        p2,t2 = mapa[(pozo_num,2)]
                        im2 = get_crop_image_pil(p2,t2)
                        tmp2 = os.path.join(tmpdir, f"t2_{tab}_{jc}_{jr}_{pozo_num}.jpg")
                        im2.save(tmp2)
                        c.drawImage(ImageReader(tmp2), x+g_w, y+s_h, s_w, s_h, preserveAspectRatio=False)
                        os.remove(tmp2)
                        
                        p3,t3 = mapa[(pozo_num,3)]
                        im3 = get_crop_image_pil(p3,t3)
                        tmp3 = os.path.join(tmpdir, f"t3_{tab}_{jc}_{jr}_{pozo_num}.jpg")
                        im3.save(tmp3)
                        c.drawImage(ImageReader(tmp3), x+g_w, y, s_w, s_h, preserveAspectRatio=False)
                        os.remove(tmp3)
                        
                        c.setLineWidth(0.5); c.rect(x, y, cell_w, cell_h)
                
                j_x = margen + jc*(juego_w+sep); j_y = margen + (J_ROWS-1-jr)*(juego_h+sep)
                c.setStrokeColorRGB(1,0,0); c.setLineWidth(4); c.rect(j_x, j_y, juego_w, juego_h)
                c.setLineWidth(2)
                for i in range(1,5): c.line(j_x+i*(juego_w/5), j_y, j_x+i*(juego_w/5), j_y+juego_h)
                for i in range(1,6): c.line(j_x, j_y+i*(juego_h/6), j_x+juego_w, j_y+i*(juego_h/6))
                c.setStrokeColorRGB(0,0,0)
        c.showPage()
    c.save()
    return buffer.getvalue()
