from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import io
from datetime import datetime

def genera_preventivo(cliente_info, studio_info, tipo_contabilita, servizi):
    doc = Document()
    
    # Debug: Stampa la struttura dei servizi
    print("Struttura dei servizi:")
    print(servizi)
    
    # Aggiungi intestazione
    doc.add_heading('Preventivo', 0)
    
    # Aggiungi informazioni del cliente
    doc.add_heading('Informazioni Cliente', level=1)
    for key, value in cliente_info.items():
        if value:  # Aggiungi solo se il valore non è vuoto
            doc.add_paragraph(f"{key.capitalize()}: {value}")
    
    # Aggiungi informazioni dello studio
    doc.add_heading('Informazioni Studio', level=1)
    for key, value in studio_info.items():
        if value:  # Aggiungi solo se il valore non è vuoto
            doc.add_paragraph(f"{key.capitalize()}: {value}")
    
    # Aggiungi tipo di contabilità
    doc.add_heading('Tipo di Contabilità', level=1)
    doc.add_paragraph(tipo_contabilita)
    
    # Crea la tabella dei servizi
    doc.add_heading('Dettaglio Servizi', level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Descrizione'
    hdr_cells[1].text = 'Quantità'
    hdr_cells[2].text = 'Prezzo'

    # Aggiungi i servizi alla tabella
    if isinstance(servizi, dict):
        for servizio, costo in servizi.get('Servizi Aggiuntivi', {}).items():
            if isinstance(costo, (int, float)) and costo > 0:
                row_cells = table.add_row().cells
                row_cells[0].text = servizio
                row_cells[1].text = "1"
                row_cells[2].text = f"€ {costo:.2f}"
    else:
        # Se servizi non è un dizionario, aggiungi una riga di errore
        row_cells = table.add_row().cells
        row_cells[0].text = "Errore: Dati dei servizi non validi"
        row_cells[1].text = ""
        row_cells[2].text = ""

    # Aggiungi il totale alla tabella
    totale = servizi.get('Totale', 0) if isinstance(servizi, dict) else 0
    row_cells = table.add_row().cells
    row_cells[0].text = "Totale"
    row_cells[1].text = ""
    row_cells[2].text = f"€ {totale:.2f}"

    # Salva il documento in memoria
    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    
    return doc_stream.getvalue()