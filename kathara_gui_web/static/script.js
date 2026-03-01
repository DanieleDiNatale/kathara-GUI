const canvas = document.getElementById('topologyCanvas');
const ctx = canvas.getContext('2d');

const DEVICE_TYPES = {
    router: { color: '#2D2D2D', label: 'ROUTER' },
    switch: { color: '#1A1A1A', label: 'SWITCH' },
    pc: { color: '#333333', label: 'PC' },
    hub: { color: '#0D0D0D', label: 'HUB' },
    cloud: { color: '#404040', label: 'CLOUD' }
};

const DEVICE_PORTS = {
    router: 4,
    switch: 4,
    pc: 2,
    hub: 2,
    cloud: 2
};

let devices = [];
let connections = [];
let selectedDevice = null;
let selectedConnection = null;
let connectMode = false;
let connectStart = null;
let selectedCableType = 'copper-straight';
let currentLabPath = '';
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let deviceCounter = { router: 0, switch: 0, pc: 0, hub: 0, cloud: 0 };

const CABLE_TYPES = {
    'copper-straight': { label: 'Copper Straight', color: '#FF6B6B' },
    'copper-cross': { label: 'Copper Cross', color: '#4ECDC4' },
    'fiber': { label: 'Fiber', color: '#45B7D1' },
    'serial': { label: 'Serial', color: '#DDA0DD' },
    'phone': { label: 'Phone', color: '#FFEAA7' },
    'coaxial': { label: 'Coaxial', color: '#795548' }
};

const DEVICE_WIDTH = 80;
const DEVICE_HEIGHT = 60;

function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    draw();
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    drawGrid();
    
    connections.forEach(conn => {
        const dev1 = devices.find(d => d.name === conn.from);
        const dev2 = devices.find(d => d.name === conn.to);
        if (dev1 && dev2) {
            drawConnection(dev1, dev2, conn.color);
        }
    });
    
    devices.forEach(device => {
        drawDevice(device);
    });
    
    if (connectStart && isDragging) {
        const mousePos = lastMousePos;
        ctx.beginPath();
        ctx.moveTo(connectStart.x + DEVICE_WIDTH/2, connectStart.y + DEVICE_HEIGHT/2);
        ctx.lineTo(mousePos.x, mousePos.y);
        ctx.strokeStyle = CABLE_TYPES[selectedCableType].color;
        ctx.lineWidth = 4;
        ctx.setLineDash([8, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
    }
}

function drawGrid() {
    ctx.strokeStyle = '#2a2a4e';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 50) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 50) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }
}

function drawDevice(device) {
    const type = DEVICE_TYPES[device.type];
    const x = device.x;
    const y = device.y;
    const isSelected = selectedDevice === device;
    
    ctx.fillStyle = type.color;
    ctx.strokeStyle = isSelected ? '#FFD700' : '#222';
    ctx.lineWidth = isSelected ? 4 : 3;
    
    ctx.beginPath();
    ctx.roundRect(x, y, DEVICE_WIDTH, DEVICE_HEIGHT, 8);
    ctx.fill();
    ctx.stroke();
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(type.label, x + DEVICE_WIDTH/2, y + 20);
    
    ctx.font = '11px Arial';
    ctx.fillText(device.name, x + DEVICE_WIDTH/2, y + 38);
    
    if (device.ip) {
        ctx.fillStyle = '#FFFF00';
        ctx.font = 'bold 10px Arial';
        ctx.fillText(`IP:${device.ip}`, x + DEVICE_WIDTH/2, y + 52);
    }
    
    ctx.fillStyle = 'white';
    ctx.beginPath();
    for (let i = 0; i < DEVICE_PORTS[device.type]; i++) {
        const portX = x + 10 + i * 18;
        const portY = y + DEVICE_HEIGHT;
        ctx.moveTo(portX, portY);
        ctx.arc(portX, portY, 5, 0, Math.PI * 2);
    }
    ctx.fill();
}

function drawConnection(dev1, dev2, color) {
    const x1 = dev1.x + DEVICE_WIDTH/2;
    const y1 = dev1.y + DEVICE_HEIGHT/2;
    const x2 = dev2.x + DEVICE_WIDTH/2;
    const y2 = dev2.y + DEVICE_HEIGHT/2;
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    const dx = x2 - x1;
    const dy = y2 - y1;
    
    const cp1x = x1 + dx * 0.25;
    const cp1y = y1 + dy * 0.1;
    const cp2x = x2 - dx * 0.25;
    const cp2y = y2 - dy * 0.1;
    
    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x2, y2);
    ctx.stroke();
    
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x1, y1, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(x2, y2, 7, 0, Math.PI * 2);
    ctx.fill();
}

