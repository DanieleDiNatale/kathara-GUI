# Guida Kathara Network Designer - GUI Desktop

## Indice
1. [Introduzione](#introduzione)
2. [Interfaccia Grafica](#interfaccia)
3. [Aggiungere Dispositivi](#aggiungere)
4. [Creare Connessioni](#connessioni)
5. [Configurare IP](#configurare-ip)
6. [Esportare il Lab](#esportare)
7. [Avviare/Fermare il Lab](#avviare)
8. [Menu e Scorciatoie](#menu)

---

## 1. Introduzione <a name="introduzione"></a>

Kathara Network Designer è un'interfaccia grafica per creare reti virtuali usando Kathara. 
Permette di:
- Disegnare topologie di rete visivamente
- Configurare indirizzi IP
- Esportare configurazioni per Kathara
- Avviare e gestire i container

---

## 2. Interfaccia Grafica <a name="interfaccia"></a>

```
┌─────────────────────────────────────────────────────────────────┐
│ TOOLBAR: Dispositivi | Connect | Delete | New | Start | Stop  │
├───────────────────────────────────────────┬───────────────────┤
│                                           │ DEVICE PROPERTIES │
│           AREA CANVAS                      │ Nome, Tipo, IP    │
│        (Topologia Rete)                   │ [Configure IP]    │
│                                           ├───────────────────┤
│    ○ PC1    ────○ Router1                 │ CABLE TYPE        │
│         \\         │                      │ (seleziona tipo)  │
│          \\    ○ Switch1                   ├───────────────────┤
│           \\      │                       │ CONNECTIONS        │
│            ○ PC2                         │ (lista cavi)      │
│                                           ├───────────────────┤
│                                           │ CONSOLE           │
│                                           │ (messaggi)        │
└───────────────────────────────────────────┴───────────────────┘
```

### Componenti Principali

| Componente | Descrizione |
|------------|-------------|
| **Toolbar** | Pulsanti per aggiungere dispositivi e azioni |
| **Canvas** | Area dove trascini i dispositivi |
| **Device Properties** | Proprietà del dispositivo selezionato |
| **Cable Type** | Seleziona il tipo di cavo |
| **Connections** | Lista delle connessioni create |
| **Console** | Messaggi di sistema |

---

## 3. Aggiungere Dispositivi <a name="aggiungere"></a>

### Passo 1: Clicca il pulsante del dispositivo
Nella toolbar in alto, clicca uno di questi pulsanti:

| Pulsante | Colore | Funzione |
|----------|--------|----------|
| **ROUTER** | Blu | Aggiungi un router |
| **SWITCH** | Arancione | Aggiungi uno switch |
| **PC** | Verde | Aggiungi un PC |
| **HUB** | Rosso | Aggiungi un hub |
| **CLOUD** | Viola | Aggiungi un cloud |

### Passo 2: Trascina il dispositivo
- Il dispositivo appare sul canvas
- Trascinalo nella posizione desiderata
- Puoi spostarlo in qualsiasi momento

### Esempio: Creare una rete semplice
```
1. Clicca "PC" → Appare PC1 sul canvas
2. Clicca "PC" → Appare PC2
3. Trascina PC1 a sinistra
4. Trascina PC2 a destra
```

---

## 4. Creare Connessioni <a name="connessioni"></a>

### Metodo 1: Connessione rapida
1. **Seleziona il tipo di cavo** dal pannello "CABLE TYPE"
2. Clicca il pulsante **CONNECT** nella toolbar (diventa giallo)
3. Clicca sul **primo dispositivo** (diventa giallo)
4. Clicca sul **secondo dispositivo**
5. Il cavo appare tra i due dispositivi

### Tipi di Cavo Disponibili

| Tipo | Colore | Uso |
|------|--------|-----|
| **Copper Straight** | Rosso | PC→Router, PC→Switch |
| **Copper Cross** | Ciano | PC→PC diretto |
| **Fiber** | Blu | Switch→Switch |
| **Serial** | Viola | Router→Router WAN |
| **Phone** | Giallo | Connessioni telefoniche |
| **Coaxial** | Marrone | Cavo coassiale |

### Eliminare una Connessione
1. Clicca sul cavo (diventa selezionato)
2. Clicca **DELETE** nella toolbar

---

## 5. Configurare IP <a name="configurare-ip"></a>

### Passo 1: Seleziona il dispositivo
- Clicca sul dispositivo nel canvas
- Le sue proprietà appaiono nel pannello "DEVICE PROPERTIES"

### Passo 2: Clicca "Configure IP"
Si apre una finestra con:
- **IP Address**: es. `192.168.1.10`
- **Gateway**: es. `192.168.1.254`

### Passo 3: Inserisci i valori
```
Esempio per PC1:
  IP Address: 192.168.1.10
  Gateway:    192.168.1.254

Esempio per PC2:
  IP Address: 192.168.1.20
  Gateway:    192.168.1.254
```

### Visualizzazione IP
- L'IP configurato appare direttamente sotto il dispositivo sul canvas

---

## 6. Esportare il Lab <a name="esportare"></a>

### Prima esportazione
1. Crea la tua topologia
2. Clicca **File → Export** (o `Ctrl+E`)
3. Seleziona la cartella dove salvare il lab
4. Vengono creati:
   - `lab.conf` - Topologia della rete
   - `*.startup` - File di configurazione per ogni dispositivo
   - `topology.txt` - Riepilogo della topologia

### Esportazione successiva
- Clicca **File → Export** per aggiornare i file

---

## 7. Avviare/Fermare il Lab <a name="avviare"></a>

### Avviare il Lab
1. Assicurati di aver esportato il lab
2. Clicca **START** nella toolbar (oppure `F5`)
3. I container Kathara vengono avviati
4. La console mostra i messaggi

### Fermare il Lab
- Clicca **STOP** nella toolbar (oppure `F6`)

### Collegarsi a un dispositivo
1. Clicca **Lab → Connect to Device**
2. Seleziona il dispositivo dalla lista
3. Si apre un terminale collegato al container

---

## 8. Menu e Scorciatoie <a name="menu"></a>

### Menu File
| Voce | Scorciatoia | Funzione |
|------|-------------|----------|
| New Lab | `Ctrl+N` | Cancella tutto e crea nuovo lab |
| Export | `Ctrl+E` | Esporta configurazioni |
| Exit | `Ctrl+Q` | Chiudi applicazione |

### Menu Lab
| Voce | Scorciatoia | Funzione |
|------|-------------|----------|
| Start | `F5` | Avvia il lab |
| Stop | `F6` | Ferma il lab |

### Toolbar
| Pulsante | Funzione |
|----------|----------|
| ROUTER/SWITCH/PC/HUB/CLOUD | Aggiungi dispositivo |
| CONNECT | Modalità connessione |
| DELETE | Elimina selezionato |
| NEW | Nuovo lab |
| START | Avvia lab |
| STOP | Ferma lab |

---

## Esempi Pratici

### Esempio 1: Due PC nella stessa rete

```
1. Clicca "PC" → PC1
2. Clicca "PC" → PC2
3. Clicca "CONNECT"
4. Clicca PC1, poi PC2
5. Seleziona PC1 → "Configure IP" → IP: 192.168.1.10
6. Seleziona PC2 → "Configure IP" → IP: 192.168.1.20
7. File → Export
8. START
9. Lab → Connect to Device → PC1
10. ping 192.168.1.20 ✓
```

### Esempio 2: Rete con Router

```
1. Clicca "PC" → PC1
2. Clicca "ROUTER" → ROUTER1
3. Clicca "PC" → PC2
4. Clicca "CONNECT" 
5. PC1 → ROUTER1
6. ROUTER1 → PC2
7. Configura IP:
   - PC1: 192.168.1.10, gw: 192.168.1.254
   - PC2: 192.168.2.10, gw: 192.168.2.254
8. Router ha già routing abilitato automaticamente
9. Export e Start
10. Test ping da PC1 a PC2
```

---

## Risoluzione Problemi

### Problema: Il lab non parte
- Assicurati che Docker Desktop sia avviato
- Verifica che Kathara sia installato (`kathara --version`)

### Problema: Non vedo i cavi
- I cavi potrebbero essere dietro i dispositivi
- Prova a ridimensionare la finestra
- Zoom con i pulsanti della viewport

### Problema: Il ping non funziona
- Verifica che i cavi siano collegati correttamente
- Controlla che i PC abbiano gateway configurato
- Ricorda: serve un router per comunicare tra reti diverse

---

## Comandi Generati

Quando esporti, vengono creati questi file:

### lab.conf
```
PC1[0]=A
PC2[0]=A
```

### PC1.startup
```
ip addr add 192.168.1.10/24 dev eth0
ip route add default via 192.168.1.254
```

### topology.txt
```
==================================================
Kathara Network Topology
==================================================

CONNECTIONS:
  PC1 <--[Copper Straight]--> PC2

DEVICE CONFIGURATION:

PC1:
  IP: 192.168.1.10/24

PC2:
  IP: 192.168.1.20/24
```

---

## Link Utili

- **Kathara**: https://www.kathara.org/
- **Docker Desktop**: https://www.docker.com/
