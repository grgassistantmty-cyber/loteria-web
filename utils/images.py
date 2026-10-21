import os
import zipfile
import streamlit as st
from PIL import Image

# --- ESTE CACHE TE AHORRA $4 DOLARES AL MES EN RAILWAY ---
@st.cache_data
def listar_barajas():
    if not os.path.exists("barajas"):
        return []
    return sorted([
        os.path.join("barajas", d) 
        for d in os.listdir("barajas") 
        if os.path.isdir(os.path.join("barajas", d)) 
        and d.lower().startswith("baraja")
    ])

@st.cache_data
def get_aspecto(files_tuple):
    # Convertimos a tuple para que sea cacheable
    files = list(files_tuple)
    asp=[]
    for p in files[:10]:
        try:
            with Image.open(p) as im: 
                asp.append(im.size[1]/im.size[0])
        except: 
            pass
    return sum(asp)/len(asp) if asp else 1.42

def cargar_files(path, limite=54):
    exts=(".png",".jpg",".jpeg",".webp",".jfif")
    if not path or not os.path.exists(path): 
        return []
    files=[os.path.join(path,f) for f in os.listdir(path) if f.lower().endswith(exts)]
    files.sort()
    return files[:limite]

def cargar_zip_temporal(uploaded_zip, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp):
            try: os.remove(os.path.join(carpeta_tmp,f))
            except: pass
        with zipfile.ZipFile(uploaded_zip) as zz:
            for name in zz.namelist():
                if name.lower().endswith((".jpg",".jpeg",".png",".webp",".jfif")):
                    open(os.path.join(carpeta_tmp, os.path.basename(name)),"wb").write(zz.read(name))
        return cargar_files(carpeta_tmp, limite)
    except: 
        return []

def cargar_imagenes_sueltas(uploaded_files, carpeta_tmp, limite=54):
    try:
        os.makedirs(carpeta_tmp, exist_ok=True)
        for f in os.listdir(carpeta_tmp):
            try: os.remove(os.path.join(carpeta_tmp,f))
            except: pass
        for uf in uploaded_files[:limite]:
            open(os.path.join(carpeta_tmp, uf.name),"wb").write(uf.getbuffer())
        return cargar_files(carpeta_tmp, limite)
    except: 
        return []

def cm_to_px(cm,dpi):
    try: 
        return int(float(cm)/2.54*int(dpi))
    except: 
        return 800

def no_chocan(a,b,la,lb):
    for i,j in zip(la,lb):
        if a[i] is None or b[j] is None: continue
        if a[i]==b[j]: return False
    return True

def limpiar_nombre(path_img, idx):
    try:
        base = os.path.basename(path_img)
        nombre = os.path.splitext(base)[0]
        nombre = "".join(c if c.isalnum() or c in " -_" else "" for c in nombre)
        return nombre[:25] if nombre else f"Fig {idx+1}"
    except:
        return f"Fig {idx+1}"

# --- TU LOGICA DE CARTAS EXACTA, SIN CAMBIOS ---
RIGHT4=[3,7,11,15]; LEFT4=[0,4,8,12]; TOP4=[0,1,2,3]; BOTTOM4=[12,13,14,15]
RIGHT5=[4,9,14,19,24]; LEFT5=[0,5,10,15,20]; TOP5=[0,1,2,3,4]; BOTTOM5=[20,21,22,23,24]
