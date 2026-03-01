# Kathara GUI

GUI per Kathara Network Emulator in stile Cisco Packet Tracer. Crea topologie di rete visivamente ed esportale direttamente per Kathara.

## ✨ Caratteristiche

### Interfacce Disponibili

- **🖥️ GUI Desktop** (PyQt6) - Applicazione desktop nativa
- **🌐 GUI Web** (Flask + JavaScript) - Applicazione web accessibile da browser

### Funzionalità Comuni

- **Dispositivi di rete**: Router, Switch, PC, Hub, Cloud
- **Connessioni visive**: Cavi colorati con diversi tipi (Copper Straight, Copper Cross, Fiber, Serial, Phone, Coaxial)
- **Configurazione IP**: Interface grafica per impostare indirizzi IP, gateway e interfaccia di rete (eth0-eth3)
- **Ping**: Esegui ping direttamente dalla GUI per testare la connettività
- **Esportazione**: Genera automaticamente file `lab.conf` e `*.startup` per Kathara
- **Gestione Lab**: Avvia, ferma e connettiti ai container
- **Console**: Messaggi di log in tempo reale

## 📋Screenshot

### GUI Desktop
```
┌─────────────────────────────────────────────────────────────────┐
│ TOOLBAR: Dispositivi | Connect | Delete | New | Start | Stop  │
├───────────────────────────────────────────┬───────────────────────┤
│                                           │ DEVICE PROPERTIES    │
│           AREA CANVAS                     │ Nome, Tipo, IP       │
│        (Topologia Rete)                  │ [SET IP]             │
│                                           ├───────────────────────┤
│    ┌─────┐      ┌─────┐                  │ CABLE TYPE           │
│    │ PC1 │──────│ROUTER│                │ (seleziona tipo)    │
│    └─────┘      └─────┘                  ├───────────────────────┤
│                        │                  │ CONNECTIONS           │
│                   ┌─────┐                  │ (lista cavi)         │
│                   │ PC2 │                  ├───────────────────────┤
│                   └─────┘                  │ CONSOLE              │
│                                           │ (messaggi)           │
└───────────────────────────────────────────┴───────────────────────┘
```

## 🚀 Installazione

### Prerequisiti

- **Python 3.8+**
- **Docker Desktop** installato e avviato
- **Kathara** installato

### 1. Installa le dipendenze

```bash
# Clona il repository
git clone https://github.com/YOUR_USERNAME/kathara-network-designer.git
cd kathara-network-designer

# Installa dipendenze per GUI Desktop
pip install PyQt6

# Installa dipendenze per GUI Web
pip install flask

# Installa Kathara (se non già installato)
pip install kathara
```

### 2. Avvio rapido

#### GUI Desktop
```bash
cd kathara_gui
python main.py
```

#### GUI Web
```bash
cd kathara_gui_web
python app.py
```
Poi apri **http://127.0.0.1:5000** nel browser

## 📖 Guida all'Uso

### Creare una Rete

1. **Aggiungi dispositivi**: Clicca i pulsanti ROUTER, SWITCH, PC, HUB, CLOUD nella toolbar
2. **Posiziona**: Trascina i dispositivi sul canvas
3. **Connetti**: 
   - Seleziona il tipo di cavo dal menu a tendina
   - Clicca "CONNECT" 
   - Clicca su due dispositivi per collegarli
4. **Configura IP**: 
   - Seleziona un dispositivo
   - Clicca "SET IP" (o doppio click sul dispositivo)
   - Seleziona l'interfaccia di rete (eth0-eth1-eth2-eth3)
   - Inserisci IP e Gateway

### Testare la Connettività (Ping)

1. Seleziona un dispositivo con IP configurato
2. Clicca "PING" 
3. Inserisci l'IP da pingare (es. gateway o altro host)
4. Visualizza il risultato nella console

### Esportare il Lab

1. Clicca "EXPORT" per generare i file di configurazione
2. Scegli la cartella di destinazione
3. Vengono creati:
   - `lab.conf` - Topologia della rete
   - `*.startup` - Configurazione per ogni dispositivo
   - `topology.txt` - Riepilogo

### Avviare il Lab

1. Clicca "START" per avviare i container Kathara
2. Usa "LIST DEVICES" per vedere i container attivi
3. Clicca "CONNECT" per collegarti a un dispositivo

## 📁 Struttura del Progetto

```
kathara-network-designer/
├── kathara_gui/           # GUI Desktop (PyQt6)
│   ├── main.py           # Codice principale
│   ├── GUIDA_GUI.md      # Guida in italiano
│   └── README.md         # Documentazione
│
├── kathara_gui_web/      # GUI Web (Flask)
│   ├── app.py           # Server Flask
│   ├── templates/       # Template HTML
│   ├── static/          # CSS e JavaScript
│   └── labs/            # Lab esportati
│
├── GUIDA_PASSO_PASSO.md   # Guida completa Kathara
└── README.md             # Questo file
```

## 🔌 Tipi di Cavi Disponibili

| Tipo | Colore | Uso Consigliato |
|------|--------|-----------------|
| Copper Straight | Rosso | PC→Router, PC→Switch |
| Copper Cross | Ciano | PC→PC diretto |
| Fiber | Blu | Switch→Switch |
| Serial | Viola | Router→Router WAN |
| Phone | Giallo | Connessioni telefoniche |
| Coaxial | Marrone | Cavo coassiale |

## 💻 Esempi Pratici

### Esempio 1: Due PC nella stessa rete

```
1. Clicca "PC" → PC1
2. Clicca "PC" → PC2
3. Clicca "CONNECT"
4. Clicca PC1, poi PC2
5. Seleziona PC1 → "SET IP" → 192.168.1.10
6. Seleziona PC2 → "SET IP" → 192.168.1.20
7. EXPORT
8. START
9. Test: ping da PC1 a PC2
```

### Esempio 2: Rete con Router

```
1. Clicca "PC" → PC1
2. Clicca "ROUTER" → ROUTER1
3. Clicca "PC" → PC2
4. Connetti: PC1 → ROUTER1 → PC2
5. Configura IP:
   - PC1: 192.168.1.10, gw: 192.168.1.254
   - PC2: 192.168.2.10, gw: 192.168.2.254
6. EXPORT e START
7. Test ping da PC1 a PC2
```

## 🔧 Comandi Utili

### Gestione Lab

```bash
# Avvia lab
kathara lstart -d nome_lab

# Ferma lab
kathara lstop -d nome_lab

# Rimuovi lab
kathara lclean -d nome_lab

# Lista container
kathara list

# Collegati a dispositivo
kathara connect -d nome_lab -n dispositivo
```

### Dentro i Container

```bash
# Visualizza IP
ip addr show

# Test connettività
ping <indirizzo_ip>

# Visualizza routing
ip route show

# Trace route
traceroute <destinazione>
```


## Base del Progetto :) 

- [Kathara](https://www.kathara.org/) - Network Emulator
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- Cisco Packet Tracer per l'ispirazione dell'interfaccia


