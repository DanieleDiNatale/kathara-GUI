# Kathará GUI (ALPHA)

GUI per Kathará Network Emulator in stile Cisco Packet Tracer. 

## ✨ Caratteristiche

### Interfacce Disponibili

- **🖥️ GUI Desktop** (PyQt6) - Applicazione desktop nativa
- **🌐 GUI Web** (Flask + JavaScript) - Applicazione web accessibile da browser

### Funzionalità Comuni

- **Dispositivi di rete**: Router, Switch, PC, Hub, Cloud
- **Connessioni visive**: Cavi colorati con diversi tipi (Copper Straight, Copper Cross, Fiber, Serial, Phone, Coaxial)
- **Configurazione IP**: Interfaccia grafica per impostare indirizzi IP, gateway e interfaccia di rete (eth0-eth3)
- **Ping**: Esegui ping direttamente dalla GUI per testare la connettività
- **Esportazione**: Genera automaticamente file `lab.conf` e `*.startup` per Kathara
- **Gestione Lab**: Avvia, ferma e connettiti ai container
- **Console**: Messaggi di log in tempo reale

---

# 🌐 GUIDA WEB GUI

<img width="1917" height="908" alt="WEB GUI " src="https://github.com/user-attachments/assets/f88acec8-3a51-49ba-8bbb-9bb6ddabcc5b" />


## 🚀 Avvio

```bash
cd kathara_gui_web
python app.py
```

Apri **http://127.0.0.1:5000** nel browser.

## 🎮 Controlli Mouse

- **Click sinistro**: Seleziona dispositivo
- **Click sinistro + trascina**: Sposta dispositivo
- **Click destro**: Menu contestuale (configura IP, elimina)

## ⌨️ Console Commands

Digita i comandi nella console in basso:

### Comandi Base

| Comando | Descrizione |
|---------|-------------|
| `add router [nome]` | Aggiungi un router |
| `add switch [nome]` | Aggiungi uno switch |
| `add pc [nome]` | Aggiungi un PC |
| `add hub [nome]` | Aggiungi un hub |
| `add cloud [nome]` | Aggiungi una cloud |
| `connect NOME1 NOME2` | Collega due dispositivi |
| `ip NOME ETH IP [GATEWAY]` | Configura IP |
| `ping NOME [target]` | Ping da dispositivo |
| `del NOME` | Elimina dispositivo |
| `list` | Mostra topologia |

### Esempi Console

```
# Creare due PC collegati
add pc pc1
add pc pc2
connect pc1 pc2
ip pc1 eth0 192.168.1.10
ip pc2 eth0 192.168.1.20
ping pc1 192.168.1.20

# Creare rete con router
add pc pc1
add router router1
add pc pc2
connect pc1 router1
connect router1 pc2
ip pc1 eth0 10.0.0.10 gateway 10.0.0.254
ip pc2 eth0 192.168.1.10 gateway 192.168.1.254
ping pc1 192.168.1.10

# Eliminare dispositivo
del pc1
```

## 🔧 Pulsanti Interfaccia

- **ADD**: Aggiungi dispositivo selezionato
- **CONNECT**: Modalità connessione (click due dispositivi)
- **DELETE**: Elimina dispositivo selezionato
- **EXPORT**: Esporta lab in formato Kathara
- **LIST DEVICES**: Mostra dispositivi attivi
- **PING**: Ping da dispositivo selezionato

## 📡 Configurazione IP

1. Click destro su dispositivo → **Set IP**
2. Seleziona interfaccia (eth0, eth1, eth2, eth3)
3. Inserisci IP (es. 192.168.1.10)
4. Inserisci Gateway (opzionale, es. 192.168.1.254)

---

# 🖥️ GUIDA DESKTOP GUI

<img width="1918" height="998" alt="Desktop GUI " src="https://github.com/user-attachments/assets/ce7c41b5-e5f6-4e0d-9557-8871e1aaf20c" />


## 🚀 Avvio

```bash
cd kathara_gui
python main.py
```

## 🎮 Controlli Mouse

- **Click sinistro**: Seleziona dispositivo
- **Click sinistro + trascina**: Sposta dispositivo
- **Doppio click**: Configura IP
- **Tasto DELETE**: Elimina dispositivo selezionato

## 🎛️ Toolbar

### Dispositivi
- **ROUTER**: Aggiungi router
- **SWITCH**: Aggiungi switch
- **PC**: Aggiungi PC
- **HUB**: Aggiungi hub
- **CLOUD**: Aggiungi cloud

### Connessioni
- **Cable Type**: Seleziona tipo cavo
- **CONNECT**: Modalità connessione

