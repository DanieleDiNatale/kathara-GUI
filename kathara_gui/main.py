import sys
import os
import subprocess
import threading
import math

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGraphicsView, QGraphicsScene, 
                             QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QGraphicsPathItem,
                             QLabel, QPushButton, QToolBar, QStatusBar, QListWidget, QLineEdit,
                             QTextEdit, QFileDialog, QMessageBox, QGroupBox, QFormLayout,
                             QDialog, QDialogButtonBox, QComboBox, QInputDialog)
    from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
    from PyQt6.QtGui import (QColor, QPen, QBrush, QAction, QPainter, QFont, 
                           QPainterPath, QPixmap, QTransform)
    print("All imports OK")
except Exception as e:
    print(f"Import error: {e}")
    input("Press Enter...")
    sys.exit(1)

DEVICE_TYPES = {
    'router': {'color': '#00BFFF', 'label': 'ROUTER'},
    'switch': {'color': '#F5A623', 'label': 'SWITCH'},
    'pc': {'color': '#7ED321', 'label': 'PC'},
    'hub': {'color': '#D0021B', 'label': 'HUB'},
    'cloud': {'color': '#9B59B6', 'label': 'CLOUD'},
}

CABLE_TYPES = {
    'copper-straight': {'label': 'Copper Straight', 'color': '#FF6B6B'},
    'copper-cross': {'label': 'Copper Cross', 'color': '#4ECDC4'},
    'fiber': {'label': 'Fiber', 'color': '#45B7D1'},
    'serial': {'label': 'Serial', 'color': '#DDA0DD'},
    'phone': {'label': 'Phone', 'color': '#FFEAA7'},
    'coaxial': {'label': 'Coaxial', 'color': '#795548'},
}

DEVICE_WIDTH = 80
DEVICE_HEIGHT = 60

