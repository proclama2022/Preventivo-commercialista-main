import streamlit as st
from estrai_info import load_document, split_text, extract_info
import os
from contabilita_fiscale import calcola_preventivo_forfettario, calcola_preventivo_semplificato, calcola_preventivo_ordinario
from genera_preventivo import genera_preventivo

# Inizializza le variabili di sessione
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = st.secrets["openai"]["api_key"]
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'cliente_info' not in st.session_state:
    st.session_state.cliente_info = {}
if 'studio_info' not in st.session_state:
    st.session_state.studio_info = {}
if 'tipo_contabilita' not in st.session_state:
    st.session_state.tipo_contabilita = None
if 'servizi_aggiuntivi' not in st.session_state:
    st.session_state.servizi_aggiuntivi = {}

def main():
    st.set_page_config(page_title="Generatore Preventivi Commercialista", layout="wide")
    
    st.title("Generatore Preventivi Commercialista")
    st.write("Benvenuto! Questo strumento ti aiuterà a creare un preventivo personalizzato in pochi semplici passaggi.")
    st.write("Il tariffario utilizzato è basato sugli onorari consigliati da ANC per il 2024.")

    st.sidebar.title("Istruzioni per la chiave API OpenAI")
    st.sidebar.markdown("""
    La chiave API di OpenAI è necessaria solo se desideri estrarre automaticamente le informazioni da una visura o altro documento per creare l'anagrafica.

    Se vuoi utilizzare questa funzione, segui questi passaggi per ottenere una chiave API:
    1. Vai su [OpenAI API](https://platform.openai.com/signup)
    2. Crea un account o accedi
    3. Vai alla sezione "API Keys"
    4. Clicca su "Create new secret key"
    5. Copia la chiave generata e incollala qui sotto

    Se non hai bisogno di estrarre informazioni da documenti, puoi lasciare questo campo vuoto e procedere con l'inserimento manuale dei dati.

    Per maggiori dettagli, consulta [questa guida](https://medium.com/@lorenzozar/how-to-get-your-own-openai-api-key-f4d44e60c327).
    """)

    # Aggiungi un campo per inserire la chiave API di OpenAI
    api_key = st.sidebar.text_input("Inserisci la tua chiave API di OpenAI (opzionale)", value=st.session_state.openai_api_key, type="password")
    
    if api_key:
        st.session_state.openai_api_key = api_key
        st.success("Chiave API salvata con successo!")
    
    # Procedi con i passaggi dell'applicazione
    steps = [
        handle_cliente_info,
        handle_studio_info,
        handle_tipo_contabilita,
        handle_servizi_aggiuntivi,
        handle_genera_preventivo
    ]

    # Mostra il progresso
    st.progress((st.session_state.step + 1) / len(steps))
    st.write(f"Passo {st.session_state.step + 1} di {len(steps)}")

    # Esegui il passo corrente
    current_step = steps[st.session_state.step]
    current_step()

    # Pulsanti per navigare tra i passi
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.step > 0:
            if st.button("Indietro"):
                st.session_state.step -= 1
                st.rerun()
    with col3:
        if st.session_state.step < len(steps) - 1:
            if st.button("Avanti"):
                st.session_state.step += 1
                st.rerun()

