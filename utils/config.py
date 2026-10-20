import os, json, streamlit as st
from datetime import datetime

EXCEL_COLORS = ["#FF0000", "#00B050", "#0070C0", "#FFC000", "#7030A0"]

def contador_visitas():
    path = "/tmp/visitas.json"
    try:
        if os.path.exists(path):
            with open(path, "r") as f: data=json.load(f)
        else: data={"total":0}
        data["total"]+=1
        with open(path,"w") as f: json.dump(data,f)
        return data["total"]
    except: return 0

def ranking_barajas():
    # tu lógica original de ranking
    return []

def ir_a(vista):
    st.session_state["vista_actual"]=vista
    st.rerun()
