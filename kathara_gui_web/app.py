from flask import Flask, render_template, request, jsonify
import subprocess
import os
import threading
import json

app = Flask(__name__)

LABS_DIR = os.path.join(os.path.dirname(__file__), 'labs')
os.makedirs(LABS_DIR, exist_ok=True)

device_counter = {'router': 0, 'switch': 0, 'pc': 0, 'hub': 0, 'cloud': 0}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/api/device/add', methods=['POST'])
def add_device():
    global device_counter
    data = request.json
    device_type = data.get('type')
    
    device_counter[device_type] += 1
    name = f"{device_type.upper()}{device_counter[device_type]}"
    
    return jsonify({'success': True, 'name': name})

@app.route('/api/lab/export', methods=['POST'])
def export_lab():
    data = request.json
    lab_name = data.get('lab_name', 'my_lab')
    devices = data.get('devices', [])
    connections = data.get('connections', [])
    
    lab_path = os.path.join(LABS_DIR, lab_name)
    os.makedirs(lab_path, exist_ok=True)
    
    networks = {}
    conf_lines = []
    topology_info = []
    
    for conn in connections:
        dev1, dev2 = conn['from'], conn['to']
        cable_type = conn.get('cableType', 'copper-straight')
        
        if dev2 not in networks:
            networks[dev2] = chr(65 + len(networks))
        net_id = networks.get(dev2, 'A')
        conf_lines.append(f"{dev1}[0]={net_id}")
        conf_lines.append(f"{dev2}[0]={net_id}")
        
        topology_info.append(f"{dev1} -- {cable_type} --> {dev2}")
    
    with open(os.path.join(lab_path, 'lab.conf'), 'w') as f:
        f.write('\n'.join(conf_lines))
    
    with open(os.path.join(lab_path, 'topology.txt'), 'w') as f:
        f.write("Kathara Network Topology\n")
        f.write("=" * 40 + "\n\n")
        f.write("Connections:\n")
        for line in topology_info:
            f.write(f"  {line}\n")
        f.write("\nCable Types:\n")
        f.write("  copper-straight: Copper Straight-Through\n")
        f.write("  copper-cross: Copper Cross-Over\n")
        f.write("  fiber: Fiber\n")
        f.write("  serial: Serial\n")
        f.write("  phone: Phone (RJ11)\n")
        f.write("  coaxial: Coaxial\n")
    
    for device in devices:
        name = device['name']
        config = device.get('config', '')
        startup_file = os.path.join(lab_path, f"{name}.startup")
        
        if device['type'] == 'pc':
            if not config:
                config = "# PC Configuration\nip addr add 10.0.0.1/24 dev eth0\nip route add default via 10.0.0.254"
        elif device['type'] == 'router':
            if not config:
                config = "# Router Configuration\nsysctl -w net.ipv4.ip_forward=1"
        
        with open(startup_file, 'w') as f:
            f.write(config)
    
    return jsonify({'success': True, 'lab_path': lab_path})

@app.route('/api/lab/start', methods=['POST'])
def start_lab():
    data = request.json
    lab_path = data.get('lab_path')
    
    if not lab_path or not os.path.exists(lab_path):
        return jsonify({'success': False, 'error': 'Lab path not found'}), 400
    
    def run():
        subprocess.run(['kathara', 'lstart'], cwd=lab_path, capture_output=True)
    
    threading.Thread(target=run, daemon=True).start()
    return jsonify({'success': True, 'message': 'Lab starting...'})

@app.route('/api/lab/stop', methods=['POST'])
def stop_lab():
    data = request.json
    lab_path = data.get('lab_path')
    
    if not lab_path:
        return jsonify({'success': False, 'error': 'Lab path required'}), 400
    
    def run():
        subprocess.run(['kathara', 'lstop'], cwd=lab_path, capture_output=True)
    
    threading.Thread(target=run, daemon=True).start()
    return jsonify({'success': True, 'message': 'Lab stopping...'})

@app.route('/ping', methods=['POST'])
def ping_device():
    data = request.json
    device_name = data.get('device_name')
    target_ip = data.get('target_ip')
    eth = data.get('eth', 'eth0')
    
    if not device_name or not target_ip:
        return jsonify({'success': False, 'message': 'Device name and target IP required'}), 400
    
    def run_ping():
        result = subprocess.run(
            ['kathara', 'connect', '-d', '.', '-c', device_name, '--', 'ping', '-c', '4', '-I', eth, target_ip],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    
    try:
        output = run_ping()
        return jsonify({'success': True, 'result': output})
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Ping timeout'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/lab/list', methods=['POST'])
def list_devices():
    data = request.json
    lab_path = data.get('lab_path')
    
    if not lab_path:
        return jsonify({'success': False, 'error': 'Lab path required'}), 400
    
    try:
        result = subprocess.run(['kathara', 'list'], cwd=lab_path, 
                              capture_output=True, text=True, timeout=10)
        return jsonify({'success': True, 'output': result.stdout})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/connect', methods=['POST'])
def connect_device():
    data = request.json
    lab_path = data.get('lab_path')
    device_name = data.get('device_name')
    
    if not lab_path or not device_name:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
    
    threading.Thread(target=lambda: subprocess.run(
        ['kathara', 'connect', '-d', lab_path, '-n', device_name],
        cwd=lab_path
    ), daemon=True).start()
    
    return jsonify({'success': True, 'message': f'Connecting to {device_name}...'})

@app.route('/api/labs', methods=['GET'])
def get_labs():
    labs = [d for d in os.listdir(LABS_DIR) if os.path.isdir(os.path.join(LABS_DIR, d))]
    return jsonify({'labs': labs})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
