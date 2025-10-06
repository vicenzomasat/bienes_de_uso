"""
🌙 BIENES DE USO - MODERN UI WITH PYSIDE6
Grey Moon Theme - Minimal, Professional, Beautiful
By Claude with ADHD Energy ⚡⚡⚡
"""

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QDateEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QTabWidget, QFrame, QSplitter, QFileDialog,
    QProgressBar, QStatusBar, QCheckBox, QSpinBox, QTextEdit,
    QScrollArea, QGridLayout, QGroupBox, QMenu
)
from PySide6.QtCore import Qt, QDate, Signal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QLinearGradient

# Importar módulos existentes
from models.bien import Bien
from models.empresa import EmpresaData
from models.indice_facpce import GestorIndicesFACPCE
from utils.validators import Validators
from utils.csv_handler import CsvHandler
from modules.amortizaciones import AmortizacionCalculator
from modules.filtros import FiltroEjercicio
from modules.inflacion_calculator import InflacionCalculator
from views.gestion_indices import GestionIndices
from db.duck import connect as duck_connect, init_schema as duck_init, save_company_state, load_by_cuit


# 🎨 GREY MOON THEME STYLESHEET
GREY_MOON_STYLE = """
/* 🌙 GREY MOON THEME - Not too dark, not too light */

QMainWindow, QDialog {
    background-color: #2a2d35;
}

/* Panels & Frames */
QWidget {
    background-color: #2a2d35;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QFrame#empresa_panel {
    background-color: #323541;
    border-radius: 8px;
    border: 1px solid #3e4149;
}

QFrame#content_panel {
    background-color: #2a2d35;
}

/* GroupBox */
QGroupBox {
    background-color: #323541;
    border: 1px solid #3e4149;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
    color: #a0a4b8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: #6c9ef8;
}

/* Labels */
QLabel {
    background: transparent;
    color: #e0e0e0;
    padding: 2px;
}

QLabel#title_label {
    font-size: 18pt;
    font-weight: bold;
    color: #6c9ef8;
    padding: 10px;
}

QLabel#subtitle_label {
    font-size: 11pt;
    color: #a0a4b8;
    padding: 5px;
}

QLabel#status_ok {
    color: #5dbd5d;
    font-weight: bold;
}

QLabel#status_pending {
    color: #f5a962;
    font-weight: bold;
}

/* Input Fields */
QLineEdit, QSpinBox, QComboBox, QDateEdit, QTextEdit {
    background-color: #3a3d47;
    border: 1px solid #4a4d57;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #6c9ef8;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 1px solid #6c9ef8;
    background-color: #424552;
}

QLineEdit:read-only {
    background-color: #2f3239;
    color: #909090;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #a0a4b8;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #3a3d47;
    border: 1px solid #4a4d57;
    selection-background-color: #6c9ef8;
    color: #e0e0e0;
}

/* Buttons */
QPushButton {
    background-color: #4a5568;
    border: 1px solid #5a6578;
    border-radius: 5px;
    padding: 8px 16px;
    color: #ffffff;
    font-weight: bold;
    min-height: 28px;
}

QPushButton:hover {
    background-color: #5a6678;
    border: 1px solid #6a7688;
}

QPushButton:pressed {
    background-color: #3a4558;
}

QPushButton:disabled {
    background-color: #35383f;
    color: #606060;
    border: 1px solid #404040;
}

/* Primary buttons */
QPushButton#primary_btn {
    background-color: #6c9ef8;
    border: 1px solid #5c8ee8;
}

QPushButton#primary_btn:hover {
    background-color: #7caef8;
}

QPushButton#primary_btn:pressed {
    background-color: #5c8ee8;
}

/* Success buttons */
QPushButton#success_btn {
    background-color: #5dbd5d;
    border: 1px solid #4dad4d;
}

QPushButton#success_btn:hover {
    background-color: #6dcd6d;
}

/* Danger buttons */
QPushButton#danger_btn {
    background-color: #e85d5d;
    border: 1px solid #d84d4d;
}

QPushButton#danger_btn:hover {
    background-color: #f86d6d;
}

/* Tables */
QTableWidget {
    background-color: #323541;
    alternate-background-color: #2d2f39;
    border: 1px solid #3e4149;
    border-radius: 6px;
    gridline-color: #3e4149;
    color: #e0e0e0;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #6c9ef8;
    color: #ffffff;
}

QTableWidget::item:hover {
    background-color: #3d4150;
}

QHeaderView::section {
    background-color: #3a3d47;
    color: #a0a4b8;
    padding: 8px;
    border: none;
    border-right: 1px solid #2a2d35;
    border-bottom: 1px solid #2a2d35;
    font-weight: bold;
}

QHeaderView::section:hover {
    background-color: #454854;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #2a2d35;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #4a4d57;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #5a5d67;
}

QScrollBar:horizontal {
    background: #2a2d35;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #4a4d57;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #5a5d67;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #4a4d57;
    background-color: #3a3d47;
}

QCheckBox::indicator:checked {
    background-color: #6c9ef8;
    border: 1px solid #5c8ee8;
}

QCheckBox::indicator:hover {
    border: 1px solid #6c9ef8;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #3e4149;
    border-radius: 6px;
    background-color: #323541;
    top: -1px;
}

QTabBar::tab {
    background-color: #3a3d47;
    color: #a0a4b8;
    padding: 10px 20px;
    border: 1px solid #3e4149;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #323541;
    color: #6c9ef8;
    border-bottom: 2px solid #6c9ef8;
}

QTabBar::tab:hover {
    background-color: #454854;
}

/* Status Bar */
QStatusBar {
    background-color: #323541;
    color: #a0a4b8;
    border-top: 1px solid #3e4149;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #3e4149;
    border-radius: 4px;
    background-color: #2a2d35;
    text-align: center;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #6c9ef8;
    border-radius: 3px;
}

/* Tooltips */
QToolTip {
    background-color: #3a3d47;
    color: #e0e0e0;
    border: 1px solid #4a4d57;
    border-radius: 4px;
    padding: 5px;
}

/* Menu */
QMenu {
    background-color: #323541;
    border: 1px solid #3e4149;
    color: #e0e0e0;
}

QMenu::item {
    padding: 8px 25px;
}

QMenu::item:selected {
    background-color: #6c9ef8;
}

/* Separators */
QFrame[frameShape="4"], /* HLine */
QFrame[frameShape="5"]  /* VLine */
{
    color: #3e4149;
}
"""


