import streamlit as st
from PIL import Image
import io, os, zipfile, glob, random

st.set_page_config(page_title="Lotería Eliud - 4 Cartas", layout="wide", page_icon="🎰")

# ========= MARCA ARRIBA =========
st.markdown("""
<style>
.marca-top {
background: linear-gradient(90deg, #FF0000, #000000);
padding: 18px;
border-radius: 16px;
color: white;
text-align: center;
border: 3px solid gold;
}
.marca-top h1 { margin:0; font-size: 32px; }
.marca-top h2 { margin:5px; font-size: 22px; color: gold; }
.btn-ws {
background: #25D366;
color: white!important;
padding: 12px 25px;
border-radius: 30px;
text-decoration: none;
font-weight: bold;
font-size: 20px;
display: inline-block;
margin-top: 10px;
}
</style>
<div class="marca-top">
<h1>🎰 LOTERÍA 4 CARTAS - FORMATO 3,3,2,2 🎰</h1>
<h2>Creado por Eliud Monsivais</h2>
<a class="btn-ws" href="https://wa.me/528115566250?text=Hola%20Eliud%20vi%20tu%20app%20de%20loteria%20quiero%20una%20baraja" target="_blank">
📲 WhatsApp: 811 556 6250 - ¡PIDE TU BARAJA PERSONALIZADA!
</a>
</div>
<br>
""", unsafe_allow_html=True)

# ========= FUNCIONES BARAJAS =========
def get_barajas_locales():
    base = "barajas"
    if not os.path.exists(base): return []
    return sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])

def cargar_baraja_local(nombre):
    carpeta = os.path.join("barajas", nombre)
    archivos = sorted(glob.glob(os.path.join(carpeta, "*")))
    imgs = []
    for f in archivos:
        if f.lower().endswith((".png",".jpg",".jpeg",".webp")):
            try:
                imgs.append(Image.open(f).convert("RGB"))
            except: pass
    return imgs[:54]

barajas_disponibles = get_barajas_locales()

# ========= SELECTOR =========
col1, col2 = st.columns(2)
with col1:
    opcion = st.radio("Origen:", ["Baraja integrada", "Subir mi ZIP"], horizontal=True)
with col2:
    if barajas_disponibles and opcion == "Baraja integrada":
        sel = st.selectbox("Elige baraja:", barajas_disponibles)

cartas = []
if opcion == "Baraja integrada" and barajas_disponibles:
    cartas = cargar_baraja_local(sel)
    st.success(f"✅ {len(cartas)} cartas de {sel} cargadas")
else:
    zip_file = st.file_uploader("Sube ZIP con 54 cartas", type=["zip"])
    if zip_file:
        with zipfile.ZipFile(zip_file) as z:
            for name in sorted(z.namelist()):
                if name.lower().endswith((".png",".jpg",".jpeg",".webp")):
                    cartas.append(Image.open(z.open(name)).convert("RGB"))
                if len(cartas) >= 54: break

# ========= PREVIEW =========
if cartas:
    st.markdown(f"### Preview {len(cartas)} cartas")
    cols = st.columns(9)
    for i, c in enumerate(cartas[:54]):
        cols[i % 9].image(c, use_container_width=True)

# ========= MEDIDAS (las tuyas) =========
if cartas:
    st.divider()
    st.subheader("Medidas para 4 cartas")
    c1,c2,c3 = st.columns(3)
    with c1: ancho = st.number_input("Ancho carta px", value=1000)
    with c2: alto = st.number_input("Alto carta px", value=1400)
    with c3: gap = st.number_input("Hueco entre cartas", value=20)

    if st.button("🎰 GENERAR LAS 4 CARTAS 3,3,2,2", type="primary", use_container_width=True):
        # Lógica simple 3,3,2,2 rotado con huecos
        random.shuffle(cartas)
        # Aquí va tu lógica real de generación, de momento genera 4 hojas de ejemplo
        # Para demo, crea 4 imágenes
        outputs = []
        idx = 0
        for hoja in range(4):
            # Crea lienzo blanco
            board = Image.new("RGB", (ancho*3 + gap*2, alto*4 + gap*3), "white")
            # Ejemplo: poner 16 cartas en formato 3,3,2,2
            # (Tu código original va aquí)
            for r in range(4):
                for col in range(3):
                    if idx < len(cartas):
                        x = col*(ancho+gap)
                        y = r*(alto+gap)
                        board.paste(cartas[idx].resize((ancho, alto)), (x,y))
                        idx+=1
            outputs.append(board)

        st.success("¡Listas!")
        for i, out in enumerate(outputs):
            st.image(out, caption=f"Hoja {i+1}", use_container_width=True)
            buf = io.BytesIO()
            out.save(buf, format="JPEG", quality=95)
            st.download_button(f"⬇️ Descargar Hoja {i+1}", buf.getvalue(), f"loteria_eliud_hoja_{i+1}.jpg", "image/jpeg", key=f"dl{i}")

        # ========= MARCA ABAJO =========
        st.markdown("""
        <br>
        <div class="marca-top">
        <h1>¿Te gustó? ¡Yo te hago tu baraja personalizada!</h1>
        <h2>Creado por Eliud Monsivais</h2>
        <a class="btn-ws" href="https://wa.me/528115566250?text=Hola%20Eliud%20vi%20tu%20app%20de%20loteria%20quiero%20una%20baraja" target="_blank">
        📲 WhatsApp: 811 556 6250
        </a>
        <p style="margin-top:10px">Monterrey, N.L. - Envíos a todo México</p>
        </div>
        """, unsafe_allow_html=True)