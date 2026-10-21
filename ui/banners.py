import streamlit.components.v1 as components

def copiar_clabe_component():
    components.html(
        """<div style="text-align:center; margin-top:10px">
        <input id="clabe" value="728969000164073671" style="position:absolute; left:-9999px;">
        <button onclick="navigator.clipboard.writeText(document.getElementById('clabe').value); 
        document.getElementById('msg').innerHTML='✅ ¡Copiada!';" 
        style="background:gold; color:black; border:none; padding:12px 22px; border-radius:25px; 
        font-weight:bold; cursor:pointer; font-size:17px;">📋 COPIAR CLABE - PICA AQUÍ</button>
        <div id="msg" style="color:green; font-weight:bold; margin-top:8px;"></div></div>""", 
        height=90
    )

def banner_top(titulo):
    from utils.counters import visitas_total, get_contador
    return f"""
    <style>
    .banner{{background:linear-gradient(90deg,#cc0000,#000);padding:18px;border-radius:16px;color:white;text-align:center;border:3px solid gold}}
    .ws{{background:#25D366;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px}}
    .fb{{background:#1877F2;color:white!important;padding:12px 28px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;font-size:18px;margin-top:10px}}
    .contador{{background:gold;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin-top:10px;font-size:18px}}
    .contador2{{background:#111;color:#ffd700;padding:8px 14px;border-radius:10px;font-weight:bold;display:inline-block;margin-top:8px;font-size:14px;border:1px solid gold}}
    .apoyo{{background:linear-gradient(180deg,#fffbe6,#ffe27a);border:3px solid #ffb700;padding:18px;border-radius:14px;margin-top:16px;color:#222;text-align:center;line-height:1.7}}
    </style>
    <div class="banner">
    <h1>🎰 {titulo} 🎰</h1>
    <h3>Creado por: Eliud Monsivais - WhatsApp 8115566250</h3>
    <a class="ws" href="https://wa.me/528115566250">📲 WHATSAPP 8115566250</a><br>
    <a class="fb" href="https://www.facebook.com/groups/1646464953556819" target="_blank">🔵 UNIRME AL GRUPO DE FACEBOOK</a><br>
    <span class="contador">👁️ Visitas: {visitas_total}</span><br>
    <span class="contador2">📊 USOS | 4x4: 👀{get_contador('visita_4x4')}/🎰{get_contador('4x4')} | 5x5: 👀{get_contador('visita_5x5')}/🎰{get_contador('5x5')} | 10C: 👀{get_contador('visita_10dobles')}/🎰{get_contador('10dobles')} | 12: 👀{get_contador('visita_12portada')}/🎰{get_contador('12portada')} | 4x4DOB FIX: 👀{get_contador('visita_4x4doblesfix')}/🎰{get_contador('4x4doblesfix')}</span>
    <div class="apoyo">💖 <b style="font-size:20px">¿TE GUSTÓ MI TRABAJO? ¡APÓYAME VOLUNTARIAMENTE!</b> 💖<br>
    Esta página es <b>100% GRATIS</b>, pero a mí me cuesta <b>pagar el servidor cada mes</b>.<br>
    Si te sirvió y quieres apoyarme con <b>$5, $10, $20, $50, $100 pesitos</b>, te lo agradezco muchísimo 🙏<br>
    <b>BANCO: SPIN by OXXO</b><br>
    <span style="font-size:22px; background:black; color:gold; padding:8px 14px; border-radius:8px;">CLABE: 728969000164073671</span><br>
    A nombre de: <b>Eliud Monsivais</b><br></div></div><br>
    """

def banner_facebook():
    return """<div style="background:#e7f3ff; border:3px solid #1877F2; border-radius:14px; padding:18px; text-align:center; margin-bottom:15px">
    <h3 style="color:#1877F2; margin:0">🔵 ¡ÚNETE A MI GRUPO DE FACEBOOK!</h3>
    <p style="color:black; font-size:17px;">Aquí subo <b>barajas nuevas GRATIS</b> y te ayudo con dudas.</p>
    <a href="https://www.facebook.com/groups/1646464953556819" target="_blank" style="background:#1877F2; color:white; padding:14px 32px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; font-size:19px">👉 ENTRAR AL GRUPO</a></div>"""

def banner_venta_offline():
    return """<div style="background:linear-gradient(90deg,#000,#4b0000); border:3px solid gold; border-radius:16px; padding:20px; text-align:center; color:white; margin:20px 0">
    <h2 style="color:gold; margin:0">💻 ¿QUIERES USARLO SIN INTERNET Y SIN LÍMITES?</h2>
    <p style="font-size:18px; line-height:1.6; margin:12px 0">Si te interesa alguno de los generadores para usarlo desde la <b>comodidad de tu casa, sin necesidad de internet</b>,<br> sin límite de juegos y sin límite de PDFs, con todas tus barajas guardadas...<br><br>
    <b style="color:#25D366; font-size:20px">¡CONTÁCTANOS POR WHATSAPP O POR EL GRUPO DE FACEBOOK QUE ESTÁ ARRIBA!</b></p>
    <a href="https://wa.me/528115566250" style="background:#25D366; color:white; padding:14px 32px; border-radius:30px; text-decoration:none; font-weight:bold; font-size:20px; display:inline-block">📲 PEDIR INFORMES DE VERSIÓN SIN LÍMITES</a></div>"""

def instrucciones_html(vista="general"):
    if vista=="catalogo":
        return """<div style="background:#fffbe6;border:3px dashed #ffaa00;padding:20px;border-radius:14px;color:black; font-size:18px"><h2 style="text-align:center">📋 CÓMO USAR</h2>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid green; margin-bottom:10px"><b>1) 4x4 - 16 figuras:</b> 4 cartas por hoja.</div>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid blue; margin-bottom:10px"><b>2) 5x5 - 25 figuras:</b> 4 cartas por hoja.</div>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid gold;"><b>3) 10 Cartas 4x4 con Dobles</b></div>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid #cc0000;"><b>4) 12 CON PORTADA:</b> Tabloide 12 cartas + portada.</div>
        <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid purple;"><b>5) 4x4 DOBLES AL CENTRO FIX</b></div></div><br>"""
    else:
        return f"""<div style="background:#fffbe6;border:2px solid #ffaa00;padding:18px;border-radius:14px;color:black; font-size:17px">
        <h3>💡 PARA QUÉ ES CADA COSA - {vista}</h3>
        <b>📁 Baraja:</b> Elige tus dibujos.<br><b>🎨 Div:</b> Grosor línea.<br>
        <b>↔️ Sep V / Sep H:</b> Espacio ENTRE las cartas.<br><br>
        <b>👁️ Primero VISTA PREVIA, luego GENERAR y DESCARGAR</b></div><br>"""