class DeviceItem(QGraphicsRectItem):
    def __init__(self, device_type, name, x, y):
        self.device_type = device_type
        self.name = name
        self.eth = "eth0"
        self.ip_address = ""
        self.gateway = ""
        
        super().__init__(0, 0, DEVICE_WIDTH, DEVICE_HEIGHT)
        self.setPos(x, y)
        
        self.setBrush(QBrush(Qt.GlobalColor.transparent))
        self.setPen(QPen(Qt.GlobalColor.transparent))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(DEVICE_TYPES[device_type]['label'])
        self.label.setDefaultTextColor(QColor('white'))
        self.label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.label.setTextWidth(DEVICE_WIDTH)
        self.label.setPos((DEVICE_WIDTH - self.label.textWidth()) / 2, -18)
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        
        self.name_label = QGraphicsTextItem(self)
        self.name_label.setPlainText(name)
        self.name_label.setDefaultTextColor(QColor('white'))
        self.name_label.setFont(QFont("Arial", 9))
        self.name_label.setTextWidth(DEVICE_WIDTH)
        self.name_label.setPos((DEVICE_WIDTH - self.name_label.textWidth()) / 2, DEVICE_HEIGHT + 4)
        self.name_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.name_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        
        self.ip_label = QGraphicsTextItem(self)
        self.ip_label.setPlainText("")
        self.ip_label.setDefaultTextColor(QColor('#FFFF00'))
        self.ip_label.setFont(QFont("Arial", 8))
        self.ip_label.setTextWidth(DEVICE_WIDTH)
        self.ip_label.setPos((DEVICE_WIDTH - self.ip_label.textWidth()) / 2, DEVICE_HEIGHT + 16)
        self.ip_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.ip_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        
        self.connections = []
        self.connection_highlight = False
    
    def boundingRect(self):
        return QRectF(0, -20, DEVICE_WIDTH, DEVICE_HEIGHT + 40)
    
    def paint(self, painter, option, widget=None):
        color = DEVICE_TYPES[self.device_type]['color']
        is_selected = self.isSelected() or self.connection_highlight
        
        offset_y = -20
        h_offset = DEVICE_HEIGHT + 20
        
        if self.device_type == 'pc':
            self._draw_pc(painter, color, is_selected, offset_y)
        elif self.device_type == 'router':
            self._draw_router(painter, color, is_selected, offset_y)
        elif self.device_type == 'switch':
            self._draw_switch(painter, color, is_selected, offset_y)
        elif self.device_type == 'hub':
            self._draw_hub(painter, color, is_selected, offset_y)
        elif self.device_type == 'cloud':
            self._draw_cloud(painter, color, is_selected, offset_y)
    
    def _draw_pc(self, painter, color, is_selected, offset_y=0):
        x, y, w, h = 0, offset_y, DEVICE_WIDTH, DEVICE_HEIGHT
        
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color) if not is_selected else QColor('#FFD700'), 3 if is_selected else 0))
        painter.drawRect(x + 10, y + 8, 60, 40)
        
        painter.setBrush(QBrush(QColor('#1a1a2e')))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawRect(x + 15, y + 12, 50, 30)
        
        painter.setBrush(QBrush(QColor('#00ff00')))
        painter.drawRect(x + 55, y + 30, 6, 6)
        
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color) if not is_selected else QColor('#FFD700'), 3 if is_selected else 0))
        painter.drawRect(x + 25, y + 48, 30, 8)
        
        painter.setPen(QPen(QColor('#222'), 2))
        painter.drawLine(x + 30, y + 56, x + 30, y + 62)
        painter.drawLine(x + 30, y + 62, x + 20, y + 62)
        painter.drawLine(x + 50, y + 56, x + 50, y + 62)
        painter.drawLine(x + 50, y + 62, x + 60, y + 62)
    
    def _draw_router(self, painter, color, is_selected, offset_y=0):
        x, y, w, h = 0, offset_y, DEVICE_WIDTH, DEVICE_HEIGHT
        cx, cy = x + w/2, y + h/2
        
        painter.setBrush(QBrush(QColor('#333333')))
        painter.setPen(QPen(QColor('#333333') if not is_selected else QColor('#FFD700'), 3 if is_selected else 0))
        painter.drawRect(x + 15, y + 15, 50, 30)
        
        painter.setBrush(QBrush(QColor('#00BFFF')))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawRect(x + 18, y + 18, 44, 24)
        
        painter.setBrush(QBrush(QColor('#1a1a2e')))
        painter.drawEllipse(int(cx) - 8, int(cy) - 8, 16, 16)
        
        painter.setBrush(QBrush(QColor('#00FF00')))
        painter.drawEllipse(int(cx) - 4, int(cy) - 4, 8, 8)
        
        painter.setPen(QPen(QColor('#00BFFF'), 2))
        painter.drawArc(int(cx) - 6, int(y + 10) - 6, 12, 12, 0, 180 * 16)
        painter.drawArc(int(cx) - 10, int(y + 5) - 10, 20, 20, 0, 180 * 16)
        painter.drawArc(int(cx) - 14, int(y) - 14, 28, 28, 0, 180 * 16)
    
    def _draw_switch(self, painter, color, is_selected, offset_y=0):
        x, y, w, h = 0, offset_y, DEVICE_WIDTH, DEVICE_HEIGHT
        
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color) if not is_selected else QColor('#FFD700'), 3 if is_selected else 0))
        painter.drawRect(x + 5, y + 15, 70, 35)
        
        painter.setBrush(QBrush(QColor('white')))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        for i in range(4):
            px = x + 15 + i * 16
            painter.drawRect(px, y + 28, 10, 8)
        
        painter.setBrush(QBrush(QColor('#00ff00')))
        for i in range(4):
            px = x + 17 + i * 16
            painter.drawRect(px, y + 30, 6, 4)
        
        painter.setBrush(QBrush(QColor('#333')))
        painter.drawRect(x + 60, y + 22, 10, 6)
    
    def _draw_hub(self, painter, color, is_selected, offset_y=0):
        x, y, w, h = 0, offset_y, DEVICE_WIDTH, DEVICE_HEIGHT
        cx, cy = x + w/2, y + h/2
        
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color) if not is_selected else QColor('#FFD700'), 3 if is_selected else 0))
        painter.drawEllipse(int(cx) - 28, int(cy) - 28, 56, 56)
        
        painter.setPen(QPen(QColor('white'), 2))
        for i in range(4):
            angle = (i * math.pi / 2) + math.pi / 4
            sx = cx + math.cos(angle) * 20
            sy = cy + math.sin(angle) * 20
            ex = cx + math.cos(angle) * 36
            ey = cy + math.sin(angle) * 36
            painter.drawLine(int(sx), int(sy), int(ex), int(ey))
    
    def _draw_cloud(self, painter, color, is_selected, offset_y=0):
        x, y, w, h = 0, offset_y, DEVICE_WIDTH, DEVICE_HEIGHT
        cx, cy = x + w/2, y + h/2
        
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color) if not is_selected else QColor('#FFD700'), 3 if is_selected else 0))
        
        path = QPainterPath()
        path.moveTo(x + 20, cy + 12)
        
        rect1 = QRectF(x + 8, cy - 12, 24, 24)
        path.arcMoveTo(rect1, 180)
        path.arcTo(rect1, 180, 180)
        
        rect2 = QRectF(x + 21, cy - 8, 28, 28)
        path.arcTo(rect2, 180, 180)
        
        rect3 = QRectF(x + 36, cy - 6, 28, 28)
        path.arcTo(rect3, 180, 180)
        
        rect4 = QRectF(x + 50, cy, 20, 20)
        path.arcTo(rect4, 180, 180)
        
        rect5 = QRectF(x + 40, cy + 8, 20, 20)
        path.arcTo(rect5, 0, 180)
        
        rect6 = QRectF(x + 20, cy + 8, 20, 20)
        path.arcTo(rect6, 0, 180)
        
        path.closeSubpath()
        painter.drawPath(path)
    
    def set_ip(self, eth, ip, gateway=""):
        self.eth = eth
        self.ip_address = ip
        self.gateway = gateway
        if ip:
            self.ip_label.setPlainText(f"{eth}:{ip}")
            self.ip_label.setPos((DEVICE_WIDTH - self.ip_label.textWidth()) / 2, DEVICE_HEIGHT + 24)
        else:
            self.ip_label.setPlainText("")

