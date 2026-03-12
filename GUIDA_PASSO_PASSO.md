# Guida Passo-Passo: Kathara Network Emulator

## Indice
1. [Introduzione](#introduzione)
2. [Installazione e Configurazione](#installazione)
3. [Esercizi Base](#esercizi-base)
4. [Esercizi con Router](#esercizi-router)
5. [Esercizi con Server](#esercizi-server)
6. [Esercizi Completi](#esercizi-completi)
7. [Comandi Essenziali](#comandi)
8. [Tips e Trucchi](#tips)

---

## 1. Introduzione <a name="introduzione"></a>

### Cos'è Kathara?
Kathara è un emulatore di rete leggero basato su container Docker. Permette di creare scenari di rete realistici senza bisogno di hardware fisico.

### Struttura di un Lab
Ogni lab Kathara è una **cartella** contenente:
```
nome_lab/
├── lab.conf           # Definizione della topologia
├── PC1.startup        # Comandi di configurazione PC1
├── PC2.startup        # Comandi di configurazione PC2
├── Router1.startup   # Comandi di configurazione Router1
└── ...
```

### Come funziona la topologia (lab.conf)
La topologia si definisce con il formato:
```
NOMEDISPOSITIVO[numero_interfaccia]=RETE
```

**Esempio:**
```
PC1[0]=A
PC2[0]=A
```
Significa: PC1 e PC2 sono collegati entrambi alla rete "A" (stessa rete).

### Configurazione Avanzata lab.conf

#### Indirizzo MAC
È possibile specificare un indirizzo MAC personalizzato per ogni dispositivo:
```
PC1[0]="A/00:00:00:00:00:01"
PC2[0]="A/00:00:00:00:00:02"
```
Il formato è: `RETE/MAC`

#### Immagine Docker
È possibile specificare l'immagine Docker utilizzata:
```
PC1[image]="kathara/base"
```

#### IPv6
Per abilitare o disabilitare IPv6:
```
PC1[ipv6]="true"   # IPv6 abilitato
PC2[ipv6]="false"  # IPv6 disabilitato
```

#### Esempio Completo
```
PC1[0]="A/00:00:00:00:00:01"
PC1[image]="kathara/base"
PC1[ipv6]="false"
PC2[0]="A/00:00:00:00:00:02"
PC2[image]="kathara/base"
PC2[ipv6]="false"
```

---

## 2. Installazione e Configurazione <a name="installazione"></a>

### Prerequisites
1. **Docker Desktop** installato e avviato
2. **Kathara** installato
3. Accesso da terminale

### Installazione Kathara
```bash
# Via pip
pip install kathara

# Verifica installazione
kathara --version
```

### Avvio Docker
Assicurati che Docker Desktop sia avviato prima di usare Kathara.

---

## 3. Esercizi Base <a name="esercizi-base"></a>

### Esercizio 1: Due PC nella stessa rete (collegamento diretto)

**Obiettivo:** Creare una rete con 2 PC collegati direttamente via cavo cross-over.

**Topologia:**
```
PC1 --- cavo cross-over --- PC2
```

**Passo 1: Crea la cartella del lab**
```bash
mkdir esercizio1
cd esercizio1
```

**Passo 2: Crea il file lab.conf**
```bash
notepad lab.conf
```
Contenuto:
```
PC1[0]=A
PC2[0]=A
```

**Passo 3: Crea PC1.startup**
```
ip addr add 192.168.1.1/24 dev eth0
```

**Passo 4: Crea PC2.startup**
```
ip addr add 192.168.1.2/24 dev eth0
```

**Passo 5: Avvia il lab**
```bash
kathara lstart -d .
```

**Passo 6: Verifica la configurazione**
```bash
# Apri un nuovo terminale
kathara connect -d esercizio1 -n PC1

# Testa la connettività
ping 192.168.1.2

# Esci
exit
```

**Risultato atteso:** Il ping tra PC1 e PC2 funziona correttamente.

---

### Esercizio 2: Due PC con Hub

**Obiettivo:** Creare una rete con 2 PC collegati a un Hub.

**Topologia:**
```
PC1
   \ 
    --- Hub1 --- PC2
   /
```

**Passo 1: Crea la cartella**
```bash
mkdir esercizio2
cd esercizio2
```

**Passo 2: lab.conf**
```
PC1[0]=A
PC2[0]=A
Hub1[0]=A
```

**Passo 3: PC1.startup**
```
ip addr add 192.168.1.1/24 dev eth0
```

**Passo 4: PC2.startup**
```
ip addr add 192.168.1.2/24 dev eth0
```

**Passo 5: Hub1.startup**
```
(nessuna configurazione necessaria - l'Hub funziona a livello 1)
```

**Passo 6: Avvia e verifica**
```bash
kathara lstart -d .
kathara connect -d esercizio2 -n PC1
ping 192.168.1.2
```

---

### Esercizio 3: Tre PC con Switch

**Obiettivo:** Creare una rete con 3 PC collegati a uno Switch.

**Topologia:**
```
         PC1
          |
    SW1 -+-- PC2
          |
         PC3
```

**Passo 1: Crea la cartella**
```bash
mkdir esercizio3
cd esercizio3
```

**Passo 2: lab.conf**
```
PC1[0]=A
PC2[0]=A
PC3[0]=A
Switch1[0]=A
```

**Passo 3: PC1.startup**
```
ip addr add 192.168.1.10/24 dev eth0
```

**Passo 4: PC2.startup**
```
ip addr add 192.168.1.20/24 dev eth0
```

**Passo 5: PC3.startup**
```
ip addr add 192.168.1.30/24 dev eth0
```

**Passo 6: Switch1.startup**
```
(nessuna configurazione necessaria per switch layer 2 base)
```

**Passo 7: Verifica**
```bash
# Da PC1, ping verso PC2 e PC3
ping 192.168.1.20
ping 192.168.1.30

# Verifica tabella ARP
arp -a
```

---

### Esercizio 4: Rete con Switch e Router

**Obiettivo:** Creare una rete con 3 PC, uno Switch e un Router.

**Topologia:**
```
         PC1
          |
    SW1 -+-- PC2 --- Router1
          |
         PC3
```

**Passo 1: Crea la cartella**
```bash
mkdir esercizio4
cd esercizio4
```

**Passo 2: lab.conf**
```
PC1[0]=A
PC2[0]=A
PC3[0]=A
Switch1[0]=A
Router1[0]=A
```

**Passo 3: PC1.startup**
```
ip addr add 192.168.10.1/24 dev eth0
ip route add default via 192.168.10.254
```

**Passo 4: PC2.startup**
```
ip addr add 192.168.10.2/24 dev eth0
ip route add default via 192.168.10.254
```

**Passo 5: PC3.startup**
```
ip addr add 192.168.10.3/24 dev eth0
ip route add default via 192.168.10.254
```

**Passo 6: Router1.startup**
```
# Abilita routing IP
sysctl -w net.ipv4.ip_forward=1

# Configura interfaccia
ip addr add 192.168.10.254/24 dev eth0
```

**Nota importante:** Il router deve sempre avere `sysctl -w net.ipv4.ip_forward=1` per instradare i pacchetti tra le reti.

---

## 4. Esercizi con Router <a name="esercizi-router"></a>

### Esercizio 5: Due Router (due sottoreti)

**Obiettivo:** Creare una rete con 2 Router che connettono 2 PC in sottoreti diverse.

**Topologia:**
```
PC1      Router1 --- Router2      PC2
  |         |         |         |
192.168.1.0   10.0.0.0   192.168.2.0
```

**Passo 1: Crea la cartella**
```bash
mkdir esercizio5
cd esercizio5
```

**Passo 2: lab.conf**
```
PC1[0]=A
Router1[0]=A
Router1[1]=B
Router2[0]=B
Router2[1]=C
PC2[0]=C
```

**Spiegazione topologia:**
- `[0]=A`: Prima interfaccia di Router1 nella rete A
- `[1]=B`: Seconda interfaccia di Router1 nella rete B
- `[0]=B`: Prima interfaccia di Router2 nella rete B
- `[1]=C`: Seconda interfaccia di Router2 nella rete C

**Passo 3: PC1.startup**
```
ip addr add 192.168.1.1/24 dev eth0
ip route add default via 192.168.1.254
```

**Passo 4: PC2.startup**
```
ip addr add 192.168.2.1/24 dev eth0
ip route add default via 192.168.2.254
```

**Passo 5: Router1.startup**
```
# Abilita routing
sysctl -w net.ipv4.ip_forward=1

# Interfaccia lato PC1 (rete A)
ip addr add 192.168.1.254/24 dev eth0

# Interfaccia lato Router2 (rete B - collegamento tra router)
ip addr add 10.0.0.1/24 dev eth1
```

**Passo 6: Router2.startup**
```
# Abilita routing
sysctl -w net.ipv4.ip_forward=1

# Interfaccia lato Router1 (rete B)
ip addr add 10.0.0.2/24 dev eth0

# Interfaccia lato PC2 (rete C)
ip addr add 192.168.2.254/24 dev eth1
```

**Passo 7: Verifica**
```bash
kathara lstart -d .
kathara connect -d esercizio5 -n PC1

# Testa connettività
ping 192.168.2.1        # Ping a PC2
traceroute 192.168.2.1  # Visualizza il percorso
```

---

### Esercizio 6: Due Router con Server

**Obiettivo:** Creare una rete con 2 Router e un Server.

**Topologia:**
```
PC1 --- Router1 --- Router2 --- PC2
                          |
                         Server
```

**Passo 1: Crea la cartella**
```bash
mkdir esercizio6
cd esercizio6
```

**Passo 2: lab.conf**
```
PC1[0]=A
Router1[0]=A
Router1[1]=B
Router2[0]=B
Router2[1]=C
PC2[0]=C
Server1[0]=C
```

**Passo 3: PC1.startup**
```
ip addr add 192.168.1.1/24 dev eth0
ip route add default via 192.168.1.254
```

**Passo 4: PC2.startup**
```
ip addr add 192.168.3.1/24 dev eth0
ip route add default via 192.168.3.254
```

**Passo 5: Server1.startup**
```
ip addr add 192.168.3.100/24 dev eth0
ip route add default via 192.168.3.254
```

**Passo 6: Router1.startup**
```
sysctl -w net.ipv4.ip_forward=1
ip addr add 192.168.1.254/24 dev eth0
ip addr add 10.0.0.1/24 dev eth1
```

**Passo 7: Router2.startup**
```
sysctl -w net.ipv4.ip_forward=1
ip.0.0 addr add 10.2/24 dev eth0
ip addr add 192.168.3.254/24 dev eth1
```

**Passo 8: Verifica**
```bash
# Da PC1
kathara connect -d esercizio6 -n PC1
ping 192.168.3.100    # Ping al server
ping 192.168.3.1      # Ping a PC2

# Verifica routing
ip route show
```

---

## 5. Esercizi con Server <a name="esercizi-server"></a>

### Esercizio 7: Server Web

**Obiettivo:** Creare una rete con un Server Web accessibile dai PC.

**Topologia:**
```
PC1 --- Switch --- Server1
```

**Passo 1: Crea la cartella**
```bash
mkdir esercizio7
cd esercizio7
```

**Passo 2: lab.conf**
```
PC1[0]=A
Server1[0]=A
Switch1[0]=A
```

**Passo 3: PC1.startup**
```
ip addr add 192.168.10.1/24 dev eth0
ip route add default via 192.168.10.254
```

**Passo 4: Server1.startup**
```
# Configura IP
ip addr add 192.168.10.100/24 dev eth0
ip route add default via 192.168.10.254

# Avvia server HTTP (Python)
python3 -m http.server 80
```

**Nota:** Il server HTTP Python deve essere avviato manualmente dopo che il container è partito.

**Passo 5: Verifica**
```bash
kathara lstart -d .

# Collegati al server
kathara connect -d esercizio7 -n Server1

# Verifica IP
ip addr show

# Testa server (se httpd è avviato)
curl http://192.168.10.100
```

---

## 6. Esercizi Completi <a name="esercizi-completi"></a>

### Esercizio Completo 1: Rete Aziendale Semplice

**Scenario:** Una piccola azienda con 3 reparti (Sales, IT, Management) collegati a uno Switch.

**Topologia:**
```
        PC-Sales1
            |
    SW1 ---+--- PC-IT1
            |
        PC-Mgmt1
```

**Passo 1: Crea la struttura**
```bash
mkdir rete_aziendale
cd rete_aziendale
```

**Passo 2: lab.conf**
```
PC-Sales1[0]=A
PC-IT1[0]=A
PC-Mgmt1[0]=A
Switch1[0]=A
```

**Passo 3: PC-Sales1.startup**
```
# Configurazione Sales
ip addr add 192.168.10.10/24 dev eth0
ip route add default via 192.168.10.254
hostname Sales-PC
```

**Passo 4: PC-IT1.startup**
```
# Configurazione IT
ip addr add 192.168.10.20/24 dev eth0
ip route add default via 192.168.10.254
hostname IT-PC
```

**Passo 5: PC-Mgmt1.startup**
```
# Configurazione Management
ip addr add 192.168.10.30/24 dev eth0
ip route add default via 192.168.10.254
hostname Mgmt-PC
```

**Passo 6: Avvia e verifica**
```bash
kathara lstart -d .

# Test connettività completa
kathara connect -d rete_aziendale -n PC-Sales1
ping 192.168.10.20   # Verso IT
ping 192.168.10.30   # Verso Management

# Visualizza tabella ARP
arp -a
```

---

### Esercizio Completo 2: Rete con due sedi (2 Router)

**Scenario:** Due sedi aziendali collegate via Router.

**Topologia:**
```
Sede Roma                    Sede Milano
   PC1                         PC2
    |                           |
  Router1 -------------------- Router2
  192.168.1.0                 192.168.2.0
  10.0.0.0 (collegamento)
```

**Passo 1: Crea la struttura**
```bash
mkdir due_sedi
cd due_sedi
```

**Passo 2: lab.conf**
```
PC1[0]=A
Router1[0]=A
Router1[1]=B
Router2[0]=B
PC2[0]=C
```

**Passo 3: PC1.startup (Roma)**
```
ip addr add 192.168.1.1/24 dev eth0
ip route add default via 192.168.1.254
```

**Passo 4: PC2.startup (Milano)**
```
ip addr add 192.168.2.1/24 dev eth0
ip route add default via 192.168.2.254
```

**Passo 5: Router1.startup (Roma)**
```
sysctl -w net.ipv4.ip_forward=1
ip addr add 192.168.1.254/24 dev eth0
ip addr add 10.0.0.1/24 dev eth1
```

**Passo 6: Router2.startup (Milano)**
```
sysctl -w net.ipv4.ip_forward=1
ip addr add 10.0.0.2/24 dev eth0
ip addr add 192.168.2.254/24 dev eth1
```

**Passo 7: Verifica**
```bash
kathara lstart -d .

# Da PC1 Roma
kathara connect -d due_sedi -n PC1

# Testa connettività
ping 192.168.2.1        # Verso PC2 Milano
traceroute 192.168.2.1  # Visualizza hops

# Verifica routing
ip route show
```

---

### Esercizio Completo 3: Rete con Accesso a Internet (NAT)

**Scenario:** Una rete locale con accesso a Internet simulato.

**Topologia:**
```
PC1 --- Router1 --- Cloud (Internet)
```

**Passo 1: Crea la struttura**
```bash
mkdir rete_nat
cd rete_nat
```

**Passo 2: lab.conf**
```
PC1[0]=A
Router1[0]=A
Router1[1]=B
Cloud1[0]=B
```

**Passo 3: PC1.startup**
```
ip addr add 192.168.1.1/24 dev eth0
ip route add default via 192.168.1.254
```

**Passo 4: Router1.startup**
```
# Abilita routing
sysctl -w net.ipv4.ip_forward=1

# Configura interfacce
ip addr add 192.168.1.254/24 dev eth0
ip addr add 10.0.0.1/24 dev eth1

# Configura NAT (Network Address Translation)
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth1 -j MASQUERADE
```

**Passo 5: Cloud1.startup**
```
# Simula gateway internet
ip addr add 10.0.0.2/24 dev eth0
ip route add default via 10.0.0.1
```

**Nota:** InKathara, il NAT funziona solo come simulazione. Per accesso reale serve configurazione aggiuntiva.

---

## 7. Comandi Essenziali <a name="comandi"></a>

### Gestione del Lab

```bash
# Avvia un lab
kathara lstart -d nome_lab

# Ferma un lab
kathara lstop -d nome_lab

# Rimuovi completamente un lab (elimina container)
kathara lclean -d nome_lab

# Lista tutti i container attivi
kathara list

# Collegati a un dispositivo
kathara connect -d nome_lab -n nome_dispositivo

# Esegui un comando su un dispositivo
kathara exec -d nome_lab -n nome_dispositivo "comando"

# Verifica versione Kathara
kathara --version
```

### Comandi dentro i Container

```bash
# Visualizza configurazione IP
ip addr show
ip a

# Visualizza tabella di routing
ip route show
ip r

# Testa connettività (ping)
ping <indirizzo_IP>

# Trace route
traceroute <destinazione>
tracert <destinazione>  # Windows

# Visualizza tabella ARP
arp -a

# Test DNS
nslookup <dominio>
dig <dominio>

# Visualizza porte in ascolto
netstat -tuln

# Cattura traffico di rete
tcpdump -i eth0

# Visualizza processo di rete
ss -tuln

# Testa connettività completo
ping -c 4 <IP>    # Linux
ping -n 4 <IP>    # Windows
```

---

## 8. Tips e Trucchi <a name="tips"></a>

### Regole per i Cavi

| Tipo di Cavo | Uso |
|--------------|-----|
| **Copper Straight-Through** | PC → Router, PC → Switch, Switch → Router |
| **Copper Cross-Over** | PC → PC diretto, Router → Router diretto |
| **Fiber** | Collegamenti tra switch (non supportato nativamente in Kathara) |
| **Serial** | Collegamenti WAN router-router |

### Regole di Rete

1. **Stessa rete (stessa lettera):** I dispositivi comunicano direttamente
2. **Rete diversa:** Serve un Router per comunicare
3. **Default Gateway:** Ogni PC deve sapere chi è il suo gateway
4. **Router:** Deve sempre avere `sysctl -w net.ipv4.ip_forward=1`

### Rete A, B, C nel lab.conf

```
# Rete A (stessa sottorete)
PC1[0]=A
PC2[0]=A

# Rete B (sottorete diversa - serve router)
Router1[1]=B

# Le reti A e B sono separate!
```

### Problemi Comuni e Soluzioni

**Problema: Il ping non funziona**
```
Soluzioni:
1. Verifica che i cavi siano configurati correttamente nel lab.conf
2. Controlla che i PC abbiano il default gateway configurato
3. Verifica che il router abbia sysctl abilitato
4. Controlla che i firewall non blocchino il traffico
```

**Problema: Il lab non parte**
```
Soluzioni:
1. Verifica che Docker sia avviato
2. Verifica che Kathara sia installato correttamente
3. Controlla la sintassi del lab.conf
4. Prova a riavviare Docker
```

**Problema: Non riesco a connettermi al dispositivo**
```
Soluzioni:
1. Il container deve essere avviato (kathara lstart)
2. Verifica che il nome del dispositivo sia corretto
3. Controlla che il lab path sia corretto
```

### Best Practices

1. **Usa nomi descriptivi:** PC1-Roma, PC2-Milano, Router-SedeCentrale
2. **Commenta i file .startup:** Usa # per aggiungere commenti
3. **Testa passo-passo:** Prima crea la rete, poi aggiungi complessità
4. **Salva le configurazioni:** Tieni备份 dei tuoi lab funzionanti
5. **Usa le stesse convenzioni:** 192.168.1.0/24 per reti locali piccole

---

## Schema Riassuntivo Esercizi

| # | Titolo | Dispositivi | Difficoltà |
|---|--------|--------------|------------|
| 1 | 2 PC diretto | PC1, PC2 | ★☆☆☆☆ |
| 2 | 2 PC + Hub | PC1, PC2, Hub1 | ★☆☆☆☆ |
| 3 | 3 PC + Switch | PC1, PC2, PC3, SW1 | ★☆☆☆☆ |
| 4 | 3 PC + Switch + Router | PC1, PC2, PC3, SW1, R1 | ★★☆☆☆ |
| 5 | 2 Router | PC1, PC2, R1, R2 | ★★☆☆☆ |
| 6 | 2 Router + Server | PC1, PC2, Server1, R1, R2 | ★★★☆☆ |
| 7 | Server Web | PC1, Server1, SW1 | ★★☆☆☆ |

---

## Link Utili

- **Documentazione Kathara:** https://www.kathara.org/
- **Comandi Kathara:** `kathara --help`
- **Docker Desktop:** https://www.docker.com/products/docker-desktop
