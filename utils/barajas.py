import os, glob
from PIL import Image
import threading

_lock = threading.Lock()

def get_lock():
    return _lock

def listar_barajas(carpeta="barajas"):
    if not os.path.exists(carpeta): return []
    return [d for d in os.listdir(carpeta) if os.path.isdir(os.path.join(carpeta, d))]

def get_aspecto(ruta_img):
    try:
        with Image.open(ruta_img) as im:
            w, h = im.size
            return w / h if h else 1.0
    except:
        return 1.0

def cm_to_px(cm, dpi=300):
    return int(cm / 2.54 * dpi)

def cargar_files(lista_paths):
    return [p for p in lista_paths if os.path.exists(p)]

def cargar_zip_temporal(uploaded_file, temp_dir="/tmp/baraja_temp"):
    import zipfile
    os.makedirs(temp_dir, exist_ok=True)
    path_zip = os.path.join(temp_dir, uploaded_file.name)
    with open(path_zip, "wb") as f:
        f.write(uploaded_file.getbuffer())
    archivos=[]
    with zipfile.ZipFile(path_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(('.png','.jpg','.jpeg','.webp')):
                    archivos.append(os.path.join(root, file))
    return archivos

def cargar_imagenes_sueltas(uploaded_files, temp_dir="/tmp/baraja_suelta"):
    os.makedirs(temp_dir, exist_ok=True)
    archivos=[]
    for uf in uploaded_files:
        path = os.path.join(temp_dir, uf.name)
        with open(path, "wb") as f:
            f.write(uf.getbuffer())
        archivos.append(path)
    return archivos
