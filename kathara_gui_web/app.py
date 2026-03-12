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
    name = f"{device_type.lower()}{device_counter[device_type]}"
    
    return jsonify({'success': True, 'name': name})

@app.route('/api/lab/export', methods=['POST'])
def export_lab():
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    lab_name = data.get('lab_name', 'my_lab')
    devices = data.get('devices', [])
    connections = data.get('connections', [])
    enable_wireshark = data.get('enable_wireshark', False)
    wireshark_networks = data.get('wireshark_networks', ['A'])
    
    lab_path = os.path.join(LABS_DIR, lab_name)
    os.makedirs(lab_path, exist_ok=True)
    
    conf_lines = []
    topology_info = []
    
    device_interfaces = {}
    
    if connections:
        processed = set()
        device_interfaces = {}
        
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
            
            device_interfaces[dev1][eth1] = net_letter
            device_interfaces[dev2][eth2] = net_letter
            
            dev1_mac = ''
            dev2_mac = ''
            for d in devices:
                if d.get('name') == dev1 and d.get('mac'):
                    dev1_mac = '/' + d.get('mac')
                if d.get('name') == dev2 and d.get('mac'):
                    dev2_mac = '/' + d.get('mac')
            
            conf_lines.append(f"{dev1}[{eth1}]=\"{net_letter}{dev1_mac}\"")
            conf_lines.append(f"{dev2}[{eth2}]=\"{net_letter}{dev2_mac}\"")
            
            device_interfaces[dev1]['next_eth'] = eth1 + 1
            device_interfaces[dev2]['next_eth'] = eth2 + 1
            
            topology_info.append(f"{dev1} -- {cable_type} --> {dev2}")
    
    if not conf_lines:
        return jsonify({'success': False, 'error': 'No connections! Connect devices before exporting.'}), 400
    
    conf_lines.insert(0, f'LAB_DESCRIPTION="Kathara Network Lab - {lab_name}"')
    conf_lines.insert(1, 'LAB_VERSION=1.0')
    conf_lines.insert(2, 'LAB_AUTHOR="Kathara GUI"')
    conf_lines.insert(3, '')
    
    for device in devices:
        name = device.get('name', '')
        device_type = device.get('type', 'pc')
        
        if device_type == 'pc':
            conf_lines.append(f'{name}[image]="kathara/base"')
        
        ip_version = device.get('ip_version', '4')
        if ip_version == '6':
            conf_lines.append(f'{name}[ipv6]="true"')
            sysctl_val = device.get('sysctl', '')
            if sysctl_val:
                conf_lines.append(f'{name}[sysctl]="{sysctl_val}"')
            else:
                conf_lines.append(f'{name}[sysctl]="net.ipv6.conf.eth0.accept_ra=2"')
        else:
            conf_lines.append(f'{name}[ipv6]="false"')
    
    if enable_wireshark:
        ws_index = 0
        for net in wireshark_networks:
            conf_lines.append(f'wireshark[{ws_index}]="{net}"')
            ws_index += 1
    
    lab_conf_path = os.path.join(lab_path, 'lab.conf')
    content = '\r\n'.join(conf_lines) + '\r\n'
    with open(lab_conf_path, 'wb') as f:
        f.write(content.encode('utf-8'))
    
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
    
    network_ips = {
        'A': '10.0.0',
        'B': '192.168.1',
        'C': '192.168.2',
        'D': '192.168.3',
        'E': '192.168.4',
        'F': '192.168.5',
        'G': '192.168.6',
        'H': '192.168.7',
    }
    
    router_networks = {}
    for device in devices:
        if device.get('type') == 'router' and device['name'] in device_interfaces:
            for eth_idx, net_letter in device_interfaces[device['name']].items():
                if isinstance(eth_idx, int):
                    if net_letter not in router_networks:
                        router_networks[net_letter] = []
                    router_networks[net_letter].append(device['name'])
    
    network_router_index = {net: 0 for net in router_networks}
    
    for device in devices:
        name = device['name']
        device_type = device.get('type', 'pc')
        ip = device.get('ip', '')
        eth = device.get('eth', 'eth0')
        gateway = device.get('gateway', '')
        
        startup_lines = []
        
        if device_type == 'router':
            if name in device_interfaces:
                eth_indices = [k for k in device_interfaces[name].keys() if isinstance(k, int)]
                for eth_idx in sorted(eth_indices):
                    net_letter = device_interfaces[name][eth_idx]
                    net_ip = network_ips.get(net_letter, f'192.168.{(ord(net_letter) - 65 + 1)}')
                    
                    routers_on_net = router_networks.get(net_letter, [])
                    if len(routers_on_net) > 1:
                        router_idx = network_router_index[net_letter]
                        network_router_index[net_letter] += 1
                        router_ip = f"{net_ip}.{1 + router_idx}"
                    else:
                        router_ip = f"{net_ip}.254"
                    
                    startup_lines.append(f"ip link set eth{eth_idx} up")
                    startup_lines.append(f"ip addr add {router_ip}/24 dev eth{eth_idx}")
            
            my_net_letters = [device_interfaces[name][k] for k in device_interfaces[name].keys() if isinstance(k, int)]
            for net_letter in router_networks.keys():
                if net_letter not in my_net_letters:
                    for next_hop_router in router_networks[net_letter]:
                        if next_hop_router != name and next_hop_router in device_interfaces:
                            for eth_idx, connected_net in device_interfaces[next_hop_router].items():
                                if isinstance(eth_idx, int) and connected_net in my_net_letters:
                                    other_net_ip = network_ips.get(net_letter, f'192.168.{(ord(net_letter) - 65 + 1)}')
                                    routers_on_net = router_networks.get(connected_net, [])
                                    if len(routers_on_net) > 1:
                                        idx = network_router_index[connected_net]
                                        hop_ip = f"{network_ips.get(connected_net, f'192.168.{(ord(connected_net) - 65 + 1)}')}.{1 + idx}"
                                    else:
                                        hop_ip = f"{network_ips.get(connected_net, f'192.168.{(ord(connected_net) - 65 + 1)}')}.254"
                                    startup_lines.append(f"ip route add {other_net_ip}.0/24 via {hop_ip}")
                                    break
                            break
            
            startup_lines.append("sysctl -w net.ipv4.ip_forward=1")
        else:
            if ip and device_type in ['pc', 'cloud']:
                if '/' in ip:
                    startup_lines.append(f"ip addr add {ip} dev {eth}")
                else:
                    startup_lines.append(f"ip addr add {ip}/24 dev {eth}")
                
                if gateway:
                    startup_lines.append(f"ip route add default via {gateway}")
        
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
                    device_interfaces[dev1] = {}
                if dev2 not in device_interfaces:
                    device_interfaces[dev2] = {}
                
                net_letter = chr(65 + len(processed) - 1)
                eth1 = device_interfaces[dev1].get('next_eth', 0)
                eth2 = device_interfaces[dev2].get('next_eth', 0)
                
                device_interfaces[dev1][eth1] = net_letter
                device_interfaces[dev2][eth2] = net_letter
                
                conf_lines.append(f"{dev1}[{eth1}]=\"{net_letter}\"")
                conf_lines.append(f"{dev2}[{eth2}]=\"{net_letter}\"")
                
                device_interfaces[dev1]['next_eth'] = eth1 + 1
                device_interfaces[dev2]['next_eth'] = eth2 + 1
        
        lab_conf_path = os.path.join(lab_path, 'lab.conf')
        content = '\r\n'.join(conf_lines) + '\r\n'
        with open(lab_conf_path, 'wb') as f:
            f.write(content.encode('utf-8'))
        
        network_ips = {
            'A': '10.0.0',
            'B': '192.168.1',
            'C': '192.168.2',
            'D': '192.168.3',
            'E': '192.168.4',
            'F': '192.168.5',
            'G': '192.168.6',
            'H': '192.168.7',
        }
        
        router_networks = {}
        for device in devices:
            if device.get('type') == 'router' and device['name'] in device_interfaces:
                for eth_idx, net_letter in device_interfaces[device['name']].items():
                    if isinstance(eth_idx, int):
                        if net_letter not in router_networks:
                            router_networks[net_letter] = []
                        router_networks[net_letter].append(device['name'])
        
        network_router_index = {net: 0 for net in router_networks}
        
        for device in devices:
            name = device['name']
            device_type = device.get('type', 'pc')
            ip = device.get('ip', '')
            eth = device.get('eth', 'eth0')
            gateway = device.get('gateway', '')
            
            startup_lines = []
            
            if device_type == 'router':
                if name in device_interfaces:
                    eth_indices = [k for k in device_interfaces[name].keys() if isinstance(k, int)]
                    for eth_idx in sorted(eth_indices):
                        net_letter = device_interfaces[name][eth_idx]
                        net_ip = network_ips.get(net_letter, f'192.168.{(ord(net_letter) - 65 + 1)}')
                        
                        routers_on_net = router_networks.get(net_letter, [])
                        if len(routers_on_net) > 1:
                            router_idx = network_router_index[net_letter]
                            network_router_index[net_letter] += 1
                            router_ip = f"{net_ip}.{1 + router_idx}"
                        else:
                            router_ip = f"{net_ip}.254"
                        
                        startup_lines.append(f"ip link set eth{eth_idx} up")
                        startup_lines.append(f"ip addr add {router_ip}/24 dev eth{eth_idx}")
                
                my_net_letters = [device_interfaces[name][k] for k in device_interfaces[name].keys() if isinstance(k, int)]
                for net_letter in router_networks.keys():
                    if net_letter not in my_net_letters:
                        for next_hop_router in router_networks[net_letter]:
                            if next_hop_router != name and next_hop_router in device_interfaces:
                                for eth_idx, connected_net in device_interfaces[next_hop_router].items():
                                    if isinstance(eth_idx, int) and connected_net in my_net_letters:
                                        other_net_ip = network_ips.get(net_letter, f'192.168.{(ord(net_letter) - 65 + 1)}')
                                        routers_on_net = router_networks.get(connected_net, [])
                                        if len(routers_on_net) > 1:
                                            idx = network_router_index[connected_net]
                                            hop_ip = f"{network_ips.get(connected_net, f'192.168.{(ord(connected_net) - 65 + 1)}')}.{1 + idx}"
                                        else:
                                            hop_ip = f"{network_ips.get(connected_net, f'192.168.{(ord(connected_net) - 65 + 1)}')}.254"
                                        startup_lines.append(f"ip route add {other_net_ip}.0/24 via {hop_ip}")
                                        break
                                break
                
                startup_lines.append("sysctl -w net.ipv4.ip_forward=1")
            else:
                if ip and device_type in ['pc', 'cloud']:
                    if '/' in ip:
                        startup_lines.append(f"ip addr add {ip} dev {eth}")
                    else:
                        startup_lines.append(f"ip addr add {ip}/24 dev {eth}")
                    
                    if gateway:
                        startup_lines.append(f"ip route add default via {gateway}")
            
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

