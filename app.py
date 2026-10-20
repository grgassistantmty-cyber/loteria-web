import streamlit as st, importlib.util, os, glob

st.set_page_config(page_title="BINGO GENERADORES", layout="wide", initial_sidebar_state="collapsed")

# init contadores sin importar como paquete
spec_cfg = importlib.util.spec_from_file_location("config", "utils/config.py")
config = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(config)
config.init_contadores()

if "pagina" not in st.session_state: st.session_state["pagina"]="catalogo"
pagina = st.session_state["pagina"]

def load_and_render(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.render()

if pagina == "catalogo":
    load_and_render("vistas/catalogo.py")
else:
    ruta = f"vistas/vista_{pagina}.py"
    if os.path.exists(ruta):
        load_and_render(ruta)
    else:
        st.session_state["pagina"]="catalogo"
        st.rerun()