### Azioni
- **NEW**: Nuovo lab
- **OPEN**: Apri lab esistente
- **EXPORT**: Esporta configurazione
- **START**: Avvia lab
- **STOP**: Ferma lab
- **DELETE**: Elimina dispositivo

### Configurazione IP
- **SET IP**: Configura IP dispositivo selezionato
- **PING**: Test ping

---

# 🏠 ESEMPI RETI

## 1. Due PC nella stessa rete (LAN)

```
    [PC1] -------- [PC2]
   192.168.1.10   192.168.1.20
```

### Configurazione Web GUI
```
add pc pc1
add pc pc2
connect pc1 pc2
ip pc1 eth0 192.168.1.10
ip pc2 eth0 192.168.1.20
```

### Configurazione Desktop GUI
1. Click **PC** → Click sul canvas → PC1
2. Click **PC** → Click sul canvas → PC2
3. Click **CONNECT**
4. Click PC1, poi PC2
5. Seleziona PC1 → Click **SET IP** → eth0, 192.168.1.10
6. Seleziona PC2 → Click **SET IP** → eth0, 192.20
7.168.1. Click **EXPORT** → Click **START**

### Test
```
ping pc1 192.168.1.20
```

---

## 2. Rete con Router (WAN)

```
    [PC1] -------- [ROUTER] -------- [PC2]
   10.0.0.10      eth0:10.0.0.254   192.168.1.10
                  eth1:192.168.1.254
```

### Configurazione Web GUI
```
add pc pc1
add router router1
add pc pc2
connect pc1 router1
connect router1 pc2
ip pc1 eth0 10.0.0.10 gateway 10.0.0.254
ip pc2 eth0 192.168.1.10 gateway 192.168.1.254
```

### Configurazione Desktop GUI
1. Click **PC** → PC1
2. Click **ROUTER** → ROUTER1  
3. Click **PC** → PC2
4. Click **CONNECT** → PC1 → ROUTER1
5. Click **CONNECT** → ROUTER1 → PC2
6. PC1: Set IP → eth0, 10.0.0.10, gateway 10.0.0.254
7. PC2: Set IP → eth0, 192.168.1.10, gateway 192.168.1.254

### 📋 Guida Completa IP Router

#### Tabella Rete → IP Gateway

| Network | Rete IP       | Gateway Router | Interfaccia |
|---------|---------------|----------------|-------------|
| A       | 10.0.0.x      | 10.0.0.254    | eth0        |
| B       | 192.168.1.x   | 192.168.1.254 | eth1        |
| C       | 192.168.2.x   | 192.168.2.254 | eth2        |
| D       | 192.168.3.x   | 192.168.3.254 | eth3        |
| E       | 192.168.4.x   | 192.168.4.254 | eth4        |
| F       | 192.168.5.x   | 192.168.5.254 | eth5        |

#### Regole per i Router:
1. Ogni connessione tra dispositivi crea una nuova rete (A, B, C, D...)
2. Il router ha un'interfaccia per ogni rete a cui è connesso
3. I PC devono usare il gateway del router sulla loro rete

#### Esempio con 2 Router:
```
[PC1]----[R1]----[R2]----[PC2]
   A        B       C        D
```

- **PC1** (rete A): IP 10.0.0.10, gateway 10.0.0.254
- **R1**: eth0→A (10.0.0.254), eth1→B (192.168.1.254)
- **R2**: eth0→B (192.168.1.254), eth1→C (192.168.2.254)
- **PC2** (rete C): IP 192.168.2.10, gateway 192.168.2.254

#### Suggerimento:
Il router assegna automaticamente gli IP alle sue interfacce basandosi sulla lettera della rete:
- Network A → 10.0.0.254
- Network B → 192.168.1.254
- Network C → 192.168.2.254
- Network D → 192.168.3.254
- Il router abilita automaticamente IP forwarding

### Test
```
ping pc1 192.168.1.10
```

---

## 3. Rete con Switch

```
    [PC1]                      [PC3]
      |                          |
   [SWITCH1] ---------------- [PC2]
```

### Configurazione Web GUI
```
add pc pc1
add pc pc2
add pc pc3
add switch switch1
connect pc1 switch1
connect pc2 switch1
connect pc3 switch1
ip pc1 eth0 192.168.1.10
ip pc2 eth0 192.168.1.20
ip pc3 eth0 192.168.1.30
```

### Configurazione Desktop GUI
1. Aggiungi 3 PC
2. Aggiungi 1 SWITCH
3. Connetti tutti i PC allo Switch
4. Configura IP: 192.168.1.10, .20, .30

### Test
```
ping pc1 192.168.1.20
ping pc1 192.168.1.30
```

