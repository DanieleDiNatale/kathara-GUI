console.log('Script starting...');

const canvas = document.getElementById('topologyCanvas');
const ctx = canvas.getContext('2d');

const DEVICE_TYPES = {
    router: { color: '#00BFFF', label: 'ROUTER' },
    switch: { color: '#F5A623', label: 'SWITCH' },
    pc: { color: '#7ED321', label: 'PC' },
    hub: { color: '#D0021B', label: 'HUB' },
    cloud: { color: '#9B59B6', label: 'CLOUD' }
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
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    draw();
}

window.addEventListener('resize', resizeCanvas);

window.addEventListener('load', function() {
    setTimeout(function() {
        resizeCanvas();
    }, 100);
});

resizeCanvas();

function draw() {
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
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
    const cx = x + DEVICE_WIDTH / 2;
    const cy = y + DEVICE_HEIGHT / 2;
    
    switch (device.type) {
        case 'pc':
            drawPC(x, y, type.color, isSelected);
            break;
        case 'router':
            drawRouter(x, y, type.color, isSelected);
            break;
        case 'switch':
            drawSwitch(x, y, type.color, isSelected);
            break;
        case 'hub':
            drawHub(x, y, type.color, isSelected);
            break;
        case 'cloud':
            drawCloud(x, y, type.color, isSelected);
            break;
    }
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 10px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(device.name, cx, y + DEVICE_HEIGHT + 12);
    
    if (device.ip && (device.type === 'pc' || device.type === 'router' || device.type === 'cloud')) {
        ctx.fillStyle = '#FFFF00';
        ctx.font = 'bold 9px Arial';
        ctx.fillText(`${device.eth}:${device.ip}`, cx, y + DEVICE_HEIGHT + 24);
    }
}

function drawPC(x, y, color, isSelected) {
    const cx = x + DEVICE_WIDTH / 2;
    const cy = y + DEVICE_HEIGHT / 2;
    
    ctx.fillStyle = color;
    ctx.strokeStyle = isSelected ? '#FFD700' : color;
    ctx.lineWidth = isSelected ? 3 : 0;
    
    ctx.fillRect(x + 10, y + 8, 60, 40);
    if (isSelected) ctx.strokeRect(x + 10, y + 8, 60, 40);
    
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(x + 15, y + 12, 50, 30);
    
    ctx.fillStyle = '#00ff00';
    ctx.fillRect(x + 55, y + 30, 6, 6);
    
    ctx.fillStyle = color;
    ctx.fillRect(x + 25, y + 48, 30, 8);
    if (isSelected) ctx.strokeRect(x + 25, y + 48, 30, 8);
    
    ctx.strokeStyle = isSelected ? '#FFD700' : '#222';
    ctx.lineWidth = isSelected ? 3 : 2;
    ctx.beginPath();
    ctx.moveTo(x + 30, y + 56);
    ctx.lineTo(x + 30, y + 62);
    ctx.lineTo(x + 20, y + 62);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x + 50, y + 56);
    ctx.lineTo(x + 50, y + 62);
    ctx.lineTo(x + 60, y + 62);
    ctx.stroke();
}

