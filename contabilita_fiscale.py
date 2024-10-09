import streamlit as st
import pandas as pd

def calcola_preventivo_forfettario():
    st.subheader("Preventivo per Contribuenti Minimi e Forfettari")

    # Visualizzazione delle tariffe
    st.write("Tariffe per il regime forfettario:")
    tariffe = {
        "Fino a 10 fatture/mese": ("€ 500,00", "€ 1.200,00"),
        "Oltre 10 fatture/mese": ("€ 750,00", "€ 1.500,00")
    }
    df_tariffe = pd.DataFrame(tariffe, index=["Minimo", "Massimo"]).T
    st.table(df_tariffe)

    # Selezione del numero di fatture
    fatture_mensili = st.radio("Numero di fatture mensili", ["Fino a 10/mese", "Oltre 10/mese"])
    if fatture_mensili == "Fino a 10/mese":
        onorario_min, onorario_max = 500, 1200
    else:
        onorario_min, onorario_max = 750, 1500

    st.write(f"Range di onorario: €{onorario_min:.2f} - €{onorario_max:.2f}")
    st.write("Questo range è basato sul numero di fatture mensili.")

    onorario_annuale = st.slider("Onorario annuale", 
                                 min_value=float(onorario_min), 
                                 max_value=float(onorario_max), 
                                 value=float(onorario_min),
                                 format="€%.2f")

    # Servizi aggiuntivi
    st.subheader("Servizi Aggiuntivi")
    servizi_aggiuntivi = {
        "Maggiorazione annua recupero corrispettivi telematici": 300,
        "Redazione situazione contabile periodica/infrannuale": 75,
    }

    servizi_selezionati = {}
    for servizio, costo_base in servizi_aggiuntivi.items():
        if st.checkbox(f"{servizio} (da €{costo_base})"):
            servizi_selezionati[servizio] = st.slider(f"Costo per {servizio}", 
                                                      min_value=float(costo_base), 
                                                      max_value=float(costo_base*2), 
                                                      value=float(costo_base),
                                                      format="€%.2f")

    # Calcolo del totale
    totale = onorario_annuale + sum(servizi_selezionati.values())

    # Riepilogo del preventivo
    st.subheader("Riepilogo Preventivo")
    st.write(f"Onorario annuale contabilità: €{onorario_annuale:.2f}")
    for servizio, costo in servizi_selezionati.items():
        st.write(f"{servizio}: €{costo:.2f}")
    st.write(f"**Totale preventivo: €{totale:.2f}**")

    return {
        "Totale": totale,
        "Servizi Aggiuntivi": {"Onorario annuale": onorario_annuale, **servizi_selezionati}
    }

