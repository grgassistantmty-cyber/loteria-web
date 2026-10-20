import os, glob, tempfile, shutil
from PIL import Image

def listar_barajas():
    return glob.glob("barajas/*") + glob.glob("baraja/*")

def cargar_files(path):
    return sorted(glob.glob(os.path.join(path, "*.jpg")) + glob.glob(os.path.join(path, "*.png")) + glob.glob(os.path.join(path, "*.jpeg")) + glob.glob(os.path.join(path, "*.webp")))

def cargar_zip_temporal(up, tmpdir, min_imgs=54):
    import zipfile; zpath=os.path.join(tmpdir, "b.zip"); open(zpath,"wb").write(up.getbuffer())
    with zipfile.ZipFile(zpath) as z: z.extractall(tmpdir)
    return cargar_files(tmpdir)

def cargar_imagenes_sueltas(ups, tmpdir, min_imgs=54):
    files=[]
    for up in ups:
        p=os.path.join(tmpdir, up.name); open(p,"wb").write(up.getbuffer()); files.append(p)
    return files

def get_aspecto(files):
    try:
        with Image.open(files[0]) as im: w,h=im.size; return h/w
    except: return 1.5

def cm_to_px(cm, dpi):
    try: return int(float(cm)/2.54 * float(dpi))
    except: return 1000