def handle_cliente_info():
    st.subheader("Informazioni Cliente")
    
    # Opzione per caricare un file
    uploaded_file = st.file_uploader("Carica un documento (visura, fattura, ecc.) per estrarre automaticamente le informazioni del cliente", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        if not st.session_state.openai_api_key:
            st.warning("Per estrarre le informazioni dal documento, è necessaria una chiave API di OpenAI. Inseriscila nella barra laterale.")
        else:
            with st.spinner("Estrazione delle informazioni in corso..."):
                doc = load_document(uploaded_file)
                text = " ".join([page.page_content for page in doc])
                extracted_info = extract_info(text)
                
                # Aggiorna le informazioni del cliente con quelle estratte
                for key, value in extracted_info.items():
                    if key.endswith('_cliente'):
                        st.session_state.cliente_info[key[:-8]] = value
    
    # Campi di input per le informazioni del cliente
    st.session_state.cliente_info['nome'] = st.text_input("Nome Cliente", st.session_state.cliente_info.get('nome', ''))
    st.session_state.cliente_info['indirizzo'] = st.text_input("Indirizzo Cliente", st.session_state.cliente_info.get('indirizzo', ''))
    st.session_state.cliente_info['email'] = st.text_input("Email Cliente", st.session_state.cliente_info.get('email', ''))
    st.session_state.cliente_info['partita_iva'] = st.text_input("Partita IVA Cliente", st.session_state.cliente_info.get('partita_iva', ''))

def handle_studio_info():
    st.subheader("Informazioni Studio")
    
    # Opzione per caricare un file
    uploaded_file = st.file_uploader("Carica un documento per estrarre automaticamente le informazioni dello studio", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        with st.spinner("Estrazione delle informazioni in corso..."):
            doc = load_document(uploaded_file)
            text = " ".join([page.page_content for page in doc])
            extracted_info = extract_info(text)
            
            # Aggiorna le informazioni dello studio con quelle estratte
            for key, value in extracted_info.items():
                if key.endswith('_studio'):
                    st.session_state.studio_info[key[:-7]] = value
    
    # Campi di input per le informazioni dello studio
    st.session_state.studio_info['nome'] = st.text_input("Nome Studio", st.session_state.studio_info.get('nome', ''))
    st.session_state.studio_info['indirizzo'] = st.text_input("Indirizzo Studio", st.session_state.studio_info.get('indirizzo', ''))
    st.session_state.studio_info['email'] = st.text_input("Email Studio", st.session_state.studio_info.get('email', ''))
    st.session_state.studio_info['partita_iva'] = st.text_input("Partita IVA Studio", st.session_state.studio_info.get('partita_iva', ''))

def handle_tipo_contabilita():
    st.subheader("Tipo di Contabilità")
    st.session_state.tipo_contabilita = st.radio("Seleziona il tipo di contabilità", 
                                                 ["Forfettaria", "Semplificata", "Ordinaria"],
                                                 index=["Forfettaria", "Semplificata", "Ordinaria"].index(st.session_state.tipo_contabilita) if st.session_state.tipo_contabilita else 0)

def handle_servizi_aggiuntivi():
    st.subheader("Servizi Aggiuntivi")
    if st.session_state.tipo_contabilita == "Forfettaria":
        st.session_state.servizi_aggiuntivi = calcola_preventivo_forfettario()
    elif st.session_state.tipo_contabilita == "Semplificata":
        st.session_state.servizi_aggiuntivi = calcola_preventivo_semplificato()
    else:
        st.session_state.servizi_aggiuntivi = calcola_preventivo_ordinario()

def handle_genera_preventivo():
    st.subheader("Riepilogo Preventivo")
    st.write("La funzione di generazione del file del preventivo verrà implementata nelle prossime settimane.")
    st.write("Ecco un riepilogo dettagliato delle informazioni generate per il preventivo:")

    st.write("**Informazioni Cliente:**")
    for key, value in st.session_state.cliente_info.items():
        st.write(f"- {key.capitalize()}: {value}")

    st.write("**Informazioni Studio:**")
    for key, value in st.session_state.studio_info.items():
        st.write(f"- {key.capitalize()}: {value}")

    st.write(f"**Tipo di Contabilità:** {st.session_state.tipo_contabilita}")

    st.write("**Servizi Aggiuntivi:**")
    for servizio, costo in st.session_state.servizi_aggiuntivi.get('Servizi Aggiuntivi', {}).items():
        st.write(f"- {servizio}: €{costo:.2f}")

    totale = st.session_state.servizi_aggiuntivi.get('Totale', 0)
    st.write(f"**Totale Preventivo: €{totale:.2f}**")

    st.write("Nelle prossime settimane verranno implementati altri servizi e funzionalità aggiuntive.")

if __name__ == "__main__":
    main()