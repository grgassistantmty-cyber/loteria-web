import os, threading
from PIL import Image

_lock = threading.Lock()
def get_lock(): return _lock

def no_chocan(x, y, w, h, ocupados, margen=0):
    x2, y2 = x+w+margen, y+h+margen
    for ox, oy, ow, oh in ocupados:
        if not (x2 < ox or x > ox+ow or y2 < oy or y > oy+oh):
            return False
    return True

# Esto arregla RIGHT5, LEFT5, RIGHT4, LEFT4, etc para TODOS los cores
def __getattr__(name):
    if name.startswith(("RIGHT","LEFT","TOP","BOTTOM")):
        return 0
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def listar_barajas(carpeta="barajas"):
    if not os.path.exists(carpeta): return []
    return [d for d in os.listdir(carpeta) if os.path.isdir(os.path.join(carpeta, d))]

def get_aspecto(ruta):
    try:
        with Image.open(ruta) as im:
            w,h = im.size
            return w/h if h else 1.0
    except: return 1.0

def cm_to_px(cm, dpi=300): return int(cm/2.54*dpi)
def cargar_files(lista): return [p for p in lista if os.path.exists(p)]

def cargar_zip_temporal(uploaded_file, temp_dir="/tmp/baraja_temp"):
    import zipfile
    os.makedirs(temp_dir, exist_ok=True)
    path_zip = os.path.join(temp_dir, uploaded_file.name)
    with open(path_zip, "wb") as f: f.write(uploaded_file.getbuffer())
    archivos=[]
    with zipfile.ZipFile(path_zip, 'r') as z:
        z.extractall(temp_dir)
        for root,_,files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(('.png','.jpg','.jpeg','.webp')):
                    archivos.append(os.path.join(root,file))
    return archivos

def cargar_imagenes_sueltas(uploaded_files, temp_dir="/tmp/baraja_suelta"):
    os.makedirs(temp_dir, exist_ok=True)
    archivos=[]
    for uf in uploaded_files:
        path = os.path.join(temp_dir, uf.name)
        with open(path, "wb") as f: f.write(uf.getbuffer())
        archivos.append(path)
    return archivos
