# Guida Kathara - Reti di Calcolatori

## Introduzione a Kathara

Kathara è un emulatore di rete basato su Docker che permette di creare scenari di rete realistici. È ampiamente utilizzato per esercitazioni CCNA e per simulare reti aziendali.

---

## Prerequisiti

1. **Docker Desktop** installato e avviato
2. **Kathara** installato (`pip install kathara`)
3. Accesso root/admin per eseguire i container

---

## Struttura di un Lab Kathara

Ogni lab Kathara è una cartella contenente:

```
mio_lab/
├── lab.conf          # Definizione della topologia
├── PC1.startup       # Configurazione PC1
├── PC2.startup       # Configurazione PC2
├── Router1.startup  # Configurazione Router1
└── ...
```

---

## Creare una Rete Semplice (Due PC)

### 1. Topologia (lab.conf)

```
PC1[0]=A
PC2[0]=A
```

Questo crea una rete privata "A" dove PC1 e PC2 sono collegati allo stesso switch.

### 2. Configurazione PC1 (PC1.startup)

```
# Configurazione interfaccia eth0
ip addr add 192.168.1.10/24 dev eth0
ip route add default via 192.168.1.254
```

### 3. Configurazione PC2 (PC2.startup)

```
ip addr add 192.168.1.20/24 dev eth0
ip route add default via 192.168.1.254
```

### 4. Avviare il Lab

```bash
kathara lstart -d mio_lab
```

---

## Rete con Router

### Topologia

```
PC1[0]=A
PC2[0]=A
Router1[0]=A
Router1[1]=B
PC3[0]=B
PC4[0]=B
```

- Rete A: 192.168.1.0/24 (lato PC1/PC2)
- Rete B: 192.168.2.0/24 (lato PC3/PC4)

### Configurazione Router1

```
sysctl -w net.ipv4.ip_forward=1
ip addr add 192.168.1.254/24 dev eth0
ip addr add 192.168.2.254/24 dev eth1
```

### Configurazione PC1

```
ip addr add 192.168.1.10/24 dev eth0
ip route add default via 192.168.1.254
```

### Configurazione PC3

```
ip addr add 192.168.2.10/24 dev eth0
ip route add default via 192.168.2.254
```

---

## Rete con VLAN

### Topologia

```
SW1[0]=A
SW1[1]=B
PC1[0]=A
PC2[0]=B
```

### Configurazione Switch (SW1.startup)

```
# Crea VLAN 10 e VLAN 20
vconfig add eth0 10
vconfig add eth0 20

# Configura le VLAN
ip link set eth0 up
ip link add link eth0 name eth0.10 up
ip link add link eth0 name eth0.20 up

# Assegna porte alle VLAN (usando vlan filter)
ip link set eth1 master eth0.10
ip link set eth2 master eth0.20

# Configura IP su VLAN di management
ip addr add 192.168.10.1/24 dev eth0.10
ip addr add 192.168.20.1/24 dev eth0.20
```

---

## Rete con DHCP

### Configurazione Router come DHCP Server

```
# Avvia dnsmasq come server DHCP
dnsmasq --interface=eth0 --dhcp-range=192.168.1.100,192.168.1.200,12h
```

### Configurazione PC (richiede DHCP client)

```
# Assicurati che il client DHCP sia attivo
udhcpc -i eth0
```

---

## Rete con NAT (Internet)

### Topologia

```
PC1[0]=A
Router1[0]=A
Router1[1]=B
Cloud[0]=B
```

### Configurazione Router1

```
sysctl -w net.ipv4.ip_forward=1
ip addr add 192.168.1.254/24 dev eth0
ip addr add 10.0.0.1/24 dev eth1

# NAT
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth1 -j MASQUERADE
```

### Configurazione Cloud

```
# Simula connessione internet
ip addr add 10.0.0.2/24 dev eth0
ip route add default via 10.0.0.1
```

---

## Rete con Server

### Topologia

```
PC1[0]=A
Server1[0]=A
Router1[0]=A
```

### Configurazione Server Web (Server1.startup)

```
# Configura IP
ip addr add 192.168.1.100/24 dev eth0
ip route add default via 192.168.1.254

# Avvia server HTTP (se disponibile)
httpd -h /var/www/html
```

oppure semplice server Python:

```
python3 -m http.server 80
```

---

## Comandi Utili

### Gestione Lab

```bash
# Avvia lab
kathara lstart -d nome_lab

# Ferma lab
kathara lstop -d nome_lab

# Rimuovi lab
kathara lclean -d nome_lab

# Lista container attivi
kathara list

# Collegati a un dispositivo
kathara connect -d nome_lab -n nome_dispositivo

# Esegui comando su dispositivo
kathara exec -d nome_lab -n nome_dispositivo "comando"
```

### Comandi dentro i Container

```bash
# Visualizza configurazione IP
ip addr show
ip route show

# Test connettività
ping <indirizzo_ip>

# Visualizza tabella ARP
arp -a

# Test DNS
nslookup <dominio>

# Visualizza porte in ascolto
netstat -tuln

# Trace route
traceroute <destinazione>
```

---

## Scenari CCNA Comuni

### 1. Rete Flat (Hub/Switch)

```
Hub1[0]=A
PC1[0]=A
PC2[0]=A
PC3[0]=A
```

Tutti i PC nella stessa rete. Usare cavi **copper-cross** per collegamento diretto PC-PC.

### 2. Rete con Switch Layer 2

```
SW1[0]=A
SW1[1]=B
PC1[0]=A
PC2[0]=A
PC3[0]=B
PC4[0]=B
```

Due VLAN su uno switch.

### 3. Rete con 3 Router (Scenario EIGRP/OSPF)

```
R1[0]=A
R1[1]=B
R2[0]=A
R2[1]=C
R3[0]=B
R3[1]=C
```

拓扑 triagolare per protocolli di routing.

### 4. Access Point WiFi

```
AP1[0]=A
PC1[0]=A
PC2[0]=A
Router1[0]=A
```

Nota: Kathara non supporta nativamente WiFi, si simula con switch.

---

## Tips & Tricks

### Debug

```bash
# Verifica connettività passo passo
ip route get <ip_dest>

# Cattura traffico
tcpdump -i eth0

# Visualizza statistiche interfacce
ip -s link show
```

### Problemi Comuni

1. **Container non parte**: Verifica che Docker sia avviato
2. **Ping non funziona**: Controlla firewall e configurazione IP
3. **Rete isolata**: Verifica che i cavi siano corretti e che le interfacce siano `UP`

---

## Riferimenti

- Documentazione ufficiale: https://www.kathara.org/
- Comandi Kathara: `kathara --help`