function getDeviceAt(x, y) {
    for (let i = devices.length - 1; i >= 0; i--) {
        const d = devices[i];
        if (x >= d.x && x <= d.x + DEVICE_WIDTH && y >= d.y && y <= d.y + DEVICE_HEIGHT) {
            return d;
        }
    }
    return null;
}

function getConnectionAt(x, y) {
    for (let i = 0; i < connections.length; i++) {
        const conn = connections[i];
        const dev1 = devices.find(d => d.name === conn.from);
        const dev2 = devices.find(d => d.name === conn.to);
        if (!dev1 || !dev2) continue;
        
        const x1 = dev1.x + DEVICE_WIDTH/2;
        const y1 = dev1.y + DEVICE_HEIGHT/2;
        const x2 = dev2.x + DEVICE_WIDTH/2;
        const y2 = dev2.y + DEVICE_HEIGHT/2;
        
        const dist = pointToLineDistance(x, y, x1, y1, x2, y2);
        if (dist < 10) {
            return conn;
        }
    }
    return null;
}

function pointToLineDistance(px, py, x1, y1, x2, y2) {
    const A = px - x1;
    const B = py - y1;
    const C = x2 - x1;
    const D = y2 - y1;
    const dot = A * C + B * D;
    const len_sq = C * C + D * D;
    let param = -1;
    if (len_sq !== 0) param = dot / len_sq;
    let xx, yy;
    if (param < 0) { xx = x1; yy = y1; }
    else if (param > 1) { xx = x2; yy = y2; }
    else { xx = x1 + param * C; yy = y1 + param * D; }
    const dx = px - xx;
    const dy = py - yy;
    return Math.sqrt(dx * dx + dy * dy);
}

let lastMousePos = { x: 0, y: 0 };

canvas.addEventListener('mousedown', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    lastMousePos = { x, y };
    
    const device = getDeviceAt(x, y);
    const conn = getConnectionAt(x, y);
    
    if (conn) {
        selectedConnection = conn;
        selectedDevice = null;
        updatePropertiesPanel();
        updateConnectionsList();
        draw();
        return;
    }
    
    if (connectMode && device) {
        if (!connectStart) {
            connectStart = device;
        } else if (connectStart !== device) {
            const exists = connections.some(c => 
                (c.from === connectStart.name && c.to === device.name) ||
                (c.from === device.name && c.to === connectStart.name)
            );
            if (!exists) {
                const cableType = CABLE_TYPES[selectedCableType];
                connections.push({
                    from: connectStart.name,
                    to: device.name,
                    cableType: selectedCableType,
                    color: cableType.color
                });
                log(`[LINK] ${connectStart.name} <-> ${device.name} (${cableType.label})`, cableType.color);
                updateConnectionsList();
            }
            connectStart = null;
            document.getElementById('connectModeBtn').classList.remove('active');
            connectMode = false;
        }
        draw();
        return;
    }
    
    if (device) {
        selectedDevice = device;
        selectedConnection = null;
        isDragging = true;
        dragOffset = { x: x - device.x, y: y - device.y };
        updatePropertiesPanel();
    } else {
        selectedDevice = null;
        selectedConnection = null;
        updatePropertiesPanel();
    }
    draw();
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    lastMousePos = { x, y };
    
    if (isDragging && selectedDevice) {
        selectedDevice.x = x - dragOffset.x;
        selectedDevice.y = y - dragOffset.y;
        draw();
    }
});

canvas.addEventListener('mouseup', () => {
    isDragging = false;
});

canvas.addEventListener('dblclick', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const device = getDeviceAt(x, y);
    if (device) {
        openIPDialog(device);
    }
});

document.querySelectorAll('.device-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        deviceCounter[type]++;
        const name = `${type.toUpperCase()}${deviceCounter[type]}`;
        
        const newDevice = {
            name,
            type,
            x: 100 + (devices.length % 4) * 150,
            y: 100 + Math.floor(devices.length / 4) * 120,
            ip: '',
            gateway: '',
            config: ''
        };
        
        devices.push(newDevice);
        updateDeviceSelect();
        log(`[+] Added: ${name}`, DEVICE_TYPES[type].color);
        draw();
    });
});

document.getElementById('connectModeBtn').addEventListener('click', () => {
    connectMode = !connectMode;
    connectStart = null;
    document.getElementById('connectModeBtn').classList.toggle('active', connectMode);
    if (connectMode) {
        log('Connect mode: click two devices to connect', '#FFD700');
    }
});