class ModernBienesApp(QMainWindow):
    """🌙 Modern UI for Bienes de Uso"""
    
    def __init__(self):
        super().__init__()
        
        # Datos principales
        self.empresa = EmpresaData()
        self.tipos_bienes = []
        self.bienes = {}
        self.next_id = 1
        self.tipos_configurados = False
        
        # Gestores y calculadoras
        self.csv_handler = CsvHandler()
        self.amort_calculator = AmortizacionCalculator()
        self.filtro_ejercicio = FiltroEjercicio()
        self.gestor_indices = GestorIndicesFACPCE()
        self.inflacion_calculator = InflacionCalculator(self.gestor_indices)
        
        # Database
        self.db_con = None
        self.db_path = "data/cartera.duckdb"
        self._dirty = False
        
        # Ventanas adicionales
        self.vista_ajustada_window = None
        
        self.init_ui()
        self.apply_theme()
        
        # Timer para mensajes de status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.clear_temp_status)
    
    def init_ui(self):
        """Initialize the complete UI"""
        self.setWindowTitle("🌙 Bienes de Uso - Modern Edition")
        self.setGeometry(100, 100, 1600, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Left panel - Empresa data
        self.create_empresa_panel()
        main_layout.addWidget(self.empresa_panel, stretch=0)
        
        # Right panel - Main content
        self.create_content_panel()
        main_layout.addWidget(self.content_panel, stretch=1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.set_status("Configure primero los datos de la empresa")
        
        # Initial state
        self.toggle_main_content(False)
        
        # Show welcome
        QTimer.singleShot(500, self.show_welcome)
    
    def create_empresa_panel(self):
        """Create left panel for empresa data"""
        self.empresa_panel = QFrame()
        self.empresa_panel.setObjectName("empresa_panel")
        self.empresa_panel.setMaximumWidth(350)
        self.empresa_panel.setMinimumWidth(320)
        
        layout = QVBoxLayout(self.empresa_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📊 Datos de la Empresa")
        title.setObjectName("subtitle_label")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form
        form_group = QGroupBox()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(15, 20, 15, 15)
        
        # Fields
        self.razon_input = QLineEdit()
        self.razon_input.setPlaceholderText("Razón Social")
        form_layout.addRow("Razón Social:", self.razon_input)
        
        # CUIT with lookup button
        cuit_layout = QHBoxLayout()
        self.cuit_input = QLineEdit()
        self.cuit_input.setPlaceholderText("XX-XXXXXXXX-X")
        cuit_layout.addWidget(self.cuit_input)
        
        self.lookup_btn = QPushButton("🔎")
        self.lookup_btn.setMaximumWidth(40)
        self.lookup_btn.setToolTip("Consultar bienes")
        self.lookup_btn.clicked.connect(self.lookup_by_cuit)
        cuit_layout.addWidget(self.lookup_btn)
        
        form_layout.addRow("C.U.I.T.:", cuit_layout)
        
        self.fecha_inicio_input = QLineEdit()
        self.fecha_inicio_input.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow("Fecha Inicio:", self.fecha_inicio_input)
        
        self.fecha_cierre_input = QLineEdit()
        self.fecha_cierre_input.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow("Fecha Cierre:", self.fecha_cierre_input)
        
        self.ejercicio_anterior_input = QLineEdit()
        self.ejercicio_anterior_input.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow("Ejercicio Anterior:", self.ejercicio_anterior_input)
        
        layout.addWidget(form_group)
        
        # Confirm button
        self.confirm_empresa_btn = QPushButton("✅ Confirmar Datos")
        self.confirm_empresa_btn.setObjectName("success_btn")
        self.confirm_empresa_btn.clicked.connect(self.confirm_empresa_data)
        self.confirm_empresa_btn.setEnabled(False)
        layout.addWidget(self.confirm_empresa_btn)
        
        # Action buttons
        self.config_tipos_btn = QPushButton("⚙️ Configurar Tipos")
        self.config_tipos_btn.clicked.connect(self.show_tipos_config)
        self.config_tipos_btn.setEnabled(False)
        layout.addWidget(self.config_tipos_btn)
        
        self.indices_btn = QPushButton("📈 Índices FACPCE")
        self.indices_btn.clicked.connect(self.abrir_gestion_indices)
        layout.addWidget(self.indices_btn)
        
        self.template_btn = QPushButton("📋 Template CSV")
        self.template_btn.clicked.connect(self.crear_template_csv)
        layout.addWidget(self.template_btn)
        
        # Status indicators
        status_group = QGroupBox("Estado")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(5)
        
        self.estado_empresa_label = QLabel("❌ Empresa: Pendiente")
        self.estado_empresa_label.setObjectName("status_pending")
        status_layout.addWidget(self.estado_empresa_label)
        
        self.estado_tipos_label = QLabel("❌ Tipos: Pendiente")
        self.estado_tipos_label.setObjectName("status_pending")
        status_layout.addWidget(self.estado_tipos_label)
        
        layout.addWidget(status_group)
        
        # Spacer
        layout.addStretch()
        
        # Connect text changes for validation
        for input_field in [self.razon_input, self.cuit_input, self.fecha_inicio_input, 
                           self.fecha_cierre_input, self.ejercicio_anterior_input]:
            input_field.textChanged.connect(self.validate_empresa_data)
    
    def create_content_panel(self):
        """Create main content panel"""
        self.content_panel = QFrame()
        self.content_panel.setObjectName("content_panel")
        
        layout = QVBoxLayout(self.content_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        title = QLabel("Sistema de Ajuste por Inflación FACPCE")
        title.setObjectName("title_label")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter and ejercicio
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍 Filtrar bienes...")
        self.filter_input.setMaximumWidth(200)
        self.filter_input.textChanged.connect(self.refresh_table)
        header_layout.addWidget(QLabel("Filtrar:"))
        header_layout.addWidget(self.filter_input)
        
        self.ejercicio_input = QLineEdit()
        self.ejercicio_input.setPlaceholderText("DD/MM/AAAA")
        self.ejercicio_input.setMaximumWidth(120)
        self.ejercicio_input.textChanged.connect(self.refresh_table)
        header_layout.addWidget(QLabel("Ejercicio:"))
        header_layout.addWidget(self.ejercicio_input)
        
        layout.addLayout(header_layout)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)
        
        self.new_btn = QPushButton("➕ Nuevo")
        self.new_btn.clicked.connect(self.new_bien)
        toolbar_layout.addWidget(self.new_btn)
        
        self.import_btn = QPushButton("📁 Importar")
        self.import_btn.clicked.connect(self.import_csv)
        toolbar_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("💾 Exportar")
        self.export_btn.clicked.connect(self.export_csv_basico)
        toolbar_layout.addWidget(self.export_btn)
        
        self.export_full_btn = QPushButton("📊 Exportar Full")
        self.export_full_btn.clicked.connect(self.export_csv_completo)
        toolbar_layout.addWidget(self.export_full_btn)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        toolbar_layout.addWidget(separator1)
        
        self.save_db_btn = QPushButton("🗄 Guardar DB")
        self.save_db_btn.setObjectName("primary_btn")
        self.save_db_btn.clicked.connect(self.save_to_duckdb)
        toolbar_layout.addWidget(self.save_db_btn)
        
        self.backup_btn = QPushButton("🛟 Backup")
        self.backup_btn.clicked.connect(self.backup_duckdb)
        toolbar_layout.addWidget(self.backup_btn)
        
        self.load_db_btn = QPushButton("📂 Cargar DB")
        self.load_db_btn.clicked.connect(self.load_from_duckdb)
        toolbar_layout.addWidget(self.load_db_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        toolbar_layout.addWidget(separator2)
        
        self.vista_ajustada_btn = QPushButton("🔥 Vista Ajustada")
        self.vista_ajustada_btn.setObjectName("primary_btn")
        self.vista_ajustada_btn.clicked.connect(self.abrir_vista_ajustada)
        toolbar_layout.addWidget(self.vista_ajustada_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Table
        self.create_table()
        layout.addWidget(self.table_widget)
    
    def create_table(self):
        """Create main table"""
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # Columns
        columns = [
            'ID', 'Descripción', 'Tipo', 'Amort.', 'Años',
            'Ejercicio', 'F.Ingreso', 'F.Baja', 'Valor Origen',
            'Amort. Inicio', 'Amort. Ejercicio', 'Amort. Acum.', 'Valor Residual'
        ]
        
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)
        
        # Column widths
        widths = [50, 200, 120, 70, 50, 70, 90, 90, 120, 120, 120, 120, 120]
        for i, width in enumerate(widths):
            self.table_widget.setColumnWidth(i, width)
        
        # Header settings
        header = self.table_widget.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionsMovable(False)
        
        # Double click to edit
        self.table_widget.doubleClicked.connect(self.edit_selected)
    
    def apply_theme(self):
        """Apply the grey moon theme"""
        self.setStyleSheet(GREY_MOON_STYLE)
    
    def show_welcome(self):
        """Show welcome message"""
        msg = QMessageBox(self)
        msg.setWindowTitle("🌙 Bienvenido")
        msg.setText("Sistema de Amortización Iniciado")
        msg.setInformativeText(
            "✅ Decimales argentinos (1.234.567,89)\n"
            "✅ CSV con separador punto y coma (;)\n"
            "✅ Ajuste por inflación FACPCE\n"
            "✅ Vista histórica y ajustada\n\n"
            "Configure primero los datos de empresa."
        )
        msg.setIcon(QMessageBox.Information)
        msg.exec()
    
    def validate_empresa_data(self):
        """Validate empresa data and enable/disable confirm button"""
        all_filled = (
            self.razon_input.text().strip() and
            self.cuit_input.text().strip() and
            self.fecha_inicio_input.text().strip() and
            self.fecha_cierre_input.text().strip() and
            self.ejercicio_anterior_input.text().strip()
        )
        self.confirm_empresa_btn.setEnabled(all_filled)
    
    def confirm_empresa_data(self):
        """Confirm and save empresa data"""
        try:
            # Validations
            fecha_inicio = self.fecha_inicio_input.text().strip()
            fecha_cierre = self.fecha_cierre_input.text().strip()
            ejercicio_anterior = self.ejercicio_anterior_input.text().strip()
            cuit = self.cuit_input.text().strip()
            
            if not Validators.validar_fecha(fecha_inicio):
                self.show_error("Fecha de inicio debe tener formato DD/MM/AAAA")
                return
            
            if not Validators.validar_fecha(fecha_cierre):
                self.show_error("Fecha de cierre debe tener formato DD/MM/AAAA")
                return
            
            es_valido, mensaje = Validators.validar_ejercicio_anterior(ejercicio_anterior, fecha_cierre)
            if not es_valido:
                self.show_error(mensaje)
                return
            
            if not Validators.validar_cuit(cuit):
                self.show_error("C.U.I.T. inválido. Verifique los 11 dígitos")
                return
            
            # Check dates
            inicio_dt = datetime.strptime(fecha_inicio, '%d/%m/%Y')
            cierre_dt = datetime.strptime(fecha_cierre, '%d/%m/%Y')
            
            if inicio_dt > cierre_dt:
                self.show_error("Fecha de inicio debe ser anterior a fecha de cierre")
                return
            
            # Save data
            self.empresa.razon_social = self.razon_input.text().strip()
            self.empresa.cuit = cuit
            self.empresa.fecha_inicio = fecha_inicio
            self.empresa.fecha_cierre = fecha_cierre
            self.empresa.ejercicio_anterior = ejercicio_anterior
            self.empresa.ejercicio_liquidacion = fecha_cierre
            self.empresa.configurada = True
            self._dirty = True
            
            self.ejercicio_input.setText(fecha_cierre)
            
            # Update status
            self.estado_empresa_label.setText("✅ Empresa: Configurado")
            self.estado_empresa_label.setObjectName("status_ok")
            self.estado_empresa_label.setStyleSheet("")  # Reset
            
            # Disable fields
            for field in [self.razon_input, self.cuit_input, self.fecha_inicio_input,
                         self.fecha_cierre_input, self.ejercicio_anterior_input]:
                field.setReadOnly(True)
            
            self.confirm_empresa_btn.setEnabled(False)
            self.config_tipos_btn.setEnabled(True)
            
            self.set_status("Empresa configurada. Configure los tipos de bienes.")
            self.show_info("Datos confirmados", "Configure los tipos de bienes")
            
        except Exception as e:
            self.show_error(f"Error al confirmar datos: {str(e)}")
    
    def show_tipos_config(self):
        """Show tipos configuration dialog"""
        dialog = TiposConfigDialog(self.tipos_bienes, self)
        if dialog.exec():
            self.tipos_bienes = dialog.get_tipos()
            self.tipos_configurados = True
            self._dirty = True
            
            self.estado_tipos_label.setText("✅ Tipos: Configurado")
            self.estado_tipos_label.setObjectName("status_ok")
            self.estado_tipos_label.setStyleSheet("")  # Reset
            
            content_enabled = self.empresa.configurada and self.tipos_configurados
            self.toggle_main_content(content_enabled)
            
            if content_enabled:
                self.set_status("Sistema listo para usar")
            
            self.show_info("Éxito", f"Configurados {len(self.tipos_bienes)} tipos de bienes")
    
    def new_bien(self):
        """Create new bien"""
        if not self.tipos_configurados:
            self.show_warning("Configure primero los tipos de bienes")
            return
        
        dialog = BienDialog(self.tipos_bienes, None, self)
        if dialog.exec():
            bien = dialog.get_bien()
            bien.id = self.next_id
            self.bienes[self.next_id] = bien
            self.next_id += 1
            self._dirty = True
            
            self.refresh_table()
            self.show_info("Éxito", f"Bien '{bien.descripcion}' creado correctamente")
    
    def edit_selected(self):
        """Edit selected bien"""
        if not self.tipos_configurados:
            return
        
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            self.show_warning("Seleccione un bien para editar")
            return
        
        bien_id = int(self.table_widget.item(current_row, 0).text())
        bien = self.bienes.get(bien_id)
        
        if not bien:
            self.show_error("Bien no encontrado")
            return
        
        dialog = BienDialog(self.tipos_bienes, bien, self)
        if dialog.exec():
            updated_bien = dialog.get_bien()
            updated_bien.id = bien_id
            self.bienes[bien_id] = updated_bien
            self._dirty = True
            
            self.refresh_table()
            self.show_info("Éxito", "Bien actualizado correctamente")
    
    def delete_selected(self):
        """Delete selected bienes"""
        if not self.tipos_configurados:
            return
        
        selected_rows = set(item.row() for item in self.table_widget.selectedItems())
        if not selected_rows:
            self.show_warning("Seleccione bienes para eliminar")
            return
        
        count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar {count} bien(es) seleccionado(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for row in selected_rows:
                bien_id = int(self.table_widget.item(row, 0).text())
                if bien_id in self.bienes:
                    del self.bienes[bien_id]
            
            self._dirty = True
            self.refresh_table()
            self.show_info("Éxito", f"{count} bien(es) eliminado(s)")
    
    def refresh_table(self):
        """Refresh the table with current data"""
        # Clear table
        self.table_widget.setRowCount(0)
        
        # Get filtered bienes
        bienes_mostrar = list(self.bienes.values())
        
        # Apply text filter
        filtro_texto = self.filter_input.text().strip().lower()
        if filtro_texto:
            bienes_mostrar = [
                b for b in bienes_mostrar
                if filtro_texto in b.descripcion.lower() or filtro_texto in b.tipo_bien.lower()
            ]
        
        # Apply ejercicio filter
        ejercicio_liquidacion = self.ejercicio_input.text().strip()
        if ejercicio_liquidacion and Validators.validar_fecha(ejercicio_liquidacion):
            bienes_mostrar = self.filtro_ejercicio.filtrar_bienes_por_ejercicio(
                bienes_mostrar, ejercicio_liquidacion
            )
            
            # Calculate amortizations
            amortizaciones = self.amort_calculator.calcular_amortizaciones_lote(
                bienes_mostrar, ejercicio_liquidacion
            )
        else:
            amortizaciones = {}
        
        # Populate table
        for bien in sorted(bienes_mostrar, key=lambda x: x.id):
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            
            amort_data = amortizaciones.get(bien.id, {})
            
            values = [
                str(bien.id),
                bien.descripcion,
                bien.tipo_bien,
                'SI' if bien.es_amortizable else 'NO',
                str(bien.anos_amortizacion),
                str(bien.ejercicio_alta),
                bien.fecha_ingreso,
                bien.fecha_baja or '',
                Validators.format_decimal_argentino(bien.valor_origen),
                Validators.format_decimal_argentino(amort_data.get('amort_inicio', 0)),
                Validators.format_decimal_argentino(amort_data.get('amort_ejercicio', 0)),
                Validators.format_decimal_argentino(amort_data.get('amort_acumulada', 0)),
                Validators.format_decimal_argentino(amort_data.get('valor_residual', bien.valor_origen))
            ]
            
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter if col != 1 else Qt.AlignLeft | Qt.AlignVCenter)
                self.table_widget.setItem(row, col, item)
        
        # Update status
        self.set_status(f"Mostrando {len(bienes_mostrar)} de {len(self.bienes)} bienes")
    
    def show_context_menu(self, position):
        """Show context menu on right click"""
        if not self.tipos_configurados:
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏ Editar")
        edit_action.triggered.connect(self.edit_selected)
        
        delete_action = menu.addAction("🗑 Eliminar")
        delete_action.triggered.connect(self.delete_selected)
        
        menu.exec(self.table_widget.viewport().mapToGlobal(position))
    
    def toggle_main_content(self, enabled):
        """Enable/disable main content"""
        for btn in [self.new_btn, self.import_btn, self.export_btn, self.export_full_btn,
                   self.vista_ajustada_btn, self.save_db_btn, self.backup_btn]:
            btn.setEnabled(enabled)
        
        self.filter_input.setEnabled(enabled)
        self.ejercicio_input.setEnabled(enabled)
        self.load_db_btn.setEnabled(True)  # Always enabled
    
    # Import/Export methods
    def import_csv(self):
        """Import bienes from CSV"""
        if not self.tipos_configurados:
            self.show_warning("Configure primero los tipos de bienes")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Bienes desde CSV", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            bienes_importados = self.csv_handler.import_from_file(file_path, self.tipos_bienes)
            
            for bien in bienes_importados:
                bien.id = self.next_id
                self.bienes[self.next_id] = bien
                self.next_id += 1
            
            self.refresh_table()
            if bienes_importados:
                self._dirty = True
            self.show_info("Éxito", f"{len(bienes_importados)} bienes importados")
            
        except Exception as e:
            self.show_error(f"Error importando CSV: {str(e)}")
    
    def export_csv_basico(self):
        """Export basic CSV"""
        if not self.bienes:
            self.show_warning("No hay bienes para exportar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Bienes (Básico)", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.csv_handler.export_to_file(list(self.bienes.values()), file_path)
            self.show_info("Éxito", f"Bienes exportados a {file_path}")
        except Exception as e:
            self.show_error(f"Error exportando: {str(e)}")
    
    def export_csv_completo(self):
        """Export complete CSV with amortizations"""
        if not self.bienes:
            self.show_warning("No hay bienes para exportar")
            return
        
        if not self.ejercicio_input.text().strip():
            self.show_warning("Configure el ejercicio a liquidar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Bienes (Completo)", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            ejercicio = self.ejercicio_input.text().strip()
            amortizaciones = self.amort_calculator.calcular_amortizaciones_lote(
                list(self.bienes.values()), ejercicio
            )
            
            for bien_id, bien in self.bienes.items():
                bien.amortizacion_data = amortizaciones.get(bien_id, {})
            
            self.csv_handler.export_to_file(
                list(self.bienes.values()), file_path, include_amortizacion=True
            )
            self.show_info("Éxito", "Bienes con amortizaciones exportados")
            
        except Exception as e:
            self.show_error(f"Error exportando: {str(e)}")
    
    # Database methods
    def _ensure_db(self):
        """Ensure database connection"""
        if self.db_con is None:
            try:
                self.db_con = duck_connect(self.db_path)
                duck_init(self.db_con)
            except Exception as e:
                self.show_error(f"No se pudo abrir DuckDB: {e}")
                self.db_con = None
        return self.db_con is not None
    
    def save_current_company(self):
        """Save current company state to DB"""
        if not self._ensure_db():
            return False
        
        cuit = self.empresa.cuit or ""
        if not Validators.validar_cuit(cuit):
            self.show_warning("Ingrese un C.U.I.T. válido antes de guardar")
            return False
        
        if not self.empresa.configurada:
            self.show_warning("Confirme los datos de la empresa antes de guardar")
            return False
        
        try:
            save_company_state(
                self.db_con, self.empresa, self.tipos_bienes,
                self.bienes, self.gestor_indices
            )
            self._dirty = False
            self.set_status(f"Datos guardados en {self.db_path}")
            return True
        except Exception as e:
            self.show_error(f"Error al guardar: {str(e)}")
            return False
    
    def save_to_duckdb(self):
        """Save to DuckDB"""
        if self.save_current_company():
            self.show_info("Guardado", f"Datos guardados en {self.db_path}")
    
    def backup_duckdb(self):
        """Create backup of database"""
        if not self._ensure_db():
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path("backups") / f"export_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            destination = backup_dir.as_posix().replace("'", "''")
            self.db_con.execute(f"EXPORT DATABASE '{destination}' (FORMAT PARQUET)")
            
            self.set_status(f"Backup exportado a {backup_dir}")
            self.show_info("Backup", f"Exportado a {backup_dir}")
        except Exception as e:
            self.show_error(f"Error de backup: {str(e)}")
    
    def lookup_by_cuit(self):
        """Lookup company by CUIT"""
        cuit = self.cuit_input.text().strip()
        if not Validators.validar_cuit(cuit):
            self.show_error("El C.U.I.T. debe contener 11 dígitos válidos")
            return
        
        if not self._ensure_db():
            return
        
        try:
            empresa, tipos, bienes, gestor = load_by_cuit(self.db_con, cuit)
            
            if not empresa:
                reply = QMessageBox.question(
                    self,
                    "CUIT no encontrado",
                    "No existen datos para este C.U.I.T. ¿Desea inicializar un conjunto vacío?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.initialize_empty_company(cuit)
                return
            
            # Load data
            self.empresa = empresa
            self.tipos_bienes = tipos
            self.bienes = bienes
            self.gestor_indices = gestor
            self.inflacion_calculator = InflacionCalculator(self.gestor_indices)
            self.next_id = (max(self.bienes.keys()) + 1) if self.bienes else 1
            
            # Update UI
            self.hydrate_empresa_panel()
            self.tipos_configurados = bool(self.tipos_bienes)
            
            self.update_status_labels()
            
            content_enabled = self.empresa.configurada and self.tipos_configurados
            self.toggle_main_content(content_enabled)
            
            self.filter_input.clear()
            self.refresh_table()
            self._dirty = False
            
            self.set_status(f"Datos cargados para C.U.I.T. {cuit}")
            self.show_info("Carga completada", f"Datos cargados para C.U.I.T. {cuit}")
            
        except Exception as e:
            self.show_error(f"Error al consultar: {str(e)}")
    
    def initialize_empty_company(self, cuit):
        """Initialize empty company"""
        self.empresa = EmpresaData()
        self.empresa.razon_social = self.razon_input.text().strip()
        self.empresa.cuit = cuit
        self.empresa.fecha_inicio = self.fecha_inicio_input.text().strip()
        self.empresa.fecha_cierre = self.fecha_cierre_input.text().strip()
        self.empresa.ejercicio_anterior = self.ejercicio_anterior_input.text().strip()
        self.empresa.ejercicio_liquidacion = self.fecha_cierre_input.text().strip()
        self.empresa.configurada = True
        
        self.bienes = {}
        self.next_id = 1
        self._dirty = True
        
        self.hydrate_empresa_panel()
        self.update_status_labels()
        
        self.toggle_main_content(self.empresa.configurada and self.tipos_configurados)
        self.refresh_table()
        
        self.set_status(f"Dataset inicializado para CUIT {cuit}")
        self.show_info("Listo", "Se creó un dataset vacío para este C.U.I.T.")
    
    def load_from_duckdb(self):
        """Load from DuckDB"""
        self.lookup_by_cuit()
    
    def hydrate_empresa_panel(self):
        """Populate empresa panel with data"""
        self.razon_input.setText(self.empresa.razon_social or "")
        self.cuit_input.setText(self.empresa.cuit or "")
        self.fecha_inicio_input.setText(self.empresa.fecha_inicio or "")
        self.fecha_cierre_input.setText(self.empresa.fecha_cierre or "")
        self.ejercicio_anterior_input.setText(self.empresa.ejercicio_anterior or "")
        
        cierre_liquidacion = self.empresa.ejercicio_liquidacion or self.empresa.fecha_cierre or ""
        self.ejercicio_input.setText(cierre_liquidacion)
        
        self.config_tipos_btn.setEnabled(True)
        
        if self.empresa.configurada:
            for field in [self.razon_input, self.cuit_input, self.fecha_inicio_input,
                         self.fecha_cierre_input, self.ejercicio_anterior_input]:
                field.setReadOnly(True)
            self.confirm_empresa_btn.setEnabled(False)
        else:
            for field in [self.razon_input, self.cuit_input, self.fecha_inicio_input,
                         self.fecha_cierre_input, self.ejercicio_anterior_input]:
                field.setReadOnly(False)
            self.validate_empresa_data()
    
    def update_status_labels(self):
        """Update status labels"""
        if self.empresa.configurada:
            self.estado_empresa_label.setText("✅ Empresa: Configurado")
            self.estado_empresa_label.setObjectName("status_ok")
        else:
            self.estado_empresa_label.setText("❌ Empresa: Pendiente")
            self.estado_empresa_label.setObjectName("status_pending")
        
        if self.tipos_configurados:
            self.estado_tipos_label.setText("✅ Tipos: Configurado")
            self.estado_tipos_label.setObjectName("status_ok")
        else:
            self.estado_tipos_label.setText("❌ Tipos: Pendiente")
            self.estado_tipos_label.setObjectName("status_pending")
        
        # Reset style
        self.estado_empresa_label.setStyleSheet("")
        self.estado_tipos_label.setStyleSheet("")
    
    # Additional methods
    def abrir_gestion_indices(self):
        """Open indices management"""
        GestionIndices(self.gestor_indices, self, on_change=lambda: setattr(self, '_dirty', True))
    
    def crear_template_csv(self):
        """Create CSV template"""
        if not self.tipos_configurados:
            self.show_warning("Configure primero los tipos de bienes")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Crear Template CSV", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.csv_handler.create_template_csv(file_path, self.tipos_bienes)
            self.show_info(
                "Éxito",
                f"Template creado en {file_path}\n\n"
                "Formato: CSV con punto y coma (;)\n"
                "Decimales: formato argentino (1.234.567,89)"
            )
        except Exception as e:
            self.show_error(f"Error creando template: {str(e)}")
    
    def abrir_vista_ajustada(self):
        """Open adjusted view"""
        if not self.tipos_configurados:
            self.show_warning("Configure primero los tipos de bienes")
            return
        
        if not self.empresa.ejercicio_anterior:
            self.show_warning("Configure el ejercicio anterior")
            return
        
        # Import here to avoid circular dependency
        from views.vista_ajustada import VistaAjustada
        
        if self.vista_ajustada_window and hasattr(self.vista_ajustada_window, 'window'):
            try:
                if self.vista_ajustada_window.window.winfo_exists():
                    self.vista_ajustada_window.window.lift()
                    return
            except:
                pass
        
        self.vista_ajustada_window = VistaAjustada(
            self,
            self.bienes.copy(),
            self.empresa.ejercicio_liquidacion,
            self.empresa.ejercicio_anterior,
            self.amort_calculator,
            self.inflacion_calculator
        )
    
    # Utility methods for messages
    def show_info(self, title, message):
        """Show info message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    def show_warning(self, message):
        """Show warning message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Advertencia")
        msg.setText(message)
        msg.exec()
    
    def show_error(self, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec()
    
    def set_status(self, message, duration=0):
        """Set status bar message"""
        self.status_bar.showMessage(message, duration)
        if duration > 0:
            self.status_timer.start(duration)
    
    def clear_temp_status(self):
        """Clear temporary status"""
        self.status_timer.stop()
    
    def closeEvent(self, event):
        """Handle close event"""
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de salir?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Yes:
                if not self.save_current_company():
                    event.ignore()
                    return
        
        event.accept()


class TiposConfigDialog(QDialog):
    """Dialog for configuring tipos de bienes"""
    
    def __init__(self, tipos_existentes, parent=None):
        super().__init__(parent)
        self.tipos = list(tipos_existentes) if tipos_existentes else []
        self.init_ui()
        self.setStyleSheet(GREY_MOON_STYLE)
    
    def init_ui(self):
        self.setWindowTitle("Configurar Tipos de Bienes")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ Configurar Tipos de Bienes")
        title.setObjectName("subtitle_label")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.tipo_input = QLineEdit()
        self.tipo_input.setPlaceholderText("Nuevo tipo de bien...")
        self.tipo_input.returnPressed.connect(self.add_tipo)
        input_layout.addWidget(self.tipo_input)
        
        add_btn = QPushButton("➕ Agregar")
        add_btn.setObjectName("success_btn")
        add_btn.clicked.connect(self.add_tipo)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        
        # List widget
        self.list_widget = QTableWidget()
        self.list_widget.setColumnCount(1)
        self.list_widget.setHorizontalHeaderLabels(["Tipo de Bien"])
        self.list_widget.horizontalHeader().setStretchLastSection(True)
        self.list_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)
        
        # Load existing
        self.refresh_list()
        
        # If empty, add defaults
        if not self.tipos:
            defaults = ["Maquinaria", "Muebles y Útiles", "Rodados", "Inmuebles", "Herramientas"]
            self.tipos = defaults
            self.refresh_list()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_btn = QPushButton("🗑 Eliminar Seleccionado")
        remove_btn.setObjectName("danger_btn")
        remove_btn.clicked.connect(self.remove_tipo)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        confirm_btn = QPushButton("✅ Confirmar")
        confirm_btn.setObjectName("success_btn")
        confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(confirm_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_list(self):
        """Refresh the list"""
        self.list_widget.setRowCount(0)
        for tipo in self.tipos:
            row = self.list_widget.rowCount()
            self.list_widget.insertRow(row)
            item = QTableWidgetItem(tipo)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.list_widget.setItem(row, 0, item)
    
    def add_tipo(self):
        """Add new tipo"""
        tipo = self.tipo_input.text().strip()
        if tipo and tipo not in self.tipos:
            self.tipos.append(tipo)
            self.refresh_list()
            self.tipo_input.clear()
    
    def remove_tipo(self):
        """Remove selected tipo"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.tipos):
            del self.tipos[current_row]
            self.refresh_list()
    
    def get_tipos(self):
        """Get configured tipos"""
        return self.tipos


class BienDialog(QDialog):
    """Dialog for creating/editing a bien"""
    
    def __init__(self, tipos_bienes, bien=None, parent=None):
        super().__init__(parent)
        self.tipos_bienes = tipos_bienes
        self.bien = bien
        self.is_edit = bien is not None
        self.init_ui()
        self.setStyleSheet(GREY_MOON_STYLE)
    
    def init_ui(self):
        title = "Editar Bien" if self.is_edit else "Nuevo Bien"
        self.setWindowTitle(title)
        self.setMinimumSize(600, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(f"📝 {title}")
        title_label.setObjectName("subtitle_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        # Fields
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descripción del bien...")
        form_layout.addRow("Descripción:*", self.desc_input)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(self.tipos_bienes)
        form_layout.addRow("Tipo de Bien:*", self.tipo_combo)
        
        self.amort_check = QCheckBox("Es amortizable")
        self.amort_check.setChecked(True)
        form_layout.addRow("", self.amort_check)
        
        self.anos_spin = QSpinBox()
        self.anos_spin.setRange(1, 100)
        self.anos_spin.setValue(5)
        form_layout.addRow("Años amortización:", self.anos_spin)
        
        self.ejercicio_spin = QSpinBox()
        self.ejercicio_spin.setRange(1900, 2100)
        self.ejercicio_spin.setValue(2024)
        form_layout.addRow("Ejercicio alta:", self.ejercicio_spin)
        
        self.fecha_ing_input = QLineEdit()
        self.fecha_ing_input.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow("Fecha ingreso:*", self.fecha_ing_input)
        
        self.fecha_baja_input = QLineEdit()
        self.fecha_baja_input.setPlaceholderText("DD/MM/AAAA (opcional)")
        form_layout.addRow("Fecha baja:", self.fecha_baja_input)
        
        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Use , para decimales (ej: 1.234.567,89)")
        form_layout.addRow("Valor origen:*", self.valor_input)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Load data if editing
        if self.is_edit:
            self.load_bien_data()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("✅ Guardar")
        save_btn.setObjectName("success_btn")
        save_btn.clicked.connect(self.save_bien)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_bien_data(self):
        """Load bien data into form"""
        if not self.bien:
            return
        
        self.desc_input.setText(self.bien.descripcion)
        
        index = self.tipo_combo.findText(self.bien.tipo_bien)
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
        
        self.amort_check.setChecked(self.bien.es_amortizable)
        self.anos_spin.setValue(self.bien.anos_amortizacion)
        self.ejercicio_spin.setValue(self.bien.ejercicio_alta)
        self.fecha_ing_input.setText(self.bien.fecha_ingreso)
        
        if self.bien.fecha_baja:
            self.fecha_baja_input.setText(self.bien.fecha_baja)
        
        self.valor_input.setText(Validators.format_decimal_argentino(self.bien.valor_origen))
    
    def save_bien(self):
        """Validate and save bien"""
        try:
            # Validations
            descripcion = self.desc_input.text().strip()
            if not descripcion:
                self.show_error("La descripción es obligatoria")
                return
            
            tipo_bien = self.tipo_combo.currentText()
            if not tipo_bien:
                self.show_error("Seleccione un tipo de bien")
                return
            
            fecha_ingreso = self.fecha_ing_input.text().strip()
            if not Validators.validar_fecha(fecha_ingreso):
                self.show_error("Fecha de ingreso debe tener formato DD/MM/AAAA")
                return
            
            valor_origen_str = self.valor_input.text().strip()
            if not valor_origen_str:
                self.show_error("El valor origen es obligatorio")
                return
            
            valor_origen = Validators.parse_decimal_argentino(valor_origen_str)
            if valor_origen <= 0:
                self.show_error("El valor origen debe ser mayor a cero")
                return
            
            es_amortizable = self.amort_check.isChecked()
            anos_amortizacion = self.anos_spin.value()
            ejercicio_alta = self.ejercicio_spin.value()
            
            fecha_baja = self.fecha_baja_input.text().strip() or None
            if fecha_baja and not Validators.validar_fecha(fecha_baja):
                self.show_error("Fecha de baja debe tener formato DD/MM/AAAA")
                return
            
            # Create bien
            self.result_bien = Bien(
                id=self.bien.id if self.bien else 0,
                descripcion=descripcion,
                tipo_bien=tipo_bien,
                es_amortizable=es_amortizable,
                anos_amortizacion=anos_amortizacion,
                ejercicio_alta=ejercicio_alta,
                fecha_ingreso=fecha_ingreso,
                fecha_baja=fecha_baja,
                valor_origen=valor_origen
            )
            
            self.accept()
            
        except Exception as e:
            self.show_error(f"Error guardando bien: {str(e)}")
    
    def get_bien(self):
        """Get the created/edited bien"""
        return self.result_bien
    
    def show_error(self, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Bienes de Uso")
    app.setOrganizationName("ModernUI")
    
    # Create and show main window
    window = ModernBienesApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
