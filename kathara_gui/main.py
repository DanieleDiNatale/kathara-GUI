import sys
import os
import subprocess
import threading

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGraphicsView, QGraphicsScene, 
                             QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QLabel, QPushButton,
                             QToolBar, QStatusBar, QListWidget, QLineEdit,
                             QTextEdit, QFileDialog, QMessageBox, QGroupBox, QFormLayout,
                             QDialog, QDialogButtonBox, QComboBox)
    from PyQt6.QtCore import Qt, QPointF, pyqtSignal
    from PyQt6.QtGui import QColor, QPen, QBrush, QAction, QPainter, QFont
    print("All imports OK")
except Exception as e:
    print(f"Import error: {e}")
    input("Press Enter...")
    sys.exit(1)

DEVICE_TYPES = {
    'router': {'color': '#4A90D9', 'label': 'ROUTER'},
    'switch': {'color': '#F5A623', 'label': 'SWITCH'},
    'pc': {'color': '#7ED321', 'label': 'PC'},
    'hub': {'color': '#D0021B', 'label': 'HUB'},
    'cloud': {'color': '#9013FE', 'label': 'CLOUD'},
}

CABLE_TYPES = {
    'copper-straight': {'label': 'Copper Straight', 'color': '#FF6B6B'},
    'copper-cross': {'label': 'Copper Cross', 'color': '#4ECDC4'},
    'fiber': {'label': 'Fiber', 'color': '#45B7D1'},
    'serial': {'label': 'Serial', 'color': '#DDA0DD'},
    'phone': {'label': 'Phone', 'color': '#FFEAA7'},
    'coaxial': {'label': 'Coaxial', 'color': '#795548'},
}

class DeviceItem(QGraphicsRectItem):
    def __init__(self, device_type, name, x, y):
        self.device_type = device_type
        self.name = name
        self.eth = "eth0"
        self.ip_address = ""
        self.gateway = ""
        
        super().__init__(-40, -30, 80, 60)
        self.setPos(x, y)
        
        self.setBrush(QBrush(QColor(DEVICE_TYPES[device_type]['color'])))
        self.setPen(QPen(QColor('white'), 3))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(DEVICE_TYPES[device_type]['label'])
        self.label.setDefaultTextColor(QColor('white'))
        self.label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.label.setTextWidth(80)
        self.label.setPos(-40, -40)
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        self.name_label = QGraphicsTextItem(self)
        self.name_label.setPlainText(name)
        self.name_label.setDefaultTextColor(QColor('white'))
        self.name_label.setFont(QFont("Arial", 9))
        self.name_label.setTextWidth(80)
        self.name_label.setPos(-40, 12)
        self.name_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        self.ip_label = QGraphicsTextItem(self)
        self.ip_label.setPlainText("")
        self.ip_label.setDefaultTextColor(QColor('#FFFF00'))
        self.ip_label.setFont(QFont("Arial", 8))
        self.ip_label.setTextWidth(80)
        self.ip_label.setPos(-40, 38)
        self.ip_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        self.connections = []
    
    def set_ip(self, eth, ip, gateway=""):
        self.eth = eth
        self.ip_address = ip
        self.gateway = gateway
        if ip:
            self.ip_label.setPlainText(f"{eth}:{ip}")
        else:
            self.ip_label.setPlainText("")

class ConnectionItem(QGraphicsLineItem):
    def __init__(self, start_device, end_device, cable_type='copper-straight'):
        super().__init__()
        self.start_device = start_device
        self.end_device = end_device
        self.cable_type = cable_type
        
        color = QColor(CABLE_TYPES[cable_type]['color'])
        self.setPen(QPen(color, 5))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.update_position()
    
    def update_position(self):
        start = self.start_device.scenePos() + QPointF(0, 30)
        end = self.end_device.scenePos() + QPointF(0, 30)
        self.setLine(start.x(), start.y(), end.x(), end.y())

