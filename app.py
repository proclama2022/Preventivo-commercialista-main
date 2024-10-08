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

def sidebar_menu():
    with st.sidebar:
        st.title("Menu Navigazione")
        step = st.radio(
            "Seleziona una sezione:",
            ("Anagrafica", "Servizi", "Preventivo"),
            index=["anagrafica", "servizi", "preventivo"].index(st.session_state.get("step", "anagrafica"))
        )
        st.session_state.step = step.lower()

def handle_anagrafica():
    st.header("Gestione Anagrafica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Informazioni Cliente")
        handle_info_input("Cliente")
    
    with col2:
        st.subheader("Informazioni Studio")
        handle_info_input("Studio")

def handle_servizi():
    st.header("Selezione Servizi")
    
    tipo_contabilita = st.radio("Tipo di contabilità", ["Forfettaria", "Semplificata", "Ordinaria"])
    
    if tipo_contabilita == "Forfettaria":
        risultato = calcola_preventivo_forfettario()
    elif tipo_contabilita == "Semplificata":
        risultato = calcola_preventivo_semplificato()
    else:
        risultato = calcola_preventivo_ordinario()
    
    st.session_state.servizi_aggiuntivi = risultato
    st.session_state.tipo_contabilita = tipo_contabilita
    
    st.success("Servizi selezionati con successo")
    st.button("Genera Preventivo", on_click=lambda: setattr(st.session_state, 'step', 'preventivo'))