@app.route('/api/devices/list', methods=['GET'])
def list_devices_simple():
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=kathara', '--format', '{{.Names}}'],
            capture_output=True, text=True, timeout=10
        )
        devices = []
        seen = set()
        for full_name in result.stdout.strip().split('\n'):
            full_name = full_name.strip()
            if full_name:
                parts = full_name.split('_')
                if len(parts) >= 3:
                    device_name = parts[2]
                    if device_name not in seen:
                        seen.add(device_name)
                        devices.append({'name': device_name, 'status': 'running'})
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/devices/list_detailed', methods=['GET'])
def list_devices_detailed():
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=kathara', '--format', '{{.Names}}\t{{.Status}}'],
            capture_output=True, text=True, timeout=10
        )
        devices = []
        seen = set()
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 1:
                full_name = parts[0]
                status = parts[1] if len(parts) > 1 else 'unknown'
                name_parts = full_name.split('_')
                if len(name_parts) >= 3:
                    device_name = name_parts[2]
                    if device_name not in seen:
                        seen.add(device_name)
                        devices.append({
                            'name': device_name, 
                            'status': 'running',
                            'docker_status': status
                        })
        
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wireshark/open', methods=['POST'])
def open_wireshark():
    try:
        import platform
        system = platform.system()
        
        if system == 'Windows':
            subprocess.Popen(['wireshark.exe'], shell=True)
        elif system == 'Darwin':
            subprocess.Popen(['open', '-a', 'Wireshark'])
        else:
            subprocess.Popen(['wireshark'])
        
        return jsonify({'success': True, 'message': 'Wireshark opened'})
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'Wireshark not found. Please install Wireshark on your PC.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wireshark/interfaces', methods=['GET'])
def get_wireshark_interfaces():
    try:
        result = subprocess.run(
            ['docker', 'network', 'ls', '--filter', 'name=kathara', '--format', '{{.Name}}'],
            capture_output=True, text=True, timeout=10
        )
        interfaces = []
        for net in result.stdout.strip().split('\n'):
            if net:
                parts = net.split('_')
                if len(parts) >= 3:
                    net_letter = parts[2]
                    network_ips = {'A': '10.0.0.x', 'B': '192.168.1.x', 'C': '192.168.2.x', 
                                   'D': '192.168.3.x', 'E': '192.168.4.x', 'F': '192.168.5.x',
                                   'G': '192.168.6.x', 'H': '192.168.7.x'}
                    interfaces.append({
                        'network': net_letter,
                        'ip_range': network_ips.get(net_letter, 'unknown'),
                        'docker_net': net
                    })
        return jsonify({'success': True, 'interfaces': interfaces})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
