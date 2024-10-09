import streamlit as st
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain.memory import ConversationBufferMemory

MAX_MESSAGES = 5  # Numero massimo di messaggi da visualizzare

def setup_faiss(pdf_path, openai_api_key, context):
    # Carica il PDF delle tariffe ANC
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Aggiungi il contesto del preventivo come un nuovo documento
    context_str = f"""
    Informazioni sul preventivo attuale:
    Tipo di contabilita: {context['tipo_contabilita']}
    Totale preventivo: {context['totale']:.2f} EUR
    
    Servizi inclusi e relativi costi:
    {', '.join([f"{k}: {v:.2f} EUR" for k, v in context['servizi_aggiuntivi'].items()])}
    
    Informazioni Cliente:
    {', '.join([f'{k}: {v}' for k, v in context['cliente_info'].items()])}
    
    Informazioni Studio:
    {', '.join([f'{k}: {v}' for k, v in context['studio_info'].items()])}
    """
    context_doc = Document(page_content=context_str, metadata={"source": "preventivo_attuale"})
    documents.append(context_doc)

    # Inizializza l'embedding model
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Crea il database vettoriale FAISS
    vectordb = FAISS.from_documents(documents, embeddings)

    return vectordb

def create_chat_chain(vectordb, openai_api_key):
    try:
        llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini", openai_api_key=openai_api_key)
    except Exception as e:
        st.warning(f"Impossibile utilizzare gpt-4o-mini. Utilizzo di gpt-3.5-turbo come fallback. Errore: {str(e)}")
        llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectordb.as_retriever(),
        memory=memory,
        return_source_documents=True,
        verbose=True
    )

    return chain

def summarize_conversation(messages, llm):
    summary_prompt = f"""
    Riassumi la seguente conversazione in pochi punti chiave:

    {' '.join([f"{m['role']}: {m['content']}" for m in messages])}

    Riassunto:
    """
    summary = llm.predict(summary_prompt)
    return summary

def search_tariffario(vectordb, query):
    results = vectordb.similarity_search(query, k=5)  # Aumenta il numero di risultati
    return "\n".join([doc.page_content for doc in results])

def chat_interface(chain, context, vectordb):
    st.subheader("Chat Assistente")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visualizza i messaggi precedenti
    for message in st.session_state.messages[-MAX_MESSAGES:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dell'utente
    prompt = st.text_input("Fai una domanda sul preventivo o chiedi un consiglio", key="chat_input")
    
    if st.button("Invia") or prompt:  # Modifica qui per inviare anche quando si preme Invio
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Cerca informazioni specifiche nel tariffario
            tariffario_info = search_tariffario(vectordb, prompt)

            critical_prompt = f"""
            Sei un assistente esperto in contabilità e tariffe ANC. Rispondi alla domanda dell'utente utilizzando le seguenti informazioni:

            Tariffario ANC:
            {tariffario_info}

            Contesto del preventivo attuale:
            {context}

            Domanda dell'utente: {prompt}

            Se la domanda riguarda specificamente il tariffario o i costi, fornisci una risposta precisa basata sulle informazioni del tariffario ANC.
            Se la domanda è sul preventivo attuale, usa le informazioni del contesto fornito.
            Se non hai informazioni specifiche, dillo chiaramente e offri consigli generali basati sulle tue conoscenze di contabilità e tariffe professionali.

            Ricorda di essere conciso ma esaustivo nella tua risposta.
            """

            response = chain({"question": critical_prompt})

            with st.chat_message("assistant"):
                st.markdown(response['answer'])
            st.session_state.messages.append({"role": "assistant", "content": response['answer']})

            # Se la conversazione diventa troppo lunga, riassumila
            if len(st.session_state.messages) > MAX_MESSAGES * 2:
                summary = summarize_conversation(st.session_state.messages[:-MAX_MESSAGES], chain.llm)
                st.session_state.messages = [{"role": "system", "content": f"Riassunto precedente: {summary}"}] + st.session_state.messages[-MAX_MESSAGES:]

            # Pulisci l'input dopo l'invio
            st.session_state.chat_input = ""

    if st.button("Resetta Chat"):
        st.session_state.messages = []
        st.rerun()

def run_chat_assistant(pdf_path, openai_api_key, context):
    if not openai_api_key:
        st.warning("La chiave API di OpenAI non è stata fornita. La funzionalità di chat assistente non è disponibile.")
        return
    
    try:
        vectordb = setup_faiss(pdf_path, openai_api_key, context)
        chain = create_chat_chain(vectordb, openai_api_key)
        chat_interface(chain, context, vectordb)
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'inizializzazione della chat assistente: {str(e)}")
        st.warning("La funzionalità di chat assistente non è disponibile al momento.")