function drawRouter(x, y, color, isSelected) {
    const cx = x + DEVICE_WIDTH / 2;
    const cy = y + DEVICE_HEIGHT / 2;
    
    ctx.fillStyle = '#333333';
    ctx.strokeStyle = isSelected ? '#FFD700' : '#333333';
    ctx.lineWidth = isSelected ? 3 : 0;
    
    ctx.fillRect(x + 15, y + 15, 50, 30);
    if (isSelected) ctx.strokeRect(x + 15, y + 15, 50, 30);
    
    ctx.fillStyle = '#00BFFF';
    ctx.fillRect(x + 18, y + 18, 44, 24);
    
    ctx.fillStyle = '#1a1a2e';
    ctx.beginPath();
    ctx.arc(x + 30, y + 30, 8, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = '#00FF00';
    ctx.beginPath();
    ctx.arc(x + 30, y + 30, 4, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.strokeStyle = '#00BFFF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x + 30, y + 10, 6, Math.PI, 0);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(x + 30, y + 5, 10, Math.PI, 0);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(x + 30, y, 14, Math.PI, 0);
    ctx.stroke();
}

function drawSwitch(x, y, color, isSelected) {
    const cx = x + DEVICE_WIDTH / 2;
    const cy = y + DEVICE_HEIGHT / 2;
    
    ctx.fillStyle = color;
    ctx.strokeStyle = isSelected ? '#FFD700' : color;
    ctx.lineWidth = isSelected ? 3 : 0;
    
    ctx.fillRect(x + 5, y + 15, 70, 35);
    if (isSelected) ctx.strokeRect(x + 5, y + 15, 70, 35);
    
    ctx.fillStyle = 'white';
    for (let i = 0; i < 4; i++) {
        const px = x + 15 + i * 16;
        ctx.fillRect(px, y + 28, 10, 8);
    }
    
    ctx.fillStyle = '#00ff00';
    for (let i = 0; i < 4; i++) {
        const px = x + 17 + i * 16;
        ctx.fillRect(px, y + 30, 6, 4);
    }
    
    ctx.fillStyle = '#333';
    ctx.fillRect(x + 60, y + 22, 10, 6);
}

function drawHub(x, y, color, isSelected) {
    const cx = x + DEVICE_WIDTH / 2;
    const cy = y + DEVICE_HEIGHT / 2;
    
    ctx.fillStyle = color;
    ctx.strokeStyle = isSelected ? '#FFD700' : color;
    ctx.lineWidth = isSelected ? 3 : 0;
    
    ctx.beginPath();
    ctx.arc(cx, cy, 28, 0, Math.PI * 2);
    ctx.fill();
    if (isSelected) ctx.stroke();
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('HUB', cx, cy);
    
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    for (let i = 0; i < 4; i++) {
        const angle = (i * Math.PI / 2) + Math.PI / 4;
        const sx = cx + Math.cos(angle) * 20;
        const sy = cy + Math.sin(angle) * 20;
        const ex = cx + Math.cos(angle) * 36;
        const ey = cy + Math.sin(angle) * 36;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(ex, ey);
        ctx.stroke();
    }
}

function drawCloud(x, y, color, isSelected) {
    const cx = x + DEVICE_WIDTH / 2;
    const cy = y + DEVICE_HEIGHT / 2;
    
    ctx.fillStyle = color;
    ctx.strokeStyle = isSelected ? '#FFD700' : color;
    ctx.lineWidth = isSelected ? 3 : 0;
    
    ctx.beginPath();
    ctx.arc(x + 20, cy + 12, 12, Math.PI, 0);
    ctx.arc(x + 35, cy + 6, 14, Math.PI, 0);
    ctx.arc(x + 50, cy + 8, 14, Math.PI, 0);
    ctx.arc(x + 60, cy + 16, 10, Math.PI, 0);
    ctx.arc(x + 50, cy + 24, 10, 0, Math.PI);
    ctx.arc(x + 35, cy + 24, 10, 0, Math.PI);
    ctx.arc(x + 20, cy + 20, 8, 0, Math.PI);
    ctx.closePath();
    ctx.fill();
    if (isSelected) ctx.stroke();
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
    if (device && (device.type === 'pc' || device.type === 'router' || device.type === 'cloud')) {
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
            eth: 'eth0',
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
    const ethEl = document.querySelector('#selectedEth .property-value');
    const ipEl = document.querySelector('#selectedIP .property-value');
    const gatewayEl = document.querySelector('#selectedGateway .property-value');
    const ethRow = document.getElementById('selectedEth');
    const ipRow = document.getElementById('selectedIP');
    const gatewayRow = document.getElementById('selectedGateway');
    const setIpBtn = document.getElementById('setIpBtn');
    const pingBtn = document.getElementById('pingBtn');
    
    const canHaveIP = selectedDevice && (selectedDevice.type === 'pc' || selectedDevice.type === 'router' || selectedDevice.type === 'cloud');
    
    if (selectedDevice) {
        nameEl.textContent = selectedDevice.name;
        typeEl.textContent = DEVICE_TYPES[selectedDevice.type].label;
        portsEl.textContent = Array.from({length: DEVICE_PORTS[selectedDevice.type]}, (_, i) => `eth${i}`).join(', ');
        
        if (canHaveIP) {
            ethEl.textContent = selectedDevice.eth || '-';
            ipEl.textContent = selectedDevice.ip || '-';
            gatewayEl.textContent = selectedDevice.gateway || '-';
            ethRow.style.display = 'flex';
            ipRow.style.display = 'flex';
            gatewayRow.style.display = 'flex';
            setIpBtn.style.display = 'inline-block';
            pingBtn.style.display = selectedDevice.ip ? 'inline-block' : 'none';
        } else {
            ethEl.textContent = '-';
            ipEl.textContent = '-';
            gatewayEl.textContent = '-';
            ethRow.style.display = 'none';
            ipRow.style.display = 'none';
            gatewayRow.style.display = 'none';
            setIpBtn.style.display = 'none';
            pingBtn.style.display = 'none';
        }
    } else if (selectedConnection) {
        const dev1 = devices.find(d => d.name === selectedConnection.from);
        const dev2 = devices.find(d => d.name === selectedConnection.to);
        nameEl.textContent = `${selectedConnection.from} <-> ${selectedConnection.to}`;
        typeEl.textContent = CABLE_TYPES[selectedConnection.cableType].label;
        portsEl.textContent = '-';
        ethEl.textContent = '-';
        ipEl.textContent = '-';
        gatewayEl.textContent = '-';
        ethRow.style.display = 'none';
        ipRow.style.display = 'none';
        gatewayRow.style.display = 'none';
        setIpBtn.style.display = 'none';
        pingBtn.style.display = 'none';
    } else {
        nameEl.textContent = '-';
        typeEl.textContent = '-';
        portsEl.textContent = '-';
        ethEl.textContent = '-';
        ipEl.textContent = '-';
        gatewayEl.textContent = '-';
        ethRow.style.display = 'none';
        ipRow.style.display = 'none';
        gatewayRow.style.display = 'none';
        setIpBtn.style.display = 'none';
        pingBtn.style.display = 'none';
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
    const ethOptions = ['eth0', 'eth1', 'eth2', 'eth3'];
    let selectedEth = device.eth || 'eth0';
    
    const eth = prompt(`Configure ${device.name}:\nSelect interface (${ethOptions.join(', ')}):`, selectedEth);
    if (eth !== null && ethOptions.includes(eth)) {
        device.eth = eth;
        const ip = prompt(`Enter IP address for ${device.name} (e.g., 192.168.1.10):`, device.ip || '');
        if (ip !== null) {
            device.ip = ip;
            const gw = prompt(`Enter Gateway for ${device.name} (optional):`, device.gateway || '');
            if (gw !== null) {
                device.gateway = gw;
            }
            updatePropertiesPanel();
            log(`[IP] ${device.name} ${eth}:${ip}` + (gw ? ` gateway: ${gw}` : ''), '#FFFF00');
            draw();
        }
    } else if (eth !== null) {
        alert('Invalid interface. Please choose: ' + ethOptions.join(', '));
    }
}

document.getElementById('setIpBtn').addEventListener('click', () => {
    if (selectedDevice) {
        openIPDialog(selectedDevice);
    }
});

document.getElementById('pingBtn').addEventListener('click', () => {
    if (selectedDevice && selectedDevice.ip) {
        const targetIP = prompt(`Enter IP address to ping from ${selectedDevice.name}:`, selectedDevice.gateway || '');
        if (targetIP) {
            if (!currentLabPath) {
                log(`[PING] Error: No lab exported. Please export and start the lab first.`, '#FF6B6B');
                return;
            }
            log(`[PING] ${selectedDevice.name} ping ${targetIP} via ${selectedDevice.eth || 'eth0'}...`, '#00FFFF');
            fetch('/api/ping', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    device_name: selectedDevice.name, 
                    target_ip: targetIP, 
                    eth: selectedDevice.eth || 'eth0',
                    lab_path: currentLabPath 
                })
            })
            .then(res => {
                if (!res.ok) {
                    return res.text().then(text => { throw new Error(`HTTP ${res.status}: ${text}`); });
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    log(`[PING] ${data.result}`, data.success ? '#7ED321' : '#FF6B6B');
                } else {
                    log(`[PING] Error: ${data.message}`, '#FF6B6B');
                }
            })
            .catch(err => {
                log(`[PING] Error: ${err.message}`, '#FF6B6B');
            });
        }
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
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
}

document.getElementById('exportBtn').addEventListener('click', async () => {
    const labName = document.getElementById('labName').value || 'my_lab';
    
    const result = await apiCall('/api/lab/export', {
        lab_name: labName,
        devices: devices.map(d => ({ name: d.name, type: d.type, eth: d.eth, ip: d.ip, gateway: d.gateway, config: d.config })),
        connections: connections
    });
    
    if (result.success) {
        currentLabPath = result.lab_path;
        log(`[EXPORT] Lab exported to: ${result.lab_path}`, '#4A90D9');
        log(`[INFO] ${devices.length} devices, ${connections.length} connections`, '#888');
    }
});

document.getElementById('startBtn').addEventListener('click', async () => {
    if (!currentLabPath) {
        const labName = document.getElementById('labName').value || 'my_lab';
        const result = await apiCall('/api/lab/export', {
            lab_name: labName,
            devices: devices.map(d => ({ name: d.name, type: d.type, eth: d.eth, ip: d.ip, gateway: d.gateway, config: d.config })),
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

document.getElementById('runCmdBtn').addEventListener('click', executeCommand);
document.getElementById('commandInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeCommand();
});

function executeCommand() {
    const input = document.getElementById('commandInput');
    const cmd = input.value.trim();
    if (!cmd) return;
    
    log(`[CMD] ${cmd}`, '#FFD700');
    input.value = '';
    
    const parts = cmd.toLowerCase().split(/\s+/);
    const command = parts[0];
    
    try {
        switch(command) {
            case 'add':
                handleAddCommand(parts);
                break;
            case 'connect':
            case 'conn':
                handleConnectCommand(parts);
                break;
            case 'ip':
                handleIPCommand(parts);
                break;
            case 'del':
            case 'delete':
                handleDeleteCommand(parts);
                break;
            case 'list':
                handleListCommand();
                break;
            case 'help':
                showCommandHelp();
                break;
            default:
                log(`[ERROR] Unknown command: ${command}. Type 'help' for available commands.`, '#FF6B6B');
        }
    } catch (err) {
        log(`[ERROR] ${err.message}`, '#FF6B6B');
    }
}

function handleAddCommand(parts) {
    if (parts.length < 3) {
        log('[ERROR] Usage: add router|switch|pc|hub|cloud NAME', '#FF6B6B');
        return;
    }
    const type = parts[1];
    const name = parts[2].toUpperCase();
    
    if (!DEVICE_TYPES[type]) {
        log(`[ERROR] Unknown device type: ${type}`, '#FF6B6B');
        return;
    }
    
    if (devices.find(d => d.name === name)) {
        log(`[ERROR] Device ${name} already exists`, '#FF6B6B');
        return;
    }
    
    const typeCount = parts[1];
    deviceCounter[type] = (deviceCounter[type] || 0) + 1;
    
    const newDevice = {
        name,
        type,
        x: 100 + (devices.length % 4) * 150,
        y: 100 + Math.floor(devices.length / 4) * 120,
        eth: 'eth0',
        ip: '',
        gateway: '',
        config: ''
    };
    
    devices.push(newDevice);
    updateDeviceSelect();
    draw();
    log(`[+] Added: ${name} (${type.toUpperCase()})`, DEVICE_TYPES[type].color);
}

function handleConnectCommand(parts) {
    if (parts.length < 3) {
        log('[ERROR] Usage: connect NAME1 NAME2 [cable_type]', '#FF6B6B');
        return;
    }
    
    const name1 = parts[1].toUpperCase();
    const name2 = parts[2].toUpperCase();
    const cableType = parts[3] || 'copper-straight';
    
    const dev1 = devices.find(d => d.name === name1);
    const dev2 = devices.find(d => d.name === name2);
    
    if (!dev1) {
        log(`[ERROR] Device ${name1} not found`, '#FF6B6B');
        return;
    }
    if (!dev2) {
        log(`[ERROR] Device ${name2} not found`, '#FF6B6B');
        return;
    }
    
    if (dev1 === dev2) {
        log('[ERROR] Cannot connect device to itself', '#FF6B6B');
        return;
    }
    
    const exists = connections.find(c => 
        (c.from === name1 && c.to === name2) || (c.from === name2 && c.to === name1)
    );
    if (exists) {
        log(`[ERROR] Connection ${name1} <-> ${name2} already exists`, '#FF6B6B');
        return;
    }
    
    if (!CABLE_TYPES[cableType]) {
        log(`[WARN] Unknown cable type: ${cableType}, using copper-straight`, '#F5A623');
    }
    
    connections.push({
        from: name1,
        to: name2,
        cableType: CABLE_TYPES[cableType] ? cableType : 'copper-straight',
        color: CABLE_TYPES[cableType]?.color || CABLE_TYPES['copper-straight'].color
    });
    
    updateConnectionsList();
    draw();
    log(`[LINK] ${name1} <-> ${name2} (${cableType})`, '#00FFFF');
}

function handleIPCommand(parts) {
    if (parts.length < 4) {
        log('[ERROR] Usage: ip NAME ETH IP [gateway]', '#FF6B6B');
        return;
    }
    
    const name = parts[1].toUpperCase();
    const eth = parts[2];
    const ip = parts[3];
    const gateway = parts[4] || '';
    
    const device = devices.find(d => d.name === name);
    if (!device) {
        log(`[ERROR] Device ${name} not found`, '#FF6B6B');
        return;
    }
    
    if (!['eth0', 'eth1', 'eth2', 'eth3'].includes(eth)) {
        log(`[ERROR] Invalid interface: ${eth}. Use eth0-eth3.`, '#FF6B6B');
        return;
    }
    
    device.eth = eth;
    device.ip = ip;
    device.gateway = gateway;
    
    updatePropertiesPanel();
    draw();
    log(`[IP] ${name} ${eth}:${ip}` + (gateway ? ` gateway:${gateway}` : ''), '#FFFF00');
}

function handleDeleteCommand(parts) {
    if (parts.length < 2) {
        log('[ERROR] Usage: del NAME', '#FF6B6B');
        return;
    }
    
    const name = parts[1].toUpperCase();
    const deviceIndex = devices.findIndex(d => d.name === name);
    
    if (deviceIndex === -1) {
        log(`[ERROR] Device ${name} not found`, '#FF6B6B');
        return;
    }
    
    connections = connections.filter(c => c.from !== name && c.to !== name);
    devices.splice(deviceIndex, 1);
    
    if (selectedDevice?.name === name) {
        selectedDevice = null;
    }
    
    updateDeviceSelect();
    updatePropertiesPanel();
    updateConnectionsList();
    draw();
    log(`[-] Deleted: ${name}`, '#D0021B');
}

function handleListCommand() {
    if (devices.length === 0) {
        log('[INFO] No devices in topology', '#888');
        return;
    }
    
    log(`[INFO] Devices (${devices.length}):`, '#888');
    devices.forEach(d => {
        const ipInfo = d.ip ? ` ${d.eth}:${d.ip}` : ' (no IP)';
        log(`  - ${d.name} (${d.type})${ipInfo}`, '#888');
    });
    
    log(`[INFO] Connections (${connections.length}):`, '#888');
    connections.forEach(c => {
        log(`  - ${c.from} <-> ${c.to}`, '#888');
    });
}

function showCommandHelp() {
    log('[HELP] Available commands:', '#00FFFF');
    log('  add router|switch|pc|hub|cloud NAME  - Add device', '#888');
    log('  connect NAME1 NAME2 [cable]          - Connect devices', '#888');
    log('  ip NAME eth0|eth1 IP [gateway]       - Set IP address', '#888');
    log('  del NAME                              - Delete device', '#888');
    log('  list                                  - Show topology', '#888');
    log('  help                                  - Show this help', '#888');
}

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
