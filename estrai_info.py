import os  # Aggiungi questa riga all'inizio del file
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import io
from PyPDF2 import PdfReader
from langchain.schema import Document

def load_document(uploaded_file):
    if uploaded_file.type == "application/pdf":
        # Per i file PDF
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return [Document(page_content=text, metadata={"source": uploaded_file.name})]
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Per i file DOCX
        return Docx2txtLoader(io.BytesIO(uploaded_file.getvalue())).load()
    else:
        # Per altri tipi di file (assumiamo che siano file di testo)
        return TextLoader(io.StringIO(uploaded_file.getvalue().decode())).load()

def split_text(text, chunk_size=4000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)

def extract_info(text):
    api_key = st.secrets["openai"]["api_key"]
    if not api_key:
        raise ValueError("La chiave API di OpenAI non è stata fornita.")
    
    llm = ChatOpenAI(
        temperature=0,
        api_key=api_key,
        model_name="gpt-4o-mini"
    )
    
    response_schemas = [
        ResponseSchema(name="nome_cliente", description="Nome o ragione sociale del cliente"),
        ResponseSchema(name="indirizzo_cliente", description="Indirizzo completo del cliente"),
        ResponseSchema(name="email_cliente", description="Email del cliente"),
        ResponseSchema(name="partita_iva_cliente", description="Partita IVA del cliente"),
        ResponseSchema(name="codice_fiscale_cliente", description="Codice fiscale del cliente"),
        ResponseSchema(name="citta_cliente", description="Città del cliente"),
        ResponseSchema(name="cap_cliente", description="CAP del cliente"),
        ResponseSchema(name="provincia_cliente", description="Provincia del cliente"),
        ResponseSchema(name="nome_studio", description="Nome dello studio commercialista"),
        ResponseSchema(name="indirizzo_studio", description="Indirizzo completo dello studio commercialista"),
        ResponseSchema(name="email_studio", description="Email dello studio commercialista"),
        ResponseSchema(name="partita_iva_studio", description="Partita IVA dello studio commercialista"),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    prompt = PromptTemplate(
        template="Estrai le seguenti informazioni dal testo, se presenti. Se non riesci a determinare se un'informazione si riferisce al cliente o allo studio, lascia il campo vuoto:\n{format_instructions}\n{text}",
        input_variables=["text"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )

    chain = prompt | llm
    result = chain.invoke({"text": text})
    
    # Estrai il contenuto del messaggio
    message_content = result.content if hasattr(result, 'content') else str(result)
    
    # Analizza il risultato e restituisci un dizionario
    parsed_result = output_parser.parse(message_content)
    
    # Filtra i campi vuoti
    filtered_result = {k: v for k, v in parsed_result.items() if v}
    
    return filtered_result