def calcola_preventivo_semplificato():
    st.subheader("Preventivo per Contabilità Semplificata")

    # Visualizzazione delle tariffe
    st.write("Tariffe per la contabilità semplificata:")
    tariffe = {
        "Fino a 600 registrazioni": ("€ 2.132,00", "€ 3.110,00"),
        "Da 601 a 2000 registrazioni": ("€ 2,20 a registrazione", "€ 3,20 a registrazione"),
        "Oltre 2000 registrazioni": ("€ 1,92 a registrazione", "€ 2,80 a registrazione")
    }
    df_tariffe = pd.DataFrame(tariffe, index=["Minimo", "Massimo"]).T
    st.table(df_tariffe)
    st.write("Nota: Per oltre 2000 registrazioni, si applica la tariffa indicata solo alle registrazioni eccedenti.")

    # Input per il numero di registrazioni
    num_registrazioni = st.number_input("Numero di registrazioni annue", min_value=1, value=100)
    
    # Calcolo dell'onorario base e del range di fatturato
    if num_registrazioni <= 600:
        onorario_min, onorario_max = 2132, 3110
        fatturato_min, fatturato_max = 0, 400000  # Range di fatturato per contabilità semplificata
    elif num_registrazioni <= 2000:
        onorario_min = 2.20 * num_registrazioni
        onorario_max = 3.20 * num_registrazioni
        fatturato_min, fatturato_max = 0, 700000  # Range di fatturato per contabilità semplificata
    else:
        onorario_min = 1920 + (num_registrazioni - 2000) * 1.92
        onorario_max = 2800 + (num_registrazioni - 2000) * 2.80
        fatturato_min, fatturato_max = 0, 700000  # Range di fatturato per contabilità semplificata

    st.write(f"Range di onorario calcolato: €{onorario_min:.2f} - €{onorario_max:.2f}")
    st.write(f"Range di fatturato per contabilità semplificata: €{fatturato_min:,.2f} - €{fatturato_max:,.2f}")
    st.write("Questo range di onorario è calcolato in base al numero di registrazioni e alle tariffe sopra indicate.")
    st.write("Il range di fatturato è basato sui limiti previsti per la contabilità semplificata.")

    onorario_annuale = st.slider("Onorario annuale", 
                                 min_value=float(onorario_min), 
                                 max_value=float(onorario_max), 
                                 value=float(onorario_min),
                                 format="€%.2f")

    # Liquidazioni IVA e comunicazioni
    st.subheader("Liquidazioni IVA e comunicazioni")
    
    # Liquidazioni IVA
    st.write("Liquidazioni IVA:")
    include_liquidazioni_iva = st.checkbox("Includere liquidazioni IVA?")
    if include_liquidazioni_iva:
        periodicita_iva = st.radio("Periodicità IVA", ["Mensile", "Trimestrale"])
        if periodicita_iva == "Mensile":
            st.write("Costo per singola liquidazione mensile: €48")
            num_liquidazioni = 12
            costo_liquidazioni = 48 * num_liquidazioni
        else:
            st.write("Costo per singola liquidazione trimestrale: €70")
            num_liquidazioni = 4
            costo_liquidazioni = 70 * num_liquidazioni
        st.write(f"Costo stimato per 12 mesi: €{costo_liquidazioni:.2f} ({num_liquidazioni} liquidazioni)")
    else:
        costo_liquidazioni = 0

    # Comunicazione dati IVA (LIPE)
    st.write("Redazione e invio telematico comunicazione dati IVA (LIPE):")
    st.write("Costo per singola comunicazione: da €48 a €125")
    include_comunicazione_iva = st.checkbox("Includere comunicazione dati IVA (LIPE)?")
    if include_comunicazione_iva:
        num_comunicazioni = 4  # Di solito sono 4 comunicazioni all'anno
        costo_min_comunicazione = 48
        costo_max_comunicazione = 125
        costo_comunicazione_iva = st.slider(
            "Costo per singola comunicazione LIPE",
            min_value=float(costo_min_comunicazione),
            max_value=float(costo_max_comunicazione),
            value=float(costo_min_comunicazione),
            step=1.0
        )
        costo_totale_comunicazioni = costo_comunicazione_iva * num_comunicazioni
        st.write(f"Costo stimato per 12 mesi: €{costo_totale_comunicazioni:.2f} ({num_comunicazioni} comunicazioni)")
    else:
        costo_totale_comunicazioni = 0

    # Modello IVA TR
    st.write("Modello IVA TR:")
    include_modello_iva_tr = st.checkbox("Includere Modello IVA TR?")
    if include_modello_iva_tr:
        costo_modello_iva_tr = st.slider("Costo Modello IVA TR", min_value=48.0, max_value=96.0, value=48.0, step=1.0)
        st.write(f"Costo Modello IVA TR: €{costo_modello_iva_tr:.2f}")
    else:
        costo_modello_iva_tr = 0

    # Dichiarazione IVA
    st.write("Dichiarazione IVA:")
    fasce_iva = {
        "Fino a 75.000,00 Euro": (187, 367),
        "da 75.001,00 a 150.000,00 Euro": (234, 457),
        "da 150.000,01 a 300.000,00 Euro": (291, 587),
        "da 300.000,01 a 500.000,00 Euro": (366, 734),
        "da 500.000,01 a 750.000,00 Euro": (439, 1025),
        "oltre 750.000,00": (586, 1830)
    }
    st.table(pd.DataFrame(fasce_iva, index=["Minimo", "Massimo"]).T)
    
    include_dichiarazione_iva = st.checkbox("Includere Dichiarazione IVA?")
    if include_dichiarazione_iva:
        fascia_iva = st.selectbox("Seleziona la fascia di volume d'affari", list(fasce_iva.keys()))
        min_iva, max_iva = fasce_iva[fascia_iva]
        costo_dichiarazione_iva = st.slider("Costo Dichiarazione IVA", min_value=float(min_iva), max_value=float(max_iva), value=float(min_iva), step=1.0)
        st.write(f"Costo Dichiarazione IVA: €{costo_dichiarazione_iva:.2f}")
    else:
        costo_dichiarazione_iva = 0

    # Dichiarazione dei redditi
    st.write("Dichiarazione dei redditi:")
    tipo_impresa = st.radio("Tipo di impresa", ["Impresa individuale", "Società"])

    fasce_redditi = {
        "Fino a 75.000,00 Euro": (292, 587),
        "da 75.001,00 a 150.000,00 Euro": (526, 791),
        "da 150.000,01 a 300.000,00 Euro": (702, 1055),
        "da 300.000,01 a 500.000,00 Euro": (878, 1318),
        "da 500.000,01 a 750.000,00 Euro": (1052, 1582),
        "oltre 750.000,00": (1315, 1976)
    }
    st.table(pd.DataFrame(fasce_redditi, index=["Minimo", "Massimo"]).T)

    include_dichiarazione_redditi = st.checkbox("Includere Dichiarazione dei redditi?")
    if include_dichiarazione_redditi:
        fascia_redditi = st.selectbox("Seleziona la fascia di reddito", list(fasce_redditi.keys()))
        min_redditi, max_redditi = fasce_redditi[fascia_redditi]
        
        if tipo_impresa == "Impresa individuale":
            costo_dichiarazione_redditi = st.slider("Costo Dichiarazione dei redditi", min_value=float(min_redditi), max_value=float(max_redditi), value=float(min_redditi), step=1.0)
            st.write(f"Costo Dichiarazione dei redditi: €{costo_dichiarazione_redditi:.2f}")
        else:  # Società
            num_soci = st.number_input("Numero di soci", min_value=1, value=1, step=1)
            costo_dichiarazione_redditi_societa = st.slider("Costo Dichiarazione dei redditi società", min_value=float(min_redditi), max_value=float(max_redditi), value=float(min_redditi), step=1.0)
            
            # Modifica per la dichiarazione dei redditi dei soci
            costo_minimo_dichiarazione_socio = 292  # Valore minimo per la dichiarazione del socio
            costo_dichiarazione_redditi_soci = st.slider(
                "Costo Dichiarazione dei redditi per socio",
                min_value=float(costo_minimo_dichiarazione_socio),
                max_value=float(costo_minimo_dichiarazione_socio * 3),  # Triplicare il valore minimo come massimo
                value=float(costo_minimo_dichiarazione_socio),
                step=1.0
            )
            st.info("Nota: Il costo della dichiarazione dei redditi per socio è una scelta dell'utente e non è legato al fatturato della società.")
            
            costo_dichiarazione_redditi = costo_dichiarazione_redditi_societa + (costo_dichiarazione_redditi_soci * num_soci)
            st.write(f"Costo Dichiarazione dei redditi società: €{costo_dichiarazione_redditi_societa:.2f}")
            st.write(f"Costo Dichiarazione dei redditi soci (x{num_soci}): €{costo_dichiarazione_redditi_soci * num_soci:.2f}")
            st.write(f"Costo totale Dichiarazioni dei redditi: €{costo_dichiarazione_redditi:.2f}")
    else:
        costo_dichiarazione_redditi = 0

    # Situazioni patrimoniali periodiche
    st.write("Predisposizione di situazioni patrimoniali periodiche:")
    st.write("Costo minimo per situazione: €110")
    include_situazioni_periodiche = st.checkbox("Includere situazioni patrimoniali periodiche?")
    if include_situazioni_periodiche:
        num_situazioni = st.number_input("Numero di situazioni patrimoniali da redigere", min_value=1, max_value=12, value=1, step=1)
        costo_situazioni = 110 * num_situazioni
        st.write(f"Costo totale per {num_situazioni} situazioni patrimoniali: €{costo_situazioni:.2f}")
    else:
        costo_situazioni = 0

    # Calcolo del totale
    totale = (onorario_annuale + costo_liquidazioni + costo_totale_comunicazioni + 
              costo_modello_iva_tr + costo_dichiarazione_iva + costo_dichiarazione_redditi +
              costo_situazioni)

    # Riepilogo
    st.subheader("Riepilogo Preventivo")
    st.write(f"Onorario annuale contabilità: €{onorario_annuale:.2f}")
    if include_liquidazioni_iva:
        st.write(f"Liquidazioni IVA: €{costo_liquidazioni:.2f}")
    if include_comunicazione_iva:
        st.write(f"Comunicazione dati IVA (LIPE): €{costo_totale_comunicazioni:.2f}")
    if include_modello_iva_tr:
        st.write(f"Modello IVA TR: €{costo_modello_iva_tr:.2f}")
    if include_dichiarazione_iva:
        st.write(f"Dichiarazione IVA: €{costo_dichiarazione_iva:.2f}")
    if include_dichiarazione_redditi:
        if tipo_impresa == "Impresa individuale":
            st.write(f"Dichiarazione dei redditi: €{costo_dichiarazione_redditi:.2f}")
        else:
            st.write(f"Dichiarazione dei redditi società: €{costo_dichiarazione_redditi_societa:.2f}")
            st.write(f"Dichiarazione dei redditi soci (x{num_soci}): €{costo_dichiarazione_redditi_soci * num_soci:.2f}")
            st.write(f"Totale Dichiarazioni dei redditi: €{costo_dichiarazione_redditi:.2f}")
    if include_situazioni_periodiche:
        st.write(f"Situazioni patrimoniali periodiche: €{costo_situazioni:.2f}")
    st.write(f"**Totale preventivo: €{totale:.2f}**")

    # Modifica manuale dei valori
    st.subheader("Modifica manuale dei valori")
    onorario_annuale_manuale = st.number_input("Onorario annuale", value=float(onorario_annuale), step=10.0)
    costo_liquidazioni_manuale = st.number_input("Costo liquidazioni IVA", 
                                                 value=float(costo_liquidazioni), 
                                                 step=1.0, 
                                                 help="48€ per liquidazione mensile, 70€ per liquidazione trimestrale")
    costo_comunicazione_iva_manuale = st.number_input("Costo Comunicazione dati IVA (LIPE)", value=float(costo_totale_comunicazioni), step=1.0)
    costo_modello_iva_tr_manuale = st.number_input("Costo Modello IVA TR", value=float(costo_modello_iva_tr), step=1.0)
    costo_dichiarazione_iva_manuale = st.number_input("Costo Dichiarazione IVA", value=float(costo_dichiarazione_iva), step=1.0)
    if tipo_impresa == "Impresa individuale":
        costo_dichiarazione_redditi_manuale = st.number_input("Costo Dichiarazione dei redditi", value=float(costo_dichiarazione_redditi), step=1.0)
    else:
        costo_dichiarazione_redditi_societa_manuale = st.number_input("Costo Dichiarazione dei redditi società", value=float(costo_dichiarazione_redditi_societa), step=1.0)
        costo_dichiarazione_redditi_soci_manuale = st.number_input("Costo Dichiarazione dei redditi soci (totale)", value=float(costo_dichiarazione_redditi_soci * num_soci), step=1.0)
        costo_dichiarazione_redditi_manuale = costo_dichiarazione_redditi_societa_manuale + costo_dichiarazione_redditi_soci_manuale
    costo_situazioni_manuale = st.number_input("Costo situazioni patrimoniali periodiche", value=float(costo_situazioni), step=1.0)

    totale_manuale = (onorario_annuale_manuale + costo_liquidazioni_manuale + costo_comunicazione_iva_manuale + 
                      costo_modello_iva_tr_manuale + costo_dichiarazione_iva_manuale + costo_dichiarazione_redditi_manuale +
                      costo_situazioni_manuale)
    st.write(f"**Totale preventivo (modificato manualmente): €{totale_manuale:.2f}**")

    return {
        "Totale": totale_manuale,
        "Servizi Aggiuntivi": {
            "Onorario annuale": onorario_annuale_manuale,
            "Liquidazioni IVA": costo_liquidazioni_manuale,
            "Comunicazione dati IVA (LIPE)": costo_comunicazione_iva_manuale,
            "Modello IVA TR": costo_modello_iva_tr_manuale,
            "Dichiarazione IVA": costo_dichiarazione_iva_manuale,
            "Dichiarazione dei redditi": costo_dichiarazione_redditi_manuale,
            "Situazioni patrimoniali periodiche": costo_situazioni_manuale,
        }
    }