def handle_preventivo():
    st.header("Preventivo Generato")
    
    st.write("Debug: Inizio handle_preventivo")
    
    cliente_info = {
        "nome": st.session_state.get('nome_cliente', ''),
        "indirizzo": st.session_state.get('indirizzo_cliente', ''),
        "partita_iva": st.session_state.get('partita_iva_cliente', ''),
        "codice_fiscale": st.session_state.get('codice_fiscale_cliente', ''),
        "email": st.session_state.get('email_cliente', '')
    }
    
    studio_info = {
        "nome": st.session_state.get('nome_studio', ''),
        "indirizzo": st.session_state.get('indirizzo_studio', ''),
        "partita_iva": st.session_state.get('partita_iva_studio', ''),
        "email": st.session_state.get('email_studio', '')
    }
    
    st.write("Debug: cliente_info creato", cliente_info)
    st.write("Debug: studio_info creato", studio_info)
    
    # Debug print per verificare i servizi aggiuntivi
    st.write("Debug: Servizi aggiuntivi:", st.session_state.get('servizi_aggiuntivi', {}))
    st.write("Debug: Tipo contabilità:", st.session_state.get('tipo_contabilita', ''))
    
    # Assicuriamoci che servizi_aggiuntivi sia un dizionario
    servizi_aggiuntivi = st.session_state.get('servizi_aggiuntivi', {})
    if not isinstance(servizi_aggiuntivi, dict):
        st.error("Errore: i servizi aggiuntivi non sono nel formato corretto.")
        servizi_aggiuntivi = {}
    
    # Passa i servizi aggiuntivi corretti
    try:
        preventivo_doc = genera_preventivo(
            cliente_info, 
            studio_info,
            st.session_state.get('tipo_contabilita', ''), 
            servizi_aggiuntivi
        )
        st.write("Debug: Preventivo generato con successo")
        
        st.download_button(
            label="Scarica Preventivo",
            data=preventivo_doc,
            file_name="preventivo.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"Errore durante la generazione del preventivo: {str(e)}")
    
    if st.button("Ricomincia"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.step = "anagrafica"
        st.experimental_rerun()

def handle_info_input(info_type):
    method = st.radio(f"Metodo di inserimento ({info_type})", ["Manuale", "Carica file", "Incolla testo"])
    
    if method == "Carica file":
        uploaded_file = st.file_uploader(f"Carica un documento {info_type} (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file and st.button(f"Estrai informazioni da file {info_type}"):
            extract_and_save_info(uploaded_file, info_type)
    elif method == "Incolla testo":
        text_input = st.text_area(f"Incolla il testo con le informazioni {info_type}")
        if st.button(f"Estrai informazioni {info_type}"):
            extract_and_save_info(text_input, info_type)

    # Mostra e permette la modifica delle informazioni
    with st.expander(f"Modifica le informazioni {info_type}", expanded=True):
        if info_type == "Cliente":
            nome = st.text_input("Nome e Cognome/Ragione Sociale", value=st.session_state.get('nome_cliente', ''), key=f"nome_{info_type}")
            partita_iva = st.text_input("Partita IVA", value=st.session_state.get('partita_iva_cliente', ''), key=f"partita_iva_{info_type}")
            codice_fiscale = st.text_input("Codice Fiscale", value=st.session_state.get('codice_fiscale_cliente', ''), key=f"codice_fiscale_{info_type}")
            indirizzo = st.text_input("Indirizzo", value=st.session_state.get('indirizzo_cliente', ''), key=f"indirizzo_{info_type}")
            citta = st.text_input("Città", value=st.session_state.get('citta_cliente', ''), key=f"citta_{info_type}")
            cap = st.text_input("CAP", value=st.session_state.get('cap_cliente', ''), key=f"cap_{info_type}")
            provincia = st.text_input("Provincia", value=st.session_state.get('provincia_cliente', ''), key=f"provincia_{info_type}")
            email = st.text_input("Email", value=st.session_state.get('email_cliente', ''), key=f"email_{info_type}")
            
            if st.button(f"Salva modifiche {info_type}"):
                st.session_state.update({
                    'nome_cliente': nome, 'partita_iva_cliente': partita_iva,
                    'codice_fiscale_cliente': codice_fiscale, 'indirizzo_cliente': indirizzo,
                    'citta_cliente': citta, 'cap_cliente': cap,
                    'provincia_cliente': provincia, 'email_cliente': email
                })
                st.success(f"Modifiche alle informazioni {info_type} salvate con successo!")
        else:  # Studio
            nome_studio = st.text_input("Nome Studio", value=st.session_state.get('nome_studio', ''), key=f"nome_{info_type}")
            partita_iva_studio = st.text_input("Partita IVA Studio", value=st.session_state.get('partita_iva_studio', ''), key=f"partita_iva_{info_type}")
            indirizzo_studio = st.text_input("Indirizzo Studio", value=st.session_state.get('indirizzo_studio', ''), key=f"indirizzo_{info_type}")
            email_studio = st.text_input("Email Studio", value=st.session_state.get('email_studio', ''), key=f"email_{info_type}")
            
            if st.button(f"Salva modifiche {info_type}"):
                st.session_state.update({
                    'nome_studio': nome_studio, 'partita_iva_studio': partita_iva_studio,
                    'indirizzo_studio': indirizzo_studio, 'email_studio': email_studio
                })
                st.success(f"Modifiche alle informazioni {info_type} salvate con successo!")

def extract_and_save_info(input_data, info_type):
    progress_placeholder = st.empty()
    
    try:
        progress_placeholder.text("Estrazione delle informazioni in corso...")
        if isinstance(input_data, str):
            extracted_info = extract_info(input_data)
        else:
            doc = load_document(input_data)
            text = " ".join([page.page_content for page in doc])
            extracted_info = extract_info(text)
        
        if info_type == "Cliente":
            st.session_state.update({k: v for k, v in extracted_info.items() if k.endswith('_cliente')})
        else:
            st.session_state.update({k: v for k, v in extracted_info.items() if k.endswith('_studio')})
        
        if extracted_info:
            st.success(f"Informazioni {info_type} estratte e salvate con successo!")
        else:
            st.warning(f"Nessuna informazione {info_type} estratta. Controlla il contenuto del file.")
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'elaborazione: {str(e)}")
    finally:
        progress_placeholder.empty()

def main():
    st.set_page_config(page_title="App Preventivo Commercialista", layout="wide")
    
    # Inizializza gli attributi di sessione se non esistono
    if "step" not in st.session_state:
        st.session_state.step = "anagrafica"
    if "servizi_aggiuntivi" not in st.session_state:
        st.session_state.servizi_aggiuntivi = {}  # Inizializza come dizionario vuoto
    
    sidebar_menu()
    
    if st.session_state.step == "anagrafica":
        handle_anagrafica()
    elif st.session_state.step == "servizi":
        handle_servizi()
    elif st.session_state.step == "preventivo":
        handle_preventivo()

if __name__ == "__main__":
    main()