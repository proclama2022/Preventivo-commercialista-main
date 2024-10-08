import streamlit as st
from estrai_info import load_document, split_text, extract_info
from dotenv import load_dotenv
import os
from contabilita_fiscale import calcola_preventivo_forfettario, calcola_preventivo_semplificato, calcola_preventivo_ordinario
from genera_preventivo import genera_preventivo

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Accedi alle variabili d'ambiente
openai_api_key = os.getenv("OPENAI_API_KEY")
debug_mode = os.getenv("DEBUG", "False").lower() == "true"

def main():
    st.set_page_config(page_title="Generatore Preventivi Commercialista", layout="wide")
    
    st.title("Generatore Preventivi Commercialista")
    st.write("Benvenuto! Questo strumento ti aiuterà a creare un preventivo personalizzato in pochi semplici passaggi.")

    # Inizializza gli step se non esistono
    if "step" not in st.session_state:
        st.session_state.step = 0

    steps = [
        ("Informazioni Cliente", handle_cliente_info),
        ("Informazioni Studio", handle_studio_info),
        ("Tipo di Contabilità", handle_tipo_contabilita),
        ("Servizi Aggiuntivi", handle_servizi_aggiuntivi),
        ("Genera Preventivo", handle_genera_preventivo)
    ]

    # Mostra la barra di progresso
    progress_bar = st.progress(0)
    st.write(f"Step {st.session_state.step + 1} di {len(steps)}")

    # Esegui lo step corrente
    step_name, step_function = steps[st.session_state.step]
    st.subheader(step_name)
    step_function()

    # Pulsanti Avanti/Indietro
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.session_state.step > 0:
            if st.button("⬅️ Indietro"):
                st.session_state.step -= 1
                st.experimental_rerun()
    
    with col3:
        if st.session_state.step < len(steps) - 1:
            if st.button("Avanti ➡️"):
                st.session_state.step += 1
                st.experimental_rerun()

    # Aggiorna la barra di progresso
    progress_bar.progress((st.session_state.step + 1) / len(steps))

def handle_cliente_info():
    st.write("Inserisci le informazioni del cliente. Puoi farlo manualmente o caricando un documento.")
    
    method = st.radio("Metodo di inserimento", ["Manuale", "Carica documento"])
    
    if method == "Carica documento":
        uploaded_file = st.file_uploader("Carica un documento del cliente (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file:
            if st.button("Estrai informazioni"):
                extract_and_save_info(uploaded_file, "Cliente")
    
    # Campi per l'inserimento manuale o la modifica
    st.session_state.nome_cliente = st.text_input("Nome e Cognome/Ragione Sociale", value=st.session_state.get('nome_cliente', ''))
    st.session_state.partita_iva_cliente = st.text_input("Partita IVA", value=st.session_state.get('partita_iva_cliente', ''))
    st.session_state.codice_fiscale_cliente = st.text_input("Codice Fiscale", value=st.session_state.get('codice_fiscale_cliente', ''))
    st.session_state.indirizzo_cliente = st.text_input("Indirizzo", value=st.session_state.get('indirizzo_cliente', ''))
    st.session_state.email_cliente = st.text_input("Email", value=st.session_state.get('email_cliente', ''))

def handle_studio_info():
    st.write("Inserisci le informazioni dello studio commercialista.")
    
    st.session_state.nome_studio = st.text_input("Nome Studio", value=st.session_state.get('nome_studio', ''))
    st.session_state.partita_iva_studio = st.text_input("Partita IVA Studio", value=st.session_state.get('partita_iva_studio', ''))
    st.session_state.indirizzo_studio = st.text_input("Indirizzo Studio", value=st.session_state.get('indirizzo_studio', ''))
    st.session_state.email_studio = st.text_input("Email Studio", value=st.session_state.get('email_studio', ''))

def handle_tipo_contabilita():
    st.write("Seleziona il tipo di contabilità per il cliente.")
    
    st.session_state.tipo_contabilita = st.radio("Tipo di contabilità", ["Forfettaria", "Semplificata", "Ordinaria"])
    
    if st.session_state.tipo_contabilita == "Forfettaria":
        st.info("La contabilità forfettaria è adatta per piccole attività con ricavi limitati.")
    elif st.session_state.tipo_contabilita == "Semplificata":
        st.info("La contabilità semplificata è adatta per attività di medie dimensioni.")
    else:
        st.info("La contabilità ordinaria è obbligatoria per società di capitali e consigliata per attività più complesse.")

def handle_servizi_aggiuntivi():
    st.write("Seleziona i servizi aggiuntivi da includere nel preventivo.")
    
    if st.session_state.tipo_contabilita == "Forfettaria":
        st.session_state.servizi_aggiuntivi = calcola_preventivo_forfettario()
    elif st.session_state.tipo_contabilita == "Semplificata":
        st.session_state.servizi_aggiuntivi = calcola_preventivo_semplificato()
    else:
        st.session_state.servizi_aggiuntivi = calcola_preventivo_ordinario()

def handle_genera_preventivo():
    st.write("Riepilogo e generazione del preventivo.")
    
    st.subheader("Riepilogo Informazioni")
    st.write(f"Cliente: {st.session_state.nome_cliente}")
    st.write(f"Studio: {st.session_state.nome_studio}")
    st.write(f"Tipo di Contabilità: {st.session_state.tipo_contabilita}")
    st.write("Servizi Aggiuntivi:")
    for servizio, costo in st.session_state.servizi_aggiuntivi.get("Servizi Aggiuntivi", {}).items():
        st.write(f"- {servizio}: €{costo:.2f}")
    
    if st.button("Genera Preventivo"):
        try:
            cliente_info = {
                "nome": st.session_state.nome_cliente,
                "indirizzo": st.session_state.indirizzo_cliente,
                "partita_iva": st.session_state.partita_iva_cliente,
                "codice_fiscale": st.session_state.codice_fiscale_cliente,
                "email": st.session_state.email_cliente
            }
            
            studio_info = {
                "nome": st.session_state.nome_studio,
                "indirizzo": st.session_state.indirizzo_studio,
                "partita_iva": st.session_state.partita_iva_studio,
                "email": st.session_state.email_studio
            }
            
            preventivo_doc = genera_preventivo(
                cliente_info, 
                studio_info,
                st.session_state.tipo_contabilita,
                st.session_state.servizi_aggiuntivi
            )
            
            st.success("Preventivo generato con successo!")
            st.download_button(
                label="Scarica Preventivo",
                data=preventivo_doc,
                file_name="preventivo.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Si è verificato un errore durante la generazione del preventivo: {str(e)}")

def extract_and_save_info(uploaded_file, info_type):
    try:
        doc = load_document(uploaded_file)
        text = " ".join([page.page_content for page in doc])
        extracted_info = extract_info(text)
        
        if info_type == "Cliente":
            st.session_state.update({k: v for k, v in extracted_info.items() if k.endswith('_cliente')})
        else:
            st.session_state.update({k: v for k, v in extracted_info.items() if k.endswith('_studio')})
        
        st.success(f"Informazioni {info_type} estratte con successo!")
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'elaborazione: {str(e)}")

if __name__ == "__main__":
    main()