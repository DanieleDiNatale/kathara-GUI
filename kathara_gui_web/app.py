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
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    lab_name = data.get('lab_name', 'my_lab')
    devices = data.get('devices', [])
    connections = data.get('connections', [])
    
    lab_path = os.path.join(LABS_DIR, lab_name)
    os.makedirs(lab_path, exist_ok=True)
    
    conf_lines = []
    topology_info = []
    
    device_interfaces = {}
    
    if connections:
        processed = set()
        for conn in connections:
            dev1, dev2 = conn['from'], conn['to']
            pair = tuple(sorted([dev1, dev2]))
            if pair in processed:
                continue
            processed.add(pair)
            
            cable_type = conn.get('cableType', 'copper-straight')
            
            net_letter = chr(65 + len(processed) - 1)
            
            if dev1 not in device_interfaces:
                device_interfaces[dev1] = {}
            if dev2 not in device_interfaces:
                device_interfaces[dev2] = {}
            
            eth1 = device_interfaces[dev1].get('next_eth', 0)
            eth2 = device_interfaces[dev2].get('next_eth', 0)
            
            conf_lines.append(f"{dev1}[{eth1}]={net_letter}")
            conf_lines.append(f"{dev2}[{eth2}]={net_letter}")
            
            device_interfaces[dev1]['next_eth'] = eth1 + 1
            device_interfaces[dev2]['next_eth'] = eth2 + 1
            
            topology_info.append(f"{dev1} -- {cable_type} --> {dev2}")
    
    if not conf_lines:
        return jsonify({'success': False, 'error': 'No connections! Connect devices before exporting.'}), 400
    
    lab_conf_path = os.path.join(lab_path, 'lab.conf')
    content = '\n'.join(conf_lines) + '\n'
    with open(lab_conf_path, 'w', newline='') as f:
        f.write(content)
    
    with open(lab_conf_path, 'rb') as rf:
        debug_content = rf.read()
    print(f"[DEBUG] lab.conf: {debug_content!r}")
    
    with open(os.path.join(lab_path, 'topology.txt'), 'w', encoding='utf-8') as f:
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
        device_type = device.get('type', 'pc')
        ip = device.get('ip', '')
        eth = device.get('eth', 'eth0')
        gateway = device.get('gateway', '')
        
        startup_lines = []
        
        if ip and device_type in ['pc', 'router', 'cloud']:
            startup_lines.append(f"ip addr add {ip}/24 dev {eth}")
            
            if gateway:
                startup_lines.append(f"ip route add default via {gateway}")
        
        if device_type == 'router':
            startup_lines.append("sysctl -w net.ipv4.ip_forward=1")
        
        config = '\n'.join(startup_lines) if startup_lines else "# No configuration"
        
        startup_file = os.path.join(lab_path, f"{name}.startup")
        with open(startup_file, 'wb') as f:
            f.write(config.encode('utf-8'))
    
    return jsonify({'success': True, 'lab_path': lab_path})

@app.route('/api/lab/start', methods=['POST'])
def start_lab():
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
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
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    lab_path = data.get('lab_path')
    
    if not lab_path:
        return jsonify({'success': False, 'error': 'Lab path required'}), 400
    
    def run():
        subprocess.run(['kathara', 'lstop'], cwd=lab_path, capture_output=True)
    
    threading.Thread(target=run, daemon=True).start()
    return jsonify({'success': True, 'message': 'Lab stopping...'})

@app.route('/api/ping', methods=['POST'])
def ping_device():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        device_name = data.get('device_name')
        target_ip = data.get('target_ip')
        lab_path = data.get('lab_path')
        devices = data.get('devices', [])
        connections = data.get('connections', [])
        
        if not device_name or not target_ip:
            return jsonify({'success': False, 'message': 'Device name and target IP required'}), 400
        
        if not lab_path or not os.path.exists(lab_path):
            return jsonify({'success': False, 'message': f'Lab not found: {lab_path}'}), 400
        
        conf_lines = []
        device_interfaces = {}
        
        if connections:
            processed = set()
            for conn in connections:
                dev1, dev2 = conn['from'], conn['to']
                pair = tuple(sorted([dev1, dev2]))
                if pair in processed:
                    continue
                processed.add(pair)
                
                if dev1 not in device_interfaces:
                    device_interfaces[dev1] = 0
                if dev2 not in device_interfaces:
                    device_interfaces[dev2] = 0
                
                net_letter = chr(65 + len(processed) - 1)
                eth1 = device_interfaces[dev1]
                eth2 = device_interfaces[dev2]
                
                conf_lines.append(f"{dev1}[{eth1}]={net_letter}")
                conf_lines.append(f"{dev2}[{eth2}]={net_letter}")
                
                device_interfaces[dev1] = eth1 + 1
                device_interfaces[dev2] = eth2 + 1
        
        lab_conf_path = os.path.join(lab_path, 'lab.conf')
        content = '\n'.join(conf_lines) + '\n'
        with open(lab_conf_path, 'w', newline='') as f:
            f.write(content)
        
        for device in devices:
            name = device['name']
            device_type = device.get('type', 'pc')
            ip = device.get('ip', '')
            eth = device.get('eth', 'eth0')
            gateway = device.get('gateway', '')
            
            startup_lines = []
            
            if ip and device_type in ['pc', 'router', 'cloud']:
                startup_lines.append(f"ip addr add {ip}/24 dev {eth}")
                
                if gateway:
                    startup_lines.append(f"ip route add default via {gateway}")
            
            if device_type == 'router':
                startup_lines.append("sysctl -w net.ipv4.ip_forward=1")
            
            config = '\n'.join(startup_lines) if startup_lines else "# No configuration"
            
            startup_file = os.path.join(lab_path, f"{name}.startup")
            with open(startup_file, 'wb') as sf:
                sf.write(config.encode('utf-8'))
        
        import time
        result_container = [""]
        
        def run_ping():
            abs_lab_path = os.path.abspath(lab_path)
            
            lab_conf_file = os.path.join(abs_lab_path, 'lab.conf')
            with open(lab_conf_file, 'r') as f:
                conf_content = f.read()
            result_container[0] += f"[DEBUG] lab.conf content:\n{conf_content}\n"
            
            start_result = subprocess.run(
                ['kathara', 'lstart', '-d', abs_lab_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            result_container[0] += f"[LSTART] stdout: {start_result.stdout}\n"
            result_container[0] += f"[LSTART] stderr: {start_result.stderr}\n"
            result_container[0] += f"[LSTART] returncode: {start_result.returncode}\n"
            
            time.sleep(5)
            
            list_result = subprocess.run(['kathara', 'list'], capture_output=True, text=True)
            result_container[0] += f"[LIST] devices: {list_result.stdout}\n"
            
            time.sleep(8)
            
            result = subprocess.run(
                ['kathara', 'exec', '-d', abs_lab_path, device_name, '--', 'ping', '-c', '4', target_ip],
                capture_output=True,
                text=True,
                timeout=30
            )
            result_container[0] += result.stdout + result.stderr
        
        thread = threading.Thread(target=run_ping)
        thread.start()
        thread.join()
        
        output = result_container[0] if result_container[0] else "No output"
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