---

## 4. Rete Complessa con Cloud

```
    [PC1] -------- [ROUTER1] -------- [ROUTER2] -------- [PC2]
   10.0.0.10       eth0:10.0.0.254     eth0:192.168.1.254    192.168.2.10
                   eth1:192.168.1.1    eth1:192.168.2.254
                         |
                       [CLOUD]
```

### Configurazione Web GUI
```
add pc pc1
add router router1
add router router2
add pc pc2
add cloud cloud1

connect pc1 router1
connect router1 router2
connect router2 pc2
connect router1 cloud1

ip pc1 eth0 10.0.0.10 gateway 10.0.0.254
ip pc2 eth0 192.168.2.10 gateway 192.168.2.254
```

### Rete Multi-Router
Il router1 avrà:
- eth0: 10.0.0.254 (verso PC1)
- eth1: 192.168.1.1 (verso router2)
- eth2: 192.168.3.254 (verso cloud)

Il router2 avrà:
- eth0: 192.168.1.254 (verso router1)
- eth1: 192.168.2.254 (verso PC2)

### Test
```
ping pc1 192.168.2.10
ping pc1 192.168.3.254  # ping cloud
```

---

## 5. Rete con Hub

```
    [PC1]
      |
   [HUB] -------- [PC2]
      |
    [PC3]
```

### Configurazione
L'hub è un dispositivo passivo che replica i pacchetti a tutte le porte (eccetto quella sorgente).

```
add pc pc1
add pc pc2
add pc pc3
add hub hub1
connect pc1 hub1
connect pc2 hub1
connect pc3 hub1

ip pc1 eth0 192.168.1.10
ip pc2 eth0 192.168.1.20
ip pc3 eth0 192.168.1.30
```

---

## 6. Rete con Multiple Interfacce

Un PC o Router può avere fino a 4 interfacce (eth0, eth1, eth2, eth3):

### Esempio: PC con 2 reti

```
    [PC1]
   eth0: 10.0.0.10 (rete A)
   eth1: 192.168.1.10 (rete B)
```

### Configurazione
```
ip pc1 eth0 10.0.0.10 gateway 10.0.0.254
ip pc1 eth1 192.168.1.10 gateway 192.168.1.254
```

---

## 7. Rete con 3 Router (Internet)

```
         [INTERNET]
             |
         [CLOUD]
             |
    [ROUTER1] -------- [ROUTER2] -------- [ROUTER3]
   192.168.1.254      192.168.2.254       192.168.3.254
        |                   |                  |
     [PC1]              [PC2]              [PC3]
   192.168.1.10       192.168.2.10       192.168.3.10
```

### Configurazione Web GUI
```
add pc pc1
add router router1
add pc pc2
add router router2
add pc pc3
add router router3
add cloud cloud1

connect pc1 router1
connect router1 router2
connect router2 router3
connect router3 cloud1
connect router1 cloud1

ip pc1 eth0 192.168.1.10 gateway 192.168.1.254
ip pc2 eth0 192.168.2.10 gateway 192.168.2.254
ip pc3 eth0 192.168.3.10 gateway 192.168.3.254
```

---

## 8. Rete con VLAN (Switch)

```
    [PC1]          [PC3]
      |              |
   [SWITCH1] ---- [SWITCH2]
      |
    [PC2]
```

Per configurare VLAN, usa i comandi dentro il container dopo l'avvio:

```
# Entra nel container
kathara exec -d nome_lab switch1 -- vlan 10
```

---

# 🔌 Tipi di Cavi

| Tipo | Colore | Uso Consigliato |
|------|--------|-----------------|
| Copper Straight | Rosso | PC→Router, PC→Switch |
| Copper Cross | Ciano | PC→PC diretto |
| Fiber | Blu | Switch→Switch |
| Serial | Viola | Router→Router WAN |
| Phone | Giallo | Connessioni telefoniche |
| Coaxial | Marrone | Cavo coassiale |

---

# 💻 Comandi Utili

## Gestione Lab

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

## Dentro i Container

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

---

# 📁 Struttura del Progetto

```
kathara-network-designer/
├── kathara_gui/           # GUI Desktop (PyQt6)
│   └── main.py           
│
├── kathara_gui_web/      # GUI Web (Flask)
│   ├── app.py           
│   ├── templates/       
│   ├── static/          
│   └── labs/            
│
├── README.md             # Questo file
└── GUIDA_PASSO_PASSO.md
```

---

## Base del Progetto 

- [Kathara](https://www.kathara.org/) - Network Emulator
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- Cisco Packet Tracer per l'ispirazione dell'interfaccia