document.getElementById('deleteBtn').addEventListener('click', () => {
    if (selectedConnection) {
        connections = connections.filter(c => c !== selectedConnection);
        log(`[-] Deleted connection ${selectedConnection.from} <-> ${selectedConnection.to}`, '#D0021B');
        selectedConnection = null;
        updateConnectionsList();
        draw();
    } else if (selectedDevice) {
        connections = connections.filter(c => 
            c.from !== selectedDevice.name && c.to !== selectedDevice.name
        );
        
        const match = selectedDevice.name.match(/(\D+)(\d+)$/);
        if (match) {
            const type = match[1].toLowerCase();
            const num = parseInt(match[2]);
            if (num === deviceCounter[type]) {
                let maxNum = 0;
                devices.forEach(d => {
                    if (d !== selectedDevice) {
                        const m = d.name.match(/(\D+)(\d+)$/);
                        if (m && m[1].toLowerCase() === type) {
                            maxNum = Math.max(maxNum, parseInt(m[2]));
                        }
                    }
                });
                deviceCounter[type] = maxNum;
            }
        }
        
        log(`[-] Deleted: ${selectedDevice.name}`, '#D0021B');
        devices = devices.filter(d => d !== selectedDevice);
        selectedDevice = null;
        updateDeviceSelect();
        updatePropertiesPanel();
        updateConnectionsList();
        draw();
    }
});

document.getElementById('cableType').addEventListener('change', (e) => {
    selectedCableType = e.target.value;
});

function updateDeviceSelect() {
    const select = document.getElementById('deviceSelect');
    select.innerHTML = '<option value="">Select device...</option>';
    devices.forEach(d => {
        const option = document.createElement('option');
        option.value = d.name;
        option.textContent = `${DEVICE_TYPES[d.type].label} ${d.name}`;
        select.appendChild(option);
    });
}

function updatePropertiesPanel() {
    const nameEl = document.querySelector('#selectedName .property-value');
    const typeEl = document.querySelector('#selectedType .property-value');
    const portsEl = document.querySelector('#selectedPorts .property-value');
    const ipEl = document.querySelector('#selectedIP .property-value');
    const gatewayEl = document.querySelector('#selectedGateway .property-value');
    const configEl = document.getElementById('deviceConfig');
    const configBtn = document.getElementById('saveConfigBtn');
    const setIpBtn = document.getElementById('setIpBtn');
    
    if (selectedDevice) {
        nameEl.textContent = selectedDevice.name;
        typeEl.textContent = DEVICE_TYPES[selectedDevice.type].label;
        portsEl.textContent = Array.from({length: DEVICE_PORTS[selectedDevice.type]}, (_, i) => `eth${i}`).join(', ');
        ipEl.textContent = selectedDevice.ip || '-';
        gatewayEl.textContent = selectedDevice.gateway || '-';
        configEl.value = selectedDevice.config || '';
        configBtn.style.display = 'inline-block';
        setIpBtn.style.display = 'inline-block';
    } else if (selectedConnection) {
        const dev1 = devices.find(d => d.name === selectedConnection.from);
        const dev2 = devices.find(d => d.name === selectedConnection.to);
        nameEl.textContent = `${selectedConnection.from} <-> ${selectedConnection.to}`;
        typeEl.textContent = CABLE_TYPES[selectedConnection.cableType].label;
        portsEl.textContent = '-';
        ipEl.textContent = '-';
        gatewayEl.textContent = '-';
        configEl.value = '';
        configBtn.style.display = 'none';
        setIpBtn.style.display = 'none';
    } else {
        nameEl.textContent = '-';
        typeEl.textContent = '-';
        portsEl.textContent = '-';
        ipEl.textContent = '-';
        gatewayEl.textContent = '-';
        configEl.value = '';
        configBtn.style.display = 'none';
        setIpBtn.style.display = 'none';
    }
}

function updateConnectionsList() {
    const list = document.getElementById('connectionsList');
    list.innerHTML = '';
    
    if (connections.length === 0) {
        const item = document.createElement('div');
        item.className = 'connection-item';
        item.textContent = 'No connections yet';
        item.style.color = '#666';
        list.appendChild(item);
        return;
    }
    
    connections.forEach((conn, idx) => {
        const item = document.createElement('div');
        item.className = 'connection-item';
        item.style.borderLeft = `4px solid ${conn.color}`;
        item.innerHTML = `<strong>${conn.from}</strong> ⟷ <strong>${conn.to}</strong><br><small>${CABLE_TYPES[conn.cableType].label}</small>`;
        item.onclick = () => {
            selectedConnection = conn;
            selectedDevice = null;
            updatePropertiesPanel();
            updateConnectionsList();
        };
        list.appendChild(item);
    });
    
    const total = document.createElement('div');
    total.className = 'connection-total';
    total.textContent = `--- Total: ${connections.length} connections ---`;
    list.appendChild(total);
}

