import streamlit as st
import pandas as pd

def calcola_preventivo_forfettario():
    st.subheader("Preventivo per Contribuenti Minimi e Forfettari")

    col1, col2 = st.columns(2)
    with col1:
        fatture_mensili = st.radio(
            "Numero di fatture mensili",
            ["Fino a 10/mese", "Oltre 10/mese"]
        )

    with col2:
        if fatture_mensili == "Fino a 10/mese":
            prezzo_min, prezzo_max = 500, 1200
        else:
            prezzo_min, prezzo_max = 750, 1500
        
        st.write(f"Range di prezzo: €{prezzo_min} - €{prezzo_max}")
        prezzo_base = st.slider("Seleziona il prezzo base", prezzo_min, prezzo_max, prezzo_min, step=50)

    st.write(f"Prezzo base selezionato per redazione della situazione contabile: €{prezzo_base}")

    st.subheader("Servizi Aggiuntivi")
    servizi_aggiuntivi = {
        "Maggiorazione annua recupero corrispettivi telematici": 300,
        "Redazione situazione contabile periodica/infrannuale": 75
    }

    servizi_selezionati = {}
    for servizio, tariffa in servizi_aggiuntivi.items():
        if st.checkbox(f"{servizio} (+€{tariffa})"):
            servizi_selezionati[servizio] = tariffa

    st.subheader("Dichiarazione dei Redditi (Opzionale)")
    dichiarazione_redditi = st.checkbox("Aggiungi Dichiarazione dei redditi")
    prezzo_dichiarazione = 0
    if dichiarazione_redditi:
        fasce_ricavi_dichiarazione = {
            "Fino a 75.000,00 Euro": (292, 587),
            "da 75.001,00 a 150.000,00 Euro": (526, 791),
            "da 150.000,01 a 300.000,00 Euro": (702, 1055),
            "da 300.000,01 a 500.000,00 Euro": (875, 1318),
            "da 500.000,01 a 750.000,00 Euro": (1050, 1582),
            "oltre 750.000,00": (1400, 2110)
        }
        
        ricavi = st.selectbox("Seleziona la fascia di ricavi", list(fasce_ricavi_dichiarazione.keys()))
        min_prezzo, max_prezzo = fasce_ricavi_dichiarazione[ricavi]
        prezzo_dichiarazione = st.slider("Prezzo Dichiarazione dei redditi", min_prezzo, max_prezzo, min_prezzo, step=10)

    # Restituisci i dettagli dei servizi selezionati
    return {
        "Prezzo Base": {
            "Contabilità Forfettaria": prezzo_base
        },
        "Servizi Aggiuntivi": servizi_selezionati,
        "Dichiarazione dei Redditi": prezzo_dichiarazione
    }

