import os, glob
from PIL import Image

RIGHT4=[3,7,11,15]; LEFT4=[0,4,8,12]; BOTTOM4=[12,13,14,15]; TOP4=[0,1,2,3]
RIGHT5=[4,9,14,19,24]; LEFT5=[0,5,10,15,20]; BOTTOM5=[20,21,22,23,24]; TOP5=[0,1,2,3,4]

# Alias para que no falle RIGHT5 viejo
RIGHT5 = RIGHT5; LEFT5 = LEFT5

def no_chocan(a,b, LA, LB):
    for i, pos_a in enumerate(LA):
        pos_b = LB[i]
        if a[pos_a] is None or b[pos_b] is None: continue
        if a[pos_a]==b[pos_b]: return False
    return True

def listar_barajas(base="barajas"):
    if not os.path.exists(base): return []
    carpetas = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base,d))]
    return carpetas

def listar_imagenes_baraja(nombre_baraja):
    path = os.path.join("barajas", nombre_baraja)
    files = glob.glob(os.path.join(path,"*.jpg")) + glob.glob(os.path.join(path,"*.png")) + glob.glob(os.path.join(path,"*.jpeg"))
    return sorted(files)

def cm_to_px(cm, dpi): return int(cm/2.54 * dpi)

def get_aspecto(ruta):
    try:
        with Image.open(ruta) as im: return im.size[1]/im.size[0]
    except: return 1.45

# Para que no truene si importan desde barajas algo que no existe
def __getattr__(name):
    if name in ["RIGHT5","LEFT5","RIGHT4","LEFT4","BOTTOM4","TOP4","BOTTOM5","TOP5"]:
        return globals().get(name, [])
    raise AttributeError(name)