function openIPDialog(device) {
    const ip = prompt(`Configure IP for ${device.name}:\nEnter IP address (e.g., 192.168.1.10)`, device.ip || '');
    if (ip !== null) {
        device.ip = ip;
        const gw = prompt(`Enter Gateway for ${device.name} (optional):`, device.gateway || '');
        if (gw !== null) {
            device.gateway = gw;
        }
        updatePropertiesPanel();
        log(`[IP] ${device.name}: ${ip}` + (gw ? ` gateway: ${gw}` : ''), '#FFFF00');
        draw();
    }
}

document.getElementById('setIpBtn').addEventListener('click', () => {
    if (selectedDevice) {
        openIPDialog(selectedDevice);
    }
});

document.getElementById('saveConfigBtn').addEventListener('click', () => {
    if (selectedDevice) {
        selectedDevice.config = document.getElementById('deviceConfig').value;
        log(`[CFG] Saved config for ${selectedDevice.name}`);
    }
});

function log(message, color = '#00ff00') {
    const consoleEl = document.getElementById('console');
    const time = new Date().toLocaleTimeString();
    consoleEl.innerHTML += `<div style="color:${color}">[${time}] ${message}</div>`;
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function apiCall(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

document.getElementById('exportBtn').addEventListener('click', async () => {
    const labName = document.getElementById('labName').value || 'my_lab';
    
    const result = await apiCall('/api/lab/export', {
        lab_name: labName,
        devices: devices.map(d => ({ name: d.name, type: d.type, ip: d.ip, gateway: d.gateway, config: d.config })),
        connections: connections
    });
    
    if (result.success) {
        currentLabPath = result.lab_path;
        log(`[EXPORT] Lab exported to: ${result.lab_path}`, '#666');
        log(`[INFO] ${devices.length} devices, ${connections.length} connections`, '#888');
    }
});

document.getElementById('startBtn').addEventListener('click', async () => {
    if (!currentLabPath) {
        const labName = document.getElementById('labName').value || 'my_lab';
        const result = await apiCall('/api/lab/export', {
            lab_name: labName,
            devices: devices.map(d => ({ name: d.name, type: d.type, ip: d.ip, gateway: d.gateway, config: d.config })),
            connections: connections
        });
        if (result.success) {
            currentLabPath = result.lab_path;
        }
    }
    
    if (currentLabPath) {
        const result = await apiCall('/api/lab/start', { lab_path: currentLabPath });
        log(result.message || result.error, result.success ? '#7ED321' : '#ff0000');
    } else {
        log('[ERROR] Please export the lab first', '#ff0000');
    }
});

document.getElementById('stopBtn').addEventListener('click', async () => {
    if (currentLabPath) {
        const result = await apiCall('/api/lab/stop', { lab_path: currentLabPath });
        log(result.message || result.error, result.success ? '#F5A623' : '#ff0000');
    }
});

document.getElementById('listBtn').addEventListener('click', async () => {
    if (!currentLabPath) {
        log('[WARN] Please export/start the lab first', '#F5A623');
        return;
    }
    const result = await apiCall('/api/lab/list', { lab_path: currentLabPath });
    if (result.success) {
        log(result.output || 'No devices running', '#7ED321');
    } else {
        log(result.error, '#ff0000');
    }
});

document.getElementById('connectBtn').addEventListener('click', async () => {
    const deviceName = document.getElementById('deviceSelect').value;
    if (!deviceName || !currentLabPath) {
        log('[WARN] Select a device and start the lab first', '#F5A623');
        return;
    }
    const result = await apiCall('/api/connect', { 
        lab_path: currentLabPath, 
        device_name: deviceName 
    });
    log(result.message || result.error, result.success ? '#9013FE' : '#ff0000');
});

document.getElementById('resetBtn').addEventListener('click', () => {
    devices = [];
    connections = [];
    deviceCounter = { router: 0, switch: 0, pc: 0, hub: 0, cloud: 0 };
    selectedDevice = null;
    selectedConnection = null;
    currentLabPath = '';
    updateDeviceSelect();
    updatePropertiesPanel();
    updateConnectionsList();
    draw();
    log('[NEW] New lab created', '#9013FE');
});

log('>>> Kathara Web GUI Ready', '#00ff00');
log('>>> Click device buttons to add them', '#888');