def calcola_preventivo_semplificato():
    st.subheader("Preventivo per Contabilità Semplificata")

    # Mostra la tabella dei range
    st.write("Fasce di onorario per contabilità semplificata:")
    fasce_onorario = {
        "Fino a 90": ("€ 1.163,00", "€ 1.679,00"),
        "fino a 180": ("€ 1.560,00", "€ 2.061,00"),
        "da 180 e fino a 360": ("€ 2.238,00", "€ 3.372,00"),
        "ogni registrazione oltre le 360": ("€ 1,65", "€ 2,35")
    }
    df_fasce = pd.DataFrame(fasce_onorario, index=["Onorario Minimo", "Onorario Massimo"]).T
    st.table(df_fasce)

    # Onorario annuale
    st.write("Onorario annuale basato sul numero di fatture o rilevazioni annue:")
    num_fatture = st.number_input("Numero di fatture o rilevazioni annue", min_value=1, value=90)
    
    if num_fatture <= 90:
        onorario_min = 1163
        onorario_max = 1679
    elif num_fatture <= 180:
        onorario_min = 1560
        onorario_max = 2061
    elif num_fatture <= 360:
        onorario_min = 2238
        onorario_max = 3372
    else:
        onorario_base_min = 2238
        onorario_base_max = 3372
        extra_registrazioni = num_fatture - 360
        onorario_min = onorario_base_min + (extra_registrazioni * 1.65)
        onorario_max = onorario_base_max + (extra_registrazioni * 2.35)
    
    st.write(f"Range di onorario per {num_fatture} fatture/rilevazioni:")
    st.write(f"Minimo: €{onorario_min:.2f}")
    st.write(f"Massimo: €{onorario_max:.2f}")

    onorario_annuale = st.slider("Seleziona l'onorario annuale", 
                                 min_value=float(onorario_min), 
                                 max_value=float(onorario_max), 
                                 value=float(onorario_min),
                                 step=0.01)
    
    st.write(f"Onorario annuale selezionato: €{onorario_annuale:.2f}")

    # Liquidazioni IVA
    st.subheader("Liquidazioni IVA")
    include_liquidazioni_iva = st.checkbox("Includere liquidazioni IVA?")
    costo_liquidazione = 0
    if include_liquidazioni_iva:
        periodicita = st.radio("Periodicità", ["Mensile", "Trimestrale"])
        if periodicita == "Mensile":
            costo_liquidazione = 12 * 48
        else:
            costo_liquidazione = 4 * 48
        st.write(f"Costo liquidazioni IVA: €{costo_liquidazione}")

    # Comunicazione dati IVA
    st.subheader("Comunicazione dati IVA")
    include_comunicazione_iva = st.checkbox("Includere comunicazione dati IVA?")
    costo_comunicazione_iva = 0
    if include_comunicazione_iva:
        costo_comunicazione_iva = st.slider("Redazione e invio telematico \"comunicazione dati IVA\"", 48, 125, 48)
        st.write(f"Costo comunicazione dati IVA: €{costo_comunicazione_iva}")
    
    # Modello IVA TR (opzionale)
    include_modello_iva_tr = st.checkbox("Includere Modello IVA TR?")
    costo_modello_iva_tr = 0
    if include_modello_iva_tr:
        costo_modello_iva_tr = st.slider("Costo Modello IVA TR", 48, 96, 48)
        st.write(f"Costo Modello IVA TR: €{costo_modello_iva_tr}")
    
    # Predisposizione di situazioni patrimoniali periodiche
    st.subheader("Predisposizione di Situazioni Patrimoniali Periodiche")
    include_situazioni_patrimoniali = st.checkbox("Includere predisposizione di situazioni patrimoniali periodiche?")
    costo_situazioni_patrimoniali = 0
    if include_situazioni_patrimoniali:
        costo_situazioni_patrimoniali = st.number_input("Onorario per situazioni patrimoniali periodiche", min_value=110, value=110, step=10)
        st.write(f"Costo situazioni patrimoniali periodiche: €{costo_situazioni_patrimoniali}")

    # Fatturazione Elettronica
    st.subheader("Fatturazione Elettronica")
    include_fatturazione_elettronica = st.checkbox("Includere servizi di fatturazione elettronica?")
    costo_fatturazione_elettronica = 0
    if include_fatturazione_elettronica:
        # Consulenza normativa e tecnica
        costo_consulenza = st.slider("Consulenza normativa e tecnica per fatturazione elettronica", 65, 295, 65)
        st.write(f"Costo consulenza fatturazione elettronica: €{costo_consulenza}")

        # Elaborazione e invio fatture elettroniche
        n_fatture_elettroniche = st.number_input("Numero di fatture elettroniche da elaborare e inviare", min_value=0, value=0)
        costo_per_fattura = st.slider("Costo per elaborazione e invio di ciascuna fattura elettronica", 15, 35, 15)
        costo_elaborazione_fatture = n_fatture_elettroniche * costo_per_fattura
        st.write(f"Costo elaborazione e invio fatture elettroniche: €{costo_elaborazione_fatture}")

        # Servizio di richiesta e importazione file xml
        n_download_massivi = st.number_input("Numero di download massivi di file xml", min_value=0, value=0)
        costo_download_massivi = n_download_massivi * 32
        st.write(f"Costo servizio di richiesta e importazione file xml: €{costo_download_massivi}")

        costo_fatturazione_elettronica = costo_consulenza + costo_elaborazione_fatture + costo_download_massivi
        st.write(f"Costo totale fatturazione elettronica: €{costo_fatturazione_elettronica}")

    # Dichiarazione IVA
    st.subheader("Dichiarazione IVA")
    include_dichiarazione_iva = st.checkbox("Includere Dichiarazione IVA?")
    costo_dichiarazione_iva = 0
    if include_dichiarazione_iva:
        fasce_iva = {
            "Fino a 75.000,00 Euro": (187, 367),
            "da 75.001,00 a 150.000,00 Euro": (234, 457),
            "da 150.000,01 a 300.000,00 Euro": (291, 587),
            "da 300.000,01 a 500.000,00 Euro": (366, 734),
            "da 500.000,01 a 750.000,00 Euro": (439, 1025),
            "oltre 750.000,00": (586, 1830)
        }
        volume_affari = st.selectbox("Seleziona il volume d'affari", list(fasce_iva.keys()))
        min_onorario, max_onorario = fasce_iva[volume_affari]
        costo_dichiarazione_iva = st.slider("Onorario per Dichiarazione IVA", min_onorario, max_onorario, min_onorario)
        st.write(f"Costo Dichiarazione IVA: €{costo_dichiarazione_iva}")

        # Certificazione del credito IVA
        include_certificazione_iva = st.checkbox("Includere Certificazione del credito IVA?")
        if include_certificazione_iva:
            tipo_cliente = st.radio("Tipo di cliente", ["Interno", "Esterno"])
            if tipo_cliente == "Interno":
                costo_certificazione_iva = st.slider("Costo certificazione credito IVA", 155, 420, 155)
            else:
                credito_iva = st.number_input("Importo del credito IVA da certificare", min_value=0, value=0)
                if credito_iva <= 60000:
                    costo_certificazione_iva = max(260, credito_iva * 0.02)
                else:
                    costo_certificazione_iva = max(520, credito_iva * 0.01)
            st.write(f"Costo certificazione credito IVA: €{costo_certificazione_iva}")
            costo_dichiarazione_iva += costo_certificazione_iva

    # Dichiarazione dei Redditi
    st.subheader("Dichiarazione dei Redditi")
    include_dichiarazione_redditi = st.checkbox("Includere Dichiarazione dei Redditi?")
    costo_dichiarazione_redditi = 0
    if include_dichiarazione_redditi:
        fasce_redditi = {
            "Fino a 150.000,00 Euro": (515, 877),
            "Fino a 300.000,00 Euro": (733, 1100),
            "da 300.000,01 a 500.000,00 Euro": (1098, 1647),
            "da 500.000,01 a 1.500.000,00 Euro": (1462, 2198),
            "da 1.500.000,01 a 3.000.000,00 Euro": (1824, 2746),
            "da 3.000.000,01 a 5.000.000,00 Euro": (2193, 3295),
            "da 5.000.000,01 a 7.500.000,00 Euro": (2557, 3846),
            "Oltre 7.500.000,00 Euro": (2557, 3846)
        }
        
        ammontare_ricavi = st.selectbox("Seleziona l'ammontare dei ricavi", list(fasce_redditi.keys()))
        min_onorario, max_onorario = fasce_redditi[ammontare_ricavi]
        
        if ammontare_ricavi == "Oltre 7.500.000,00 Euro":
            st.write("Per ricavi oltre 7.500.000,00 Euro, l'onorario è a discrezione. Inserisci i valori desiderati:")
            min_onorario = st.number_input("Onorario minimo", value=min_onorario, step=100)
            max_onorario = st.number_input("Onorario massimo", value=max_onorario, step=100)
        
        costo_dichiarazione_redditi = st.slider("Onorario per Dichiarazione dei Redditi", min_onorario, max_onorario, min_onorario)
        st.write(f"Costo Dichiarazione dei Redditi: €{costo_dichiarazione_redditi}")

    # Calcolo del totale iniziale
    totale = (onorario_annuale + costo_liquidazione + costo_comunicazione_iva + 
              costo_modello_iva_tr + costo_situazioni_patrimoniali + costo_fatturazione_elettronica +
              costo_dichiarazione_iva + costo_dichiarazione_redditi)

    # Riepilogo del preventivo
    st.subheader("Riepilogo Preventivo Contabilità Semplificata")
    riepilogo = {
        "Onorario annuale contabilità": onorario_annuale,
        "Liquidazioni IVA": costo_liquidazione,
        "Comunicazione dati IVA": costo_comunicazione_iva,
        "Modello IVA TR": costo_modello_iva_tr,
        "Situazioni patrimoniali periodiche": costo_situazioni_patrimoniali,
        "Fatturazione elettronica": costo_fatturazione_elettronica,
        "Dichiarazione IVA": costo_dichiarazione_iva,
        "Dichiarazione dei Redditi": costo_dichiarazione_redditi
    }

    for voce, importo in riepilogo.items():
        if importo > 0:
            st.write(f"{voce}: €{importo:.2f}")

    st.write(f"**Totale preventivo: €{totale:.2f}**")

    # Opzione per modificare i valori minimi
    with st.expander("Modifica valori minimi"):
        st.write("Modifica i valori minimi per ciascuna voce del preventivo:")
        nuovi_valori = {}
        for voce, importo in riepilogo.items():
            if importo > 0:
                nuovi_valori[voce] = st.number_input(f"Nuovo valore minimo per {voce}", 
                                                     min_value=0.0, 
                                                     value=float(importo), 
                                                     step=10.0)
        
        if st.button("Ricalcola preventivo"):
            nuovo_totale = sum(nuovi_valori.values())
            st.write("Nuovo riepilogo del preventivo:")
            for voce, importo in nuovi_valori.items():
                st.write(f"{voce}: €{importo:.2f}")
            st.write(f"**Nuovo totale preventivo: €{nuovo_totale:.2f}**")
            totale = nuovo_totale

    return {
        "Totale": totale,
        "Servizi Aggiuntivi": riepilogo
    }

