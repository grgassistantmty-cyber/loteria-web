import os
import glob

def listar_barajas():
    base = "barajas" if os.path.exists("barajas") else "BARAJAS"
    barajas = []
    if not os.path.exists(base):
        return []
    for entry in os.listdir(base):
        full = os.path.join(base, entry)
        if os.path.isdir(full):
            imgs = glob.glob(os.path.join(full, "*.jpg")) + glob.glob(os.path.join(full, "*.png"))
            if len(imgs) > 0:
                barajas.append(entry)
    barajas.sort()
    return barajas

def listar_portadas():
    # SOLO lo de adentro de portadas01, portadas02 etc
    # NO las sueltas del menú
    base = "portadas" if os.path.exists("portadas") else "PORTADAS"
    if not os.path.exists(base):
        return []
    
    portadas = []
    for entry in os.listdir(base):
        full = os.path.join(base, entry)
        # Solo carpetas, ignoramos los archivos sueltos del menú
        if os.path.isdir(full):
            for ext in ("*.jpg", "*.png", "*.jpeg", "*.JPG", "*.PNG"):
                files = glob.glob(os.path.join(full, ext))
                for f in files:
                    # guardamos como portadas01/nombre.jpg
                    portadas.append(f"{entry}/{os.path.basename(f)}")
    
    portadas.sort()
    return portadas

def listar_previews_menu():
    # Estas son las del menú, las sueltas
    base = "portadas" if os.path.exists("portadas") else "PORTADAS"
    previews = []
    if not os.path.exists(base):
        return []
    for ext in ("*.jpg", "*.png", "*.jpeg"):
        previews.extend([os.path.basename(p) for p in glob.glob(os.path.join(base, ext))])
    return sorted(previews)

def cargar_files(nombre_baraja, expected=54):
    base = "barajas" if os.path.exists("barajas") else "BARAJAS"
    carpeta = os.path.join(base, nombre_baraja)
    if os.path.isdir(nombre_baraja):
        carpeta = nombre_baraja
    files = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.JPG", "*.PNG"):
        files.extend(glob.glob(os.path.join(carpeta, ext)))
    return sorted(files)

def cargar_portada_files(nombre_portada):
    base = "portadas" if os.path.exists("portadas") else "PORTADAS"
    path = os.path.join(base, nombre_portada)
    if os.path.isfile(path):
        return [path]
    return []
