import streamlit.components.v1 as components

def banner_top(titulo="CATALOGO DE LOTERIAS"):
    return f"""
    <div style="background:#111; color:white; padding:30px; text-align:center; border-radius:15px;">
        <h1 style="margin:0; font-size:32px;">{titulo}</h1>
        <p style="opacity:0.7;">Generador de Loterías Web</p>
    </div>
    """

def copiar_clabe_component():
    return components.html("""
    <div style="background:#f0f0f0; padding:15px; text-align:center; margin:10px 0; border-radius:10px;">
        <b>CLABE para pagos</b><br>012345678901234567
    </div>
    """, height=100)

def banner_facebook():
    return """
    <div style="background:#1877f2; color:white; padding:15px; text-align:center; border-radius:10px;">
        Síguenos en Facebook
    </div>
    """

def banner_venta_offline():
    return """
    <div style="background:#222; color:white; padding:20px; text-align:center; border-radius:10px;">
        Venta Offline disponible
    </div>
    """

def banner_mid():
    return banner_top("GENERADOR")

def banner_bottom():
    return banner_facebook()