def calcola_preventivo_ordinario():
    st.subheader("Preventivo per Contabilità Ordinaria")

    # Mostra la tabella dei range
    st.write("Fasce di onorario per contabilità ordinaria:")
    fasce_onorario = {
        "Fino a 600": ("€ 2.665,00", "€ 3.887,00"),
        "oltre 600 fino a 2000": ("€ 2,75 a registrazione", "€ 4,00 a registrazione"),
        "oltre 2000": ("€ 2,40 a registrazione", "€ 3,50 a registrazione")
    }
    df_fasce = pd.DataFrame(fasce_onorario, index=["Onorario Minimo", "Onorario Massimo"]).T
    st.table(df_fasce)

    # Onorario annuale
    st.write("Onorario annuale basato sul numero di fatture o rilevazioni annue:")
    num_fatture = st.number_input("Numero di fatture o rilevazioni annue", min_value=1, value=100)
    
    # Logica per calcolare onorario_min e onorario_max
    if num_fatture <= 600:
        onorario_min = 2665
        onorario_max = 3887
    elif num_fatture <= 2000:
        onorario_min = 2.75 * num_fatture
        onorario_max = 4.00 * num_fatture
    else:
        onorario_min = 2400 + (num_fatture - 2000) * 2.40
        onorario_max = 3500 + (num_fatture - 2000) * 3.50

    st.write(f"Range di onorario per {num_fatture} fatture/rilevazioni:")
    st.write(f"Minimo: €{onorario_min:.2f}")
    st.write(f"Massimo: €{onorario_max:.2f}")

    onorario_annuale = st.slider("Seleziona l'onorario annuale", 
                                 min_value=float(onorario_min), 
                                 max_value=float(onorario_max), 
                                 value=float(onorario_min),
                                 step=0.01)
    
    st.write(f"Onorario annuale selezionato: €{onorario_annuale:.2f}")

    # Liquidazioni IVA
    st.subheader("Liquidazioni IVA")
    include_liquidazioni_iva = st.checkbox("Includere liquidazioni IVA?")
    costo_liquidazione = 0
    if include_liquidazioni_iva:
        periodicita = st.radio("Periodicità", ["Mensile", "Trimestrale"])
        if periodicita == "Mensile":
            costo_liquidazione = 12 * 48
        else:
            costo_liquidazione = 4 * 48
        st.write(f"Costo liquidazioni IVA: €{costo_liquidazione}")

    # Comunicazione dati IVA
    st.subheader("Comunicazione dati IVA")
    include_comunicazione_iva = st.checkbox("Includere comunicazione dati IVA?")
    costo_comunicazione_iva = 0
    if include_comunicazione_iva:
        costo_comunicazione_iva = st.slider("Redazione e invio telematico \"comunicazione dati IVA\"", 48, 125, 48)
        st.write(f"Costo comunicazione dati IVA: €{costo_comunicazione_iva}")
    
    # Modello IVA TR (opzionale)
    include_modello_iva_tr = st.checkbox("Includere Modello IVA TR?")
    costo_modello_iva_tr = 0
    if include_modello_iva_tr:
        costo_modello_iva_tr = st.slider("Costo Modello IVA TR", 48, 96, 48)
        st.write(f"Costo Modello IVA TR: €{costo_modello_iva_tr}")
    
    # Predisposizione di situazioni patrimoniali periodiche
    st.subheader("Predisposizione di Situazioni Patrimoniali Periodiche")
    include_situazioni_patrimoniali = st.checkbox("Includere predisposizione di situazioni patrimoniali periodiche?")
    costo_situazioni_patrimoniali = 0
    if include_situazioni_patrimoniali:
        costo_situazioni_patrimoniali = st.number_input("Onorario per situazioni patrimoniali periodiche", min_value=110, value=110, step=10)
        st.write(f"Costo situazioni patrimoniali periodiche: €{costo_situazioni_patrimoniali}")

    # Fatturazione Elettronica
    st.subheader("Fatturazione Elettronica")
    include_fatturazione_elettronica = st.checkbox("Includere servizi di fatturazione elettronica?")
    costo_fatturazione_elettronica = 0
    if include_fatturazione_elettronica:
        # Consulenza normativa e tecnica
        costo_consulenza = st.slider("Consulenza normativa e tecnica per fatturazione elettronica", 65, 295, 65)
        st.write(f"Costo consulenza fatturazione elettronica: €{costo_consulenza}")

        # Elaborazione e invio fatture elettroniche
        n_fatture_elettroniche = st.number_input("Numero di fatture elettroniche da elaborare e inviare", min_value=0, value=0)
        costo_per_fattura = st.slider("Costo per elaborazione e invio di ciascuna fattura elettronica", 15, 35, 15)
        costo_elaborazione_fatture = n_fatture_elettroniche * costo_per_fattura
        st.write(f"Costo elaborazione e invio fatture elettroniche: €{costo_elaborazione_fatture}")

        # Servizio di richiesta e importazione file xml
        n_download_massivi = st.number_input("Numero di download massivi di file xml", min_value=0, value=0)
        costo_download_massivi = n_download_massivi * 32
        st.write(f"Costo servizio di richiesta e importazione file xml: €{costo_download_massivi}")

        costo_fatturazione_elettronica = costo_consulenza + costo_elaborazione_fatture + costo_download_massivi
        st.write(f"Costo totale fatturazione elettronica: €{costo_fatturazione_elettronica}")

    # Dichiarazione IVA
    st.subheader("Dichiarazione IVA")
    include_dichiarazione_iva = st.checkbox("Includere Dichiarazione IVA?")
    costo_dichiarazione_iva = 0
    if include_dichiarazione_iva:
        fasce_iva = {
            "Fino a 75.000,00 Euro": (187, 367),
            "da 75.001,00 a 150.000,00 Euro": (234, 457),
            "da 150.000,01 a 300.000,00 Euro": (291, 587),
            "da 300.000,01 a 500.000,00 Euro": (366, 734),
            "da 500.000,01 a 750.000,00 Euro": (439, 1025),
            "oltre 750.000,00": (586, 1830)
        }
        volume_affari = st.selectbox("Seleziona il volume d'affari", list(fasce_iva.keys()))
        min_onorario, max_onorario = fasce_iva[volume_affari]
        costo_dichiarazione_iva = st.slider("Onorario per Dichiarazione IVA", min_onorario, max_onorario, min_onorario)
        st.write(f"Costo Dichiarazione IVA: €{costo_dichiarazione_iva}")

        # Certificazione del credito IVA
        include_certificazione_iva = st.checkbox("Includere Certificazione del credito IVA?")
        if include_certificazione_iva:
            tipo_cliente = st.radio("Tipo di cliente", ["Interno", "Esterno"])
            if tipo_cliente == "Interno":
                costo_certificazione_iva = st.slider("Costo certificazione credito IVA", 155, 420, 155)
            else:
                credito_iva = st.number_input("Importo del credito IVA da certificare", min_value=0, value=0)
                if credito_iva <= 60000:
                    costo_certificazione_iva = max(260, credito_iva * 0.02)
                else:
                    costo_certificazione_iva = max(520, credito_iva * 0.01)
            st.write(f"Costo certificazione credito IVA: €{costo_certificazione_iva}")
            costo_dichiarazione_iva += costo_certificazione_iva

    # Dichiarazione dei Redditi
    st.subheader("Dichiarazione dei Redditi")
    include_dichiarazione_redditi = st.checkbox("Includere Dichiarazione dei Redditi?")
    costo_dichiarazione_redditi = 0
    if include_dichiarazione_redditi:
        fasce_redditi = {
            "Fino a 150.000,00 Euro": (515, 877),
            "Fino a 300.000,00 Euro": (733, 1100),
            "da 300.000,01 a 500.000,00 Euro": (1098, 1647),
            "da 500.000,01 a 1.500.000,00 Euro": (1462, 2198),
            "da 1.500.000,01 a 3.000.000,00 Euro": (1824, 2746),
            "da 3.000.000,01 a 5.000.000,00 Euro": (2193, 3295),
            "da 5.000.000,01 a 7.500.000,00 Euro": (2557, 3846),
            "Oltre 7.500.000,00 Euro": (2557, 3846)
        }
        
        ammontare_ricavi = st.selectbox("Seleziona l'ammontare dei ricavi", list(fasce_redditi.keys()))
        min_onorario, max_onorario = fasce_redditi[ammontare_ricavi]
        
        if ammontare_ricavi == "Oltre 7.500.000,00 Euro":
            st.write("Per ricavi oltre 7.500.000,00 Euro, l'onorario è a discrezione. Inserisci i valori desiderati:")
            min_onorario = st.number_input("Onorario minimo", value=min_onorario, step=100)
            max_onorario = st.number_input("Onorario massimo", value=max_onorario, step=100)
        
        costo_dichiarazione_redditi = st.slider("Onorario per Dichiarazione dei Redditi", min_onorario, max_onorario, min_onorario)
        st.write(f"Costo Dichiarazione dei Redditi: €{costo_dichiarazione_redditi}")

    # Calcolo del totale iniziale
    totale = (onorario_annuale + costo_liquidazione + costo_comunicazione_iva + 
              costo_modello_iva_tr + costo_situazioni_patrimoniali + costo_fatturazione_elettronica +
              costo_dichiarazione_iva + costo_dichiarazione_redditi)

    # Riepilogo del preventivo
    st.subheader("Riepilogo Preventivo Contabilità Ordinaria")
    riepilogo = {
        "Onorario annuale contabilità": onorario_annuale,
        "Liquidazioni IVA": costo_liquidazione,
        "Comunicazione dati IVA": costo_comunicazione_iva,
        "Modello IVA TR": costo_modello_iva_tr,
        "Situazioni patrimoniali periodiche": costo_situazioni_patrimoniali,
        "Fatturazione elettronica": costo_fatturazione_elettronica,
        "Dichiarazione IVA": costo_dichiarazione_iva,
        "Dichiarazione dei Redditi": costo_dichiarazione_redditi
    }

    for voce, importo in riepilogo.items():
        if importo > 0:
            st.write(f"{voce}: €{importo:.2f}")

    st.write(f"**Totale preventivo: €{totale:.2f}**")

    # Opzione per modificare i valori minimi
    with st.expander("Modifica valori minimi"):
        st.write("Modifica i valori minimi per ciascuna voce del preventivo:")
        nuovi_valori = {}
        for voce, importo in riepilogo.items():
            if importo > 0:
                nuovi_valori[voce] = st.number_input(f"Nuovo valore minimo per {voce}", 
                                                     min_value=0.0, 
                                                     value=float(importo), 
                                                     step=10.0)
        
        if st.button("Ricalcola preventivo"):
            nuovo_totale = sum(nuovi_valori.values())
            st.write("Nuovo riepilogo del preventivo:")
            for voce, importo in nuovi_valori.items():
                st.write(f"{voce}: €{importo:.2f}")
            st.write(f"**Nuovo totale preventivo: €{nuovo_totale:.2f}**")
            totale = nuovo_totale

    return {
        "Totale": totale,
        "Servizi Aggiuntivi": riepilogo
    }