class TopologyScene(QGraphicsScene):
    device_added = pyqtSignal(str, str, float, float)
    connection_created = pyqtSignal(object, object)
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.devices = {}
        self.connections = []
        self.connection_mode = False
        self.connection_start = None
        self.selected_cable_type = 'copper-straight'
        self.device_counter = {'router': 0, 'switch': 0, 'pc': 0, 'hub': 0, 'cloud': 0}
        
        self.setBackgroundBrush(QColor('#1a1a2e'))
        
        for i in range(-20, 20):
            self.addLine(i * 50, -1000, i * 50, 1000, QPen(QColor('#2a2a4e'), 1))
            self.addLine(-1000, i * 50, 1000, i * 50, QPen(QColor('#2a2a4e'), 1))
    
    def add_device(self, device_type, x, y):
        self.device_counter[device_type] += 1
        name = f"{device_type.upper()}{self.device_counter[device_type]}"
        
        if name in self.devices:
            return None
        
        device = DeviceItem(device_type, name, x, y)
        self.addItem(device)
        self.devices[name] = device
        
        self.device_added.emit(device_type, name, x, y)
        return device
    
    def remove_device(self, name):
        if name in self.devices:
            device = self.devices[name]
            for conn in list(device.connections):
                self.remove_connection(conn)
            self.removeItem(device)
            del self.devices[name]
    
    def add_connection(self, start_device, end_device):
        if start_device == end_device:
            return None
        for conn in start_device.connections:
            if conn.end_device == end_device:
                return None
            
        conn = ConnectionItem(start_device, end_device, self.selected_cable_type)
        self.addItem(conn)
        start_device.connections.append(conn)
        end_device.connections.append(conn)
        self.connections.append(conn)
        self.connection_created.emit(start_device, end_device)
        return conn
    
    def remove_connection(self, connection):
        if connection in connection.start_device.connections:
            connection.start_device.connections.remove(connection)
        if connection in connection.end_device.connections:
            connection.end_device.connections.remove(connection)
        if connection in self.connections:
            self.connections.remove(connection)
        self.removeItem(connection)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.scenePos(), None)
            if self.connection_mode and isinstance(item, DeviceItem):
                if self.connection_start is None:
                    self.connection_start = item
                    item.setBrush(QBrush(QColor('#FFD700')))
                else:
                    item.setBrush(QBrush(QColor(DEVICE_TYPES[item.device_type]['color'])))
                    self.add_connection(self.connection_start, item)
                    self.connection_start.setBrush(QBrush(QColor(DEVICE_TYPES[self.connection_start.device_type]['color'])))
                    self.connection_start = None
                    self.connection_mode = False
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        for conn in self.connections:
            conn.update_position()
        super().mouseMoveEvent(event)
    
    def generate_full_lab(self, lab_path):
        if not os.path.exists(lab_path):
            os.makedirs(lab_path)
        
        conf_lines = []
        network_id = 0
        
        processed = set()
        for conn in self.connections:
            pair = tuple(sorted([conn.start_device.name, conn.end_device.name]))
            if pair in processed:
                continue
            processed.add(pair)
            
            net_letter = chr(65 + network_id)
            conf_lines.append(f"{conn.start_device.name}[0]={net_letter}")
            conf_lines.append(f"{conn.end_device.name}[0]={net_letter}")
            network_id += 1
        
        with open(os.path.join(lab_path, 'lab.conf'), 'w') as f:
            f.write('\n'.join(conf_lines))
        
        with open(os.path.join(lab_path, 'topology.txt'), 'w') as f:
            f.write("=" * 50 + "\n")
            f.write("Kathara Network Topology\n")
            f.write("=" * 50 + "\n\n")
            f.write("CONNECTIONS:\n")
            for conn in self.connections:
                cable_info = CABLE_TYPES[conn.cable_type]
                f.write(f"  {conn.start_device.name} <--[{cable_info['label']}]--> {conn.end_device.name}\n")
            f.write("\n\nDEVICE CONFIGURATION:\n")
            for name, device in self.devices.items():
                if device.ip_address:
                    f.write(f"\n{name}:\n  IP: {device.ip_address}/24\n")
                    if device.gateway:
                        f.write(f"  Gateway: {device.gateway}\n")
        
        for name, device in self.devices.items():
            startup_file = os.path.join(lab_path, f"{name}.startup")
            with open(startup_file, 'w') as f:
                if device.ip_address:
                    f.write(f"ip addr add {device.ip_address}/24 dev eth0\n")
                if device.gateway:
                    f.write(f"ip route add default via {device.gateway}\n")
                if device.device_type == 'router':
                    f.write("sysctl -w net.ipv4.ip_forward=1\n")

