import streamlit as st
from estrai_info import load_document, split_text, extract_info
import os
from contabilita_fiscale import calcola_preventivo_forfettario, calcola_preventivo_semplificato, calcola_preventivo_ordinario
from genera_preventivo import genera_preventivo
from chat_assistente import run_chat_assistant

# Inizializza le variabili di sessione
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""  # Inizializza con una stringa vuota
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
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = "Onorari-Consigliati-2024_vers-2.pdf"  # Aggiorna il nome del file

def main():
    st.set_page_config(page_title="Generatore Preventivi Commercialista", layout="wide")
    
    st.title("Generatore Preventivi Commercialista")
    st.write("Benvenuto! Questo strumento ti aiuterà a creare un preventivo personalizzato in pochi semplici passaggi.")
    st.write("Il tariffario utilizzato è basato sugli onorari consigliati da ANC per il 2024.")

    # Aggiungi il disclaimer in un expander
    with st.expander("DISCLAIMER - Leggi prima dell'uso"):
        st.warning("""
        Questo strumento utilizza il modello di linguaggio GPT-4o-mini di OpenAI. 
        Si prega di notare che:
        
        1. Ogni interazione con il modello comporta un costo addebitato al tuo account OpenAI.
        2. I costi e i consumi possono essere monitorati sulla dashboard di OpenAI.
        3. Il numero di interazioni e il relativo costo non sono prevedibili in anticipo.
        4. Si raccomanda di fare attenzione al numero di interazioni per evitare costi inaspettati.
        
        Inserendo la tua chiave API, accetti di essere responsabile per eventuali costi associati all'uso di questo strumento.
        """)

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
        st.warning("Ricorda: l'uso della chiave API comporterà costi addebitati al tuo account OpenAI. Usa con cautela.")

    # Verifica che il file delle tariffe ANC esista
    if not os.path.exists(st.session_state.pdf_path):
        st.error(f"Il file delle tariffe ANC non è stato trovato nel percorso: {st.session_state.pdf_path}")
        return

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
    st.header("Riepilogo Preventivo e Chat Assistente")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Riepilogo Preventivo")
        with st.expander("Informazioni Cliente", expanded=True):
            for key, value in st.session_state.cliente_info.items():
                st.text(f"{key.capitalize()}: {value}")

        with st.expander("Informazioni Studio", expanded=True):
            for key, value in st.session_state.studio_info.items():
                st.text(f"{key.capitalize()}: {value}")

        with st.expander("Dettagli Preventivo", expanded=True):
            st.text(f"Tipo di Contabilità: {st.session_state.tipo_contabilita}")
            
            st.subheader("Servizi Aggiuntivi")
            for servizio, costo in st.session_state.servizi_aggiuntivi.get('Servizi Aggiuntivi', {}).items():
                st.text(f"{servizio}: €{costo:.2f}")

            totale = st.session_state.servizi_aggiuntivi.get('Totale', 0)
            st.subheader(f"Totale Preventivo: €{totale:.2f}")

    with col2:
        st.subheader("Chat Assistente")
        
        # Aggiungi il messaggio "Coming Soon"
        st.info("🚧 Coming Soon! 🚧\n\nLa funzionalità di chat assistente sarà disponibile a breve. Stiamo lavorando per fornirvi un'esperienza ancora migliore!")
        
        # Commenta o rimuovi temporaneamente il codice della chat
        """
        if st.session_state.openai_api_key:
            context = {
                "cliente_info": st.session_state.cliente_info,
                "studio_info": st.session_state.studio_info,
                "tipo_contabilita": st.session_state.tipo_contabilita,
                "servizi_aggiuntivi": st.session_state.servizi_aggiuntivi.get('Servizi Aggiuntivi', {}),
                "totale": st.session_state.servizi_aggiuntivi.get('Totale', 0)
            }
            
            # Crea un container scrollabile per la chat
            chat_container = st.container()
            
            # Imposta un'altezza fissa per il container della chat
            chat_container_height = 400  # Riduci l'altezza per lasciare spazio all'input
            
            # Aggiungi uno stile CSS per rendere il container scrollabile
            st.markdown(f'''
                <style>
                    .chat-container {{
                        height: {chat_container_height}px;
                        overflow-y: scroll;
                        border: 1px solid #ddd;
                        padding: 10px;
                        border-radius: 5px;
                        margin-bottom: 10px;
                    }}
                </style>
            ''', unsafe_allow_html=True)
            
            # Crea un div con la classe chat-container
            with st.markdown('<div class="chat-container">', unsafe_allow_html=True):
                run_chat_assistant(st.session_state.pdf_path, st.session_state.openai_api_key, context)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("La chiave API di OpenAI non è stata fornita. La funzionalità di chat assistente non è disponibile.")
        """

    st.info("Nelle prossime settimane verranno implementati altri servizi e funzionalità aggiuntive.")

if __name__ == "__main__":
    main()