class ConnectionItem(QGraphicsPathItem):
    def __init__(self, start_device, end_device, cable_type='copper-straight'):
        super().__init__()
        self.start_device = start_device
        self.end_device = end_device
        self.cable_type = cable_type
        
        color = QColor(CABLE_TYPES[cable_type]['color'])
        self.setPen(QPen(color, 5))
        self.setBrush(QBrush(Qt.GlobalColor.transparent))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.update_position()
    
    def update_position(self):
        path = QPainterPath()
        
        start = self.start_device.scenePos() + QPointF(DEVICE_WIDTH/2, DEVICE_HEIGHT/2)
        end = self.end_device.scenePos() + QPointF(DEVICE_WIDTH/2, DEVICE_HEIGHT/2)
        
        path.moveTo(start.x(), start.y())
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        cp1x = start.x() + dx * 0.25
        cp1y = start.y() + dy * 0.1
        cp2x = end.x() - dx * 0.25
        cp2y = end.y() - dy * 0.1
        
        path.cubicTo(cp1x, cp1y, cp2x, cp2y, end.x(), end.y())
        
        self.setPath(path)
    
    def paint(self, painter, option, widget=None):
        color = QColor(CABLE_TYPES[self.cable_type]['color'])
        painter.setPen(QPen(color, 5))
        painter.setBrush(QBrush(color))
        
        painter.drawPath(self.path())
        
        start = self.start_device.scenePos() + QPointF(DEVICE_WIDTH/2, DEVICE_HEIGHT/2)
        end = self.end_device.scenePos() + QPointF(DEVICE_WIDTH/2, DEVICE_HEIGHT/2)
        
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(start.x()) - 7, int(start.y()) - 7, 14, 14)
        painter.drawEllipse(int(end.x()) - 7, int(end.y()) - 7, 14, 14)

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
        name = f"{device_type.lower()}{self.device_counter[device_type]}"
        
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
            pos = event.scenePos()
            item = self.itemAt(pos, QTransform())
            if item is not None and isinstance(item, DeviceItem):
                if self.connection_mode:
                    try:
                        if self.connection_start is None:
                            self.connection_start = item
                            item.connection_highlight = True
                            item.update()
                        else:
                            item.connection_highlight = False
                            item.update()
                            self.add_connection(self.connection_start, item)
                            self.connection_start.connection_highlight = False
                            self.connection_start.update()
                            self.connection_start = None
                            self.connection_mode = False
                        return
                    except Exception as e:
                        print(f"Connection error: {e}")
                        self.connection_start = None
                        self.connection_mode = False
                        return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        for conn in self.connections:
            try:
                if conn.start_device is not None and conn.end_device is not None:
                    conn.update_position()
                    conn.update()
            except (RuntimeError, AttributeError):
                pass
        super().mouseMoveEvent(event)
        self.update()
    
    def generate_full_lab(self, lab_path):
        if not os.path.exists(lab_path):
            os.makedirs(lab_path)
        
        conf_lines = []
        
        device_interfaces = {}
        
        processed = set()
        for conn in self.connections:
            pair = tuple(sorted([conn.start_device.name, conn.end_device.name]))
            if pair in processed:
                continue
            processed.add(pair)
            
            dev1 = conn.start_device.name
            dev2 = conn.end_device.name
            
            if dev1 not in device_interfaces:
                device_interfaces[dev1] = 0
            if dev2 not in device_interfaces:
                device_interfaces[dev2] = 0
            
            net_letter = chr(65 + len(processed) - 1)
            eth1 = device_interfaces[dev1]
            eth2 = device_interfaces[dev2]
            
            conf_lines.append(f"{dev1}[{eth1}]=\"{net_letter}\"")
            conf_lines.append(f"{dev2}[{eth2}]=\"{net_letter}\"")
            
            device_interfaces[dev1] = eth1 + 1
            device_interfaces[dev2] = eth2 + 1
        
        with open(os.path.join(lab_path, 'lab.conf'), 'wb') as f:
            f.write(('\r\n'.join(conf_lines) + '\r\n').encode('utf-8'))
        
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
                    f.write(f"\n{name}:\n  Interface: {device.eth}\n  IP: {device.ip_address}/24\n")
                    if device.gateway:
                        f.write(f"  Gateway: {device.gateway}\n")
        
        for name, device in self.devices.items():
            startup_file = os.path.join(lab_path, f"{name}.startup")
            startup_cmds = []
            if device.ip_address:
                startup_cmds.append(f"ip addr add {device.ip_address}/24 dev {device.eth}")
            if device.gateway:
                startup_cmds.append(f"ip route add default via {device.gateway}")
            if device.device_type == 'router':
                startup_cmds.append("sysctl -w net.ipv4.ip_forward=1")
            
            content = '\n'.join(startup_cmds) + '\n' if startup_cmds else '# No configuration\n'
            with open(startup_file, 'wb') as f:
                f.write(content.encode('utf-8'))

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
        
        self.ping_btn = QPushButton("Ping")
        self.ping_btn.setStyleSheet("background-color: #4A90D9; color: white; padding: 8px; border: none;")
        self.ping_btn.clicked.connect(self.ping_device)
        self.ping_btn.setEnabled(False)
        layout.addRow("", self.ping_btn)
        
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
        
        cmd_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("add | connect | ip | ping | del | list | help")
        self.cmd_input.setStyleSheet("background-color: #1a1a2e; color: white; padding: 5px; border: 1px solid #444;")
        self.cmd_input.returnPressed.connect(self.execute_command)
        
        cmd_btn = QPushButton("RUN")
        cmd_btn.setStyleSheet("background-color: #FF6B6B; color: white; border: none; padding: 5px 15px;")
        cmd_btn.clicked.connect(self.execute_command)
        
        cmd_layout.addWidget(self.cmd_input)
        cmd_layout.addWidget(cmd_btn)
        layout.addLayout(cmd_layout)
        
        group.setLayout(layout)
        parent.addWidget(group)
        
        self.console.log(">>> Kathara Console Ready")
        self.console.log(">>> Commands: add, connect, ip, del, list, help")
    
    def execute_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        
        self.console.log(f"[CMD] {cmd}", "#FFD700")
        self.cmd_input.setText("")
        
        parts = cmd.lower().split()
        if not parts:
            return
        
        command = parts[0]
        
        try:
            if command == "add":
                if len(parts) < 3:
                    self.console.log("[ERROR] Usage: add router|switch|pc|hub|cloud NAME", "#FF6B6B")
                    return
                device_type = parts[1]
                name = parts[2].lower()
                if device_type not in DEVICE_TYPES:
                    self.console.log(f"[ERROR] Unknown device type: {device_type}", "#FF6B6B")
                    return
                x = 200 + (len(self.scene.devices) % 4) * 180
                y = 150 + (len(self.scene.devices) // 4) * 150
                device = self.scene.add_device(device_type, x, y)
                if device:
                    self.console.log(f"[+] Added: {device.name} ({device_type.upper()})", DEVICE_TYPES[device_type]['color'])
                    self.refresh_connections()
                    
            elif command in ("connect", "conn"):
                if len(parts) < 3:
                    self.console.log("[ERROR] Usage: connect NAME1 NAME2 [cable]", "#FF6B6B")
                    return
                name1 = parts[1].lower()
                name2 = parts[2].lower()
                cable = parts[3] if len(parts) > 3 else "copper-straight"
                
                dev1 = self.scene.devices.get(name1)
                dev2 = self.scene.devices.get(name2)
                
                if not dev1 or not dev2:
                    self.console.log("[ERROR] Device not found", "#FF6B6B")
                    return
                
                existing = any((c.start_device.name == name1 and c.end_device.name == name2) or 
                              (c.start_device.name == name2 and c.end_device.name == name1) 
                              for c in self.scene.connections)
                if existing:
                    self.console.log("[ERROR] Connection already exists", "#FF6B6B")
                    return
                
                if cable not in CABLE_TYPES:
                    cable = "copper-straight"
                
                conn = ConnectionItem(dev1, dev2, cable)
                self.scene.addItem(conn)
                self.scene.connections.append(conn)
                dev1.connections.append(conn)
                dev2.connections.append(conn)
                self.console.log(f"[LINK] {name1} <-> {name2} ({cable})", "#00FFFF")
                self.refresh_connections()
                
            elif command == "ip":
                if len(parts) < 4:
                    self.console.log("[ERROR] Usage: ip NAME ETH IP [gateway]", "#FF6B6B")
                    return
                name = parts[1].lower()
                eth = parts[2]
                ip = parts[3]
                gateway = parts[4] if len(parts) > 4 else ""
                
                device = self.scene.devices.get(name)
                if not device:
                    self.console.log("[ERROR] Device not found", "#FF6B6B")
                    return
                
                if device.device_type in ['hub', 'switch']:
                    self.console.log(f"[ERROR] {device.device_type.upper()} cannot have IP", "#FF6B6B")
                    return
                
                if eth not in ['eth0', 'eth1', 'eth2', 'eth3']:
                    self.console.log("[ERROR] Invalid interface. Use eth0-eth3", "#FF6B6B")
                    return
                
                device.set_ip(eth, ip, gateway)
                self.on_selection_changed()
                self.console.log(f"[IP] {name} {eth}:{ip}" + (f" gateway:{gateway}" if gateway else ""), "#FFFF00")
                
            elif command in ("del", "delete"):
                if len(parts) < 2:
                    self.console.log("[ERROR] Usage: del NAME", "#FF6B6B")
                    return
                name = parts[1].lower()
                if name in self.scene.devices:
                    self.scene.remove_device(name)
                    self.refresh_connections()
                    self.console.log(f"[-] Deleted: {name}", "#D0021B")
                else:
                    self.console.log("[ERROR] Device not found", "#FF6B6B")
                    
            elif command == "list":
                if not self.scene.devices:
                    self.console.log("[INFO] No devices", "#888")
                    return
                self.console.log(f"[INFO] Devices ({len(self.scene.devices)}):", "#888")
                for d in self.scene.devices.values():
                    ip_info = f" {d.eth}:{d.ip}" if d.ip else " (no IP)"
                    self.console.log(f"  - {d.name} ({d.device_type}){ip_info}", "#888")
                self.console.log(f"[INFO] Connections ({len(self.scene.connections)}):", "#888")
                for c in self.scene.connections:
                    self.console.log(f"  - {c.start_device.name} <-> {c.end_device.name}", "#888")
            
            elif command == "ping":
                if len(parts) < 2:
                    self.console.log("[ERROR] Usage: ping NAME [target_ip]", "#FF6B6B")
                    return
                name = parts[1].lower()
                target_ip = parts[2] if len(parts) > 2 else "8.8.8.8"
                
                device = self.scene.devices.get(name)
                if not device:
                    self.console.log("[ERROR] Device not found", "#FF6B6B")
                    return
                
                if not device.ip_address:
                    self.console.log(f"[PING] {name} has no IP address", "#FF6B6B")
                    return
                
                if not self.current_lab_path:
                    self.console.log("[ERROR] Please export a lab first!", "#FF6B6B")
                    return
                
                self.console.log(f"[PING] {name} -> {target_ip}...", "#00BFFF")
                self.console.log("[INFO] Starting lab and waiting...", "#F5A623")
                
                def run_ping():
                    import time
                    try:
                        subprocess.run(["kathara", "lstart", "-d", self.current_lab_path], 
                                     capture_output=True, timeout=60)
                        time.sleep(10)
                        
                        result = subprocess.run(
                            ["kathara", "exec", "-d", self.current_lab_path, name, "--", "ping", "-c", "4", target_ip],
                            capture_output=True, text=True, timeout=30
                        )
                        output = result.stdout + result.stderr
                        
                        self.console.log("[OK] Lab started!", "#7ED321")
                        self.console.log(f"[PING] Result:", "#7ED321")
                        for line in output.split('\n')[:10]:
                            if line.strip():
                                self.console.log(f"  {line}", "#888")
                                
                    except subprocess.TimeoutExpired:
                        self.console.log("[PING] Timeout", "#FF6B6B")
                    except Exception as e:
                        self.console.log(f"[PING] Error: {str(e)}", "#FF6B6B")
                
                threading.Thread(target=run_ping, daemon=True).start()
                    
            elif command == "help":
                self.console.log("[HELP] Available commands:", "#00FFFF")
                self.console.log("  add router|switch|pc|hub|cloud NAME", "#888")
                self.console.log("  connect NAME1 NAME2 [cable]", "#888")
                self.console.log("  ip NAME eth0|eth1 IP [gateway]", "#888")
                self.console.log("  ping NAME [target_ip]", "#888")
                self.console.log("  del NAME", "#888")
                self.console.log("  list", "#888")
                self.console.log("  help", "#888")
                
            else:
                self.console.log(f"[ERROR] Unknown command: {command}", "#FF6B6B")
        except Exception as e:
            self.console.log(f"[ERROR] {str(e)}", "#FF6B6B")
        
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
            dt = device_type
            btn.clicked.connect(lambda checked, dt=dt: self.add_device(dt))
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
    
    def ping_device(self):
        items = self.canvas.scene().selectedItems()
        if items and isinstance(items[0], DeviceItem):
            device = items[0]
            if not device.ip_address:
                self.console.log("[PING] Device has no IP address", "#FF6B6B")
                return
            
            target_ip, ok = QInputDialog.getText(self, "Ping", f"Ping from {device.name} to:", text="8.8.8.8")
            if not ok or not target_ip:
                return
            
            if not self.current_lab_path:
                QMessageBox.warning(self, "Warning", "Please export a lab first!")
                return
            
            self.console.log(f"[PING] {device.name} -> {target_ip}...", "#00BFFF")
            self.console.log("[INFO] Starting lab and waiting...", "#F5A623")
            
            def run_ping():
                import time
                try:
                    subprocess.run(["kathara", "lstart", "-d", self.current_lab_path], 
                                 capture_output=True, timeout=60)
                    time.sleep(10)
                    
                    result = subprocess.run(
                        ["kathara", "exec", "-d", self.current_lab_path, device.name, "--", "ping", "-c", "4", target_ip],
                        capture_output=True, text=True, timeout=30
                    )
                    output = result.stdout + result.stderr
                    
                    self.console.log("[OK] Lab started!", "#7ED321")
                    self.console.log(f"[PING] Result:", "#7ED321")
                    for line in output.split('\n')[:10]:
                        if line.strip():
                            self.console.log(f"  {line}", "#888")
                            
                except subprocess.TimeoutExpired:
                    self.console.log("[PING] Timeout", "#FF6B6B")
                except Exception as e:
                    self.console.log(f"[PING] Error: {str(e)}", "#FF6B6B")
            
            threading.Thread(target=run_ping, daemon=True).start()
    
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
                self.ping_btn.setEnabled(bool(device.ip_address))
            else:
                self.eth_label.setText("-")
                self.ip_label.setText("-")
                self.gateway_label.setText("-")
                self.config_ip_btn.setEnabled(False)
                self.ping_btn.setEnabled(False)
        else:
            self.name_label.setText("-")
            self.type_label.setText("-")
            self.eth_label.setText("-")
            self.ip_label.setText("-")
            self.gateway_label.setText("-")
            self.config_ip_btn.setEnabled(False)
            self.ping_btn.setEnabled(False)
    
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