class IPConfigDialog(QDialog):
    def __init__(self, device_name, current_ip="", current_gateway="", current_eth="eth0", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Configure - {device_name}")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel(f"<h3>Configure: {device_name}</h3>")
        layout.addWidget(info_label)
        
        form = QFormLayout()
        
        self.eth_combo = QComboBox()
        self.eth_combo.addItems(["eth0", "eth1", "eth2", "eth3"])
        self.eth_combo.setCurrentText(current_eth)
        form.addRow("Interface:", self.eth_combo)
        
        self.ip_edit = QLineEdit(current_ip)
        self.ip_edit.setPlaceholderText("192.168.1.10")
        form.addRow("IP Address:", self.ip_edit)
        
        self.gateway_edit = QLineEdit(current_gateway)
        self.gateway_edit.setPlaceholderText("192.168.1.254")
        form.addRow("Gateway:", self.gateway_edit)
        
        layout.addLayout(form)
        
        hint = QLabel("<i>Note: Each interface must be on a different network</i>")
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_values(self):
        return self.eth_combo.currentText(), self.ip_edit.text().strip(), self.gateway_edit.text().strip()

class ConsoleWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #0d0d0d; color: #00ff00; font-family: monospace; font-size: 11px; border: 2px solid #333;")
    
    def log(self, message, color="#00ff00"):
        self.append(f"<span style='color:{color}'>{message}</span>")
        sb = self.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kathara Network Designer")
        self.setGeometry(50, 50, 1500, 900)
        
        self.current_lab_path = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        self.scene = TopologyScene()
        self.scene.device_added.connect(self.on_device_added)
        self.scene.connection_created.connect(self.on_connection_created)
        
        self.canvas = QGraphicsView(self.scene)
        self.canvas.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.canvas.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        main_layout.addWidget(self.canvas, 4)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)
        
        self.setup_device_panel(right_layout)
        self.setup_connections_panel(right_layout)
        self.setup_console_panel(right_layout)
        
        main_layout.addWidget(right_panel, 1)
        
        self.statusBar().showMessage("Ready - Add devices and create connections")
        
    def setup_device_panel(self, parent):
        group = QGroupBox("DEVICE PROPERTIES")
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #444; padding: 10px; }")
        layout = QFormLayout()
        
        self.name_label = QLabel("-")
        self.type_label = QLabel("-")
        self.eth_label = QLabel("-")
        self.ip_label = QLabel("-")
        self.gateway_label = QLabel("-")
        
        layout.addRow("Name:", self.name_label)
        layout.addRow("Type:", self.type_label)
        layout.addRow("Interface:", self.eth_label)
        layout.addRow("IP:", self.ip_label)
        layout.addRow("Gateway:", self.gateway_label)
        
        self.config_ip_btn = QPushButton("Configure IP")
        self.config_ip_btn.setStyleSheet("background-color: #333; color: white; padding: 8px; border: none;")
        self.config_ip_btn.clicked.connect(self.configure_device_ip)
        self.config_ip_btn.setEnabled(False)
        layout.addRow("", self.config_ip_btn)
        
        group.setLayout(layout)
        parent.addWidget(group)
        
        cable_group = QGroupBox("CABLE TYPE")
        cable_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #FF6B6B; padding: 10px; }")
        cable_layout = QVBoxLayout()
        
        self.cable_combo = QComboBox()
        for ct, info in CABLE_TYPES.items():
            self.cable_combo.addItem(info['label'], ct)
        cable_layout.addWidget(self.cable_combo)
        cable_group.setLayout(cable_layout)
        parent.addWidget(cable_group)
        
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.cable_combo.currentIndexChanged.connect(self.on_cable_changed)
        
    def setup_connections_panel(self, parent):
        group = QGroupBox("CONNECTIONS")
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #555; padding: 10px; }")
        layout = QVBoxLayout()
        
        self.connections_list = QListWidget()
        self.connections_list.addItem("No connections")
        layout.addWidget(self.connections_list)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("background-color: #444; color: white; padding: 5px; border: none;")
        refresh_btn.clicked.connect(self.refresh_connections)
        layout.addWidget(refresh_btn)
        
        group.setLayout(layout)
        parent.addWidget(group)
        
    def setup_console_panel(self, parent):
        group = QGroupBox("CONSOLE")
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #9013FE; padding: 10px; }")
        layout = QVBoxLayout()
        
        self.console = ConsoleWidget()
        layout.addWidget(self.console)
        
        group.setLayout(layout)
        parent.addWidget(group)
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        new_action = QAction("New Lab", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_lab)
        file_menu.addAction(new_action)
        
        export_action = QAction("Export", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_to_kathara)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        lab_menu = menubar.addMenu("Lab")
        start_action = QAction("Start", self)
        start_action.setShortcut("F5")
        start_action.triggered.connect(self.start_lab)
        lab_menu.addAction(start_action)
        
        stop_action = QAction("Stop", self)
        stop_action.setShortcut("F6")
        stop_action.triggered.connect(self.stop_lab)
        lab_menu.addAction(stop_action)
        
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("background-color: #2d2d2d;")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        for device_type, info in DEVICE_TYPES.items():
            btn = QPushButton(info['label'])
            btn.setMinimumSize(70, 45)
            btn.setStyleSheet(f"background-color: {info['color']}; color: white; border: 2px solid #222; border-radius: 5px; font-weight: bold;")
            btn.clicked.connect(lambda dt=device_type: self.add_device(dt))
            toolbar.addWidget(btn)
        
        toolbar.addSeparator()
        
        self.connect_mode_btn = QPushButton("CONNECT")
        self.connect_mode_btn.setMinimumSize(80, 45)
        self.connect_mode_btn.setCheckable(True)
        self.connect_mode_btn.setStyleSheet("background-color: #FF6B6B; color: white; border: 2px solid #222; border-radius: 5px; font-weight: bold;")
        self.connect_mode_btn.clicked.connect(self.toggle_connection_mode)
        toolbar.addWidget(self.connect_mode_btn)
        
        delete_btn = QPushButton("DELETE")
        delete_btn.setMinimumSize(70, 45)
        delete_btn.setStyleSheet("background-color: #D0021B; color: white; border: 2px solid #222; border-radius: 5px; font-weight: bold;")
        delete_btn.clicked.connect(self.delete_selected)
        toolbar.addWidget(delete_btn)
        
        toolbar.addSeparator()
        
        new_btn = QPushButton("NEW")
        new_btn.setMinimumSize(60, 45)
        new_btn.setStyleSheet("background-color: #666; color: white; border: 2px solid #222; border-radius: 5px; font-weight: bold;")
        new_btn.clicked.connect(self.new_lab)
        toolbar.addWidget(new_btn)
        
        start_btn = QPushButton("START")
        start_btn.setMinimumSize(60, 45)
        start_btn.setStyleSheet("background-color: #7ED321; color: white; border: 2px solid #222; border-radius: 5px; font-weight: bold;")
        start_btn.clicked.connect(self.start_lab)
        toolbar.addWidget(start_btn)
        
        stop_btn = QPushButton("STOP")
        stop_btn.setMinimumSize(60, 45)
        stop_btn.setStyleSheet("background-color: #F5A623; color: white; border: 2px solid #222; border-radius: 5px; font-weight: bold;")
        stop_btn.clicked.connect(self.stop_lab)
        toolbar.addWidget(stop_btn)
    
    def add_device(self, device_type):
        try:
            x = 200 + (len(self.scene.devices) % 4) * 180
            y = 150 + (len(self.scene.devices) // 4) * 150
            device = self.scene.add_device(device_type, x, y)
            if device:
                self.console.log(f"[+] Added: {device.name}")
                self.refresh_connections()
        except Exception as e:
            print(f"Error adding device: {e}")
    
    def configure_device_ip(self):
        items = self.canvas.scene().selectedItems()
        if items and isinstance(items[0], DeviceItem):
            device = items[0]
            if device.device_type in ['hub', 'switch']:
                self.console.log(f"[INFO] {device.device_type.upper()} cannot have IP address", '#FF6B6B')
                return
            dialog = IPConfigDialog(device.name, device.ip_address, device.gateway, device.eth, self)
            if dialog.exec():
                eth, ip, gateway = dialog.get_values()
                device.set_ip(eth, ip, gateway)
                self.on_selection_changed()
                if ip:
                    self.console.log(f"[IP] {device.name}: {ip}")
    
    def on_device_added(self, device_type, name, x, y):
        pass
    
    def on_connection_created(self, start, end):
        cable_info = CABLE_TYPES[self.scene.selected_cable_type]
        self.console.log(f"[LINK] {start.name} <-> {end.name} ({cable_info['label']})")
        self.refresh_connections()
    
    def on_selection_changed(self):
        items = self.canvas.scene().selectedItems()
        if items and isinstance(items[0], DeviceItem):
            device = items[0]
            self.name_label.setText(device.name)
            self.type_label.setText(DEVICE_TYPES[device.device_type]['label'])
            
            can_have_ip = device.device_type in ['pc', 'router', 'cloud']
            
            if can_have_ip:
                self.eth_label.setText(device.eth)
                self.ip_label.setText(device.ip_address if device.ip_address else "-")
                self.gateway_label.setText(device.gateway if device.gateway else "-")
                self.config_ip_btn.setEnabled(True)
            else:
                self.eth_label.setText("-")
                self.ip_label.setText("-")
                self.gateway_label.setText("-")
                self.config_ip_btn.setEnabled(False)
        else:
            self.name_label.setText("-")
            self.type_label.setText("-")
            self.eth_label.setText("-")
            self.ip_label.setText("-")
            self.gateway_label.setText("-")
            self.config_ip_btn.setEnabled(False)
    
    def on_cable_changed(self):
        self.scene.selected_cable_type = self.cable_combo.currentData()
    
    def toggle_connection_mode(self):
        self.scene.connection_mode = self.connect_mode_btn.isChecked()
        if self.scene.connection_mode:
            self.statusBar().showMessage("Connect mode: Click two devices")
        else:
            self.statusBar().showMessage("Ready")
    
    def delete_selected(self):
        items = self.canvas.scene().selectedItems()
        for item in items:
            if isinstance(item, DeviceItem):
                self.console.log(f"[-] Deleted: {item.name}")
                self.scene.remove_device(item.name)
            elif isinstance(item, ConnectionItem):
                self.scene.remove_connection(item)
        self.refresh_connections()
    
    def refresh_connections(self):
        self.connections_list.clear()
        if not self.scene.connections:
            self.connections_list.addItem("No connections")
            return
        for conn in self.scene.connections:
            self.connections_list.addItem(f"{conn.start_device.name} <-> {conn.end_device.name}")
        self.connections_list.addItem(f"--- Total: {len(self.scene.connections)} ---")
    
    def new_lab(self):
        self.scene.devices.clear()
        self.scene.connections.clear()
        self.scene.clear()
        
        for i in range(-20, 20):
            self.scene.addLine(i * 50, -1000, i * 50, 1000, QPen(QColor('#2a2a4e'), 1))
            self.scene.addLine(-1000, i * 50, 1000, i * 50, QPen(QColor('#2a2a4e'), 1))
        
        self.scene.device_counter = {'router': 0, 'switch': 0, 'pc': 0, 'hub': 0, 'cloud': 0}
        self.current_lab_path = None
        self.console.log("[NEW] New lab created")
        self.refresh_connections()
    
    def export_to_kathara(self):
        if not self.current_lab_path:
            self.current_lab_path = QFileDialog.getExistingDirectory(self, "Select Lab Directory")
        if not self.current_lab_path:
            return
        
        self.scene.generate_full_lab(self.current_lab_path)
        self.console.log(f"[EXPORT] Lab exported to: {self.current_lab_path}")
        QMessageBox.information(self, "Export", f"Lab exported to:\n{self.current_lab_path}")
    
    def run_kathara_command(self, cmd, description):
        if not self.current_lab_path:
            QMessageBox.warning(self, "Warning", "Please export a lab first!")
            return
        
        self.console.log(f"[RUN] {description}...")
        
        def run():
            try:
                result = subprocess.run(cmd, shell=True, cwd=self.current_lab_path,
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.statusBar().showMessage(f"{description}: Done")
                else:
                    self.console.log(f"[ERROR] {result.stderr}", "#ff0000")
            except Exception as e:
                self.console.log(f"[ERROR] {str(e)}", "#ff0000")
        
        threading.Thread(target=run, daemon=True).start()
    
    def start_lab(self):
        if not self.current_lab_path:
            self.export_to_kathara()
        self.run_kathara_command("kathara lstart", "Starting Lab")
    
    def stop_lab(self):
        self.run_kathara_command("kathara lstop", "Stopping Lab")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor('#1a1a2e'))
    palette.setColor(palette.ColorRole.WindowText, QColor('white'))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
