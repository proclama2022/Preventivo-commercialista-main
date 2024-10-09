import streamlit as st
from estrai_info import load_document, split_text, extract_info
import os
from contabilita_fiscale import calcola_preventivo_forfettario, calcola_preventivo_semplificato, calcola_preventivo_ordinario
from genera_preventivo import genera_preventivo

# Rimuovi l'importazione di run_chat_assistant
# from chat_assistente import run_chat_assistant

# Inizializza le variabili di sessione
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
    st.session_state.pdf_path = "Onorari-Consigliati-2024_vers-2.pdf"

def main():
    st.set_page_config(page_title="Generatore Preventivi Commercialista", layout="wide")
    
    st.title("Generatore Preventivi Commercialista")
    st.write("Benvenuto! Questo strumento ti aiuterà a creare un preventivo personalizzato in pochi semplici passaggi.")
    st.write("Il tariffario utilizzato è basato sugli onorari consigliati da ANC per il 2024.")

    # Rimuovi il disclaimer e il campo per l'API key

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
        st.info("🚧 Coming Soon! 🚧\n\nLa funzionalità di chat assistente sarà disponibile a breve. Stiamo lavorando per fornirvi un'esperienza ancora migliore!")

    st.info("Nelle prossime settimane verranno implementati altri servizi e funzionalità aggiuntive.")

if __name__ == "__main__":
    main()