# Kathara Network Designer (Desktop)

GUI in stile Cisco Packet Tracer per Kathara Network Emulator.

## Requisiti

- Python 3.8+
- PyQt6 (`pip install PyQt6`)
- Kathara installato
- Docker Desktop avviato

## Installazione

```bash
pip install PyQt6
pip install kathara
```

## Avvio

```bash
python main.py
```

## Funzionalità

### Toolbar Dispositivi (sinistra)
- **Router** - Router di rete
- **Switch** - Switch layer 2
- **PC** - Host finale
- **Hub** - Hub di rete
- **Cloud** - Connettività cloud

### Tipi di Cavo
- Copper Straight-Through (PC-Router, PC-Switch)
- Copper Cross-Over (PC-PC diretto)
- Fiber
- Serial
- Phone (RJ11)
- Coaxial

### Pannello Proprietà (destra)
- Nome, tipo e porte del dispositivo selezionato
- Selezione tipo di cavo
- Configurazione startup
- Path del lab

### Come usare

1. **Aggiungi dispositivi**: Clicca sui pulsanti nella toolbar
2. **Sposta**: Trascina i dispositivi sul canvas
3. **Connetti**: 
   - Seleziona il tipo di cavo dal pannello
   - Clicca "Connect" 
   - Clicca due dispositivi per collegarli
4. **Elimina**: Seleziona e clicca "Delete"
5. **Nuovo lab**: Clicca "New" per resettare

### Esporta e avvia

1. Crea la topologia
2. Clicca "Browse..." per scegliere la cartella
3. Clicca **File > Export to Kathara**
4. Clicca **Start** (pulsante verde)
5. Usa **Lab > Connect to Device**

### Scorciatoie

- `Ctrl+N`: Nuovo lab
- `Ctrl+O`: Apri lab
- `Ctrl+S`: Salva lab
- `Ctrl+E`: Esporta
- `F5`: Start Lab
- `F6`: Stop Lab
- `Ctrl+Q`: Esci

### Menu Help

- **Help > Guide**: Guida rapida con esempi di configurazione