def calcola_preventivo_ordinario():
    st.subheader("Preventivo per Contabilità Ordinaria")

    # Visualizzazione delle tariffe
    st.write("Tariffe per la contabilità ordinaria:")
    tariffe = {
        "Fino a 600 registrazioni": ("€ 2.665,00", "€ 3.887,00"),
        "Da 601 a 2000 registrazioni": ("€ 2,75 a registrazione", "€ 4,00 a registrazione"),
        "Oltre 2000 registrazioni": ("€ 2,40 a registrazione", "€ 3,50 a registrazione")
    }
    df_tariffe = pd.DataFrame(tariffe, index=["Minimo", "Massimo"]).T
    st.table(df_tariffe)
    st.write("Nota: Per oltre 2000 registrazioni, si applica la tariffa indicata solo alle registrazioni eccedenti.")

    # Input per il numero di registrazioni
    num_registrazioni = st.number_input("Numero di registrazioni annue", min_value=1, value=100)
    
    # Calcolo dell'onorario base
    if num_registrazioni <= 600:
        onorario_min = 2665
        onorario_max = 3887
    elif num_registrazioni <= 2000:
        onorario_min = 2.75 * num_registrazioni
        onorario_max = 4.00 * num_registrazioni
    else:
        onorario_min = 2665 + (2000 - 600) * 2.75 + (num_registrazioni - 2000) * 2.40
        onorario_max = 3887 + (2000 - 600) * 4.00 + (num_registrazioni - 2000) * 3.50
    
    st.write(f"Range di onorario calcolato: €{onorario_min:.2f} - €{onorario_max:.2f}")
    st.write("Questo range è calcolato in base al numero di registrazioni e alle tariffe sopra indicate.")

    onorario_base = st.slider("Seleziona l'onorario base", min_value=float(onorario_min), max_value=float(onorario_max), value=float(onorario_min), step=10.0)
    st.write(f"Onorario base selezionato: €{onorario_base:.2f}")

    # Liquidazioni IVA e comunicazioni
    st.subheader("Liquidazioni IVA e comunicazioni")
    
    # Liquidazioni IVA
    st.write("Liquidazioni IVA:")
    include_liquidazioni_iva = st.checkbox("Includere liquidazioni IVA?")
    if include_liquidazioni_iva:
        periodicita_iva = st.radio("Periodicità IVA", ["Mensile", "Trimestrale"])
        if periodicita_iva == "Mensile":
            num_liquidazioni = 12
        else:
            num_liquidazioni = 4
        costo_liquidazioni = 48 * num_liquidazioni
        st.write(f"Costo stimato per 12 mesi: €{costo_liquidazioni:.2f} ({num_liquidazioni} liquidazioni)")
    else:
        costo_liquidazioni = 0

    # Comunicazione dati IVA (LIPE)
    st.write("Redazione e invio telematico comunicazione dati IVA (LIPE):")
    st.write("Costo per singola comunicazione: da €48 a €125")
    include_comunicazione_iva = st.checkbox("Includere comunicazione dati IVA (LIPE)?")
    if include_comunicazione_iva:
        num_comunicazioni = 4  # Di solito sono 4 comunicazioni all'anno
        costo_min_comunicazione = 48
        costo_max_comunicazione = 125
        costo_comunicazione_iva = st.slider(
            "Costo per singola comunicazione LIPE",
            min_value=float(costo_min_comunicazione),
            max_value=float(costo_max_comunicazione),
            value=float(costo_min_comunicazione),
            step=1.0
        )
        costo_totale_comunicazioni = costo_comunicazione_iva * num_comunicazioni
        st.write(f"Costo stimato per 12 mesi: €{costo_totale_comunicazioni:.2f} ({num_comunicazioni} comunicazioni)")
    else:
        costo_totale_comunicazioni = 0

    # Modello IVA TR
    st.write("Modello IVA TR:")
    include_modello_iva_tr = st.checkbox("Includere Modello IVA TR?")
    if include_modello_iva_tr:
        costo_modello_iva_tr = st.slider("Costo Modello IVA TR", min_value=48.0, max_value=96.0, value=48.0, step=1.0)
        st.write(f"Costo Modello IVA TR: €{costo_modello_iva_tr:.2f}")
    else:
        costo_modello_iva_tr = 0

    # Dichiarazione IVA
    st.write("Dichiarazione IVA:")
    fasce_iva = {
        "Fino a 75.000,00 Euro": (187, 367),
        "da 75.001,00 a 150.000,00 Euro": (234, 457),
        "da 150.000,01 a 300.000,00 Euro": (291, 587),
        "da 300.000,01 a 500.000,00 Euro": (366, 734),
        "da 500.000,01 a 750.000,00 Euro": (439, 1025),
        "oltre 750.000,00": (586, 1830)
    }
    st.table(pd.DataFrame(fasce_iva, index=["Minimo", "Massimo"]).T)
    
    include_dichiarazione_iva = st.checkbox("Includere Dichiarazione IVA?")
    if include_dichiarazione_iva:
        fascia_iva = st.selectbox("Seleziona la fascia di volume d'affari", list(fasce_iva.keys()))
        min_iva, max_iva = fasce_iva[fascia_iva]
        costo_dichiarazione_iva = st.slider("Costo Dichiarazione IVA", min_value=float(min_iva), max_value=float(max_iva), value=float(min_iva), step=1.0)
        st.write(f"Costo Dichiarazione IVA: €{costo_dichiarazione_iva:.2f}")
    else:
        costo_dichiarazione_iva = 0

    # Dichiarazione dei redditi per società di capitali
    st.write("Dichiarazione dei redditi per società di capitali:")
    fasce_redditi = {
        "Fino a 150.000,00 Euro": (515, 877),
        "Fino a 300.000,00 Euro": (733, 1100),
        "da 300.000,01 a 500.000,00 Euro": (1098, 1647),
        "da 500.000,01 a 1.500.000,00 Euro": (1462, 2198),
        "da 1.500.000,01 a 3.000.000,00 Euro": (1824, 2746),
        "da 3.000.000,01 a 5.000.000,00 Euro": (2193, 3295),
        "da 5.000.000,01 a 7.500.000,00 Euro": (2557, 3846),
        "Oltre": ("a discrezione", "a discrezione")
    }
    st.table(pd.DataFrame(fasce_redditi, index=["Minimo", "Massimo"]).T)
    
    include_dichiarazione_redditi = st.checkbox("Includere Dichiarazione dei redditi?")
    if include_dichiarazione_redditi:
        fascia_redditi = st.selectbox("Seleziona la fascia di reddito", list(fasce_redditi.keys()))
        min_redditi, max_redditi = fasce_redditi[fascia_redditi]
        if fascia_redditi != "Oltre":
            costo_dichiarazione_redditi = st.slider("Costo Dichiarazione dei redditi", min_value=float(min_redditi), max_value=float(max_redditi), value=float(min_redditi), step=1.0)
        else:
            costo_dichiarazione_redditi = st.number_input("Inserisci il costo per la Dichiarazione dei redditi", min_value=0.0, step=100.0)
        st.write(f"Costo Dichiarazione dei redditi: €{costo_dichiarazione_redditi:.2f}")
    else:
        costo_dichiarazione_redditi = 0

    # Bilanci
    st.write("Bilanci:")
    fasce_bilanci = {
        "Fino a 130.000,00 Euro": (352, 555),
        "da 130.000,01 a 500.000,00 Euro": (555, 976),
        "Da 500.000,01 a 1.300.000,00 Euro": (976, 1392),
        "Da 1.300.000,01 a 2.600.000,00 Euro": (1392, 2087),
        "da 2.600.000,01 a 5.750.000,00 Euro": (2087, 2783),
        "Oltre": ("a discrezione", "a discrezione")
    }
    st.table(pd.DataFrame(fasce_bilanci, index=["Minimo", "Massimo"]).T)
    
    include_bilancio = st.checkbox("Includere Bilancio?")
    if include_bilancio:
        fascia_bilancio = st.selectbox("Seleziona la fascia di attività-perdite", list(fasce_bilanci.keys()))
        min_bilancio, max_bilancio = fasce_bilanci[fascia_bilancio]
        if fascia_bilancio != "Oltre":
            costo_bilancio = st.slider("Costo Bilancio", min_value=float(min_bilancio), max_value=float(max_bilancio), value=float(min_bilancio), step=1.0)
        else:
            costo_bilancio = st.number_input("Inserisci il costo per il Bilancio", min_value=0.0, step=100.0)
        st.write(f"Costo Bilancio: €{costo_bilancio:.2f}")
    else:
        costo_bilancio = 0

    # Componenti positivi di reddito
    st.write("Componenti positivi di reddito:")
    fasce_componenti_positivi = {
        "Fino a 150.000,00 Euro": (352, 696),
        "Fino a 300.000,00 Euro": (415, 765),
        "da 300.000,01 a 500.000,00 Euro": (565, 976),
        "da 500.000,01 a 1.500.000,00 Euro": (696, 1114),
        "da 1.500.000,01 a 3.000.000,00 Euro": (1044, 1392),
        "da 3.000.000,01 a 5.000.000,00 Euro": (1392, 2087),
        "da 5.000.000,01 a 7.500.000,00 Euro": (2087, 2783),
        "Oltre": ("a discrezione", "a discrezione")
    }
    st.table(pd.DataFrame(fasce_componenti_positivi, index=["Minimo", "Massimo"]).T)
    
    include_componenti_positivi = st.checkbox("Includere calcolo componenti positivi di reddito?")
    if include_componenti_positivi:
        fascia_componenti_positivi = st.selectbox("Seleziona la fascia di componenti positivi di reddito", list(fasce_componenti_positivi.keys()))
        min_componenti_positivi, max_componenti_positivi = fasce_componenti_positivi[fascia_componenti_positivi]
        if fascia_componenti_positivi != "Oltre":
            costo_componenti_positivi = st.slider("Costo calcolo componenti positivi", min_value=float(min_componenti_positivi), max_value=float(max_componenti_positivi), value=float(min_componenti_positivi), step=1.0)
        else:
            costo_componenti_positivi = st.number_input("Inserisci il costo per il calcolo dei componenti positivi", min_value=0.0, step=100.0)
        st.write(f"Costo calcolo componenti positivi: €{costo_componenti_positivi:.2f}")
    else:
        costo_componenti_positivi = 0

    # Altri servizi
    altri_servizi = {
        "Predisposizione per l'invio telematico dei bilanci delle società di capitali": 350,
        "Adempimenti connessi alla nomina o al rinnovo dell'organo amministrativo delle società di capitali": 420
    }
    
    st.write("Altri servizi disponibili:")
    for servizio, costo in altri_servizi.items():
        if st.checkbox(f"{servizio} (€{costo})"):
            st.write(f"- {servizio}: €{costo}")
        else:
            altri_servizi[servizio] = 0

    # Situazioni patrimoniali periodiche
    st.write("Predisposizione di situazioni patrimoniali periodiche:")
    st.write("Costo minimo per situazione: €110")
    include_situazioni_periodiche = st.checkbox("Includere situazioni patrimoniali periodiche?")
    if include_situazioni_periodiche:
        num_situazioni = st.number_input("Numero di situazioni patrimoniali da redigere", min_value=1, max_value=12, value=1, step=1)
        costo_situazioni = 110 * num_situazioni
        st.write(f"Costo totale per {num_situazioni} situazioni patrimoniali: €{costo_situazioni:.2f}")
    else:
        costo_situazioni = 0

    # Calcolo del totale
    totale = (onorario_base + costo_liquidazioni + costo_totale_comunicazioni + 
              costo_modello_iva_tr + costo_dichiarazione_iva + costo_dichiarazione_redditi + 
              costo_bilancio + costo_componenti_positivi + costo_situazioni + sum(altri_servizi.values()))

    # Riepilogo
    st.subheader("Riepilogo Preventivo")
    st.write(f"Onorario base: €{onorario_base:.2f}")
    if include_liquidazioni_iva:
        st.write(f"Liquidazioni IVA: €{costo_liquidazioni:.2f}")
    if include_comunicazione_iva:
        st.write(f"Comunicazione dati IVA (LIPE): €{costo_totale_comunicazioni:.2f}")
    if include_modello_iva_tr:
        st.write(f"Modello IVA TR: €{costo_modello_iva_tr:.2f}")
    if include_dichiarazione_iva:
        st.write(f"Dichiarazione IVA: €{costo_dichiarazione_iva:.2f}")
    if include_dichiarazione_redditi:
        st.write(f"Dichiarazione dei redditi: €{costo_dichiarazione_redditi:.2f}")
    if include_bilancio:
        st.write(f"Bilancio: €{costo_bilancio:.2f}")
    if include_componenti_positivi:
        st.write(f"Calcolo componenti positivi: €{costo_componenti_positivi:.2f}")
    for servizio, costo in altri_servizi.items():
        if costo > 0:
            st.write(f"{servizio}: €{costo:.2f}")
    if include_situazioni_periodiche:
        st.write(f"Situazioni patrimoniali periodiche: €{costo_situazioni:.2f}")
    st.write(f"**Totale preventivo: €{totale:.2f}**")

    # Modifica manuale dei valori
    st.subheader("Modifica manuale dei valori")
    onorario_base_manuale = st.number_input("Onorario base", value=float(onorario_base), step=10.0)
    costo_liquidazioni_manuale = st.number_input("Costo liquidazioni IVA", 
                                                 value=float(costo_liquidazioni), 
                                                 step=1.0, 
                                                 help="48€ per liquidazione mensile, 70€ per liquidazione trimestrale")
    costo_comunicazione_iva_manuale = st.number_input("Costo Comunicazione dati IVA (LIPE)", value=float(costo_totale_comunicazioni), step=1.0)
    costo_modello_iva_tr_manuale = st.number_input("Costo Modello IVA TR", value=float(costo_modello_iva_tr), step=1.0)
    costo_dichiarazione_iva_manuale = st.number_input("Costo Dichiarazione IVA", value=float(costo_dichiarazione_iva), step=1.0)
    costo_dichiarazione_redditi_manuale = st.number_input("Costo Dichiarazione dei redditi", value=float(costo_dichiarazione_redditi), step=1.0)
    costo_bilancio_manuale = st.number_input("Costo Bilancio", value=float(costo_bilancio), step=1.0)
    costo_componenti_positivi_manuale = st.number_input("Costo calcolo componenti positivi", value=float(costo_componenti_positivi), step=1.0)
    costo_situazioni_manuale = st.number_input("Costo situazioni patrimoniali periodiche", value=float(costo_situazioni), step=1.0)

    totale_manuale = (onorario_base_manuale + costo_liquidazioni_manuale + costo_comunicazione_iva_manuale + 
                      costo_modello_iva_tr_manuale + costo_dichiarazione_iva_manuale + costo_dichiarazione_redditi_manuale + 
                      costo_bilancio_manuale + costo_componenti_positivi_manuale + costo_situazioni_manuale + sum(altri_servizi.values()))
    st.write(f"**Totale preventivo (modificato manualmente): €{totale_manuale:.2f}**")

    return {
        "Totale": totale_manuale,
        "Servizi Aggiuntivi": {
            "Onorario base": onorario_base_manuale,
            "Liquidazioni IVA": costo_liquidazioni_manuale,
            "Comunicazione dati IVA (LIPE)": costo_comunicazione_iva_manuale,
            "Modello IVA TR": costo_modello_iva_tr_manuale,
            "Dichiarazione IVA": costo_dichiarazione_iva_manuale,
            "Dichiarazione dei redditi": costo_dichiarazione_redditi_manuale,
            "Bilancio": costo_bilancio_manuale,
            "Calcolo componenti positivi": costo_componenti_positivi_manuale,
            "Situazioni patrimoniali periodiche": costo_situazioni_manuale,
            **{k: v for k, v in altri_servizi.items() if v > 0}
        }
    }