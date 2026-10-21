if cartas:
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            st.session_state["prev_final5"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {juegos} JUEGOS", type="primary", use_container_width=True, key="gen5"):
                    inc_contador("5x5", 1); inc_baraja(nombre_baraja, "5x5")
                    with lock:
                        lista_final=[]; lista_orig=[]; bar=st.progress(0)
                        for j in range(juegos):
                            cartas=generar_logica_5x5(files)
                            if not cartas: continue
                            orig=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,None,W_usar)
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=generar_hoja_5x5(cartas,color,div,sep_v,sep_h,marco,asp,(Wf,Hf),W_usar)
                            lista_orig.append(orig); lista_final.append(final); bar.progress((j+1)/juegos)
                        st.session_state["lista_final5"]=lista_final; st.session_state["lista_orig5"]=lista_orig
            if "prev_final5" in st.session_state: st.image(st.session_state["prev_final5"], caption="Vista previa", use_container_width=True)
            if "lista_final5" in st.session_state and st.session_state["lista_final5"]:
                finales=st.session_state["lista_final5"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig5"]
                for i,im in enumerate(finales): st.image(im, caption=f"Juego {i+1}", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=92); zf.writestr(f"juego_5x5_{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"loteria_5x5_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"loteria_5x5_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="10dobles":
    registrar_entrada_generador("10dobles")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("10 Cartas 4x4 con Dobles - 54 por Hoja (3x -2)"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_10dobles')} | 🎰 {get_contador('10dobles')}")
    st.markdown(instrucciones_html("10 Cartas 4x4 con Dobles - 54 por Hoja (3x -2)"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo10")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel10")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip10")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs10")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        layout=st.selectbox("LAYOUT", ["5x2","2x5"], key="layout10")
        div=st.number_input("Div", value=1, key="div10"); sep_v=st.number_input("Sep V", value=40, key="sepv10"); sep_h=st.number_input("Sep H", value=40, key="seph10"); marco=st.number_input("Marco", value=4, key="marco10")
        color=st.color_picker("Color", "#FF00FF", key="color10")
        ancho=st.text_input("Ancho cm","54", key="ancho10"); alto=st.text_input("Alto cm","35", key="alto10"); dpi=st.text_input("DPI","300", key="dpi10")
        ciclos=st.number_input("Ciclos (1 ciclo=6 hojas)", value=1, min_value=1, max_value=10, key="ciclos10")
        st.info(f"💡 1 ciclo = 6 hojas para completar las 54 dobles. Aquí limitado a {ciclos} ciclo(s). ¿Necesitas más? Versión COMPLETA sin límites para PC disponible por WhatsApp.")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out10")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA 10C FULL", use_container_width=True, key="prev10"):
                    with lock:
                        st.session_state["uso_global_10"]={}; st.session_state["uso_como_dup_10"]={}; st.session_state["hash_10"]=set()
                        cartas,dups=generar_logica_10_cartas_54(files, es_nuevo_juego=True)
                        if cartas:
                            orig, final = generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                            st.session_state["prev_orig10"]=orig; st.session_state["prev_final10"]=final
            with cgen:
                if st.button(f"🎰 GENERAR {ciclos} CICLOS - 54xHOJA", type="primary", use_container_width=True, key="gen10"):
                    inc_contador("10dobles", 1); inc_baraja(nombre_baraja, "10dobles")
                    with lock:
                        lista_final=[]; lista_orig=[]; st.session_state["uso_global_10"]={}; st.session_state["uso_como_dup_10"]={}; st.session_state["hash_10"]=set()
                        bar=st.progress(0); total_h = ciclos*6; cnt=0
                        for ciclo in range(1, ciclos+1):
                            st.session_state["uso_global_10"]={}; st.session_state["uso_como_dup_10"]={}; st.session_state["hash_10"]=set()
                            for h in range(1,7):
                                cartas,dups=generar_logica_10_cartas_54(files, es_nuevo_juego=(h==1))
                                if not cartas: continue
                                orig, final = generar_con_resize_10(cartas, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                                lista_orig.append(orig); lista_final.append(final); cnt+=1; bar.progress(cnt/total_h)
                        st.session_state["lista_final10"]=lista_final; st.session_state["lista_orig10"]=lista_orig
            if "prev_final10" in st.session_state: st.image(st.session_state["prev_final10"], caption=f"Vista previa {layout} - 10C FULL 54xHOJA", use_container_width=True)
            if "lista_final10" in st.session_state and st.session_state["lista_final10"]:
                finales=st.session_state["lista_final10"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig10"]
                for i,im in enumerate(finales): st.image(im, caption=f"Hoja {i+1} - 10 Cartas", use_container_width=True)
                pdf_bytes=io.BytesIO(); finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], quality=92)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=95); zf.writestr(f"10C_FULL_{layout}_H{i+1:02d}.jpg", b.getvalue())
                st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"10C_FULL_{layout}_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"10C_FULL_{layout}_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="12portada":
    registrar_entrada_generador("12portada")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("GENERADOR 12 CARTAS CON PORTADA"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_12portada')} | 🎰 {get_contador('12portada')}")
    st.markdown(instrucciones_html("12 CON PORTADA"), unsafe_allow_html=True)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo_baraja=st.radio("Fuente", ["INCLUIDAS","IMPORTADAS ZIP"], key="fuente12")
        baraja_files=[]; portada_files=[]; baraja_nombre="baraja"; portada_nombre="portada"; nombre_baraja="Baraja_Personalizada"
        if modo_baraja=="INCLUIDAS":
            if barajas:
                sel_b=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel_b_12")
                path_b=[p for p in barajas if os.path.basename(p)==sel_b][0]
                baraja_files=cargar_files(path_b,54); baraja_nombre=sel_b; nombre_baraja=sel_b
            if os.path.exists("portadas"):
                port_dirs=[os.path.join("portadas",d) for d in os.listdir("portadas") if os.path.isdir(os.path.join("portadas",d))]
                if port_dirs:
                    sel_p=st.selectbox("Portada", [os.path.basename(p) for p in port_dirs], key="sel_p_12")
                    path_p=[p for p in port_dirs if os.path.basename(p)==sel_p][0]
                    portada_files=cargar_files(path_p,54); portada_nombre=sel_p
        else:
            zb=st.file_uploader("ZIP Baraja 54", type=["zip"], key="zip_b_12")
            if zb: baraja_files=cargar_zip_temporal(zb, tempfile.mkdtemp(), 54); nombre_baraja=zb.name
            zp=st.file_uploader("ZIP Portada 54", type=["zip"], key="zip_p_12")
            if zp: portada_files=cargar_zip_temporal(zp, tempfile.mkdtemp(), 54)
        modo_gen=st.radio("Modo", ["UNA - Solo 1 hoja","TODAS - 54 hojas"], key="modo_gen_12")
        st.info("💡 En modo GRATIS puedes generar 1 hoja o las 54 de un jalón. Si necesitas hacer cientos sin internet, tenemos la versión COMPLETA para computadora. ¡Pregunta por WhatsApp!")
        num_fav=st.number_input("Número favorita (1-54)", value=46, min_value=1, max_value=54, key="num_fav_12")
        lista_excel=[f"{k:02d} - {v}" for k,v in EXCEL_COLORS.items()]
        sel_excel=st.selectbox("Color Excel", lista_excel, index=2, key="excel_12")
        hex_excel=EXCEL_COLORS.get(int(sel_excel.split("-")[0].strip()), "#FF0000")
        color_entre=st.color_picker("Color HEX", hex_excel, key="color_12")
        div_interno=st.number_input("Div. interna", value=8, key="div_12")
        sep_entre=st.number_input("Sep. entre cartas", value=40, key="sep_12")
        ancho=st.text_input("Ancho cm tabloide","28", key="ancho12"); alto=st.text_input("Alto cm tabloide","43", key="alto12"); dpi=st.text_input("DPI","300", key="dpi12")
    with col2:
        if baraja_files and portada_files:
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁 VISTA PREVIA", use_container_width=True, key="prev12"):
                    with lock:
                        idx=max(0,min(num_fav-1, min(len(baraja_files),len(portada_files))-1))
                        sheet=generar_tabloide_12_con_portada_PULIDO(baraja_files, portada_files[idx], baraja_files[idx], color_entre, div_interno, sep_entre)
                        if sheet:
                            st.session_state["orig12"]=sheet
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            st.session_state["final12"]=sheet.resize((Wf,Hf), Image.LANCZOS)
            with cgen:
                if st.button("🖼 EXPORTAR TABLOIDE", type="primary", use_container_width=True, key="gen12"):
                    inc_contador("12portada", 1); inc_baraja(nombre_baraja, "12portada")
                    with lock:
                        lista_final=[]; lista_nombres=[]; bar=st.progress(0)
                        if "UNA" in modo_gen:
                            idx=max(0,min(num_fav-1, min(len(baraja_files),len(portada_files))-1))
                            lista=[(portada_files[idx], baraja_files[idx])]
                        else:
                            n=min(len(baraja_files), len(portada_files),54)
                            lista=[(portada_files[i], baraja_files[i]) for i in range(n)]
                        for i,(cover_path,fav_path) in enumerate(lista,1):
                            sheet=generar_tabloide_12_con_portada_PULIDO(baraja_files, cover_path, fav_path, color_entre, div_interno, sep_entre)
                            if not sheet: continue
                            Wf=cm_to_px(ancho,int(dpi)); Hf=cm_to_px(alto,int(dpi))
                            final=sheet.resize((Wf,Hf), Image.LANCZOS)
                            lista_final.append(final); lista_nombres.append(limpiar_nombre(fav_path,i))
                            bar.progress(i/len(lista))
                        st.session_state["lista_final12"]=lista_final; st.session_state["lista_nombres12"]=lista_nombres
            if "orig12" in st.session_state: st.image(st.session_state["final12"], caption="Vista previa - Alta Calidad Final", use_container_width=True)
            if "lista_final12" in st.session_state and st.session_state["lista_final12"]:
                finales=st.session_state["lista_final12"]; nombres=st.session_state["lista_nombres12"]
                for i,im in enumerate(finales): st.image(im, caption=f"{i+1:02d} - {nombres[i]}", use_container_width=True)
                pdf_bytes=io.BytesIO()
                if len(finales)==1: finales[0].save(pdf_bytes, format="PDF", resolution=300, quality=95)
                else: finales[0].save(pdf_bytes, format="PDF", save_all=True, append_images=finales[1:], resolution=300, quality=95)
                zip_bytes=io.BytesIO()
                with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                    fecha=datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    for i,im in enumerate(finales):
                        b=io.BytesIO(); im.save(b, format="JPEG", quality=95, dpi=(300,300))
                        zf.writestr(f"{i+1:02d} - {nombres[i]} - {fecha}.jpg", b.getvalue())
                d1,d2=st.columns(2)
                with d1: st.download_button(f"⬇️ PDF {len(finales)}", pdf_bytes.getvalue(), f"TABLOIDE_{len(finales)}.pdf", "application/pdf", use_container_width=True, type="primary")
                with d2: st.download_button(f"⬇️ ZIP {len(finales)}", zip_bytes.getvalue(), f"TABLOIDE_{len(finales)}.zip", "application/zip", use_container_width=True)
    st.stop()
if st.session_state.vista=="4x4doblesfix":
    registrar_entrada_generador("4x4doblesfix")
    if st.button("⬅️ Volver al Catalogo"): ir_a("catalogo")
    st.markdown(banner_top("🆕 4x4 DOBLES AL CENTRO - 54 DOBLES FIX"), unsafe_allow_html=True)
    st.markdown(banner_facebook(), unsafe_allow_html=True); copiar_clabe_component()
    st.caption(f"👀 {get_contador('visita_4x4doblesfix')} | 🎰 {get_contador('4x4doblesfix')}")
    st.markdown(instrucciones_html("4x4 DOBLES AL CENTRO FIX - 54 DOBLES"), unsafe_allow_html=True)
    if os.path.exists("portadas/portada_4x4-dobles-al-centro.jpg"): st.image("portadas/portada_4x4-dobles-al-centro.jpg", use_container_width=False)
    elif os.path.exists("portada_4x4-dobles-al-centro.jpg"): st.image("portada_4x4-dobles-al-centro.jpg", use_container_width=False)
    barajas=listar_barajas(); col1,col2=st.columns([1,2.5])
    with col1:
        modo=st.radio("Baraja", ["Integrada","Subir ZIP","Subir Fotos Sueltas"], key="modo4dobfix")
        files=None; nombre_baraja="Baraja_Personalizada"
        if modo=="Integrada" and barajas:
            sel=st.selectbox("Baraja", [os.path.basename(p) for p in barajas], key="sel4dobfix")
            path_sel=[p for p in barajas if os.path.basename(p)==sel][0]
            files=cargar_files(path_sel); nombre_baraja=sel
        elif "ZIP" in modo:
            up=st.file_uploader("ZIP 54 fotos", type=["zip"], key="zip4dobfix")
            if up: files=cargar_zip_temporal(up, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs"); nombre_baraja=up.name
        else:
            ups=st.file_uploader("54 fotos sueltas", type=["jpg","jpeg","png","webp"], accept_multiple_files=True, key="imgs4dobfix")
            if ups: files=cargar_imagenes_sueltas(ups, tempfile.mkdtemp(), 54); st.success(f"{len(files)} imgs")
        st.divider()
        layout=st.selectbox("LAYOUT", ["2x2","1x4"], key="layout4dobfix")
        div=st.number_input("Div", value=1, key="div4dobfix"); sep_v=st.number_input("Sep V", value=80, key="sepv4dobfix"); sep_h=st.number_input("Sep H", value=80, key="seph4dobfix"); marco=st.number_input("Marco", value=6, key="marco4dobfix")
        color=st.color_picker("Color entre cartas", "#FF00FF", key="color4dobfix")
        ancho=st.text_input("Ancho cm (resize)","21", key="ancho4dobfix"); alto=st.text_input("Alto cm (resize)","28", key="alto4dobfix"); dpi=st.text_input("DPI","300", key="dpi4dobfix")
        st.info("💡 Limitado a 1 ciclo = 14 hojas. 54 dobles garantizadas + 2 repetidas. Fix sin huecos rosas, marco parejo 4 lados. Con PDF + JPG + info_54_dobles.txt")
        tipo_salida=st.radio("Salida", ["RESIZE cm","ORIGINAL"], horizontal=True, key="out4dobfix")
    with col2:
        if files:
            asp=get_aspecto(files)
            cprev,cgen=st.columns(2)
            with cprev:
                if st.button("👁️ VISTA PREVIA - 2 PREVIEWS", use_container_width=True, key="prev4dobfix"):
                    with lock:
                        hojas_ciclo, dobles, repetidas = generar_ciclo_54_dobles_4x4dob(files)
                        primera = hojas_ciclo[0]
                        orig, final = generar_con_resize_4x4dob(primera, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                        st.session_state["prev_orig4dobfix"]=orig; st.session_state["prev_final4dobfix"]=final
                        st.session_state["hojas4dobfix"]=hojas_ciclo; st.session_state["dobles4dobfix"]=dobles; st.session_state["repetidas4dobfix"]=repetidas
            with cgen:
                if st.button(f"🎰 GENERAR CICLO 14 HOJAS + PDF", type="primary", use_container_width=True, key="gen4dobfix"):
                    inc_contador("4x4doblesfix", 1); inc_baraja(nombre_baraja, "4x4doblesfix")
                    with lock:
                        hojas_ciclo, dobles, repetidas = generar_ciclo_54_dobles_4x4dob(files)
                        originales=[]; resizes=[]; bar=st.progress(0)
                        for idx, hoja in enumerate(hojas_ciclo,1):
                            o,f = generar_con_resize_4x4dob(hoja, color, div, sep_v, sep_h, marco, ancho, alto, dpi, asp, layout)
                            originales.append(o); resizes.append(f); bar.progress(idx/len(hojas_ciclo))
                        st.session_state["lista_orig4dobfix"]=originales; st.session_state["lista_final4dobfix"]=resizes
                        st.session_state["hojas4dobfix"]=hojas_ciclo; st.session_state["dobles4dobfix"]=dobles; st.session_state["repetidas4dobfix"]=repetidas
            if "prev_final4dobfix" in st.session_state:
                c1p,c2p=st.columns(2)
                with c1p: st.image(st.session_state["prev_orig4dobfix"], caption=f"1- ORIGINAL FIJO {st.session_state['prev_orig4dobfix'].size}", use_container_width=True)
                with c2p: st.image(st.session_state["prev_final4dobfix"], caption=f"2- RESIZE {st.session_state['prev_final4dobfix'].size}", use_container_width=True)
            if "lista_final4dobfix" in st.session_state and st.session_state["lista_final4dobfix"]:
                finales = st.session_state["lista_final4dobfix"] if tipo_salida=="RESIZE cm" else st.session_state["lista_orig4dobfix"]
                for i,im in enumerate(finales): st.image(im, caption=f"Hoja {i+1}/14", use_container_width=True)
                pdf_orig = imagenes_a_pdf_4x4dob(st.session_state["lista_orig4dobfix"])
                pdf_res = imagenes_a_pdf_4x4dob(st.session_state["lista_final4dobfix"])
                lista_nombres = [os.path.basename(f) for f in st.session_state["dobles4dobfix"]]; rep_nombres = [os.path.basename(f) for f in st.session_state["repetidas4dobfix"]]
                unicas = sorted(set(lista_nombres)); fecha=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                info_text = f"""LOTERIA 4x4 DOBLES FIX - 54 DOBLES
Fecha: {fecha}
Layout: {layout}
Div {div} SepV {sep_v} SepH {sep_h} Marco {marco} Color {color}
Resize: {ancho}x{alto}cm {dpi}DPI - Sin huecos, marco parejo

REPETIDAS:
{chr(10).join([f"- {r}" for r in rep_nombres])}

56 DOBLES:
{chr(10).join([f"{i+1:02d}. {n}" for i,n in enumerate(lista_nombres)])}

54 UNICAS:
{chr(10).join([f"- {n}" for n in unicas])}
Total: {len(unicas)}/54
"""
                zip_buf=io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i,(o,r) in enumerate(zip(st.session_state["lista_orig4dobfix"], st.session_state["lista_final4dobfix"]),1):
                        bo=io.BytesIO(); o.save(bo, format="JPEG", quality=95); zf.writestr(f"JPG_ORIGINAL_H{i:02d}.jpg", bo.getvalue())
                        br=io.BytesIO(); r.save(br, format="JPEG", quality=95, dpi=(int(dpi),int(dpi))); zf.writestr(f"JPG_RESIZE_H{i:02d}.jpg", br.getvalue())
                    zf.writestr(f"PDF_ORIGINAL_{layout}_{fecha}.pdf", pdf_orig)
                    zf.writestr(f"PDF_RESIZE_{layout}_{fecha}.pdf", pdf_res)
                    zf.writestr("info_54_dobles.txt", info_text)
                c1d,c2d,c3d=st.columns(3)
                with c1d: st.download_button(f"📦 ZIP TODO", zip_buf.getvalue(), f"4x4DOBLES_FIX_{layout}_{fecha}.zip", "application/zip", use_container_width=True, type="primary")
                with c2d: st.download_button(f"📄 PDF ORIGINAL", pdf_orig, f"ORIGINAL_{layout}_{fecha}.pdf", "application/pdf", use_container_width=True)
                with c3d: st.download_button(f"📄 PDF RESIZE", pdf_res, f"RESIZE_{layout}_{fecha}.pdf", "application/pdf", use_container_width=True)
    st.stop()
